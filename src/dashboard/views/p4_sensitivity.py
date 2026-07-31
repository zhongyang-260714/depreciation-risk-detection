"""P4 · 权重敏感性分析

拖动 D1-D5 权重滑块，实时归一化重算综合分：
- 头部：公司当前综合分 + 风险等级徽章 + 草稿状态徽章
- 滑块：默认值随公司/财年切换自动更新（key 绑定 ticker+fy），支持一键恢复默认
- 对比图：原始贡献（weight×score）vs 自定义贡献（归一化 wi/Σwi×Di）
- 敏感性排序：单维度权重 +0.05（归一化）对综合分的影响，找出评分"杠杆点"
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_common as ui
from data_loader import find_case


def _slider_keys(dim_ids: list[str], ticker: str, fy: int) -> dict[str, str]:
    return {d: f"p4_w_{d}_{ticker}_{fy}" for d in dim_ids}


def render(data: dict) -> None:
    cases = data.get("cases", [])
    if not cases:
        st.warning("未找到标注数据，请先确认 data/annotated/ 下存在正式标注 JSON。")
        return

    # ---- 公司 / 财年联动选择 ----
    company_names: dict[str, str] = {}
    for c in cases:
        company_names.setdefault(c["ticker"], c.get("name", ""))
    tickers = sorted(company_names)

    col_co, col_fy = st.columns([2, 1])
    with col_co:
        ticker = st.selectbox(
            "选择公司",
            tickers,
            format_func=lambda t: f"{t} · {company_names.get(t, '')}".rstrip(" ·"),
            key="p4_company",
        )
    fy_options = sorted(
        c["fiscal_year"] for c in cases if c["ticker"] == ticker
    )
    with col_fy:
        fy = st.selectbox("选择财年", fy_options, key=f"p4_fy_{ticker}")

    case = find_case(cases, ticker, int(fy))
    if case is None:
        st.warning(f"未找到 {ticker} {fy} 财年的标注数据。")
        return

    dims = case.get("dimensions", [])
    if not dims:
        st.warning("该标注缺少维度评分（dimensions），无法进行敏感性分析。")
        return

    # ---- 头部：当前分数 + 徽章 ----
    head_l, head_r = st.columns([1, 2])
    with head_l:
        st.markdown(
            f"<div class='big-score'>{case['score']:.2f}"
            f"<small> / {case.get('max_score', 5):.0f} 分</small></div>",
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown(
            f"**{case.get('name', ticker)}（{ticker}）· {case['fiscal_year']} 财年**　"
            + ui.risk_badge(case.get("risk_level", "未知"), case.get("color", ui.MUTED))
            + "　"
            + ui.status_badge(case.get("review_status", "")),
            unsafe_allow_html=True,
        )
    st.divider()

    # ---- 权重滑块 ----
    ui.section("权重调节（自动归一化）")
    default_weights = case.get("weights", {})
    keys = _slider_keys([d["id"] for d in dims], ticker, case["fiscal_year"])

    if st.button("恢复默认权重", key="p4_reset"):
        for k in keys.values():
            st.session_state.pop(k, None)
        st.rerun()

    slider_cols = st.columns(len(dims))
    raw_w: dict[str, float] = {}
    for col, d in zip(slider_cols, dims):
        with col:
            raw_w[d["id"]] = st.slider(
                f"{d['id']} {d.get('name', '')}",
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                value=float(default_weights.get(d["id"], d.get("weight", 0.0))),
                key=keys[d["id"]],
            )

    # ---- 实时重算 ----
    sum_w = sum(raw_w.values())
    orig = float(case["score"])
    ui.section("重算结果")
    if sum_w <= 0:
        st.info("当前所有权重均为 0，无法归一化。请至少上调一个维度的权重。")
        st.metric("原始综合分", f"{orig:.2f}")
        return

    new_score = sum(raw_w[d["id"]] * float(d.get("score", 0.0)) for d in dims) / sum_w
    res_l, res_r = st.columns([1, 1])
    with res_l:
        st.metric(
            "重算综合分（自定义权重）",
            f"{new_score:.2f}",
            delta=f"{new_score - orig:+.2f}",
            delta_color="inverse",  # 分数升高 = 风险升高，红色提示
        )
    with res_r:
        st.metric("原始综合分（默认权重）", f"{orig:.2f}")

    # ---- 对比图：原始贡献 vs 自定义贡献 ----
    ui.section("维度贡献对比")
    dim_labels = [f"{d['id']}<br>{d.get('name', '')}" for d in dims]
    orig_contrib = [float(d.get("weight", 0.0)) * float(d.get("score", 0.0)) for d in dims]
    cust_contrib = [raw_w[d["id"]] / sum_w * float(d.get("score", 0.0)) for d in dims]
    fig = go.Figure(
        [
            go.Bar(
                name="原始贡献（默认权重×维度分）",
                x=dim_labels,
                y=orig_contrib,
                marker_color=ui.PRIMARY,
                text=[f"{v:.2f}" for v in orig_contrib],
                textposition="outside",
            ),
            go.Bar(
                name="自定义贡献（归一化权重×维度分）",
                x=dim_labels,
                y=cust_contrib,
                marker_color="#D9A62E",
                text=[f"{v:.2f}" for v in cust_contrib],
                textposition="outside",
            ),
        ]
    )
    fig.update_layout(
        **ui.PLOTLY_LAYOUT,
        barmode="group",
        height=360,
        yaxis_title="对综合分的贡献",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig, width="stretch", key="p4_contrib_chart")

    # ---- 敏感性排序表 ----
    ui.section("敏感性排序：谁是评分「杠杆点」")
    rows = []
    for d in dims:
        perturbed = dict(raw_w)
        perturbed[d["id"]] = perturbed[d["id"]] + 0.05
        sum_p = sum(perturbed.values())
        perturbed_score = (
            sum(perturbed[dd["id"]] * float(dd.get("score", 0.0)) for dd in dims) / sum_p
        )
        rows.append(
            {
                "维度": d["id"],
                "维度名称": d.get("name", ""),
                "当前归一化权重": raw_w[d["id"]] / sum_w,
                "维度分": float(d.get("score", 0.0)),
                "权重 +0.05 后分数变化": perturbed_score - new_score,
            }
        )
    rows.sort(key=lambda r: abs(r["权重 +0.05 后分数变化"]), reverse=True)
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        width="stretch",
        column_config={
            "当前归一化权重": st.column_config.ProgressColumn(
                "当前归一化权重", format="%.2f", min_value=0, max_value=1
            ),
            "维度分": st.column_config.NumberColumn("维度分", format="%.2f"),
            "权重 +0.05 后分数变化": st.column_config.NumberColumn(
                "权重 +0.05 后分数变化", format="%+.3f"
            ),
        },
    )
    top = rows[0]
    st.caption(
        f"杠杆点：**{top['维度']} {top['维度名称']}** —— 该维度权重单独上调 0.05（其余不变、重新归一化）"
        f"可使综合分变化 {top['权重 +0.05 后分数变化']:+.3f} 分，是所有维度中对评分影响最大的一个；"
        "分数越高说明该维度当前得分与整体均值的偏离越大，权重调整越敏感。"
    )

    # ---- 说明 ----
    ui.section("为什么做敏感性分析")
    st.markdown(
        "评委会问「权重凭什么这么定」——本页就是回答工具：通过实时重算可以看到，"
        "默认权重下综合分对哪个维度最敏感（杠杆点），从而论证权重设定并非拍脑袋，"
        "而是与维度区分度相匹配；若小幅调整权重后公司风险排序保持稳定，则说明评分结论对权重选择具有稳健性。"
    )
    if case.get("is_draft"):
        st.caption("⚠️ 该公司为草稿标注，维度分后续可能微调，敏感性结论仅供参考。")
