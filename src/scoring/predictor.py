# -*- coding: utf-8 -*-
"""折旧风险评分器（PoC 演示版）

加载 depreciation_scorer_v03 模型，对输入指标输出：
- 综合评分（1-5，截断到量表范围）
- 风险等级（高风险 ≥4.0 / 中高风险 3.0-3.99 / 低风险 <3.0，对应报告第四章分组）
- SHAP 单项贡献 Top N（解释本次评分主要由哪些指标推高/拉低）

定位：30 样本可行性验证（PoC）模型的演示推理，不构成预测能力声明。
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# 常用特征的展示用中文名（未收录的回退为原始列名）
FEATURE_LABELS = {
    "capex_to_revenue": "资本开支/营收",
    "ppe_net": "固定资产净额",
    "depreciation": "折旧费用",
    "ppe_turnover": "固定资产周转率（营收/固定资产）",
    "total_assets": "总资产",
    "rd_expense": "研发费用",
    "life_extended_current_period": "当期是否延长折旧年限",
    "asset_turnover": "总资产周转率",
    "rd_intensity": "研发强度（研发/营收）",
    "server_life_min_years": "服务器折旧年限下限（年）",
    "server_life_max_years": "服务器折旧年限上限（年）",
    "building_life_min_years": "房屋建筑折旧年限下限（年）",
    "depreciation_rate_ppe": "折旧率（折旧/固定资产）",
    "capex_to_ppe_net": "资本开支/固定资产净额",
    "accumulated_depreciation": "累计折旧",
    "revenue": "营收",
    "net_income": "净利润",
    "operating_income": "营业利润",
    "goodwill": "商誉",
    "intangible_assets_net": "无形资产净额",
    "capex_ppe": "资本开支（PP&E）",
    "amortization": "摊销费用",
    "impairment_loss": "减值损失",
    "inventory_writedown": "存货减记",
    "revenue_growth_rate": "营收同比增速",
    "capex_yoy_growth": "资本开支同比增速",
    "depreciation_growth_rate": "折旧费用同比增速",
}


class DepreciationScorer:
    """XGBoost 折旧风险评分器（演示用）。"""

    def __init__(self, model_dir: str | Path):
        model_dir = Path(model_dir)
        self.meta = json.loads(
            (model_dir / "depreciation_scorer_v03_meta.json").read_text(encoding="utf-8"))
        self.model = joblib.load(model_dir / "depreciation_scorer_v03.joblib")
        self.feature_cols = self.meta["feature_cols"]
        self._explainer = None  # shap 按需加载（首次预测时初始化）

    def _get_explainer(self):
        if self._explainer is None:
            import shap
            self._explainer = shap.TreeExplainer(self.model)
        return self._explainer

    def risk_level_of(self, score: float) -> str:
        for band in self.meta["risk_bands"]:
            if score >= band["min"]:
                return band["level"]
        return self.meta["risk_bands"][-1]["level"]

    def predict(self, features: dict, top_n: int = 5) -> dict:
        """单样本评分。

        Args:
            features: {特征名: 数值}，缺失特征自动按 NaN 处理（XGBoost 原生缺失值路由）。
            top_n: 返回的 SHAP 贡献条目数。

        Returns:
            dict: score / risk_level / top_contributors / n_features_provided / disclaimer 等。
        """
        row = {c: features.get(c, np.nan) for c in self.feature_cols}
        X = pd.DataFrame([row], columns=self.feature_cols).astype(float)

        raw = float(self.model.predict(X)[0])
        lo, hi = self.meta["score_range"]
        score = float(np.clip(raw, lo, hi))

        shap_values = self._get_explainer().shap_values(X)[0]
        order = np.argsort(-np.abs(shap_values))[:top_n]
        contributors = [
            {
                "feature": self.feature_cols[i],
                "label": FEATURE_LABELS.get(self.feature_cols[i], self.feature_cols[i]),
                "value": (None if pd.isna(X.iloc[0, i]) else float(X.iloc[0, i])),
                "shap": float(shap_values[i]),
                "direction": "推高评分" if shap_values[i] > 0 else "拉低评分",
            }
            for i in order
        ]

        provided = sum(1 for c in self.feature_cols
                       if c in features and features[c] is not None
                       and not (isinstance(features[c], float) and np.isnan(features[c])))
        return {
            "score": round(score, 3),
            "risk_level": self.risk_level_of(score),
            "top_contributors": contributors,
            "n_features_provided": provided,
            "n_features_total": len(self.feature_cols),
            "model_version": self.meta["model_version"],
            "reference_metrics": self.meta["reference_metrics"],
            "disclaimer": self.meta["disclaimer"],
        }


# 模块级单例（Streamlit / FastAPI 共用，避免重复加载）
_SCORER: DepreciationScorer | None = None


def get_scorer(model_dir: str | Path) -> DepreciationScorer:
    global _SCORER
    if _SCORER is None:
        _SCORER = DepreciationScorer(model_dir)
    return _SCORER
