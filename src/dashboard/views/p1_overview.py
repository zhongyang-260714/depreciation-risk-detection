"""P1 总览热力图页

KPI 行 → 公司 × 财年风险热力图（可切换维度）→ 最新财年综合分排行 → 明细表。
所有数据均由外壳传入的 data 动态读取，不做任何硬编码。
"""

import pandas as pd
import plotly.express as px
import streamlit as st

import ui_common as ui

# 可切换的热力图维度：列名 → 展示名
Z_OPTIONS = {
    "composite_score": "综合分",
    "D1_depreciation_vs_tech_life": "D1 折旧年限 vs 技术寿命",
    "D2_accounting_conservatism": "D2 会计稳健性",
    "D3_impairment_risk": "D3 减值风险",
    "D4_capex_intensity": "D4 资本开支强度",
    "D5_competition_substitution": "D5 竞争替代",
}


def _fmt_pct(v) -> str:
    """百分数保留 1 位；输入为比率（0-1）时乘 100，已 >1 视为百分数直用。"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(x) <= 1.5:
        x *= 100
    return f"{x:.1f}%"


def render(data: dict) -> None:
    panel = data.get("panel") if isinstance(data, dict) else None
    cases = data.get("cases", []) if isinstance(data, dict) else []
    if not isinstance(panel, pd.DataFrame) or panel.empty:
        st.info("暂无总览数据，请先运行数据处理与标注流程。")
        return

    df = panel.copy()
    df["市场"] = "美股"

    # ---- 合并 A股标注案例：双市场风险全景 ----
    DIM_COL = {
        "D1": "D1_depreciation_vs_tech_life",
        "D2": "D2_accounting_conservatism",
        "D3": "D3_impairment_risk",
        "D4": "D4_capex_intensity",
        "D5": "D5_competition_substitution",
    }
    cn_rows = []
    for c in cases if isinstance(cases, list) else []:
        if not isinstance(c, dict):
            continue
        t = c.get("ticker", "")
        if not t or not t[0].isdigit():
            continue  # 美股案例已包含在训练面板中
        row = {
            "ticker": t,
            "company_name": c.get("name") or t,
            "fiscal_year": c.get("fiscal_year"),
            "composite_score": c.get("score"),
            "risk_level": c.get("risk_level"),
            "color": c.get("color"),
            "市场": "A股",
        }
        for d in c.get("dimensions", []):
            col = DIM_COL.get(d.get("id"))
            if col:
                row[col] = d.get("score")
        cn_rows.append(row)
    if cn_rows:
        df = pd.concat([df, pd.DataFrame(cn_rows)], ignore_index=True)

    # ---------- KPI 行 ----------
    n_cases = len(cases) if isinstance(cases, list) else 0
    n_companies = df["ticker"].nunique() if "ticker" in df.columns else 0
    avg_score = df["composite_score"].mean() if "composite_score" in df.columns else None
    n_drafts = 0
    if isinstance(cases, list):
        n_drafts = sum(1 for c in cases if isinstance(c, dict) and c.get("is_draft"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("标注总数", f"{n_cases} 份")
    c2.metric("覆盖公司数", f"{n_companies} 家")
    c3.metric("平均综合分", f"{avg_score:.2f}" if pd.notna(avg_score) else "—")
    c4.metric("草稿待审", f"{n_drafts} 份")

    # ---------- 主图：公司 × 财年热力图 ----------
    ui.section("公司 × 财年 风险热力图")
    z_label = st.selectbox(
        "热力图维度", list(Z_OPTIONS.values()), index=0, key="p1_z_dim"
    )
    z_col = next(k for k, v in Z_OPTIONS.items() if v == z_label)

    if z_col not in df.columns or "fiscal_year" not in df.columns:
        st.info(f"数据缺少 {z_label} 或财年字段，无法绘制热力图。")
    else:
        # y 轴公司按平均分降序排序（底部为最高风险）
        order = (
            df.groupby("ticker")[z_col]
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )
        name_map = (
            df.drop_duplicates("ticker")
            .assign(
                label=lambda x: x["company_name"].fillna(x["ticker"])
                + x["市场"].map(lambda m: "（A股）" if m == "A股" else "")
            )
            .set_index("ticker")["label"]
            .to_dict()
            if "company_name" in df.columns
            else {}
        )
        pivot = df.pivot_table(
            index="ticker", columns="fiscal_year", values=z_col, aggfunc="mean"
        ).reindex(order)

        # hover 辅助信息：公司名 / 财年 / 风险等级 → customdata 逐格携带
        risk_map = (
            df.set_index(["ticker", "fiscal_year"])["risk_level"].to_dict()
            if "risk_level" in df.columns
            else {}
        )
        customdata = [
            [
                [name_map.get(t, t), y, risk_map.get((t, y), "—")]
                for y in pivot.columns
            ]
            for t in pivot.index
        ]

        # x 轴财年加 FY 前缀：纯数字字符串会被前端强制转成连续数值轴
        pivot.columns = [f"FY{y}" for y in pivot.columns]

        y_labels = [name_map.get(t, t) for t in pivot.index]
        fig = px.imshow(
            pivot,
            color_continuous_scale=ui.HEAT_COLORSCALE,
            zmin=1,
            zmax=5,
            aspect="auto",
            labels=dict(x="财年", y="公司", color=z_label),
        )
        fig.update_traces(
            text=pivot.round(2).astype(str).where(pivot.notna(), "—").values,
            texttemplate="%{text}",
            customdata=customdata,
            hovertemplate=(
                "公司：%{customdata[0]}<br>财年：%{customdata[1]}"
                "<br>风险等级：%{customdata[2]}<br>"
                + z_label
                + "：%{z:.2f}<extra></extra>"
            ),
        )
        fig.update_layout(
            **ui.PLOTLY_LAYOUT,
            xaxis=dict(type="category", title="财年"),  # 强制类别轴，防止财年变连续刻度
            yaxis=dict(tickmode="array", tickvals=pivot.index, ticktext=y_labels),
            coloraxis_colorbar=dict(title=z_label),
            height=max(360, 34 * len(pivot) + 120),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- 排行图：最新财年综合分 ----------
    ui.section("最新财年综合分排行")
    if {"ticker", "fiscal_year", "composite_score"} <= set(df.columns):
        latest_year = int(df["fiscal_year"].max())
        latest = df[df["fiscal_year"] == latest_year].copy()
        latest = latest.sort_values("composite_score", ascending=True)

        draft_tickers = set()
        if isinstance(cases, list):
            draft_tickers = {
                c.get("ticker")
                for c in cases
                if isinstance(c, dict) and c.get("is_draft")
            }
        labels = [
            f"{name_map.get(t, t)}{' 📝' if t in draft_tickers else ''}"
            for t in latest["ticker"]
        ]
        colors = (
            latest["color"].tolist()
            if "color" in latest.columns
            else [ui.PRIMARY] * len(latest)
        )

        fig2 = px.bar(
            latest,
            x="composite_score",
            y=labels,
            orientation="h",
            text=latest["composite_score"].map(lambda v: f"{v:.2f}"),
            labels={"composite_score": "综合分", "y": "公司"},
        )
        fig2.update_traces(marker_color=colors, textposition="outside")
        fig2.update_layout(
            **ui.PLOTLY_LAYOUT,
            xaxis=dict(range=[0, 5.6], title="综合分（1-5）"),
            yaxis=dict(title=""),
            height=max(320, 30 * len(latest) + 100),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("数据缺少综合分字段，无法绘制排行图。")

    # ---------- 明细表 ----------
    ui.section("标注明细")
    show_cols = [
        "company_name",
        "ticker",
        "市场",
        "fiscal_year",
        "composite_score",
        "risk_level",
        "capex_to_revenue",
        "depreciation_to_revenue",
        "life_extended_current_period",
    ]
    show_cols = [c for c in show_cols if c in df.columns]
    table = df[show_cols].copy()
    rename = {
        "company_name": "公司",
        "ticker": "代码",
        "fiscal_year": "财年",
        "composite_score": "综合分",
        "risk_level": "风险等级",
        "capex_to_revenue": "资本开支/营收",
        "depreciation_to_revenue": "折旧/营收",
        "life_extended_current_period": "本期延长折旧年限",
    }
    table = table.rename(columns=rename)
    if "综合分" in table.columns:
        table["综合分"] = table["综合分"].map(
            lambda v: f"{v:.2f}" if pd.notna(v) else "—"
        )
    for c in ("资本开支/营收", "折旧/营收"):
        if c in table.columns:
            table[c] = table[c].map(_fmt_pct)
    if "本期延长折旧年限" in table.columns:
        table["本期延长折旧年限"] = table["本期延长折旧年限"].map(
            lambda v: "是" if bool(v) else "否"
        )
    st.dataframe(table, use_container_width=True, hide_index=True)
