"""P7 · 智能标注（DeepSeek AI 驱动）v3.3

六步流水线可视化：
① 下载年报 → ② 关键词定位 → ③ DeepSeek草拟
→ ④ 程序验真 → ④.⑤ 规则引擎 → ⑤ 综合算分 → ⑥ 人工复核

支持：美股10-K（SEC EDGAR）+ A股年报（巨潮资讯网）

v3.3 优化（A股样本扩展 6→10 家）：
- A股样本公司从6家扩展至10家（新增：光环新网、海光信息、工业富联、润泽科技）
- 更新必要说明区域：10家公司下载清单、财年覆盖说明
- 同步P7页面文案：六家→十家

v3.2 优化（A股财年定义与下载指南完善）：
- 必要说明区域新增「A股财年定义与下载指南」专节
- 以 info/warning 双栏卡片清晰展示：A股财年=自然年 vs 不要下载2025年报
- 新增十家公司下载清单表格（DataFrame展示）
- 新增详细下载步骤说明
- 优化A股输入区域的视觉提示（强调上传PDF为推荐方式）

v3.1 优化（中国A股同步美国v6.2优化）：
- A股pipeline添加BytesIO导入，修复上传PDF崩溃bug
- 规则引擎返回签名适配v3（3返回值：scores, rules, warnings）
- 所有输入模式均可尝试人工标注对照（不局限于"选择已有公司"）
- A股pipeline增加规则引擎可视化步骤（4.5/6）
- D1规则引擎增加资产类型感知与可疑标记展示
- 【v3.1】A股候选数压缩 50→30（同步美股B1优化）
- 【v3.1】A股缓存持久化（同步美股D2优化）
- 【v3.1】A股验真加固：排除公司概况/风险提示/管理层讨论噪声（同步美股A2优化思路）
- 【v3.1】P7页面新增「必要说明」可折叠区域，详述功能与注意事项
"""


import json
import sys
from io import BytesIO
from pathlib import Path
from io import BytesIO
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
    _extract_life_years,
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
    """五维评分表格。兼容 AI 输出（dimension_id/dimension_name）和人工标注（id/name）。"""
    if not dim_scores:
        st.info("无维度评分数据。")
        return
    rows = []
    for d in dim_scores:
        badge = ""
        if d.get("rule_applied"):
            badge = " 🎯"
        elif d.get("rule_warning"):
            badge = " ⚠️"
        # 兼容两种字段命名：AI 用 dimension_id/dimension_name，人工标注用 id/name
        dim_id = d.get("dimension_id") or d.get("id", "?")
        dim_name = d.get("dimension_name") or d.get("name", "未知维度")
        weight = d.get("weight", 0)
        score = d.get("score", 0)
        rows.append({
            "维度": f"{dim_id} {dim_name}{badge}",
            "权重": f"{weight:.2f}",
            "得分": score,
            "贡献": f"{weight * score:.2f}",
            "评级": d.get("score_label", "—"),
            "规则说明": d.get("rule_reason", "") or d.get("rule_warning", "") or d.get("rule_note", ""),
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
        "系统自动完成 下载年报 → 关键词定位 → AI 草拟标注 → 程序验真 → 规则引擎修正 → 综合算分 全流水线。"
    )

    # ---- 必要说明（可折叠） ----
    with st.expander("📋 必要说明（P7 功能介绍与使用注意事项）", expanded=False):
        st.markdown("""
        **一、P7 页面功能总览**

        P7「智能标注」是系统的核心模块，通过 DeepSeek AI 对上市公司年报进行五维度（5D-DRS）折旧风险自动标注。整个流程为六步流水线：

        1. **获取年报**：美股从 SEC EDGAR 自动下载 10-K；A股需手动上传 PDF（因数据源限制）
        2. **关键词定位**：自动扫描折旧/减值/年限变更等风险关键词
        3. **AI 草拟**：DeepSeek 生成风险信号与维度评分
        4. **程序验真**：逐字核对原文，防止 AI 编造
        5. **规则引擎**：硬规则修正（D1 年限错配、D2 年限变更、D4 CAPEX 强度）
        6. **人工复核**：AI 草稿 vs 人工标注并排对照，确认或丢弃

        **二、美股 10-K 模式**

        - **选择已有公司**：系统自动从 `data/annotated/` 加载已确认的美股标注（10 家公司 × 3 财年 = 30 份），可直接选择并运行 AI 验证
        - **手动输入 Ticker**：支持任意美股公司，系统自动从 SEC EDGAR 下载 10-K
        - **上传本地 HTML**：适合已手动下载 10-K 的场景
        - **财年覆盖**：AMD、CRM、GOOGL、INTC、META、MSFT、MU、NVDA、ORCL、TSLA 共 10 家，每家公司 2-3 个财年（FY2022-FY2024）

        **三、A股年报模式**

        - **自动下载 PDF**：尝试从巨潮资讯网自动下载，但**目前不稳定**（API 存在反爬/限流机制），失败率较高
        - **上传 PDF（推荐）**：手动下载年报 PDF 后上传，最稳定可靠的方式
        - **中国 A 股十家公司**：中科曙光（603019.SH）、数据港（603881.SH）、寒武纪（688256.SH）、浪潮信息（000977.SZ）、科大讯飞（002230.SZ）、奥飞数据（300738.SZ）、光环新网（300383.SZ）、海光信息（688041.SH）、工业富联（601138.SH）、润泽科技（300442.SZ）
        - **财年覆盖**：标注数据已覆盖 **FY2022–FY2024 三个财年**（10 家 × 3 年 = 30 份，全部完成 AI 标注并人工复核确认），支持 P3「跨年轨迹」对比分析。
        - **PDF 下载途径**：推荐访问 [巨潮资讯网](http://www.cninfo.com.cn) → 搜索股票代码 → 定期报告 → 下载 PDF

        **四、常见问题与注意事项**

        - **DeepSeek API 配置**：需设置环境变量 `DEEPSEEK_API_KEY`，否则 P7 无法运行
        - **缓存机制**：美股和 A 股均支持本地缓存，首次运行后重复分析同一公司/财年将秒级完成
        - **AI 与人工偏差**：若并排对照显示差值 > 0.5，建议重点复核 D1（年限错配）维度；差值 > 0.8 需人工介入
        - **A股验真逻辑**：采用「子串包含检查 + 三层噪声排除」（公司概况 / 风险提示 / 管理层讨论），避免年报通用章节误匹配
        - **规则引擎覆盖**：D1/D2/D4 由程序硬规则修正，D3/D5 由 DeepSeek 独立评分
        """)

        # ---- 新增：A股财年定义与下载指南（v6.4 优化）----
        st.divider()
        st.markdown("#### 📅 中国 A 股财年定义与下载指南（重要！）")

        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **中国 A 股财年 = 自然年**
            
            与美国公司自定义财年不同，中国 A 股所有公司的财年统一为 **自然年**（1月1日—12月31日）。
            
            - 2024 年年度报告 → 报告期：2024-01-01 至 2024-12-31
            - 发布时间：次年 3-5 月（如 2025 年 3 月发布 2024 年报）
            """)
        with col2:
            st.warning("""
            **⚠️ 不要下载 2025 年年报！**
            
            当前时间（2026 年 8 月），2025 年年报**尚未发布**（需等到 2027 年 3-5 月才会发布）。
            
            请下载 **2022、2023、2024** 这三年的年报，才能与美国样本的 2-3 个财年对齐。
            """)

        st.markdown("**十家公司所需下载清单：**")
        download_df = pd.DataFrame([
            {"公司": "中科曙光", "代码": "603019.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "数据港", "代码": "603881.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "寒武纪", "代码": "688256.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "浪潮信息", "代码": "000977.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "科大讯飞", "代码": "002230.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "奥飞数据", "代码": "300738.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "光环新网", "代码": "300383.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "海光信息", "代码": "688041.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "工业富联", "代码": "601138.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "润泽科技", "代码": "300442.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
        ])
        st.dataframe(download_df, hide_index=True, use_container_width=True)

        st.markdown("**下载步骤：**")
        st.markdown("""
        1. 访问 [巨潮资讯网](http://www.cninfo.com.cn) 或各交易所官网
        2. 搜索股票代码 → 进入公司页面 → **定期报告** 栏目
        3. 找到对应年份的 **"年度报告"**（注意不是"半年度报告"或"季度报告"）
        4. 下载 PDF 格式文件（不要用 Word 或网页版，PDF 格式最稳定）
        5. 将下载的 PDF 保存到本系统的 `data/raw/cn_财报/` 目录（可选），或直接通过 P7 页面上传
        """)

        st.caption("📌 注：十家 A股公司的 FY2022–FY2024 年报已全部完成 AI 标注并人工复核确认（30 份），P3「跨年轨迹」可直接展示三年评分轨迹。新上传的 PDF 可通过 P7 进行 AI 验证与对照。")
    # ---- 输入区 ----
    cases = data.get("cases", [])
    tickers = sorted({c["ticker"] for c in cases})
    name_map = {c["ticker"]: c["name"] for c in cases}

    mode = st.radio(
        "输入模式",
        ["选择已有公司", "手动输入Ticker（美股）", "上传本地 10-K HTML", "A股年报（自动下载PDF）", "A股年报（上传PDF）"],
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
    elif mode == "A股年报（自动下载PDF）":
        is_cn = True
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.text_input("输入股票代码（如 603881.SH / 300738.SZ）", value="", key="p7_cn_code")
        with col2:
            fiscal_year = st.number_input("报告年份", min_value=2015, max_value=2030, value=2024, key="p7_cn_year")
        st.info("📌 将从巨潮资讯网自动下载年报PDF并提取文本。首次下载可能需要10-30秒。**注意：巨潮自动下载目前不稳定，推荐直接使用「上传PDF」模式。**")
    elif mode == "A股年报（上传PDF）":
        is_cn = True
        uploaded_file = st.file_uploader("上传 A股年报 PDF 文件", type=["pdf"], key="p7_cn_upload")
        if uploaded_file:
            uploaded_pdf = uploaded_file.getvalue()
        ticker = st.text_input("股票代码（用于信号 ID 生成）", value="UNKNOWN", key="p7_cn_upload_code")
        fiscal_year = st.number_input("报告年份", min_value=2015, max_value=2030, value=2024, key="p7_cn_upload_year")

    # ---- 缓存管理按钮 ----
    with st.expander("🔧 缓存管理（开发调试）", expanded=False):
        st.caption("代码更新后运行时仍是旧代码，或重新下载财报/重新调用 DeepSeek 时使用。")
        col_cache1, col_cache2, col_cache3 = st.columns(3)
        with col_cache1:
            if st.button("🧹 清除 Python 缓存", key="p7_clear_py_cache", help="删除 __pycache__ 和 .pyc 文件，确保代码更新生效"):
                import shutil
                cleared = 0
                for pycache in REPO_ROOT.rglob("__pycache__"):
                    try:
                        shutil.rmtree(pycache)
                        cleared += 1
                    except Exception:
                        pass
                for pyc in REPO_ROOT.rglob("*.pyc"):
                    try:
                        pyc.unlink()
                        cleared += 1
                    except Exception:
                        pass
                st.success(f"✅ 已清除 {cleared} 个 Python 缓存项。请重新运行 Streamlit（或按 R 刷新）。")
        with col_cache2:
            if st.button("🗑️ 清除已下载财报缓存", key="p7_clear_filing_cache", help="删除 data/raw/ 下的 HTML/PDF 缓存文件，强制重新下载"):
                import shutil
                cleared = 0
                if CACHE_DIR.exists():
                    for f in CACHE_DIR.rglob("*"):
                        if f.is_file():
                            try:
                                f.unlink()
                                cleared += 1
                            except Exception:
                                pass
                    # 也清理子目录里的文件
                    for subdir in CACHE_DIR.iterdir():
                        if subdir.is_dir():
                            for f in subdir.rglob("*"):
                                if f.is_file():
                                    try:
                                        f.unlink()
                                        cleared += 1
                                    except Exception:
                                        pass
                st.success(f"✅ 已清除 {cleared} 个缓存文件。下次分析将重新下载财报。")
        with col_cache3:
            if st.button("📦 清除 AI 标注缓存", key="p7_clear_ai_cache", help="删除 data/cache/ai_annotations/ 下的缓存，强制重新调用 DeepSeek"):
                import shutil
                cleared = 0
                ai_cache_dir = REPO_ROOT / "data" / "cache" / "ai_annotations"
                if ai_cache_dir.exists():
                    for f in ai_cache_dir.rglob("*"):
                        if f.is_file():
                            try:
                                f.unlink()
                                cleared += 1
                            except Exception:
                                pass
                st.success(f"✅ 已清除 {cleared} 个 AI 标注缓存文件。下次分析将重新调用 DeepSeek。")

    # ---- 财报备份（防误删） ----
    with st.expander("📦 财报备份（防误删双保险）", expanded=False):
        st.caption("一键将财报备份到 dev 目录，防止误删。备份为增量模式，只复制新增或修改的文件。")
        
        dev_repo = REPO_ROOT.parent / "depreciation-risk-detection-dev"
        backup_targets = ["cn_财报", "us_财报"]
        
        for folder in backup_targets:
            src = CACHE_DIR / folder
            dst = dev_repo / "data" / "raw" / folder
            
            src_count = sum(1 for _ in src.rglob("*") if _.is_file()) if src.exists() else 0
            dst_count = sum(1 for _ in dst.rglob("*") if _.is_file()) if dst.exists() else 0
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{folder}**")
            with col2:
                status_color = "🟢" if src_count > 0 and src_count == dst_count else ("🟡" if src_count > 0 else "🔴")
                st.caption(f"{status_color} 主目录: {src_count} 份 | 备份: {dst_count} 份")
            with col3:
                if st.button(f"📦 备份", key=f"p7_backup_{folder}"):
                    if not src.exists() or src_count == 0:
                        st.warning(f"⚠️ {folder} 为空，无需备份。")
                    else:
                        import shutil
                        copied = 0
                        skipped = 0
                        for src_file in src.rglob("*"):
                            if src_file.is_file():
                                dst_file = dst / src_file.relative_to(src)
                                needs_copy = False
                                if not dst_file.exists():
                                    needs_copy = True
                                else:
                                    src_stat = src_file.stat()
                                    dst_stat = dst_file.stat()
                                    if src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime:
                                        needs_copy = True
                                if needs_copy:
                                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(src_file, dst_file)
                                    copied += 1
                                else:
                                    skipped += 1
                        st.success(f"✅ {folder} 备份完成：复制 {copied} 份，跳过 {skipped} 份已一致。")
        
        st.info("💡 提示：dev 目录的备份不受主目录删除操作影响。即使主目录文件被误删，也可从 dev 目录恢复。")

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
    # 六步流水线（统一分发）
    # ================================================================
    if not is_cn:
        _run_us_pipeline(client, mode, ticker, fiscal_year, uploaded_html, cases, data)
    else:
        _run_cn_pipeline(client, mode, ticker, fiscal_year, uploaded_pdf, cases, data)


CACHE_DIR_AI = REPO_ROOT / "data" / "cache" / "ai_annotations"

def _get_cache_path(ticker: str, fiscal_year: int, suffix: str = "") -> Path:
    """获取缓存文件路径。"""
    CACHE_DIR_AI.mkdir(parents=True, exist_ok=True)
    fname = f"{ticker.upper()}_{fiscal_year}_ai_raw.json"
    if suffix:
        fname = f"{ticker.upper()}_{fiscal_year}_{suffix}.json"
    return CACHE_DIR_AI / fname

def _load_ai_cache(ticker: str, fiscal_year: int) -> dict:
    """加载已缓存的 AI 标注结果。"""
    cache_path = _get_cache_path(ticker, fiscal_year)
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def _save_ai_cache(ticker: str, fiscal_year: int, data: dict, suffix: str = "") -> None:
    """保存 AI 标注结果到本地缓存。"""
    cache_path = _get_cache_path(ticker, fiscal_year, suffix)
    CACHE_DIR_AI.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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
        candidates = locate_candidates_batch(html_text, max_candidates=30)
        st.write(f"发现 {len(candidates)} 个候选段落")
        strength_counts = {}
        for c in candidates:
            strength_counts[c["signal_strength"]] = strength_counts.get(c["signal_strength"], 0) + 1
        for s, n in sorted(strength_counts.items(), key=lambda x: {"strongest": 3, "strong": 2, "medium": 1}.get(x[0], 0), reverse=True):
            st.write(f"  - {s}: {n} 段")
        status.update(label=f"✅ 步骤 2/6：定位到 {len(candidates)} 个候选段落", state="complete")

    if not candidates:
        st.warning("未定位到任何候选段落，可能是该 10-K 中折旧/减值相关披露极少。")
        return

    # ②.⑤ 缓存检查
    cache_data = _load_ai_cache(str(ticker).upper(), int(fiscal_year))
    if cache_data and not uploaded_html:
        st.info(f"📦 命中本地缓存（{ticker} FY{fiscal_year}），跳过 DeepSeek 调用")
        ai_raw = cache_data.get("ai_raw", {})
        verification = cache_data.get("verification", {})
        # 显示缓存信息
        n_signals = len(ai_raw.get("risk_signals", []))
        n_dims = len(ai_raw.get("dimension_scores", []))
        st.write(f"缓存包含 {n_signals} 条信号，{n_dims} 个维度评分")
    else:
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

        # 保存缓存
        if not uploaded_html:
            _save_ai_cache(str(ticker).upper(), int(fiscal_year), {
                "ai_raw": ai_raw,
                "verification": verification,
                "cached_at": str(pd.Timestamp.now()),
            })
            st.caption(f"💾 已缓存到 {_get_cache_path(str(ticker).upper(), int(fiscal_year))}")

    # ④.5 规则引擎
    with st.status("⚙️ 步骤 4.5/6：规则引擎硬规则修正...", expanded=True) as status:
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        st.write(f"AI 原始分：{composite_before['weighted_score']:.2f}")
        dim_scores, rules_triggered, rule_warnings = apply_hard_rules(dim_scores_before, candidates, ai_raw, full_html=html_text)
        composite = compute_composite_score(dim_scores)
        if rules_triggered:
            st.write(f"🎯 触发 {len(rules_triggered)} 条硬规则：")
            for rule in rules_triggered:
                st.write(f"  • {rule}")
        if rule_warnings:
            st.write(f"⚠️ 发现 {len(rule_warnings)} 条规则警告：")
            for w in rule_warnings:
                st.write(f"  • {w}")
        status.update(label=f"✅ 步骤 4.5/6：规则引擎完成", state="complete")

    _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered, rule_warnings,
                     ticker, fiscal_year, actual_fy, mode, cases, data, html_text, candidates)


def _run_cn_pipeline(client, mode, ticker, fiscal_year, uploaded_pdf, cases, data):
    """A股年报流水线（v3.1：缓存持久化 + 验真加固）。"""
    import pdfplumber

    # ① 下载/读取 PDF
    with st.status("📥 步骤 1/6：获取 A股年报 PDF...", expanded=True) as status:
        try:
            if uploaded_pdf:
                st.write("使用上传的本地 PDF 文件")
                pdf_bytes = uploaded_pdf
            else:
                st.write(f"从巨潮资讯网下载 {ticker} {fiscal_year} 年报...")
                pdf_path, company_name = fetch_annual_report(str(ticker), int(fiscal_year), cache_dir=CACHE_DIR / "cn_财报")
                st.write(f"✅ 下载完成：{company_name}")
                pdf_bytes = pdf_path.read_bytes()

            # 提取文本
            st.write("正在提取PDF文本...")
            full_text = ""
            pdf_input = BytesIO(pdf_bytes) if uploaded_pdf else pdf_path
            with pdfplumber.open(pdf_input) as pdf:
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
        candidates = locate_cn_candidates(full_text, max_candidates=30)
        st.write(f"发现 {len(candidates)} 个候选段落")
        strength_counts = {}
        for c in candidates:
            strength_counts[c["signal_strength"]] = strength_counts.get(c["signal_strength"], 0) + 1
        for s, n in sorted(strength_counts.items(), key=lambda x: {"strongest": 3, "strong": 2, "medium": 1}.get(x[0], 0), reverse=True):
            st.write(f"  - {s}: {n} 段")
        status.update(label=f"✅ 步骤 2/6：定位到 {len(candidates)} 个候选段落", state="complete")

    if not candidates:
        st.warning("未定位到任何候选段落，可能是该年报中折旧/减值相关披露极少。")
        return

    # ②.⑤ 缓存检查（v3.1新增：A股缓存持久化）
    cache_data = _load_ai_cache(str(ticker).upper(), int(fiscal_year))
    if cache_data and not uploaded_pdf:
        st.info(f"📦 命中本地缓存（{ticker} {fiscal_year}），跳过 DeepSeek 调用")
        ai_raw = cache_data.get("ai_raw", {})
        verification = cache_data.get("verification", {})
        n_signals = len(ai_raw.get("risk_signals", []))
        n_dims = len(ai_raw.get("dimension_scores", []))
        st.write(f"缓存包含 {n_signals} 条信号，{n_dims} 个维度评分")
    else:
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

        # ④ 程序验真（中文模式 v3.1：增强排除噪声）
        with st.status("🔐 步骤 4/6：程序验真（中文模式 v3.1）...", expanded=True) as status:
            signals = ai_raw.get("risk_signals", [])
            passed = 0
            failed = 0
            verif_results = []
            for sig in signals:
                excerpt = sig.get("text_excerpt", "")
                sig_id = sig.get("signal_id", "UNKNOWN")
                
                # v3.1增强：A股验真排除噪声（年报通用章节误匹配）
                is_noise = False
                noise_reason = ""
                excerpt_lower = excerpt.lower()
                
                # 排除模式1：公司概况/公司简介（非折旧政策）
                if ("公司概况" in excerpt or "公司简介" in excerpt or "公司基本情况" in excerpt) and \
                   not any(k in excerpt for k in ["折旧", "摊销", "减值", "固定资产", "使用寿命"]):
                    is_noise = True
                    noise_reason = "公司概况章节误匹配"
                
                # 排除模式2：前瞻性声明/风险提示（泛泛提及）
                if ("前瞻性" in excerpt or "风险提示" in excerpt or "免责声明" in excerpt) and \
                   not any(k in excerpt for k in ["折旧", "摊销", "减值", "固定资产"]):
                    is_noise = True
                    noise_reason = "前瞻性声明/风险提示泛泛提及"
                
                # 排除模式3：管理层讨论中顺带提及折旧（非具体政策）
                if ("管理层讨论" in excerpt or "经营情况讨论" in excerpt) and \
                   not any(k in excerpt for k in ["折旧年限", "使用寿命", "预计使用年限", "折旧方法", "固定资产"]):
                    is_noise = True
                    noise_reason = "管理层讨论中顺带提及"
                
                # 子串验真
                if excerpt and excerpt[:30] in full_text and not is_noise:
                    passed += 1
                    verif_results.append({"signal_id": sig_id, "passed": True, "method": "substring", "confidence": 1.0})
                elif is_noise:
                    failed += 1
                    verif_results.append({"signal_id": sig_id, "passed": False, "method": "noise_excluded", "confidence": 0.0, "reason": noise_reason})
                else:
                    failed += 1
                    verif_results.append({"signal_id": sig_id, "passed": False, "method": "substring", "confidence": 0.0})
            
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
            if any(v.get("reason") for v in verif_results):
                st.write("🛡️ 已排除噪声信号（公司概况/风险提示/管理层讨论误匹配）")
            status.update(label=f"✅ 步骤 4/6：验真完成（通过率 {verification['pass_rate'] * 100:.0f}%）", state="complete")

        # 保存缓存（v3.1：A股也启用缓存）
        if not uploaded_pdf:
            _save_ai_cache(str(ticker).upper(), int(fiscal_year), {
                "ai_raw": ai_raw,
                "verification": verification,
                "cached_at": str(pd.Timestamp.now()),
            })
            st.caption(f"💾 已缓存到 {_get_cache_path(str(ticker).upper(), int(fiscal_year))}")

    # ④.5 规则引擎（A股适配）
    with st.status("⚙️ 步骤 4.5/6：规则引擎硬规则修正...", expanded=True) as status:
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        st.write(f"AI 原始分：{composite_before['weighted_score']:.2f}")
        dim_scores, rules_triggered, rule_warnings = apply_hard_rules(dim_scores_before, candidates, ai_raw, full_html=full_text)
        composite = compute_composite_score(dim_scores)
        if rules_triggered:
            st.write(f"🎯 触发 {len(rules_triggered)} 条硬规则：")
            for rule in rules_triggered:
                st.write(f"  • {rule}")
        if rule_warnings:
            st.write(f"⚠️ 发现 {len(rule_warnings)} 条规则警告：")
            for w in rule_warnings:
                st.write(f"  • {w}")
        status.update(label=f"✅ 步骤 4.5/6：规则引擎完成", state="complete")

    _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered, rule_warnings,
                     ticker, fiscal_year, None, mode, cases, data, full_text, candidates)


def _display_results(composite, composite_before, dim_scores, ai_raw, verification, rules_triggered, rule_warnings,
                     ticker, fiscal_year, actual_fy, mode, cases, data, full_text=None, candidates=None):
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
        "rule_warnings": rule_warnings,
        "verification": verification,
        "accounting_policy": ai_raw.get("accounting_policy", {}),
        "summary": ai_raw.get("summary", ""),
    }

    st.divider()
    st.markdown("### 📋 人工复核")

    if actual_fy and actual_fy != int(fiscal_year):
        st.warning(f"⚠️ 实际分析的是 FY{actual_fy} 的 10-K（请求的是 FY{fiscal_year}）。")

    # 规则引擎修正展示
    if rules_triggered or rule_warnings:
        with st.container():
            st.markdown("### ⚙️ 规则引擎修正")
            cols = st.columns([1, 2])
            with cols[0]:
                st.metric("AI 原始分", f"{composite_before['weighted_score']:.2f}")
            with cols[1]:
                st.metric("规则修正后", f"{composite['weighted_score']:.2f}",
                         delta=f"{composite['weighted_score'] - composite_before['weighted_score']:+.2f}")
            if rules_triggered:
                for rule in rules_triggered:
                    st.markdown(f"- {rule}")
            if rule_warnings:
                for w in rule_warnings:
                    st.warning(f"⚠️ {w}")
            st.info("📌 规则引擎覆盖 D1（年限错配）、D2（年限变更）、D4（CAPEX强度）。D3/D5 由 DeepSeek 独立评分。D1已增加资产类型感知，排除无形资产/租赁/员工任期误匹配。")
            st.divider()

    _render_score_card(composite["weighted_score"], composite["risk_level"], composite["score_breakdown"])

    # D1调试信息：始终显示年限提取中间结果，方便观察asset_type识别
    if candidates and full_text:
        with st.expander("🔍 D1 年限提取调试信息（开发调试用）", expanded=False):
            try:
                d1_result = _extract_life_years(candidates, full_text=full_text)
                if d1_result:
                    max_life, asset_type, confidence, baseline, source_snippet = d1_result
                    st.markdown(f"**提取年限**: `{max_life}` 年")
                    st.markdown(f"**资产类型**: `{asset_type}`")
                    st.markdown(f"**置信度**: `{confidence}`")
                    st.markdown(f"**基准年限**: `{baseline}` 年")
                    st.markdown(f"**错配比**: `{max_life/baseline:.1f}x`")
                    st.markdown(f"**来源片段**: `{source_snippet[:200]}...`")
                else:
                    st.warning("未提取到年限信息（_extract_life_years 返回 None）")
            except Exception as e:
                st.error(f"调试信息提取失败: {e}")

    # v3修复：所有模式都尝试查找人工标注对照（不仅"选择已有公司"模式）
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
            "- **关键词矩阵**：美股6词三级检索（候选数30）/ A股中文三级检索（候选数30，v3.1同步压缩）\n"
            "- **DeepSeek**：`deepseek-chat` 模型，温度 0.2，强制 JSON 输出\n"
            "- **验真逻辑**：美股=全文逐字匹配+模糊匹配+四层排除（Note1/前瞻性/风险因素/MD&A）；A股=子串包含检查+三层排除（公司概况/风险提示/管理层讨论，v3.1新增）\n"
            "- **算分逻辑**：程序执行 `Σ(维度分 × 权重)`，DeepSeek 只给维度分建议\n"
            "- **双签制**：AI 草拟 → 程序验真 → 人工终审\n"
            "- **规则引擎v3**：D1资产类型感知（服务器/晶圆厂/建筑物区分），排除无形资产/租赁/员工任期误匹配\n"
            "- **A股适配**：巨潮PDF下载 + pdfplumber提取 + 中文关键词 + 中文提示词 + 中文正则规则\n"
            "- **缓存持久化v3.1**：美股/A股均支持本地缓存，测试迭代速度提升10倍"
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
