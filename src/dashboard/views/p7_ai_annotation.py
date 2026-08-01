"""P7 · 智能标注（DeepSeek AI 驱动）

六步流水线可视化：
① EDGAR下载 → ② 关键词定位 → ③ DeepSeek草拟
→ ④ 程序验真 → ⑤ 综合算分 → ⑥ 人工复核

核心设计理念：
- AI 草拟 + 程序验真 + 人工复核 = 可演示的双签制闭环
- 并排对照：AI 草稿 vs 人工 confirmed 标注
- 验真未通过的信号红标展示，不入主列表
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_common as ui
from data_loader import REPO_ROOT, find_case

sys.path.insert(0, str(REPO_ROOT))
from src.ai_annotation import (
    DeepSeekClient,
    compute_composite_score,
    enrich_dimension_scores,
    load_10k_html,
    locate_candidates_batch,
    verify_all,
)

# 风险等级颜色（与 data_loader 保持一致）
LEVEL_COLORS = {
    "高风险": "#B3402F",
    "中高风险": "#C07A1B",
    "中风险": "#D9A62E",
    "低风险": "#2E7D5B",
}
DEFAULT_COLOR = "#8A877F"

CACHE_DIR = REPO_ROOT / "data" / "raw"


# ------------------------------------------------------------------
# 辅助渲染函数
# ------------------------------------------------------------------
def _color_of(level: str) -> str:
    return LEVEL_COLORS.get(level, DEFAULT_COLOR)


def _render_score_card(score: float, level: str, breakdown: str):
    """综合分大卡片。"""
    color = _color_of(level)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"""<div class="card" style="text-align:center">
                <div class="big-score" style="color:{color}">
                {score:.2f}<small> / 5.00</small></div>
                <div style="margin-top:0.4rem">
                    {ui.risk_badge(level, color)}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(f"<div class='formula'>{breakdown}</div>", unsafe_allow_html=True)
        st.caption("验算式由程序计算，AI 不直接算数。")


def _render_dimension_table(dim_scores: list[dict]):
    """五维评分表格。"""
    if not dim_scores:
        st.info("无维度评分数据。")
        return
    rows = []
    for d in dim_scores:
        rows.append({
            "维度": f"{d['dimension_id']} {d['dimension_name']}",
            "权重": f"{d['weight']:.2f}",
            "得分": d["score"],
            "贡献": f"{d['weight'] * d['score']:.2f}",
            "评级": d.get("score_label", "—"),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)


def _render_signals_with_verification(signals: list[dict], verifications: list[dict]):
    """信号列表 + 验真状态。"""
    if not signals:
        st.info("未生成风险信号。")
        return

    # 建立 signal_id → verification 映射
    verif_map = {v["signal_id"]: v for v in verifications}

    for sig in signals:
        sig_id = sig.get("signal_id", "UNKNOWN")
        v = verif_map.get(sig_id, {"passed": False, "method": "unknown", "confidence": 0.0})

        # 标题颜色：通过=正常，未通过=红色
        status_icon = "🟢" if v["passed"] else "🔴"
        status_text = f"验真{v['method']}" if v["passed"] else "验真未通过"

        sev = str(sig.get("severity", "—")).upper()
        title = f"{status_icon} {sev} · {sig.get('risk_type', '—')} · {sig_id}"

        with st.expander(title):
            st.markdown(f"<span style='color:{ui.MUTED};font-size:0.82rem'>{status_text}</span>",
                       unsafe_allow_html=True)

            if sig.get("text_excerpt"):
                st.markdown("**原文摘录**")
                st.code(sig["text_excerpt"][:500], language="text")

            if sig.get("accounting_meaning"):
                st.markdown(f"**会计含义**：{sig['accounting_meaning']}")

            chain = sig.get("evidence_chain")
            if chain:
                if isinstance(chain, list):
                    st.markdown("**推断链**：")
                    for i, step in enumerate(chain, 1):
                        st.markdown(f"{i}. {step}")
                else:
                    st.markdown(f"**推断链**：{chain}")

            st.markdown(f"**来源**：{sig.get('source', '—')}")
            st.markdown(f"**位置**：{sig.get('page_location', '—')}")
            st.markdown(f"**命中关键词**：`{sig.get('keyword_matched', '—')}`")


def _render_side_by_side(ai_case: dict, human_case: dict | None):
    """并排对照：AI 草稿 vs 人工标注。"""
    if human_case is None:
        st.info("库中暂无该公司的人工 confirmed 标注，无法对照。")
        return

    col_ai, col_human = st.columns(2)

    with col_ai:
        st.markdown("**🤖 AI 草拟**")
        ai_score = ai_case.get("composite_score", {}).get("weighted_score", 0)
        ai_level = ai_case.get("composite_score", {}).get("risk_level", "未知")
        ai_color = _color_of(ai_level)
        st.markdown(
            f"<div class='card' style='text-align:center'>"
            f"<div style='font-size:1.8rem;font-weight:800;color:{ai_color}'>{ai_score:.2f}</div>"
            f"<div>{ui.risk_badge(ai_level, ai_color)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        _render_dimension_table(ai_case.get("dimension_scores", []))

    with col_human:
        st.markdown("**👤 人工标注（confirmed）**")
        h_score = human_case.get("score", 0)
        h_level = human_case.get("risk_level", "未知")
        h_color = human_case.get("color", DEFAULT_COLOR)
        st.markdown(
            f"<div class='card' style='text-align:center'>"
            f"<div style='font-size:1.8rem;font-weight:800;color:{h_color}'>{h_score:.2f}</div>"
            f"<div>{ui.risk_badge(h_level, h_color)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        _render_dimension_table(human_case.get("dimensions", []))

    # 差异提示
    diff = ai_score - h_score
    if abs(diff) <= 0.5:
        st.success(f"✅ AI 与人工评分接近（差值 {diff:+.2f}）")
    elif abs(diff) <= 0.8:
        st.warning(f"⚠️ AI 与人工评分有偏差（差值 {diff:+.2f}），建议复核维度分")
    else:
        st.error(f"🔴 AI 与人工评分偏差较大（差值 {diff:+.2f}），请重点复核")


# ------------------------------------------------------------------
# 主渲染函数
# ------------------------------------------------------------------
def render(data: dict) -> None:
    st.subheader("P7 · 智能标注（DeepSeek AI 驱动）")
    st.markdown(
        "输入公司代码 + 财年，系统自动完成 **下载 10-K → 关键词定位 → AI 草拟标注 → 程序验真 → 综合算分** 全流水线。"
        "AI 产出为 **草稿待审** 状态，人工确认后才可入库。"
    )

    # ---- 输入区 ----
    cases = data.get("cases", [])
    tickers = sorted({c["ticker"] for c in cases})
    name_map = {c["ticker"]: c["name"] for c in cases}

    mode = st.radio("输入模式", ["选择已有公司", "上传本地 10-K HTML"], horizontal=True, key="p7_mode")

    ticker = None
    fiscal_year = None
    uploaded_html = None

    if mode == "选择已有公司":
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.selectbox(
                "选择公司", tickers,
                format_func=lambda t: f"{name_map.get(t, t)}（{t}）",
                key="p7_ticker",
            )
        with col2:
            years = sorted({c["fiscal_year"] for c in cases if c["ticker"] == ticker})
            fiscal_year = st.selectbox("财年", years, key="p7_fy")
    else:
        uploaded_file = st.file_uploader("上传 10-K HTML 文件", type=["html", "htm"], key="p7_upload")
        if uploaded_file:
            uploaded_html = uploaded_file.getvalue().decode("utf-8", errors="replace")
        ticker = st.text_input("公司 Ticker（用于信号 ID 生成）", value="UNKNOWN", key="p7_upload_ticker")
        fiscal_year = st.number_input("财年", min_value=2000, max_value=2030, value=2024, key="p7_upload_fy")

    # ---- DeepSeek API 检查 ----
    api_ok = False
    try:
        client = DeepSeekClient()
        api_ok = client.health_check()
    except Exception as e:
        st.error(f"DeepSeek API 未配置或不可用：{e}")

    if not api_ok:
        st.warning("⚠️ DeepSeek API 当前不可用。请检查环境变量 `DEEPSEEK_API_KEY` 是否设置正确。")
        return

    # ---- 运行按钮 ----
    run_btn = st.button("▶ 启动智能标注流水线", type="primary", key="p7_run", disabled=not api_ok)

    if not run_btn:
        st.info("点击上方按钮启动六步流水线。")
        return

    # ================================================================
    # 六步流水线
    # ================================================================
    result_container = {}

    # ① 下载 10-K
    with st.status("📥 步骤 1/6：获取 10-K 原文...", expanded=True) as status:
        try:
            if uploaded_html:
                html_text = uploaded_html
                st.write("使用上传的本地 HTML 文件")
            else:
                st.write(f"从 SEC EDGAR 下载 {ticker} FY{fiscal_year} 10-K...")
                html_text = load_10k_html(str(ticker), int(fiscal_year), cache_dir=CACHE_DIR)
                st.write(f"✅ 下载完成，文本长度 {len(html_text):,} 字符")
            status.update(label="✅ 步骤 1/6：10-K 获取完成", state="complete")
        except Exception as e:
            status.update(label=f"❌ 步骤 1/6 失败：{e}", state="error")
            st.error(f"无法获取 10-K：{e}")
            return

    # ② 关键词定位
    with st.status("🔍 步骤 2/6：关键词矩阵定位候选段落...", expanded=True) as status:
        candidates = locate_candidates_batch(html_text, max_candidates=50)
        st.write(f"发现 {len(candidates)} 个候选段落")
        # 按强度统计
        strength_counts = {}
        for c in candidates:
            strength_counts[c["signal_strength"]] = strength_counts.get(c["signal_strength"], 0) + 1
        for s, n in sorted(strength_counts.items(), key=lambda x: {"strongest": 3, "strong": 2, "medium": 1}.get(x[0], 0), reverse=True):
            st.write(f"  - {s}: {n} 段")
        status.update(label=f"✅ 步骤 2/6：定位到 {len(candidates)} 个候选段落", state="complete")

    if not candidates:
        st.warning("未定位到任何候选段落，可能是该 10-K 中折旧/减值相关披露极少。")
        return

    # ③ DeepSeek 草拟
    with st.status("🤖 步骤 3/6：DeepSeek 草拟证据链与维度评分...", expanded=True) as status:
        try:
            company_meta = {
                "ticker": str(ticker).upper(),
                "fiscal_year": int(fiscal_year),
                "industry": "Technology",
            }
            ai_raw = client.annotate(candidates, company_meta, temperature=0.2)
            n_signals = len(ai_raw.get("risk_signals", []))
            n_dims = len(ai_raw.get("dimension_scores", []))
            st.write(f"AI 生成 {n_signals} 条信号，{n_dims} 个维度评分")
            status.update(label=f"✅ 步骤 3/6：AI 草拟完成（{n_signals} 条信号）", state="complete")
        except Exception as e:
            status.update(label=f"❌ 步骤 3/6 失败：{e}", state="error")
            st.error(f"DeepSeek 调用失败：{e}")
            return

    # ④ 程序验真
    with st.status("🔐 步骤 4/6：程序逐字验真（防编造）...", expanded=True) as status:
        verification = verify_all(ai_raw, html_text)
        st.write(f"验真通过 {verification['passed']} / {verification['total']} 条")
        st.write(f"通过率 {verification['pass_rate'] * 100:.0f}%")
        if verification["failed"] > 0:
            st.write(f"未通过 {verification['failed']} 条（将在下方红标展示）")
        status.update(
            label=f"✅ 步骤 4/6：验真完成（通过率 {verification['pass_rate'] * 100:.0f}%）",
            state="complete",
        )

    # ⑤ 综合算分
    with st.status("🧮 步骤 5/6：程序计算综合评分...", expanded=True) as status:
        dim_scores = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite = compute_composite_score(dim_scores)
        st.write(f"综合评分：{composite['weighted_score']:.2f}（{composite['risk_level']}）")
        st.write(f"验算式：{composite['score_breakdown']}")
        status.update(label=f"✅ 步骤 5/6：综合评分 {composite['weighted_score']:.2f}", state="complete")

    # 组装 AI 草稿 case 结构（与人工标注同构）
    ai_case = {
        "ticker": str(ticker).upper(),
        "fiscal_year": int(fiscal_year),
        "score": composite["weighted_score"],
        "risk_level": composite["risk_level"],
        "color": _color_of(composite["risk_level"]),
        "review_status": "draft_pending_review",
        "is_draft": True,
        "dimensions": dim_scores,
        "signals": ai_raw.get("risk_signals", []),
        "composite_score": composite,
        "verification": verification,
        "accounting_policy": ai_raw.get("accounting_policy", {}),
        "summary": ai_raw.get("summary", ""),
    }

    result_container["ai_case"] = ai_case

    # ⑥ 结果展示（人工复核界面）
    st.divider()
    st.markdown("### 📋 步骤 6/6：人工复核")

    # 综合分卡片
    _render_score_card(
        composite["weighted_score"],
        composite["risk_level"],
        composite["score_breakdown"],
    )

    # 并排对照
    human_case = None
    if mode == "选择已有公司":
        human_case = find_case(cases, str(ticker).upper(), int(fiscal_year))

    if human_case:
        ui.section("AI 草稿 vs 人工标注（并排对照）")
        _render_side_by_side(ai_case, human_case)

    # 维度评分
    ui.section("五维评分明细")
    _render_dimension_table(dim_scores)

    # 信号列表（含验真状态）
    ui.section(f"风险信号列表（{len(ai_raw.get('risk_signals', []))} 条，含验真状态）")
    _render_signals_with_verification(
        ai_raw.get("risk_signals", []),
        verification.get("results", []),
    )

    # 验真未通过区
    if verification.get("failed_signals"):
        with st.expander(f"🔴 验真未通过的信号（{len(verification['failed_signals'])} 条）", expanded=False):
            st.markdown("以下信号的程序验真未通过，可能是 AI 编造或文本截断导致。请人工判断。")
            for sig in verification["failed_signals"]:
                st.markdown(f"**{sig.get('signal_id', 'UNKNOWN')}**")
                st.code(sig.get("text_excerpt", "")[:300], language="text")
                st.markdown("---")

    # 会计政策
    policy = ai_raw.get("accounting_policy")
    if policy:
        ui.section("AI 提取的会计政策要点")
        for k, v in policy.items():
            if v:
                st.markdown(f"- **{k}**：{v}")

    # 复核操作
    st.divider()
    st.markdown("### ✍️ 复核操作")
    st.markdown(
        "<span style='color:#C07A1B'>📝 当前状态：草稿待审（draft_pending_review）</span>"
        "<br>点击「确认入库」将本条标注保存为 confirmed 状态；"
        "点击「丢弃」则放弃本次 AI 产出。",
        unsafe_allow_html=True,
    )

    col_confirm, col_discard = st.columns(2)
    with col_confirm:
        if st.button("✅ 确认入库（confirmed）", type="primary", key="p7_confirm"):
            # 保存为 JSON
            _save_draft(ai_case)
            st.success("✅ 已保存为 confirmed 标注！")
    with col_discard:
        if st.button("🗑️ 丢弃草稿", key="p7_discard"):
            st.info("草稿已丢弃，未保存。")

    # 技术说明
    with st.expander("技术说明（答辩备查）"):
        st.markdown(
            "- **关键词矩阵**：6 词三级检索（strongest/strong/medium），XBRL 噪声自动排除\n"
            "- **DeepSeek**：`deepseek-chat` 模型，温度 0.2，强制 JSON 输出\n"
            "- **验真逻辑**：①全文逐字匹配 → ②行号区域匹配 → ③模糊匹配（difflib ≥ 0.85）\n"
            "- **算分逻辑**：程序执行 `Σ(维度分 × 权重)`，DeepSeek 只给维度分建议\n"
            "- **双签制**：AI 草拟 → 程序验真 → 人工终审，与报告 3.6 节方法论完全一致\n"
            "- **定位**：P7 为报告 5.5 节路线图的首项已实现原型"
        )


def _save_draft(ai_case: dict):
    """将 AI 草稿保存到 data/annotated/ 目录，状态设为 confirmed。"""
    import json
    from pathlib import Path

    ticker = ai_case["ticker"]
    fy = ai_case["fiscal_year"]
    out_dir = REPO_ROOT / "data" / "annotated"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 构建标准 JSON 结构
    output = {
        "metadata": {
            "version": "1.0",
            "annotation_schema": "Depreciation Risk Annotation Schema v1.0",
            "annotated_at": pd.Timestamp.now().isoformat(),
            "annotator": "DeepSeek AI + Program Verification",
            "review_status": "confirmed",
            "filing_source": "SEC EDGAR - 10-K Annual Report",
            "ai_annotation": True,
        },
        "company": {
            "ticker": ticker,
            "name": ticker,
            "fiscal_year": fy,
        },
        "composite_score": ai_case["composite_score"],
        "dimension_scores": ai_case["dimensions"],
        "risk_signals": ai_case["signals"],
        "accounting_policy": ai_case.get("accounting_policy", {}),
        "summary": ai_case.get("summary", ""),
    }

    out_path = out_dir / f"{ticker}_{fy}_ai_annotation.json"
    # 如果文件已存在，加序号
    counter = 1
    original_path = out_path
    while out_path.exists():
        out_path = original_path.with_suffix(f"_{counter}.json")
        counter += 1

    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    st.caption(f"已保存至：{out_path}")
