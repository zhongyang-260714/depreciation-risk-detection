"""P7 · 智能标注（DeepSeek AI 驱动）

六步流水线可视化：
① 下载年报 → ② 关键词定位 → ③ DeepSeek草拟
→ ④ 程序验真 → ⑤ 综合算分 → ⑥ 人工复核

支持：美股10-K（SEC EDGAR）+ A股年报（巨潮资讯网）
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import re
import streamlit as st

import ui_common as ui
from data_loader import REPO_ROOT, find_case

sys.path.insert(0, str(REPO_ROOT))
from src.ai_annotation import (
    DeepSeekClient,
    apply_hard_rules,
    compute_composite_score,
    enrich_dimension_scores,
    fetch_annual_report,
    load_10k_html,
    locate_candidates_batch,
    locate_cn_candidates,
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
    """五维评分表格。兼容AI标注和人工标注的不同键名。"""
    if not dim_scores:
        st.info("无维度评分数据。")
        return
    rows = []
    for d in dim_scores:
        # 兼容AI标注(dimension_id/dimension_name)和人工标注(id/name)的不同键名
        dim_id = d.get("dimension_id") or d.get("id", "?")
        dim_name = d.get("dimension_name") or d.get("name", "未知")
        weight = d.get("weight", 0)
        score = d.get("score", 0)
        rows.append({
            "维度": f"{dim_id} {dim_name}",
            "权重": f"{weight:.2f}",
            "得分": score,
            "贡献": f"{weight * score:.2f}",
            "评级": d.get("score_label", d.get("level", "—")),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)


def _render_signals_with_verification(signals: list[dict], verifications: list[dict]):
    """信号列表 + 验真状态。"""
    if not signals:
        st.info("未生成风险信号。")
        return

    verif_map = {v["signal_id"]: v for v in verifications}

    for sig in signals:
        sig_id = sig.get("signal_id", "UNKNOWN")
        v = verif_map.get(sig_id, {"passed": False, "method": "unknown", "confidence": 0.0})
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
        _render_dimension_table(ai_case.get("dimensions", []))
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
        "支持 **美股 10-K**（SEC EDGAR）与 **A股年报**（巨潮资讯网）两种模式。"
        "系统自动完成 下载年报 → 关键词定位 → AI 草拟标注 → 程序验真 → 综合算分 全流水线。"
    )

    # ---- 输入区 ----
    cases = data.get("cases", [])
    tickers = sorted({c["ticker"] for c in cases})
    name_map = {c["ticker"]: c["name"] for c in cases}

    mode = st.radio(
        "输入模式",
        ["选择已有公司", "手动输入Ticker（美股）", "上传本地 10-K HTML", "A股年报（上传PDF）"],
        horizontal=True,
        key="p7_mode",
    )

    ticker = None
    fiscal_year = None
    uploaded_html = None
    uploaded_pdf = None
    is_cn = False  # 是否为A股模式

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
    elif mode == "手动输入Ticker（美股）":
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.text_input("输入 Ticker（如 GOOGL, META, NVDA）", value="", key="p7_manual_ticker")
        with col2:
            fiscal_year = st.number_input("财年", min_value=2000, max_value=2030, value=2023, key="p7_manual_fy")
    elif mode == "上传本地 10-K HTML":
        uploaded_file = st.file_uploader("上传 10-K HTML 文件", type=["html", "htm"], key="p7_upload")
        if uploaded_file:
            uploaded_html = uploaded_file.getvalue().decode("utf-8", errors="replace")
        ticker = st.text_input("公司 Ticker（用于信号 ID 生成）", value="UNKNOWN", key="p7_upload_ticker")
        fiscal_year = st.number_input("财年", min_value=2000, max_value=2030, value=2024, key="p7_upload_fy")
    elif mode == "A股年报（上传PDF）":
        is_cn = True
        st.info("📌 巨潮资讯网自动下载API暂时不可用（返回空数据），请手动下载年报PDF后上传。下载地址：http://www.cninfo.com.cn")
        uploaded_file = st.file_uploader("上传 A股年报 PDF 文件", type=["pdf"], key="p7_cn_upload")
        if uploaded_file:
            uploaded_pdf = uploaded_file.getvalue()
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.text_input("输入股票代码（如 688256.SH / 603881.SH）", value="", key="p7_cn_upload_code")
        with col2:
            fiscal_year = st.number_input("报告年份", min_value=2015, max_value=2030, value=2024, key="p7_cn_upload_year")
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
    # 六步流水线（美股分支）
    # ================================================================
    if not is_cn:
        _run_us_pipeline(client, mode, ticker, fiscal_year, uploaded_html, cases, data)
    else:
        _run_cn_pipeline(client, mode, ticker, fiscal_year, uploaded_pdf)


def _run_us_pipeline(client, mode, ticker, fiscal_year, uploaded_html, cases, data):
    """美股 10-K 流水线。"""
    result_container = {}
    actual_fy = None

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
                actual_fy = None
                if html_text.startswith("<!-- actual_fiscal_year:"):
                    m = re.search(r"<!-- actual_fiscal_year: (\d+) \(requested: (\d+)\) -->", html_text)
                    if m:
                        actual_fy = int(m.group(1))
                        requested_fy = int(m.group(2))
                        st.warning(f"⚠️ 未找到精确匹配的 FY{requested_fy}，已回退到 FY{actual_fy}")
            status.update(label="✅ 步骤 1/6：10-K 获取完成", state="complete")
        except Exception as e:
            status.update(label=f"❌ 步骤 1/6 失败：{e}", state="error")
            st.error(f"无法获取 10-K：{e}")
            return

    # ② 关键词定位
    with st.status("🔍 步骤 2/6：关键词矩阵定位候选段落...", expanded=True) as status:
        candidates = locate_candidates_batch(html_text, max_candidates=50)
        # 防御：过滤非字典元素
        candidates = [c for c in candidates if isinstance(c, dict)]
        st.write(f"发现 {len(candidates)} 个候选段落")
        strength_counts = {}
        for c in candidates:
            strength = c.get("signal_strength") or c.get("keyword_strength", "unknown")
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        for s, n in sorted(strength_counts.items(), key=lambda x: {"strongest": 3, "strong": 2, "medium": 1}.get(x[0], 0), reverse=True):
            st.write(f"  - {s}: {n} 段")
        status.update(label=f"✅ 步骤 2/6：定位到 {len(candidates)} 个候选段落", state="complete")

    if not candidates:
        st.warning("未定位到任何候选段落，可能是该 10-K 中折旧/减值相关披露极少。")
        return

    # ③ DeepSeek 草拟
    with st.status("🤖 步骤 3/6：DeepSeek 草拟证据链与维度评分...", expanded=True) as status:
        try:
            company_meta = {"ticker": str(ticker).upper(), "fiscal_year": int(fiscal_year), "industry": "Technology"}
            ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="en")
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
        status.update(label=f"✅ 步骤 4/6：验真完成（通过率 {verification['pass_rate'] * 100:.0f}%）", state="complete")

    # ④.5 规则引擎
    with st.status("⚙️ 步骤 4.5/6：规则引擎硬规则修正...", expanded=True) as status:
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        st.write(f"AI 原始分：{composite_before['weighted_score']:.2f}")
        dim_scores, rules_triggered = apply_hard_rules(dim_scores_before, candidates, ai_raw, full_html=html_text)
        composite = compute_composite_score(dim_scores)
        if rules_triggered:
            st.write(f"🎯 触发 {len(rules_triggered)} 条硬规则：")
            for rule in rules_triggered:
                st.write(f"  • {rule}")
        status.update(label=f"✅ 步骤 4.5/6：规则引擎完成", state="complete")

    _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered,
                     ticker, fiscal_year, actual_fy, mode, cases, data)


def _run_cn_pipeline(client, mode, ticker, fiscal_year, uploaded_pdf):
    """A股年报流水线。"""
    import pdfplumber

    # ① 下载/读取 PDF
    with st.status("📥 步骤 1/6：获取 A股年报 PDF...", expanded=True) as status:
        try:
            if uploaded_pdf:
                st.write("使用上传的本地 PDF 文件")
                pdf_bytes = uploaded_pdf
            else:
                st.write(f"从巨潮资讯网下载 {ticker} {fiscal_year} 年报...")
                pdf_path, company_name = fetch_annual_report(str(ticker), int(fiscal_year), cache_dir=CACHE_DIR / "cn")
                st.write(f"✅ 下载完成：{company_name}")
                pdf_bytes = pdf_path.read_bytes()

            # 提取文本
            st.write("正在提取PDF文本...")
            full_text = ""
            with pdfplumber.open(BytesIO(pdf_bytes) if uploaded_pdf else pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- 第{i+1}页 ---\n{text}\n"
            st.write(f"✅ 文本提取完成，共 {len(full_text):,} 字符")
            status.update(label="✅ 步骤 1/6：年报获取完成", state="complete")
        except Exception as e:
            status.update(label=f"❌ 步骤 1/6 失败：{e}", state="error")
            st.error(f"无法获取年报：{e}")
            return

    # ② 中文关键词定位
    with st.status("🔍 步骤 2/6：中文关键词矩阵定位候选段落...", expanded=True) as status:
        candidates = locate_cn_candidates(full_text, max_candidates=50)
        # 防御：过滤非字典元素
        candidates = [c for c in candidates if isinstance(c, dict)]
        st.write(f"发现 {len(candidates)} 个候选段落")
        strength_counts = {}
        for c in candidates:
            strength = c.get("signal_strength") or c.get("keyword_strength", "unknown")
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        for s, n in sorted(strength_counts.items(), key=lambda x: {"strongest": 3, "strong": 2, "medium": 1}.get(x[0], 0), reverse=True):
            st.write(f"  - {s}: {n} 段")
        status.update(label=f"✅ 步骤 2/6：定位到 {len(candidates)} 个候选段落", state="complete")

    if not candidates:
        st.warning("未定位到任何候选段落，可能是该年报中折旧/减值相关披露极少。")
        return

    # ③ DeepSeek 中文草拟
    with st.status("🤖 步骤 3/6：DeepSeek 中文草拟证据链与维度评分...", expanded=True) as status:
        try:
            company_meta = {"ticker": str(ticker).upper(), "fiscal_year": int(fiscal_year), "industry": "Technology"}
            ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="cn")
            n_signals = len(ai_raw.get("risk_signals", []))
            n_dims = len(ai_raw.get("dimension_scores", []))
            st.write(f"AI 生成 {n_signals} 条信号，{n_dims} 个维度评分")
            status.update(label=f"✅ 步骤 3/6：AI 草拟完成（{n_signals} 条信号）", state="complete")
        except Exception as e:
            status.update(label=f"❌ 步骤 3/6 失败：{e}", state="error")
            st.error(f"DeepSeek 调用失败：{e}")
            return

    # ④ 程序验真（中文适配：简化为文本包含检查）
    with st.status("🔐 步骤 4/6：程序验真（中文模式）...", expanded=True) as status:
        # 中文验真：检查原文摘录是否在PDF文本中（模糊匹配）
        signals = ai_raw.get("risk_signals", [])
        passed = 0
        failed = 0
        verif_results = []
        for sig in signals:
            excerpt = sig.get("text_excerpt", "")
            # 简化的验真：检查摘录的前20个字符是否在原文中
            if excerpt and excerpt[:20] in full_text:
                passed += 1
                verif_results.append({"signal_id": sig.get("signal_id", ""), "passed": True, "method": "substring", "confidence": 1.0})
            else:
                failed += 1
                verif_results.append({"signal_id": sig.get("signal_id", ""), "passed": False, "method": "substring", "confidence": 0.0})
        total = len(signals)
        verification = {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": passed / total if total > 0 else 0,
            "results": verif_results,
            "failed_signals": [s for s, v in zip(signals, verif_results) if not v["passed"]],
        }
        st.write(f"验真通过 {verification['passed']} / {verification['total']} 条")
        st.write(f"通过率 {verification['pass_rate'] * 100:.0f}%")
        status.update(label=f"✅ 步骤 4/6：验真完成（通过率 {verification['pass_rate'] * 100:.0f}%）", state="complete")

    # ⑤ 综合算分（A股规则引擎暂用英文规则，后续可扩展中文规则）
    with st.status("🧮 步骤 5/6：程序计算综合评分...", expanded=True) as status:
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        # A股规则引擎：暂用相同规则（阈值逻辑跨语言通用）
        dim_scores, rules_triggered = apply_hard_rules(dim_scores_before, candidates, ai_raw, full_html=full_text)
        composite = compute_composite_score(dim_scores)
        st.write(f"综合评分：{composite['weighted_score']:.2f}（{composite['risk_level']}）")
        st.write(f"验算式：{composite['score_breakdown']}")
        status.update(label=f"✅ 步骤 5/6：综合评分 {composite['weighted_score']:.2f}", state="complete")

    _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered,
                     ticker, fiscal_year, None, mode, [], {})


def _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered,
                     ticker, fiscal_year, actual_fy, mode, cases, data):
    """统一展示结果（美股/A股共用）。"""
    ai_case = {
        "ticker": str(ticker).upper(),
        "fiscal_year": int(fiscal_year),
        "actual_fiscal_year": actual_fy,
        "score": composite["weighted_score"],
        "risk_level": composite["risk_level"],
        "color": _color_of(composite["risk_level"]),
        "review_status": "draft_pending_review",
        "is_draft": True,
        "dimensions": dim_scores,
        "signals": ai_raw.get("risk_signals", []),
        "composite_score": composite,
        "composite_score_before_rules": composite_before.get("weighted_score") if rules_triggered else None,
        "rules_triggered": rules_triggered,
        "verification": verification,
        "accounting_policy": ai_raw.get("accounting_policy", {}),
        "summary": ai_raw.get("summary", ""),
    }

    st.divider()
    st.markdown("### 📋 人工复核")

    if actual_fy and actual_fy != int(fiscal_year):
        st.warning(f"⚠️ 实际分析的是 FY{actual_fy} 的 10-K（请求的是 FY{fiscal_year}）。")

    if rules_triggered:
        with st.container():
            st.markdown("### ⚙️ 规则引擎修正")
            cols = st.columns([1, 2])
            with cols[0]:
                st.metric("AI 原始分", f"{composite_before['weighted_score']:.2f}")
            with cols[1]:
                st.metric("规则修正后", f"{composite['weighted_score']:.2f}",
                         delta=f"{composite['weighted_score'] - composite_before['weighted_score']:+.2f}")
            for rule in rules_triggered:
                st.markdown(f"- {rule}")
            st.info("📌 规则引擎覆盖 D1（年限错配）、D2（年限变更）、D4（CAPEX强度）。D3/D5 由 DeepSeek 独立评分。")
            st.divider()

    _render_score_card(composite["weighted_score"], composite["risk_level"], composite["score_breakdown"])

    human_case = None
    if mode == "选择已有公司":
        human_case = find_case(cases, str(ticker).upper(), int(fiscal_year))
    if human_case:
        ui.section("AI 草稿 vs 人工标注（并排对照）")
        _render_side_by_side(ai_case, human_case)

    ui.section("五维评分明细")
    _render_dimension_table(dim_scores)

    ui.section(f"风险信号列表（{len(ai_raw.get('risk_signals', []))} 条，含验真状态）")
    _render_signals_with_verification(ai_raw.get("risk_signals", []), verification.get("results", []))

    if verification.get("failed_signals"):
        with st.expander(f"🔴 验真未通过的信号（{len(verification['failed_signals'])} 条）", expanded=False):
            st.markdown("以下信号的程序验真未通过，可能是 AI 编造或文本截断导致。请人工判断。")
            for sig in verification["failed_signals"]:
                st.markdown(f"**{sig.get('signal_id', 'UNKNOWN')}**")
                st.code(sig.get("text_excerpt", "")[:300], language="text")
                st.markdown("---")

    policy = ai_raw.get("accounting_policy")
    if policy:
        ui.section("AI 提取的会计政策要点")
        for k, v in policy.items():
            if v:
                st.markdown(f"- **{k}**：{v}")

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
            _save_draft(ai_case)
            st.success("✅ 已保存为 confirmed 标注！")
    with col_discard:
        if st.button("🗑️ 丢弃草稿", key="p7_discard"):
            st.info("草稿已丢弃，未保存。")

    with st.expander("技术说明（答辩备查）"):
        st.markdown(
            "- **关键词矩阵**：美股6词三级检索 / A股中文三级检索\n"
            "- **DeepSeek**：`deepseek-chat` 模型，温度 0.2，强制 JSON 输出\n"
            "- **验真逻辑**：美股=全文逐字匹配+模糊匹配；A股=子串包含检查\n"
            "- **算分逻辑**：程序执行 `Σ(维度分 × 权重)`，DeepSeek 只给维度分建议\n"
            "- **双签制**：AI 草拟 → 程序验真 → 人工终审\n"
            "- **A股适配**：巨潮PDF下载 + pdfplumber提取 + 中文关键词 + 中文提示词"
        )


def _save_draft(ai_case: dict):
    """将 AI 草稿保存到 data/annotated/ 目录。"""
    import json
    ticker = ai_case["ticker"]
    fy = ai_case["fiscal_year"]
    out_dir = REPO_ROOT / "data" / "annotated"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {
            "version": "1.0",
            "annotation_schema": "Depreciation Risk Annotation Schema v1.0",
            "annotated_at": pd.Timestamp.now().isoformat(),
            "annotator": "DeepSeek AI + Program Verification",
            "review_status": "confirmed",
            "filing_source": "SEC EDGAR / 巨潮资讯网",
            "ai_annotation": True,
        },
        "company": {"ticker": ticker, "name": ticker, "fiscal_year": fy},
        "composite_score": ai_case["composite_score"],
        "dimension_scores": ai_case["dimensions"],
        "risk_signals": ai_case["signals"],
        "accounting_policy": ai_case.get("accounting_policy", {}),
        "summary": ai_case.get("summary", ""),
    }
    out_path = out_dir / f"{ticker}_{fy}_ai_annotation.json"
    counter = 1
    original_path = out_path
    while out_path.exists():
        out_path = original_path.with_suffix(f"_{counter}.json")
        counter += 1
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    st.caption(f"已保存至：{out_path}")
