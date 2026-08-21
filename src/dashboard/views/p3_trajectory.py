"""P3 跨年轨迹 —— 同一公司多年评分轨迹，标注折旧政策变更事件点

外壳 app.py 通过 ``render(data)`` 调用本模块。
data = {"panel": DataFrame(30 行), "cases": [case, ...]}，全部动态读取。

页面结构：
1. 公司多选 + 指标下拉（综合分 / D1-D5 单维度）
2. 主图：折线图，每家公司一条线（固定取该司 panel 首行 color），
   草稿年份用空心标记，已确认用实心标记
3. 政策变更事件点：life_extended_current_period == True 的行叠加星形标记，
   hover 显示财年、服务器折旧年限、年限延长减少的折旧费用（利润影响）
4. 事件清单表：所有政策变更行
5. 辅助图：capex_to_revenue 资本开支强度跨年轨迹（AI 军备竞赛背景）
"""

import math
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui_common as ui

# 已知指标列 → 中文展示名（未知 D 列自动降级为列名本身）
METRIC_LABELS = {
    "composite_score": "综合分 composite_score",
    "D1_depreciation_vs_tech_life": "D1 · 折旧年限 vs 技术寿命",
    "D2_depreciation_coverage": "D2 · 折旧覆盖度",
    "D3_capex_efficiency": "D3 · 资本开支效率",
    "D4_financial_discretion": "D4 · 财务操纵空间",
    "D5_competition_substitution": "D5 · 竞争替代压力",
}


def _metric_columns(panel: pd.DataFrame) -> list[str]:
    """动态识别可用指标列：composite_score + 所有 D<数字> 开头的维度列。"""
    cols = []
    if "composite_score" in panel.columns:
        cols.append("composite_score")
    dim_cols = sorted(
        (c for c in panel.columns if re.match(r"^D\d", str(c))),
        key=lambda c: (int(re.match(r"^D(\d+)", c).group(1)), c),
    )
    return cols + dim_cols


def _metric_label(col: str) -> str:
    return METRIC_LABELS.get(col, f"维度 · {col}")


def _company_color(sub: pd.DataFrame) -> str:
    """同一家公司固定取 panel 中该司首行 color（缺失时退回主色）。"""
    if "color" in sub.columns and not sub.empty:
        val = sub.iloc[0]["color"]
        if isinstance(val, str) and val:
            return val
    return ui.PRIMARY


def _company_label(sub: pd.DataFrame) -> str:
    ticker = str(sub.iloc[0]["ticker"])
    name = str(sub.iloc[0].get("company_name", "") or "")
    return f"{ticker} · {name}" if name else ticker


def _fmt_money(val) -> str:
    """$X,XXX M 格式化；空值显示为 —。"""
    try:
        f = float(val)
        if math.isnan(f):
            return "—"
        return f"${f:,.0f} M"
    except (TypeError, ValueError):
        return "—"


def _fmt_years(val) -> str:
    try:
        f = float(val)
        if math.isnan(f):
            return "—"
        return f"{f:g} 年"
    except (TypeError, ValueError):
        return "—"


def _fmt_score(val) -> str:
    try:
        f = float(val)
        if math.isnan(f):
            return "—"
        return f"{f:.2f}"
    except (TypeError, ValueError):
        return "—"


def _draft_keys(cases: list[dict]) -> set[tuple[str, int]]:
    """草稿待审的 (ticker, fiscal_year) 集合，用于主图空心标记。"""
    keys = set()
    for c in cases or []:
        try:
            if c.get("is_draft"):
                keys.add((str(c.get("ticker", "")), int(c.get("fiscal_year", 0))))
        except (TypeError, ValueError):
            continue
    return keys


def render(data: dict) -> None:
    panel = data.get("panel")
    cases = data.get("cases", [])

    if panel is None or panel.empty:
        st.info("面板数据为空，无法绘制跨年轨迹。请确认 data/processed 下已生成训练面板。")
        return

    panel = panel.copy()
    panel["fiscal_year"] = panel["fiscal_year"].astype(int)
    panel = panel.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)

    # ---------- 1. 控件：公司多选 + 指标选择 ----------
    tickers = sorted(panel["ticker"].astype(str).unique().tolist())

    col_sel, col_metric = st.columns([2, 1])
    with col_sel:
        selected = st.multiselect(
            "选择公司（可多选）",
            options=tickers,
            default=tickers[:5],
            key="p3_tickers",
        )
    with col_metric:
        metric_cols = _metric_columns(panel)
        metric = st.selectbox(
            "轨迹指标",
            options=metric_cols,
            format_func=_metric_label,
            key="p3_metric",
        )

    if not selected:
        st.info("请至少选择一家公司以绘制跨年轨迹。")
        return

    draft_keys = _draft_keys(cases)
    metric_label = _metric_label(metric)

    # ---------- 2. 主图：评分/维度跨年轨迹 ----------
    ui.section("跨年风险轨迹")

    fig = go.Figure()
    for ticker in selected:
        sub = panel[panel["ticker"].astype(str) == ticker]
        if sub.empty:
            continue
        color = _company_color(sub)
        label = _company_label(sub)

        years = sub["fiscal_year"].tolist()
        values = pd.to_numeric(sub[metric], errors="coerce").tolist()
        statuses = [
            "草稿待审" if (ticker, int(y)) in draft_keys else "已确认" for y in years
        ]
        hover_texts = [
            f"{label}<br>FY{y} · {metric_label}：{_fmt_score(v)} · {s}"
            for y, v, s in zip(years, values, statuses)
        ]

        # 主线：全部年份连成一条（保证草稿点不断线），实心标记
        fig.add_trace(
            go.Scatter(
                x=years,
                y=values,
                mode="lines+markers",
                name=label,
                legendgroup=ticker,
                line=dict(color=color, width=2.2),
                marker=dict(size=9, color=color, symbol="circle"),
                hovertext=hover_texts,
                hoverinfo="text",
            )
        )

        # 草稿年份：空心标记叠加（同色系，不入图例）
        draft_mask = [(ticker, int(y)) in draft_keys for y in years]
        if any(draft_mask):
            fig.add_trace(
                go.Scatter(
                    x=[y for y, m in zip(years, draft_mask) if m],
                    y=[v for v, m in zip(values, draft_mask) if m],
                    mode="markers",
                    name=f"{label}（草稿）",
                    legendgroup=ticker,
                    showlegend=False,
                    marker=dict(
                        size=11,
                        symbol="circle-open",
                        color=color,
                        line=dict(width=2.2, color=color),
                    ),
                    hovertext=[t for t, m in zip(hover_texts, draft_mask) if m],
                    hoverinfo="text",
                )
            )

    fig.update_layout(
        **ui.PLOTLY_LAYOUT,
        height=430,
        xaxis=dict(title="财年", dtick=1, showgrid=False),
        yaxis=dict(title=metric_label, rangemode="tozero", gridcolor="#EDE9E2"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True, key="p3_main_chart")
    st.caption("● 实心点 = 已确认 · ○ 空心点 = 草稿待审 · ★ 星形 = 折旧年限政策变更")

    # ---------- 3 + 4. 政策变更事件点与事件清单 ----------
    ui.section("折旧年限政策变更事件")

    if "life_extended_current_period" in panel.columns:
        events = panel[panel["life_extended_current_period"] == True].copy()  # noqa: E712
    else:
        events = panel.iloc[0:0].copy()

    if events.empty:
        st.info("当前样本区间内没有公司发生折旧年限延长（政策变更）事件。")
    else:
        # 事件点：叠加到主图对应公司折线上的星形标记（单独一图强调展示）
        fig_ev = go.Figure()
        for ticker in selected:
            sub_ev = events[events["ticker"].astype(str) == ticker]
            if sub_ev.empty:
                continue
            base = panel[panel["ticker"].astype(str) == ticker]
            color = _company_color(base)
            label = _company_label(base)

            hover_texts = [
                "★ 折旧年限政策变更<br>"
                f"{label}<br>"
                f"FY{int(r['fiscal_year'])}<br>"
                f"服务器折旧年限：{_fmt_years(r.get('server_useful_life'))}<br>"
                f"利润影响（减少折旧费用）：{_fmt_money(r.get('life_extension_reduction_millions'))}"
                for _, r in sub_ev.iterrows()
            ]
            fig_ev.add_trace(
                go.Scatter(
                    x=sub_ev["fiscal_year"].tolist(),
                    y=pd.to_numeric(sub_ev[metric], errors="coerce").tolist(),
                    mode="markers",
                    name=label,
                    legendgroup=ticker,
                    marker=dict(
                        symbol="star",
                        size=14,
                        color=color,
                        line=dict(width=1.2, color="#FFFFFF"),
                    ),
                    hovertext=hover_texts,
                    hoverinfo="text",
                )
            )

        if not fig_ev.data:
            st.info("所选公司在样本区间内没有折旧年限政策变更事件，可在上方多选框调整公司范围。")
        else:
            fig_ev.update_layout(
                **ui.PLOTLY_LAYOUT,
                height=300,
                xaxis=dict(title="财年", dtick=1, showgrid=False),
                yaxis=dict(title=metric_label, rangemode="tozero", gridcolor="#EDE9E2"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(fig_ev, use_container_width=True, key="p3_event_chart")

        # 事件清单表（所有公司，不限于当前选择）
        table_cols = [
            "ticker",
            "fiscal_year",
            "server_useful_life",
            "life_extension_reduction_millions",
            "composite_score",
            "risk_level",
        ]
        table = events[[c for c in table_cols if c in events.columns]].rename(
            columns={
                "ticker": "公司",
                "fiscal_year": "财年",
                "server_useful_life": "服务器折旧年限（年）",
                "life_extension_reduction_millions": "年限延长减少折旧费用（$M）",
                "composite_score": "综合分",
                "risk_level": "风险等级",
            }
        )
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "财年": st.column_config.NumberColumn(format="%d"),
                "服务器折旧年限（年）": st.column_config.NumberColumn(format="%.1f"),
                "年限延长减少折旧费用（$M）": st.column_config.NumberColumn(format="$,.0f"),
                "综合分": st.column_config.NumberColumn(format="%.2f"),
            },
        )
        st.caption("事件清单覆盖全部样本公司；星形图仅展示当前所选公司。")

    # ---------- 5. 辅助视角：资本开支强度 ----------
    ui.section("资本开支强度（capex / revenue）—— AI 军备竞赛背景")

    if "capex_to_revenue" not in panel.columns:
        st.info("面板数据缺少 capex_to_revenue 列，无法绘制资本开支强度轨迹。")
        return

    fig_cap = go.Figure()
    for ticker in selected:
        sub = panel[panel["ticker"].astype(str) == ticker]
        if sub.empty:
            continue
        color = _company_color(sub)
        label = _company_label(sub)
        values = pd.to_numeric(sub["capex_to_revenue"], errors="coerce").tolist()
        hover_texts = [
            f"{label}<br>FY{int(y)} · 资本开支强度：" + (f"{v:.1%}" if pd.notna(v) else "—")
            for y, v in zip(sub["fiscal_year"].tolist(), values)
        ]
        fig_cap.add_trace(
            go.Scatter(
                x=sub["fiscal_year"].tolist(),
                y=values,
                mode="lines+markers",
                name=label,
                legendgroup=ticker,
                line=dict(color=color, width=2, dash="dot"),
                marker=dict(size=7, color=color),
                hovertext=hover_texts,
                hoverinfo="text",
            )
        )

    fig_cap.update_layout(
        **ui.PLOTLY_LAYOUT,
        height=340,
        xaxis=dict(title="财年", dtick=1, showgrid=False),
        yaxis=dict(title="资本开支 / 营收", tickformat=".0%", gridcolor="#EDE9E2"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_cap, use_container_width=True, key="p3_capex_chart")
    st.caption(
        "资本开支强度持续走高，反映 AI 算力军备竞赛下的重资产化趋势——"
        "折旧年限政策对利润的影响也随之放大。"
    )
