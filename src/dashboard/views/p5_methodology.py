"""P5 · 方法论

讲清三件事：
1. 为什么错配 —— "三重错配"：时间 / 规则 / 激励
2. 怎么度量 —— 五维评分体系（权重、锚点、公式、等级区间全部动态读取）
3. 数据可信度 —— 来源、流程、60 份标注清单（美股 30 + A股 30）、草稿状态、局限性

所有分数、权重、等级区间、公司名单一律从 data 动态生成，禁止硬编码。
"""

import pandas as pd
import streamlit as st

import ui_common as ui


# ----------------------------------------------------------------------
# 通用描述文字（方法论叙事，与具体公司/分数无关，允许写死）
# ----------------------------------------------------------------------

_TRIPLE_MISMATCH = [
    {
        "icon": "⏳",
        "title": "时间错配",
        "body": (
            "AI 技术迭代周期约 1–3 年（GPU 代际、模型架构、软件框架快速换代），"
            "而会计折旧年限普遍设定为 5–10 年。资产在账面上按线性节奏缓慢折旧，"
            "经济价值却可能早已随技术迭代断崖式衰减 —— “账面活着，市场死了”。"
        ),
    },
    {
        "icon": "📐",
        "title": "规则错配",
        "body": (
            "现行会计准则成形于工业时代，面向厂房、机床等实体资产设计；"
            "面对 GPU 集群、数据中心、自研 AI 基础设施这类数字时代资产，"
            "折旧年限、残值假设、减值触发条件都缺乏针对性的强制约束，"
            "为管理层留下了宽泛的自由裁量空间。"
        ),
    },
    {
        "icon": "🎭",
        "title": "激励错配",
        "body": (
            "AI 军备竞赛迫使企业持续大额资本开支，而资本市场又以利润为核心估值锚。"
            "拉长折旧年限、推迟减值确认，可以同时在当期“做大利润、摊薄成本”，"
            "形成系统性的报表美化动机 —— 规则弹性 × 业绩压力 = 折旧操纵温床。"
        ),
    },
]

_FORMULA_TEXT = "综合分 = Σ ( 维度权重 wᵢ × 维度得分 sᵢ )"

_ANCHOR_NOTE = (
    "五维评分采用 1–5 分锚点制：1 分 = 保守 / 低风险（折旧政策谨慎、减值充分、"
    "披露透明）；5 分 = 激进 / 高风险（折旧年限显著长于技术寿命、减值回避、"
    "披露含糊）。每个维度按统一锚点评分后加权汇总。"
)

_PIPELINE_STEPS = [
    "下载 10-K",
    "定位折旧政策 / 风险章节",
    "五维评分",
    "交叉复核",
    "入库",
]

_LIMITATIONS = [
    "**样本量有限**：当前标注样本为双市场 60 份（美股 10 家 × 3 财年 + A股 10 家 × 3 年），"
    "统计结论需以“初步信号”理解，后续将扩充行业与年份覆盖。",
    "**单一年份截面**：评分基于各财年 10-K 的静态快照，"
    "尚未纳入折旧政策跨期变更的差分检验与事件研究。",
    "**评分规则待升级**：五维权重目前为专家规则设定，"
    "下一阶段将以标注样本训练 XGBoost 模型，用数据学习权重与非线性交互。",
    "**文本特征待深化**：信号定位目前依赖关键词与人工判读，"
    "计划接入 FinBERT 抽取风险段落语义特征，降低对关键词表的依赖。",
]


# ----------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------

def _card(icon: str, title: str, body: str) -> str:
    return (
        f"<div class='card'><h4>{icon} {title}</h4>"
        f"<p>{body}</p></div>"
    )


def _pick_dimension_source(cases: list[dict]) -> dict | None:
    """取任一维度定义完整的 case 作为维度定义来源。"""
    for case in cases:
        dims = case.get("dimensions") or []
        if dims and all(d.get("id") and d.get("name") for d in dims):
            return case
    return None


# ----------------------------------------------------------------------
# 各区块渲染
# ----------------------------------------------------------------------

def _render_mismatch():
    ui.section("核心问题 · 三重错配")
    st.markdown(
        "<div class='quote'>AI 技术迭代周期（1–3 年）远短于会计折旧年限（5–10 年），"
        "导致资产“账面活着、市场死了”，利润被系统性虚增。本项目从三个层面拆解这一错配。"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, item in zip(cols, _TRIPLE_MISMATCH):
        with col:
            st.markdown(
                _card(item["icon"], item["title"], item["body"]),
                unsafe_allow_html=True,
            )


def _render_scoring_system(cases: list[dict]):
    ui.section("五维评分体系")

    source = _pick_dimension_source(cases)
    if source is None:
        st.info("暂未读取到维度定义数据，评分体系表无法生成。")
        return

    dims = source["dimensions"]
    df = pd.DataFrame(
        [
            {
                "维度编号": d.get("id", ""),
                "维度名称": d.get("name", ""),
                "英文名称": d.get("name_en", ""),
                "权重": d.get("weight", 0),
            }
            for d in dims
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    total_weight = sum(d.get("weight", 0) for d in dims)
    weight_str = " + ".join(
        f"{d.get('weight', 0):.2f}×{d.get('id', '')}" for d in dims
    )
    st.markdown(
        f"<div class='formula'>{_FORMULA_TEXT} &nbsp;= {weight_str}"
        f"&nbsp;（当前权重合计 {total_weight:.2f}）</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"维度定义动态读取自标注文件（示例来源：{source.get('ticker', '')} "
        f"{source.get('fiscal_year', '')} 财年标注），权重如有调整自动生效。"
    )
    st.markdown(
        f"<div class='quote'>{_ANCHOR_NOTE}</div>",
        unsafe_allow_html=True,
    )


def _render_level_table(panel: pd.DataFrame):
    ui.section("风险等级划分")
    if panel is None or panel.empty or "risk_level" not in panel.columns:
        st.info("暂无训练面板数据，等级划分表无法生成。")
        return

    score_col = "composite_score" if "composite_score" in panel.columns else None
    if score_col is None:
        st.info("面板数据缺少综合分列，等级划分表无法生成。")
        return

    grp = (
        panel.dropna(subset=["risk_level"])
        .groupby("risk_level", dropna=False)
        .agg(
            分数下限=(score_col, "min"),
            分数上限=(score_col, "max"),
            标注数量=(score_col, "size"),
        )
        .reset_index()
        .rename(columns={"risk_level": "风险等级"})
        .sort_values("分数下限", ascending=False)
        .reset_index(drop=True)
    )
    grp["分数下限"] = grp["分数下限"].round(2)
    grp["分数上限"] = grp["分数上限"].round(2)

    st.dataframe(grp, use_container_width=True, hide_index=True)
    st.caption(
        "分数区间与数量由训练面板按 risk_level 分组实时统计，"
        "等级阈值的通用说明：综合分越高，折旧激进程度与报表失真风险越高。"
    )


def _render_data_source(cases: list[dict]):
    ui.section("数据来源与标注流程")

    tickers = sorted({c.get("ticker", "") for c in cases if c.get("ticker")})
    years = sorted({c.get("fiscal_year") for c in cases if c.get("fiscal_year")})
    year_text = f"{years[0]}–{years[-1]}" if len(years) >= 2 else (str(years[0]) if years else "—")

    st.markdown(
        f"<div class='quote'>数据来自美国 SEC EDGAR 披露的 10-K 年度报告，"
        f"采用“AI 辅助定位 + 人工标注复核”的方式完成。当前已入库标注 "
        f"<b>{len(cases)}</b> 份，覆盖 <b>{len(tickers)}</b> 家科创企业、"
        f"财年跨度 <b>{year_text}</b>。</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # 流程：箭头串联
    step_html = ""
    for i, step in enumerate(_PIPELINE_STEPS):
        step_html += (
            f"<span class='chip' style='font-size:0.85rem; padding:0.3rem 0.9rem'>"
            f"{i + 1}. {step}</span>"
        )
        if i < len(_PIPELINE_STEPS) - 1:
            step_html += (
                f"<span style='color:{ui.MUTED}; margin:0 0.35rem'>→</span>"
            )
    st.markdown(f"<div style='line-height:2.4'>{step_html}</div>", unsafe_allow_html=True)
    st.caption(
        "AI 辅助环节负责在 10-K 全文中定位折旧政策、减值迹象与竞争风险相关段落；"
        "评分、证据链与结论均由标注人员人工完成并复核。"
    )


def _render_annotation_table(cases: list[dict]):
    ui.section("标注清单总表")
    if not cases:
        st.info("暂无标注数据。")
        return

    status_map = {"confirmed": "已确认", "draft_pending_review": "草稿待审"}
    rows = []
    for c in cases:
        rows.append(
            {
                "股票代码": c.get("ticker", ""),
                "公司名称": c.get("name", ""),
                "财年": c.get("fiscal_year", ""),
                "综合分": round(float(c.get("score", 0)), 2),
                "风险等级": c.get("risk_level", ""),
                "审核状态": status_map.get(c.get("review_status", ""), c.get("review_status", "未知")),
                "版本": c.get("version", ""),
                "标注时间": str(c.get("annotated_at", ""))[:10],
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_draft_notice(cases: list[dict]):
    ui.section("草稿状态声明")
    if not cases:
        st.info("暂无标注数据，无法统计草稿状态。")
        return

    drafts = [c for c in cases if c.get("is_draft")]
    n_draft = len(drafts)
    n_total = len(cases)
    if n_draft == 0:
        st.success(
            f"当前 {n_total} 份标注全部已确认，无待审草稿。"
        )
    else:
        names = "、".join(
            f"{c.get('ticker', '')} {c.get('fiscal_year', '')}" for c in drafts
        )
        st.warning(
            f"当前共有 **{n_draft} / {n_total}** 份标注为草稿待审状态（{names}）。"
            "草稿分数经项目总负责人复核后可能微调；本看板全部动态读取标注文件，"
            "复核调整一经入库即自动生效，无需手动更新看板。"
        )


def _render_limitations():
    ui.section("局限性与下一步")
    for item in _LIMITATIONS:
        st.markdown(f"- {item}")


# ----------------------------------------------------------------------
# 页面入口
# ----------------------------------------------------------------------

def render(data: dict) -> None:
    """P5 · 方法论 页面入口。data: {'panel': DataFrame, 'cases': [case, ...]}"""
    panel = data.get("panel") if isinstance(data, dict) else None
    cases = data.get("cases", []) if isinstance(data, dict) else []
    if cases is None:
        cases = []

    _render_mismatch()
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_scoring_system(cases)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_level_table(panel)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_data_source(cases)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_annotation_table(cases)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_draft_notice(cases)
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    _render_limitations()
