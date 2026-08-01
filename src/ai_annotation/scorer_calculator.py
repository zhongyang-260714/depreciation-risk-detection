"""评分计算器

根据五维度得分和固定权重计算综合分，判定风险等级。
不让 LLM 做算术，程序来算。
"""

from typing import List, Dict


# 固定权重（与报告 3.4.1 完全一致）
WEIGHTS = {
    "D1": 0.25,
    "D2": 0.20,
    "D3": 0.20,
    "D4": 0.20,
    "D5": 0.15,
}

RISK_LEVEL_THRESHOLDS = [
    (4.0, "高风险", "High Risk"),
    (3.0, "中高风险", "Medium-High Risk"),
    (2.0, "中风险", "Medium Risk"),
    (0.0, "低风险", "Low Risk"),
]


def compute_composite_score(dimension_scores: List[Dict]) -> Dict:
    """计算综合评分。

    Args:
        dimension_scores: DeepSeek 返回的 dimension_scores 列表

    Returns:
        {
            "weighted_score": float,
            "max_score": 5.0,
            "risk_level": str,
            "risk_level_en": str,
            "score_breakdown": str,  # 验算式，如 "4×0.25+3×0.20+...=3.45"
        }
    """
    total = 0.0
    parts = []

    for d in dimension_scores:
        dim_id = d.get("dimension_id", "")
        score = float(d.get("score", 0))
        weight = WEIGHTS.get(dim_id, d.get("weight", 0))
        weighted = score * weight
        total += weighted
        parts.append(f"{score}×{weight:.2f}={weighted:.2f}")

    breakdown = "+".join(parts) + f"={total:.2f}"

    # 判定风险等级
    risk_level = "未知"
    risk_level_en = "Unknown"
    for threshold, level, level_en in RISK_LEVEL_THRESHOLDS:
        if total >= threshold:
            risk_level = level
            risk_level_en = level_en
            break

    return {
        "weighted_score": round(total, 2),
        "max_score": 5.0,
        "risk_level": risk_level,
        "risk_level_en": risk_level_en,
        "score_breakdown": breakdown,
    }


def enrich_dimension_scores(dimension_scores: List[Dict]) -> List[Dict]:
    """给维度评分补充权重（如果 DeepSeek 没填的话）。"""
    for d in dimension_scores:
        dim_id = d.get("dimension_id", "")
        if "weight" not in d or d["weight"] is None:
            d["weight"] = WEIGHTS.get(dim_id, 0.20)
    return dimension_scores
