"""评分计算器 v2 — 增加规则引擎后处理

根据五维度得分和固定权重计算综合分，判定风险等级。
新增：规则引擎后处理，用硬规则覆盖 AI 的模糊判断。
"""

import re
from typing import List, Dict, Optional


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

# ============================================================
# 规则引擎：硬规则覆盖
# ============================================================

# 英文数字 → 阿拉伯数字映射
_WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
}

# D2 规则：年限变更检测
D2_LIFE_CHANGE_PATTERNS = [
    # "increased the estimate of useful lives from four years to six years"
    re.compile(r"increased\s+(?:the\s+)?(?:estimate\s+of\s+)?(?:useful\s+)?(?:life|lives)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "extended the useful life from 5 to 8 years"
    re.compile(r"extended\s+(?:the\s+)?(?:useful\s+)?(?:life|lives)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "changed the useful life of servers from four to six years"
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+\w+\s+(?:from|was)\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "useful lives were increased from X to Y years"
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+(?:were\s+)?(?:increased|extended)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # 泛化模式："increase in the estimated useful lives ... to 5.5 years" (META风格)
    re.compile(r"(?:increase|extension|lengthening)\s+(?:in\s+)?(?:the\s+)?(?:estimated\s+)?(?:useful\s+)?(?:life|lives).{0,40}(?:to|up\s+to)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "useful lives of most servers ... to 5.5 years"
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+.{0,30}(?:to|up\s+to)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # 更泛化：只要有 useful life + increase/extend/change + 数字年限
    re.compile(r"(?:useful\s+)?(?:life|lives).{0,80}?(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:useful\s+)?(?:life|lives).{0,30}(?:increased|extended|lengthened|changed).{0,80}?(\d+(?:\.\d+)?)\s*years?", re.I),
]

# D1 规则：提取具体年限
D1_LIFE_YEAR_PATTERNS = [
    # "useful lives of our servers and network equipment of four to six years"
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+.*?\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "estimated useful life of five years" / "to 5.5 years"
    re.compile(r"(?:estimated\s+)?(?:useful\s+)?(?:life|lives)\s+(?:of\s+|to\s+|up\s+to\s+)(\d+(?:\.\d+)?)\s*years?", re.I),
    # "depreciated over 5 to 7 years"
    re.compile(r"depreciat\w+\s+over\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    # "useful life ... X years" 更泛化（非贪婪，扩大范围到80字符）
    re.compile(r"(?:useful\s+)?(?:life|lives).{0,80}?(\d+(?:\.\d+)?)\s*years?", re.I),
]

# D4 规则：提取 CAPEX 和 Revenue（兼容有无$前缀）
D4_CAPEX_PATTERNS = [
    re.compile(r"\$?([\d,.]+)\s*(?:billion|million|B|M)\s+(?:on\s+)?capital\s+expenditures", re.I),
    re.compile(r"capital\s+expenditures\s+(?:of\s+)?\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
]
D4_REVENUE_PATTERNS = [
    re.compile(r"revenues?\s+(?:of\s+)?\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
    re.compile(r"total\s+revenues?\s+\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
]


def _parse_number_word(word: str) -> Optional[float]:
    """解析英文数字或阿拉伯数字为浮点数。"""
    word = word.lower().strip()
    try:
        return float(word)
    except ValueError:
        pass
    return _WORD_TO_NUM.get(word)


def _extract_life_years(text: str) -> Optional[float]:
    """从文本中提取折旧年限（取最大值）。"""
    text_lower = text.lower()
    years = []
    
    for pattern in D1_LIFE_YEAR_PATTERNS:
        for m in pattern.finditer(text_lower):
            groups = m.groups()
            if len(groups) == 2:
                y1 = _parse_number_word(groups[0])
                y2 = _parse_number_word(groups[1])
                if y1 is not None and y2 is not None:
                    years.append(max(y1, y2))
            elif len(groups) == 1:
                y = _parse_number_word(groups[0])
                if y is not None and 1.5 <= y <= 30:
                    years.append(y)
    
    if not years:
        word_pattern = re.compile(
            r"(?:useful\s+)?(?:life|lives).{0,80}?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\s*years?",
            re.I,
        )
        for m in word_pattern.finditer(text_lower):
            y = _parse_number_word(m.group(1))
            if y is not None and 1.5 <= y <= 30:
                years.append(y)
    
    return max(years) if years else None


def _detect_life_extension(text: str) -> bool:
    """检测文本中是否有年限延长变更。"""
    for pattern in D2_LIFE_CHANGE_PATTERNS:
        if pattern.search(text):
            return True
    return False


def _extract_capex_ratio(text: str) -> Optional[float]:
    """从文本中提取 CAPEX/Revenue 比率。"""
    capex = None
    revenue = None
    
    for pattern in D4_CAPEX_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                val_str = m.group(1).replace(",", "")
                snippet = text[m.start():m.end()].lower()
                if "billion" in snippet or "b" in snippet:
                    capex = float(val_str)
                elif "million" in snippet or "m" in snippet:
                    capex = float(val_str) / 1000
            except (ValueError, IndexError):
                pass
            break
    
    for pattern in D4_REVENUE_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                val_str = m.group(1).replace(",", "")
                snippet = text[m.start():m.end()].lower()
                if "billion" in snippet or "b" in snippet:
                    revenue = float(val_str)
                elif "million" in snippet or "m" in snippet:
                    revenue = float(val_str) / 1000
            except (ValueError, IndexError):
                pass
            break
    
    if capex is not None and revenue is not None and revenue > 0:
        return round(capex / revenue * 100, 1)
    return None


def apply_hard_rules(
    dimension_scores: List[Dict],
    candidates: List[Dict],
    raw_deepseek: Optional[Dict] = None,
    full_html: Optional[str] = None,
) -> tuple:
    """应用硬规则覆盖 AI 评分。

    规则：
    1. D2: 如果任何段落/全文包含年限延长，D2 强制 ≥4
    2. D1: 如果提取到具体年限，按错配倍数校准
    3. D4: 如果提取到 CAPEX/Revenue，按比率校准（阈值与报告锚点表一致：25/15/8/3）
    """
    all_text = " ".join(c.get("text_excerpt", "") for c in candidates)
    all_text_lower = all_text.lower()
    
    search_text = all_text_lower
    if full_html:
        search_text = full_html.lower()
    
    dim_map = {d.get("dimension_id", ""): d for d in dimension_scores}
    rules_applied = []
    
    # === 规则 1: D2 年限变更 ===
    if _detect_life_extension(search_text):
        d2 = dim_map.get("D2")
        if d2 and d2.get("score", 0) < 4:
            old_score = d2["score"]
            d2["score"] = 4
            d2["rule_applied"] = True
            d2["rule_reason"] = "Detected current-period useful life extension"
            rules_applied.append(f"D2: {old_score} → 4 (life extension detected)")
    
    # === 规则 2: D1 年限错配 ===
    max_life = _extract_life_years(search_text)
    if max_life is not None:
        d1 = dim_map.get("D1")
        if d1:
            mismatch_ratio = max_life / 1.5
            old_score = d1.get("score", 0)
            
            if mismatch_ratio >= 4:
                new_score = 5
            elif mismatch_ratio >= 2.5:
                new_score = 4
            elif mismatch_ratio >= 1.8:
                new_score = 3
            elif mismatch_ratio >= 1.2:
                new_score = 2
            else:
                new_score = 1
            
            if new_score != old_score:
                d1["score"] = new_score
                d1["rule_applied"] = True
                d1["rule_reason"] = f"Extracted useful life = {max_life} years, mismatch ratio = {mismatch_ratio:.1f}x"
                rules_applied.append(f"D1: {old_score} → {new_score} (life={max_life}y, ratio={mismatch_ratio:.1f}x)")
    
    # === 规则 3: D4 CAPEX 强度 ===
    capex_search_text = search_text if full_html else all_text
    capex_ratio = _extract_capex_ratio(capex_search_text)
    if capex_ratio is not None:
        d4 = dim_map.get("D4")
        if d4:
            old_score = d4.get("score", 0)
            if capex_ratio >= 25:
                new_score = 5
            elif capex_ratio >= 15:
                new_score = 4
            elif capex_ratio >= 8:
                new_score = 3
            elif capex_ratio >= 3:
                new_score = 2
            else:
                new_score = 1
            
            if new_score != old_score:
                d4["score"] = new_score
                d4["rule_applied"] = True
                d4["rule_reason"] = f"Calculated CAPEX/Revenue = {capex_ratio:.1f}%"
                rules_applied.append(f"D4: {old_score} → {new_score} (CAPEX/Revenue={capex_ratio:.1f}%)")
    
    return list(dim_map.values()), rules_applied


# ============================================================
# 原有函数（保持不变）
# ============================================================

def compute_composite_score(dimension_scores: List[Dict]) -> Dict:
    """计算综合评分。"""
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
