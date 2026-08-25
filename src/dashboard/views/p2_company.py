"""P2 公司画像 —— 五维评分 + 验算式 + 证据链原文

核心看点：
- 现场验算 Σ(weight × score)，与标注综合分对比（草稿微调属正常）
- 证据链原文逐条展开，severity 低饱和着色
- 全部数据动态读取自 data["cases"]，禁止硬编码
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_common as ui
from data_loader import find_case

# severity 低饱和配色（红系 / 橙系 / 灰系）
_SEVERITY_COLORS = {
    "critical": "#B3402F",
    "high": "#B3402F",
    "medium": "#C07A1B",
    "low": "#8A877F",
}
_EMPTY_TOKENS = {None, "", "NA", "N/A", "na", "n/a", "None", "null"}


def _fmt_num(v: float) -> str:
    """整数不显示小数，其余保留两位。"""
    return f"{v:g}" if float(v) == int(v) else f"{v:.2f}"


def _beautify_key(key: str) -> str:
    """键名美化：去后缀/下划线转空格，首字母大写。"""
    return key.replace("_millions", "").replace("_", " ").strip().title()


def _is_empty(v) -> bool:
    return v in _EMPTY_TOKENS


def _severity_color(severity: str) -> str:
    return _SEVERITY_COLORS.get(str(severity).lower(), ui.MUTED)


def _render_header(case: dict):
    """头部卡片行：左卡公司信息 + 审核状态；右卡综合分 + 风险徽章。"""
    col_info, col_score = st.columns([3, 2])
    with col_info:
        st.markdown(
            f"""<div class="card">
                <h4>{case["name"]}（{case["ticker"]}）</h4>
                <p>FY{case["fiscal_year"]} · {case.get("risk_level_en", "")}</p>
                <p style="margin-top:0.5rem">{ui.status_badge(case["review_status"])}
                <span style="color:{ui.MUTED};font-size:0.78rem;margin-left:0.4rem">
                版本 {case.get("version", "—")} · 标注于 {case.get("annotated_at", "—")}</span></p>
            </div>""",
            unsafe_allow_html=True,
        )
    with col_score:
        confidence = case.get("confidence")
        conf_line = (
            f"<p style='margin-top:0.35rem'>置信度：{confidence}</p>"
            if not _is_empty(confidence)
            else ""
        )
        st.markdown(
            f"<div class='card' style='text-align:center'>"
            f"<div class='big-score' style='color:{case['color']}'>"
            f"{case['score']:.2f}<small> / {case['max_score']:.1f}</small></div>"
            f"<div style='margin-top:0.4rem'>{ui.risk_badge(case['risk_level'], case['color'])}</div>"
            f"{conf_line}</div>",
            unsafe_allow_html=True,
        )


def _render_dimensions(case: dict):
    """五维评分区：逐维信息行 + 五维雷达图 + 贡献值横向条形图 + 评分依据。"""
    dims = case.get("dimensions") or []
    if not dims:
        st.info("该标注暂无维度评分明细。")
        return

    for d in dims:
        c1, c2, c3, c4 = st.columns([4, 1, 1.5, 2])
        c1.markdown(f"**{d['id']} · {d['name']}**")
        c2.markdown(f"权重 {d['weight']:.2f}")
        c3.markdown(f"得分 **{_fmt_num(d['score'])}** / {_fmt_num(d['max'])}")
        c4.markdown(f"<span style='color:{ui.MUTED}'>{d.get('label', '')}</span>",
                    unsafe_allow_html=True)
        if d.get("reasoning"):
            with st.expander("评分依据"):
                st.markdown(d["reasoning"])

    # 五维风险雷达图（D1–D5 得分全貌）
    radar_theta = [f"{d['id']} {d['name']}" for d in dims]
    radar_r = [float(d["score"]) for d in dims]
    radar_max = max(float(d.get("max", 5)) for d in dims)
    fig_radar = go.Figure(
        go.Scatterpolar(
            r=radar_r + radar_r[:1],
            theta=radar_theta + radar_theta[:1],
            fill="toself",
            fillcolor="rgba(23, 112, 92, 0.18)",
            line_color=ui.PRIMARY,
            marker=dict(color=ui.PRIMARY, size=6),
            name="维度得分",
        )
    )
    fig_radar.update_layout(
        **ui.PLOTLY_LAYOUT,
        height=360,
        title=dict(text="五维风险雷达图（D1–D5 得分）", font_size=13),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, radar_max],
                            tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=False,
    )
    st.plotly_chart(fig_radar, width="stretch", key="p2_radar_chart")

    contribs = [d["weight"] * d["score"] for d in dims]
    fig = go.Figure(
        go.Bar(
            x=contribs,
            y=[f"{d['id']} {d['name']}" for d in dims],
            orientation="h",
            marker_color=ui.PRIMARY,
            text=[f"{c:.2f}" for c in contribs],
            textposition="outside",
        )
    )
    max_contrib = max(contribs) if contribs else 1
    fig.update_layout(
        **ui.PLOTLY_LAYOUT,
        height=60 + 46 * len(dims),
        title=dict(text="各维度贡献值（权重 × 得分）", font_size=13),
        xaxis=dict(title="贡献值", range=[0, max_contrib * 1.25]),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch", key="p2_contrib_chart")


def _render_verification(case: dict):
    """验算式区（本页核心）：现场计算 Σ(weight×score) 并与标注综合分对比。"""
    dims = case.get("dimensions") or []
    if not dims:
        st.info("无维度数据，无法验算。")
        return

    terms = " + ".join(f"{d['weight']:.2f}×{_fmt_num(d['score'])}" for d in dims)
    total = sum(d["weight"] * d["score"] for d in dims)
    st.markdown(
        f"<div class='formula'>{terms} = {total:.2f}</div>",
        unsafe_allow_html=True,
    )

    diff = abs(total - case["score"])
    if diff < 0.01:
        st.success(f"✓ 验算一致（标注综合分 {case['score']:.2f}）")
    else:
        st.warning(
            f"⚠ 验算值 {total:.2f} 与标注综合分 {case['score']:.2f} 差值 {diff:.2f}"
            "（草稿分数可能微调，属正常现象）"
        )

    table = pd.DataFrame(
        [
            {
                "维度": f"{d['id']} {d['name']}",
                "权重": f"{d['weight']:.2f}",
                "得分": _fmt_num(d["score"]),
                "贡献": f"{d['weight'] * d['score']:.2f}",
            }
            for d in dims
        ]
    )
    st.table(table)


def _render_signals(case: dict):
    """证据链原文区：逐条 signal 展开，severity 低饱和着色。"""
    signals = case.get("signals") or []
    if not signals:
        st.info("该标注未摘录风险信号原文。")
        return

    for s in signals:
        color = _severity_color(s.get("severity", ""))
        sev_label = str(s.get("severity", "—")).upper()
        title = f"{sev_label} · {s.get('risk_type', '—')} · {s.get('id', '')}"
        with st.expander(title):
            st.markdown(
                f"<span style='display:inline-block;width:0.7rem;height:0.7rem;"
                f"border-radius:50%;background:{color}'></span> "
                f"<span style='color:{color};font-weight:600'>severity：{sev_label}</span>",
                unsafe_allow_html=True,
            )
            if s.get("excerpt"):
                st.markdown(f"> {s['excerpt']}")
            st.markdown(f"**来源**：{s.get('source', '—')}")
            st.markdown(f"**页码位置**：{s.get('page_location', '—')}")
            st.markdown(f"**命中关键词**：`{s.get('keyword', '—')}`")
            if s.get("relevance"):
                st.markdown(f"**与折旧相关性**：{s['relevance']}")
            if s.get("evidence_chain"):
                st.markdown(f"**证据链**：{s['evidence_chain']}")


def _render_accounting_policy(case: dict):
    """会计政策卡：非空键值对，键名美化，None/NA 跳过。"""
    policy = case.get("accounting_policy") or {}
    items = [(k, v) for k, v in policy.items() if not _is_empty(v)]
    if not items:
        st.info("该标注未提供会计政策信息。")
        return
    rows = "".join(
        f"<p><b style='color:{ui.INK}'>{_beautify_key(k)}</b>：{v}</p>" for k, v in items
    )
    st.markdown(
        f"<div class='card'><h4>会计政策要点</h4>{rows}</div>",
        unsafe_allow_html=True,
    )


def _render_financial_highlights(case: dict):
    """财务亮点：以 _millions 结尾的数值键，一行 4 个 st.metric。"""
    highlights = case.get("financial_highlights") or {}
    items = [
        (k, v)
        for k, v in highlights.items()
        if k.endswith("_millions") and isinstance(v, (int, float))
    ]
    if not items:
        st.info("该标注未提供财务亮点数值。")
        return
    for i in range(0, len(items), 4):
        cols = st.columns(4)
        for col, (k, v) in zip(cols, items[i : i + 4]):
            col.metric(label=_beautify_key(k) + "（百万）", value=f"{v:,.0f}")


def render(data: dict) -> None:
    cases = data.get("cases") or []
    if not cases:
        st.warning("未加载到任何标注数据，请检查 data/annotated 目录。")
        return

    # ---- 1. 公司 / 财年联动选择 ----
    tickers = sorted({c["ticker"] for c in cases})
    name_map = {c["ticker"]: c["name"] for c in cases}
    col_a, col_b = st.columns([2, 1])
    ticker = col_a.selectbox(
        "选择公司",
        tickers,
        format_func=lambda t: f"{name_map.get(t, t)}（{t}）",
        key="p2_ticker",
    )
    years = sorted({c["fiscal_year"] for c in cases if c["ticker"] == ticker})
    fiscal_year = col_b.selectbox("选择财年", years, key="p2_fy")

    case = find_case(cases, ticker, fiscal_year)
    if case is None:
        st.error(f"未找到 {ticker} FY{fiscal_year} 的标注记录。")
        return

    if case.get("is_draft"):
        st.caption("📝 该标注为草稿待审状态，分数后续微调会自动生效。")

    # ---- 2. 头部卡片行 ----
    _render_header(case)

    # ---- 3. 五维评分区 ----
    ui.section("五维评分")
    _render_dimensions(case)

    # ---- 4. 验算式区（本页核心）----
    ui.section("综合分验算式")
    _render_verification(case)

    # ---- 5. 证据链原文区 ----
    ui.section(f"证据链原文（{len(case.get('signals') or [])} 条）")
    _render_signals(case)

    # ---- 6. 会计政策 + 7. 财务亮点 ----
    ui.section("会计政策与财务亮点")
    _render_accounting_policy(case)
    st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)
    _render_financial_highlights(case)

    # ---- 8. 总结 ----
    summary = case.get("summary")
    if not _is_empty(summary):
        ui.section("画像总结")
        st.markdown(f"> {summary}")
