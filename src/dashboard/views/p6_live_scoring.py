"""P6 · 实时评分演示（PoC 模型推理）

两种演示模式：
- 样本公司演示：从 v06 面板选择公司/财年，预填 55 项指标，
  展示"模型评分 vs 人工评分"对照（样本内回代，演示评分流程）。
- 自定义指标输入：手工录入关键指标（资本开支强度、折旧年限变更等 Top 特征），
  模型实时输出评分、风险等级与 SHAP 单项贡献——展示"输入指标 → 实时推理"能力。

模型：depreciation_scorer_v03（30 样本可行性验证模型，附录 F 同款超参数）。
免责：输出为 PoC 演示，不构成预测能力声明或投资建议。
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

import ui_common as ui
from data_loader import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))

# 自定义输入模式下展示的关键指标（SHAP Top 10，附录 F 表 F-2）
# 注：life_extended_current_period 为 0/1 开关，单独用单选框渲染，不入此列表
KEY_FEATURES = [
    ("capex_to_revenue", "资本开支 / 营收", 0.25, "比值，如 0.25 = 25%"),
    ("server_life_min_years", "服务器折旧年限下限（年）", 5.0, "如 4–6 年区间填下限"),
    ("ppe_net", "固定资产净额（百万美元）", 100000.0, "PP&E, net"),
    ("depreciation", "折旧费用（百万美元）", 15000.0, "当期折旧（不含摊销）"),
    ("ppe_turnover", "固定资产周转率（营收/固定资产）", 2.0, "比值"),
    ("total_assets", "总资产（百万美元）", 300000.0, "缺失行较多，可不填"),
    ("rd_expense", "研发费用（百万美元）", 30000.0, ""),
    ("rd_intensity", "研发强度（研发/营收）", 0.20, "比值"),
    ("asset_turnover", "总资产周转率", 0.8, "比值"),
]

LEVEL_BADGE = {"高风险": "#B3402F", "中高风险": "#C07A1B", "低风险": "#2E7D5B"}


@st.cache_data(show_spinner="正在加载 v06 面板……")
def _load_v06() -> pd.DataFrame:
    df = pd.read_csv(REPO_ROOT / "data" / "processed" / "training_v06_panel_30_full.csv",
                     encoding="utf-8-sig")
    return df.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)


@st.cache_resource(show_spinner="正在加载评分模型……")
def _scorer():
    from src.scoring.predictor import get_scorer
    return get_scorer(REPO_ROOT / "models")


def _show_result(result: dict, human_score: float | None = None) -> None:
    """统一的结果展示区：评分 + 等级徽章 + SHAP 贡献 + 免责。"""
    color = LEVEL_BADGE.get(result["risk_level"], "#8A877F")
    cols = st.columns([1, 1, 2])
    with cols[0]:
        st.metric("模型综合评分", f"{result['score']:.2f} / 5.00")
    with cols[1]:
        if human_score is not None:
            st.metric("人工五维评分（对照）", f"{human_score:.2f}",
                      delta=f"{result['score'] - human_score:+.2f}", delta_color="off")
    with cols[2]:
        st.markdown(
            f"<div style='margin-top:0.6rem;'>风险等级 "
            f"<span style='background:{color};color:#fff;border-radius:999px;"
            f"padding:0.25rem 1rem;font-weight:600;'>{result['risk_level']}</span></div>",
            unsafe_allow_html=True)
        st.caption(f"已提供指标 {result['n_features_provided']}/{result['n_features_total']} 项"
                   f" · 缺失指标由 XGBoost 原生缺失值机制自动处理")

    st.markdown("**本次评分的主要驱动因素（SHAP 单项贡献）**")
    contrib = pd.DataFrame(result["top_contributors"])
    contrib["指标"] = contrib["label"]
    contrib["输入值"] = contrib["value"].map(lambda v: "未提供" if v is None else f"{v:,.4g}")
    contrib["贡献方向"] = contrib["direction"]
    contrib["SHAP 贡献"] = contrib["shap"].map(lambda s: f"{s:+.3f}")
    st.dataframe(contrib[["指标", "输入值", "贡献方向", "SHAP 贡献"]],
                 hide_index=True, width="stretch")

    st.caption(f"⚠️ {result['disclaimer']}方法学参考指标：{result['reference_metrics']}")


def render(data: dict) -> None:
    st.subheader("P6 · 实时评分演示（模型推理）")
    st.markdown(
        "前五个页面展示的是 **30 份人工复核标注库** 的结果；本页展示模型的 **实时推理能力**："
        "输入财务指标，XGBoost 评分模型实时输出综合评分、风险等级与驱动因素解释。")

    model_ok = (REPO_ROOT / "models" / "depreciation_scorer_v03.joblib").exists()
    if not model_ok:
        st.error("未找到模型文件 models/depreciation_scorer_v03.joblib，"
                 "请先运行 train_scorer.py 训练并序列化模型。")
        return

    mode = st.radio("演示模式", ["样本公司演示", "自定义指标输入"],
                    horizontal=True, key="p6_mode")
    st.divider()

    if mode == "样本公司演示":
        df = _load_v06()
        col1, col2 = st.columns([2, 1])
        with col1:
            ticker = st.selectbox("选择公司", sorted(df["ticker"].unique()), key="p6_ticker")
        with col2:
            years = sorted(df.loc[df["ticker"] == ticker, "fiscal_year"].unique())
            fy = st.selectbox("财年", years, index=len(years) - 1, key="p6_fy")

        row = df[(df["ticker"] == ticker) & (df["fiscal_year"] == fy)].iloc[0]
        scorer = _scorer()
        features = {c: (None if pd.isna(row[c]) else float(row[c]))
                    for c in scorer.feature_cols}
        human = float(row["composite_score"])

        if st.button("▶ 运行实时评分", type="primary", key="p6_run_sample"):
            with st.spinner("模型推理中……"):
                result = scorer.predict({k: v for k, v in features.items() if v is not None})
            _show_result(result, human_score=human)
            st.caption("说明：该行为训练样本，此处为样本内回代，用于演示评分流程与解释输出；"
                       "模型对全新公司的复现能力以附录 F 的 LOGO（留一公司法）交叉验证为准。")
        else:
            st.info("点击「运行实时评分」查看模型输出。")

    else:
        st.markdown("录入关键指标（默认值为一组中型云厂商画像，可直接运行），其余指标按缺失处理：")
        features: dict[str, float] = {}
        # 0/1 开关单独渲染为单选，杜绝非法输入（如误填 2）
        extended = st.radio(
            "当期是否延长折旧年限", ["否（0）", "是（1）"], index=1,
            horizontal=True, key="p6_in_life_extended",
            help="本财年是否发生折旧年限延长变更（报告发现②的核心事件信号）")
        features["life_extended_current_period"] = 1.0 if extended.startswith("是") else 0.0
        grid = st.columns(2)
        for i, (name, label, default, help_text) in enumerate(KEY_FEATURES):
            with grid[i % 2]:
                features[name] = st.number_input(
                    label, value=float(default), key=f"p6_in_{name}", help=help_text or None)

        if st.button("▶ 运行实时评分", type="primary", key="p6_run_custom"):
            with st.spinner("模型推理中……"):
                result = _scorer().predict(features)
            _show_result(result)
        else:
            st.info("点击「运行实时评分」查看模型输出。")

    with st.expander("技术说明（答辩备查）"):
        st.markdown(
            "- 模型：XGBoost 回归（与附录 F 完全同款超参数：200 棵树、深度 3、学习率 0.05），"
            "在 30 行 × 55 特征面板（10 家 × 3 财年）上全量拟合后序列化（`models/depreciation_scorer_v03.joblib`）\n"
            "- 解释：SHAP TreeExplainer 单项贡献，展示每次评分由哪些指标推高/拉低\n"
            "- 缺失值：XGBoost 原生缺失值路由，无需插补，支持部分指标输入\n"
            "- 同源接口：FastAPI `POST /predict` / `POST /batch_predict`（`src/api/main.py`），"
            "本页面与 API 调用同一评分器实例\n"
            "- 定位：可行性验证（PoC）演示，不构成预测能力声明")
