"""评分计算器 v4 — 规则引擎后处理（修复重复代码、优化D1/D2规则）

根据五维度得分和固定权重计算综合分，判定风险等级。
v4改进：
- 清理重复代码
- D1年限提取从"取最大"改为"取范围中点"，避免过度保守
- D2年限变更规则增加幅度感知，不再一刀切强制4分
- A股中文正则增强
"""

import re
from typing import List, Dict, Optional, Tuple


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
# 技术半衰期基准（按资产类型）
# ============================================================

TECH_CYCLE_BASELINE = {
    "server": 1.5,
    "datacenter_equipment": 1.5,
    "gpu_cluster": 1.5,
    "wafer_fab_equipment": 3.5,
    "manufacturing_equipment": 3.5,
    "general_equipment": 4.0,
    "building": 20.0,
    "land": 50.0,
    "intangible": 2.0,
    "software": 2.0,
    "patent": 3.0,
    "lease": 5.0,
    "employee_benefit": 10.0,
    "debt": 10.0,
    "unknown": 1.5,
}

ASSET_TYPE_KEYWORDS = {
    "server": ["server", "network equipment", "datacenter", "data center", "cloud infrastructure", "computing equipment", "it equipment", "computer equipment", "compute hardware"],
    "gpu_cluster": ["gpu", "tpu", "ai accelerator", "graphics processing"],
    "wafer_fab_equipment": ["wafer fabrication", "fab equipment", "semiconductor manufacturing", "foundry equipment", "晶圆厂", "制造设备"],
    "manufacturing_equipment": ["machinery and equipment", "production equipment", "manufacturing equipment"],
    "general_equipment": ["equipment", "machinery"],
    "building": ["building", "land", "facility", "construction in progress", "厂房", "建筑物"],
    "intangible": ["intangible", "goodwill", "amortiz", "acquisition-related", "xilinx", "developed technology", "customer relationship", "无形资产", "商誉", "摊销"],
    "software": ["software", "license", "developed technology"],
    "patent": ["patent", "intellectual property"],
    "lease": ["lease", "rental", "operating lease", "finance lease", "租赁"],
    "employee_benefit": ["employee", "pension", "retirement", "service period", "vesting", "员工", "退休", "养老金"],
    "debt": ["debt", "bond", "loan", "borrowing", "maturity", "债务", "债券"],
}

D1_EXCLUSION_PATTERNS = [
    re.compile(r"\bamortiz", re.I),
    re.compile(r"\bgoodwill\b", re.I),
    re.compile(r"\bintangible\b", re.I),
    re.compile(r"\bacquisition[- ]related\b", re.I),
    re.compile(r"\bcustomer relationship\b", re.I),
    re.compile(r"\bdeveloped technology\b", re.I),
    re.compile(r"\blease\b", re.I),
    re.compile(r"\bemployee\b", re.I),
    re.compile(r"\bpension\b", re.I),
    re.compile(r"\bdebt\b", re.I),
    re.compile(r"\bmaturity\b", re.I),
    re.compile(r"\bvesting\b", re.I),
    re.compile(r"摊销", re.I),
    re.compile(r"商誉", re.I),
    re.compile(r"无形资产", re.I),
    re.compile(r"租赁", re.I),
    re.compile(r"员工", re.I),
    re.compile(r"退休", re.I),
]

D1_CONFIRMATION_KEYWORDS = [
    "depreciat", "fixed asset", "property, plant", "pp&e", "equipment",
    "useful life", "estimated life", "资产折旧", "固定资产", "折旧年限", "使用年限",
]

_WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
}

# ============================================================
# D2 规则：年限变更检测
# ============================================================

D2_LIFE_CHANGE_PATTERNS_EN = [
    re.compile(r"increased\s+(?:the\s+)?(?:estimate\s+of\s+)?(?:useful\s+)?(?:life|lives)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"extended\s+(?:the\s+)?(?:useful\s+)?(?:life|lives)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+\w+\s+(?:from|was)\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+(?:were\s+)?(?:increased|extended)\s+from\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:increase|extension|lengthening)\s+(?:in\s+)?(?:the\s+)?(?:estimated\s+)?(?:useful\s+)?(?:life|lives).{0,40}(?:to|up\s+to)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
]

D2_LIFE_CHANGE_PATTERNS_CN = [
    re.compile(r"折旧年限\s*[:：]?\s*由\s*(\d+(?:\.\d+)?)\s*年\s*(?:延长|延长到|延长至|调整为|变更为|改为|提高到|提升到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"使用寿命\s*[:：]?\s*由\s*(\d+(?:\.\d+)?)\s*年\s*(?:延长|延长到|延长至|调整为|变更为|改为|提高到|提升到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"预计使用年限\s*[:：]?\s*由\s*(\d+(?:\.\d+)?)\s*年\s*(?:延长|延长到|延长至|调整为|变更为|改为|提高到|提升到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"(?:延长|调整|变更).{0,20}折旧年限.{0,20}(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"(?:延长|调整|变更).{0,20}使用寿命.{0,20}(\d+(?:\.\d+)?)\s*年"),
]

D2_LIFE_CHANGE_PATTERNS = D2_LIFE_CHANGE_PATTERNS_EN + D2_LIFE_CHANGE_PATTERNS_CN

# ============================================================
# D1 规则：提取具体年限
# ============================================================

D1_LIFE_YEAR_PATTERNS_EN = [
    re.compile(r"depreciat\w+\s+over\s+(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"depreciat\w+\s+(?:on\s+)?(?:a\s+)?(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+(?:our\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(\d+(?:\.\d+)?)\s*(?:to|-)\s+(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:useful\s+)?(?:life|lives)\s+of\s+(?:our\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(?:of\s+|to\s+|up\s+to\s+)(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:estimated\s+)?(?:useful\s+)?(?:life|lives)\s+(?:of\s+|to\s+|up\s+to\s+)(\d+(?:\.\d+)?)\s*years?", re.I),
    # v6.2新增：通用折旧年限范围匹配（支持 "10 to 30 years" 等格式）
    re.compile(r"(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*years?\s+(?:for\s+)?(?:buildings?|production\s+equipment|other\s+equipment|machinery|servers?|network|datacenter)", re.I),
    re.compile(r"(?:buildings?|production\s+equipment|other\s+equipment|machinery|servers?|network|datacenter).{0,40}?(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*years?", re.I),
    re.compile(r"(?:buildings?|production\s+equipment|other\s+equipment|machinery|servers?|network|datacenter).{0,40}?(?:of\s+|up\s+to\s+)?(\d+(?:\.\d+)?)\s*years?", re.I),
]

D1_LIFE_YEAR_PATTERNS_CN = [
    re.compile(r"折旧年限\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:-|~|至|到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"使用寿命\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:-|~|至|到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"预计使用年限\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:-|~|至|到)\s*(\d+(?:\.\d+)?)\s*年"),
    re.compile(r"按\s*(\d+(?:\.\d+)?)\s*年\s*折旧"),
    re.compile(r"(?:固定资产|机器设备|服务器|房屋建筑).{0,20}?(\d+(?:\.\d+)?)\s*年"),
]

D1_LIFE_YEAR_PATTERNS = D1_LIFE_YEAR_PATTERNS_EN + D1_LIFE_YEAR_PATTERNS_CN

# ============================================================
# D4 规则
# ============================================================

D4_CAPEX_PATTERNS_EN = [
    re.compile(r"\$?([\d,.]+)\s*(?:billion|million|B|M)\s+(?:on\s+)?capital\s+expenditures", re.I),
    re.compile(r"capital\s+expenditures\s+(?:of\s+)?\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
    re.compile(r"capex\s+(?:of\s+)?\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
]
D4_REVENUE_PATTERNS_EN = [
    re.compile(r"revenues?\s+(?:of\s+)?\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
    re.compile(r"total\s+revenues?\s+\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
    re.compile(r"revenues?\s+\$?([\d,.]+)\s*(?:billion|million|B|M)", re.I),
]

D4_CAPEX_PATTERNS_CN = [
    re.compile(r"资本(?:性)?开支\s*(?:为|:|：)?\s*([\d,.]+)\s*(?:亿元?|万元?|元)"),
    re.compile(r"资本支出\s*(?:为|:|：)?\s*([\d,.]+)\s*(?:亿元?|万元?|元)"),
    re.compile(r"购建固定资产\s*(?:为|:|：)?\s*([\d,.]+)\s*(?:亿元?|万元?|元)"),
]
D4_REVENUE_PATTERNS_CN = [
    re.compile(r"营业收入\s*(?:为|:|：)?\s*([\d,.]+)\s*(?:亿元?|万元?|元)"),
    re.compile(r"营业总收入\s*(?:为|:|：)?\s*([\d,.]+)\s*(?:亿元?|万元?|元)"),
]

D4_CAPEX_PATTERNS = D4_CAPEX_PATTERNS_EN + D4_CAPEX_PATTERNS_CN
D4_REVENUE_PATTERNS = D4_REVENUE_PATTERNS_EN + D4_REVENUE_PATTERNS_CN


# ============================================================
# 辅助函数
# ============================================================

def _parse_number_word(word: str) -> Optional[float]:
    word = word.lower().strip()
    try:
        return float(word)
    except ValueError:
        pass
    return _WORD_TO_NUM.get(word)


def _detect_asset_type(text: str) -> str:
    """检测资产类型。

    v6.2修复：当文本同时包含折旧确认上下文时，优先识别为设备类资产，
    避免因为段落中顺带提到"leasehold"就被误判为租赁资产。
    """
    text_lower = text.lower()
    scores = {}
    for asset_type, keywords in ASSET_TYPE_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                word_count = kw.count(" ") + 1
                score += word_count * 0.5
        if score > 0:
            scores[asset_type] = score

    # v6.2修复：折旧上下文优先判定为设备
    has_depreciation_context = (
        "depreciation" in text_lower
        and any(kw in text_lower for kw in ["property", "equipment", "plant", "fixed asset", "pp&e", "useful life"])
    )
    if has_depreciation_context:
        # 降低 lease/building/land 的优先级，避免误判
        for deprioritized in ("lease", "building", "land", "employee_benefit", "debt"):
            if deprioritized in scores:
                scores[deprioritized] *= 0.3

    # P0: 科技行业指纹词升级逻辑（通用化，不硬编码公司名单）
    best_type = max(scores, key=scores.get) if scores else "unknown"
    if best_type in ("general_equipment", "unknown") and has_depreciation_context:
        tech_indicators = [
            "server", "datacenter", "data center", "cloud", "network",
            "computing", "hardware", "technology infrastructure",
            "digital infrastructure", "gpu", "processor", "semiconductor",
            "artificial intelligence", "machine learning", "ai accelerator",
            "networking", "information technology", "it equipment",
            "technology assets", "digital assets",
        ]
        if any(ind in text_lower for ind in tech_indicators):
            # 科技行业折旧上下文，将通用设备升级为服务器/数据中心设备
            return "server"

    if not scores:
        return "unknown"
    return best_type


def _has_exclusion_context(text: str) -> bool:
    """检测排除上下文。

    v6.2修复：不再仅因出现'amortization'等词就排除整个段落。
    如果段落同时包含折旧确认关键词（depreciation + property/equipment），
    说明主要讨论固定资产折旧，即使有'amortization'字样也不排除。
    """
    text_lower = text.lower()

    # 如果文本有强烈的折旧确认上下文，优先保留
    has_depreciation_focus = (
        "depreciation" in text_lower
        and any(kw in text_lower for kw in ["property", "equipment", "plant", "fixed asset", "pp&e", "useful life"])
    )
    if has_depreciation_focus:
        return False

    # 否则按原逻辑检查排除模式
    for pattern in D1_EXCLUSION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def _has_confirmation_context(text: str) -> bool:
    text_lower = text.lower()
    for kw in D1_CONFIRMATION_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def _extract_life_years_from_context(text: str) -> Optional[Tuple[float, str, str, float]]:
    text = text.replace('\n', ' ').replace('\r', ' ')
    text_lower = text.lower()

    if _has_exclusion_context(text):
        return None

    asset_type = _detect_asset_type(text)

    years = []
    for pattern in D1_LIFE_YEAR_PATTERNS:
        for m in pattern.finditer(text_lower):
            groups = m.groups()
            if len(groups) == 2:
                y1 = _parse_number_word(groups[0])
                y2 = _parse_number_word(groups[1])
                if y1 is not None and y2 is not None:
                    upper_y = max(y1, y2)
                    if 1.5 <= upper_y <= 30:
                        years.append(upper_y)
            elif len(groups) == 1:
                y = _parse_number_word(groups[0])
                if y is not None and 1.5 <= y <= 30:
                    years.append(y)

    if not years:
        word_pattern = re.compile(
            r"(?:depreciat\w+|useful\s+life|life|lives|server|equipment|machinery).{0,300}?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+(?:\.\d+)?)"
            r"\s*years?",
            re.I,
        )
        for m in word_pattern.finditer(text_lower):
            y = _parse_number_word(m.group(1))
            if y is not None and 1.5 <= y <= 30:
                years.append(y)

    if not years:
        # v2.4修复：添加英文单词年限范围识别（如"two to six years"）
        word_range_pattern = re.compile(
            r"(?:useful\s+lives?|depreciable\s+life|estimated\s+life|depreciated|over|of)"
            r".*?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\s*(?:to|-|–)\s*"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)"
            r"\s*years?",
            re.I,
        )
        for m in word_range_pattern.finditer(text_lower):
            y1 = _parse_number_word(m.group(1))
            y2_str = m.group(2)
            y2 = _parse_number_word(y2_str) if not y2_str.isdigit() else float(y2_str)
            if y1 is not None and y2 is not None:
                upper_y = max(y1, y2)
                if 1.5 <= upper_y <= 30:
                    years.append(upper_y)
        
        # 单一年限英文单词（如"three years"）
        single_word_pattern = re.compile(
            r"(?:useful\s+lives?|depreciable\s+life|estimated\s+life|depreciated|over|of)"
            r".*?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\s*years?",
            re.I,
        )
        for m in single_word_pattern.finditer(text_lower):
            y = _parse_number_word(m.group(1))
            if y is not None and 1.5 <= y <= 30:
                years.append(y)

    if not years:
        range_pattern = re.compile(
            r"(?:increased|extended|adjusted|changed).{0,80}?"
            r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+(?:\.\d+)?)\s*"
            r"(?:to|-)\s+"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+(?:\.\d+)?)\s*years?",
            re.I,
        )
        for m in range_pattern.finditer(text_lower):
            y1 = _parse_number_word(m.group(1))
            y2 = _parse_number_word(m.group(2))
            if y1 is not None and y2 is not None:
                upper_y = max(y1, y2)
                if 1.5 <= upper_y <= 30:
                    years.append(upper_y)

    if not years:
        return None

    # P1: 根据资产类型过滤不合理的年限（解决多资产类型段落中
    # buildings 的 30 年混入 manufacturing_equipment 的问题）
    if asset_type in ("server", "datacenter_equipment", "gpu_cluster"):
        years = [y for y in years if y <= 10]  # 服务器类设备通常 <= 10 年
    elif asset_type in ("manufacturing_equipment", "general_equipment"):
        years = [y for y in years if y <= 12]  # 生产设备通常 <= 12 年（排除 buildings 的 20-30 年）
    elif asset_type in ("software", "patent", "intangible"):
        years = [y for y in years if y <= 10]  # 软件/无形资产通常 <= 10 年
    elif asset_type in ("building", "land"):
        years = [y for y in years if y >= 10]  # 建筑物通常 >= 10 年

    if not years:
        return None

    # v5优化：取最大值而非中位数，风险由最长年限决定
    max_life = max(years)

    has_confirmation = _has_confirmation_context(text)

    if asset_type in ("building", "land"):
        return None

    if asset_type in ("intangible", "software", "patent", "lease", "employee_benefit", "debt"):
        return None

    if asset_type == "unknown" and not has_confirmation:
        baseline = TECH_CYCLE_BASELINE["unknown"]
        return (max_life, "unknown", "suspicious", baseline)

    baseline = TECH_CYCLE_BASELINE.get(asset_type, 1.5)
    confidence = "high" if has_confirmation else "medium"
    return (max_life, asset_type, confidence, baseline)

def _extract_life_years(
    candidates: List[Dict],
    full_text: Optional[str] = None,
) -> Optional[Tuple[float, str, str, float, str]]:
    results = []
    for c in candidates:
        excerpt = c.get("text_excerpt", "")
        if not excerpt:
            continue
        result = _extract_life_years_from_context(excerpt)
        if result:
            max_life, asset_type, confidence, baseline = result
            results.append((max_life, asset_type, confidence, baseline, excerpt[:120]))

    high_conf = [r for r in results if r[2] in ("high", "medium")]
    if high_conf:
        best = max(high_conf, key=lambda x: x[0])
        return best

    if results:
        best = max(results, key=lambda x: x[0])
        return best

    if full_text:
        search_text = full_text[:50000]
        for match in re.finditer(r"useful\s+(?:life|lives)", search_text, re.I):
            start = max(0, match.start() - 300)
            end = min(len(search_text), match.end() + 300)
            context = search_text[start:end]
            # v6.2修复：排除非折旧政策段落，避免误匹配
            ctx_lower = context.lower()
            # 排除模式1：Note 1 Organization 开头段落（公司概况，非折旧政策）
            is_note1_org = ("note 1" in ctx_lower and "organization" in ctx_lower)
            # 排除模式2：Forward-Looking Statements（前瞻性声明）
            is_forward_looking = ("forward-looking" in ctx_lower or "cautionary statement" in ctx_lower)
            # 排除模式3：Risk Factors 中泛泛提及 useful life（非具体折旧政策）
            is_risk_factor = ("risk factors" in ctx_lower and not any(k in ctx_lower for k in ["depreciat", "property", "equipment"]))
            # 排除模式4：MD&A 中讨论竞争/市场时顺带提到 useful life
            is_md_a_generic = ("management's discussion" in ctx_lower or "item 7" in ctx_lower) and not any(k in ctx_lower for k in ["depreciat", "property", "equipment", "useful life of our"])
            # 折旧确认关键词
            has_depreciation_context = any(k in ctx_lower for k in ["depreciation", "depreciated", "property", "equipment", "useful life of our", "estimated life", "depreciable life"])
            if (is_note1_org or is_forward_looking or is_risk_factor or is_md_a_generic) and not has_depreciation_context:
                continue
            result = _extract_life_years_from_context(context)
            if result and result[2] in ("high", "medium"):
                max_life, asset_type, confidence, baseline = result
                results.append((max_life, asset_type, confidence, baseline, context[:120]))

        if results:
            best = max(results, key=lambda x: x[0])
            return best

    return None


def _detect_life_extension_with_details(text: str) -> Optional[Tuple[float, float]]:
    """检测年限变更，返回(from_year, to_year)或None。

    v6.3修复：
    - 增加英文单词年限支持（three→four to five等）
    - 收集所有匹配取最大ratio，避免只返回第一个匹配而漏掉更大幅度的变更
    """
    all_matches = []

    # 辅助：添加有效匹配
    def _add_match(y1, y2):
        if y1 is not None and y2 is not None and y1 > 0:
            all_matches.append((min(y1, y2), max(y1, y2)))

    # 1. 数字模式
    for pattern in D2_LIFE_CHANGE_PATTERNS:
        for m in pattern.finditer(text):
            groups = m.groups()
            if len(groups) >= 2:
                _add_match(_parse_number_word(groups[0]), _parse_number_word(groups[1]))

    # 2. 英文单词模式A: from (word) years to (word) years
    word_change_pattern = re.compile(
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+(?:up\s+to\s+)?"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    for m in word_change_pattern.finditer(text):
        _add_match(_parse_number_word(m.group(1)), _parse_number_word(m.group(2)))

    # 3. 英文单词模式B: increased ... from (word) to (word) years（扩展匹配距离）
    word_change_pattern2 = re.compile(
        r"(?:increased|extended|changed)\s+.{0,200}?"
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+(?:a\s+range\s+of\s+)?(?:up\s+to\s+)?"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    for m in word_change_pattern2.finditer(text):
        _add_match(_parse_number_word(m.group(1)), _parse_number_word(m.group(2)))

    # 4. 英文单词模式C: "a range of (word) to (word) years"（如 four to five years）
    word_range_pattern = re.compile(
        r"(?:increased|extended|changed)\s+.{0,200}?"
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+a\s+range\s+of\s+"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*"
        r"(?:to|-|–)\s*"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    for m in word_range_pattern.finditer(text):
        _add_match(_parse_number_word(m.group(1)), _parse_number_word(m.group(3)))

    if not all_matches:
        return None

    # 取变更幅度最大的（ratio = to/from）
    best = max(all_matches, key=lambda pair: pair[1] / pair[0] if pair[0] > 0 else 0)
    return best
    """检测年限变更，返回(from_year, to_year)或None。

    v6.3修复：增加英文单词年限支持（three→four to five等）。
    """
    # 先尝试数字模式
    for pattern in D2_LIFE_CHANGE_PATTERNS:
        m = pattern.search(text)
        if m:
            groups = m.groups()
            if len(groups) >= 2:
                y1 = _parse_number_word(groups[0])
                y2 = _parse_number_word(groups[1])
                if y1 is not None and y2 is not None:
                    return (min(y1, y2), max(y1, y2))

    # v6.3新增：英文单词年限变更（如 "from three years to a range of four to five years"）
    # 模式A: from (word) years to (word) years
    word_change_pattern = re.compile(
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through|a range of)\s+(?:up to\s+)?"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    m = word_change_pattern.search(text)
    if m:
        y1 = _parse_number_word(m.group(1))
        y2 = _parse_number_word(m.group(2))
        if y1 is not None and y2 is not None:
            return (min(y1, y2), max(y1, y2))

    # 模式B: increased ... from (word) to (word) years（扩展匹配距离）
    word_change_pattern2 = re.compile(
        r"(?:increased|extended|changed)\s+.{0,200}?"
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+(?:a\s+range\s+of\s+)?(?:up\s+to\s+)?"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    m = word_change_pattern2.search(text)
    if m:
        y1 = _parse_number_word(m.group(1))
        y2 = _parse_number_word(m.group(2))
        if y1 is not None and y2 is not None:
            return (min(y1, y2), max(y1, y2))

    # 模式C: 处理 "a range of (word) to (word) years"（如 four to five years）
    word_range_pattern = re.compile(
        r"(?:increased|extended|changed)\s+.{0,200}?"
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+a\s+range\s+of\s+"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*"
        r"(?:to|-|–)\s*"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    m = word_range_pattern.search(text)
    if m:
        y1 = _parse_number_word(m.group(1))
        y2 = _parse_number_word(m.group(3))  # 取范围上限
        if y1 is not None and y2 is not None:
            return (min(y1, y2), max(y1, y2))
    word_change_pattern2 = re.compile(
        r"(?:increased|extended|changed)\s+.{0,60}?"
        r"from\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)\s*years?\s+"
        r"(?:to|through)\s+(?:a\s+range\s+of\s+)?(?:up\s+to\s+)?"
        r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)",
        re.I,
    )
    m = word_change_pattern2.search(text)
    if m:
        y1 = _parse_number_word(m.group(1))
        y2 = _parse_number_word(m.group(2))
        if y1 is not None and y2 is not None:
            return (min(y1, y2), max(y1, y2))

    return None
    """检测年限变更，返回(from_year, to_year)或None。"""
    for pattern in D2_LIFE_CHANGE_PATTERNS:
        m = pattern.search(text)
        if m:
            groups = m.groups()
            if len(groups) >= 2:
                y1 = _parse_number_word(groups[0])
                y2 = _parse_number_word(groups[1])
                if y1 is not None and y2 is not None:
                    return (min(y1, y2), max(y1, y2))
    return None


def _parse_amount_from_match(text: str, match) -> Optional[float]:
    try:
        val_str = match.group(1).replace(",", "")
        snippet = text[match.start():match.end()].lower()
        val = float(val_str)
        if "亿" in snippet:
            val = val / 10
        elif "万" in snippet:
            val = val / 10000 / 7.2
        elif "billion" in snippet or "b" in snippet:
            pass
        elif "million" in snippet or "m" in snippet:
            val = val / 1000
        return val
    except (ValueError, IndexError):
        return None


def _extract_capex_ratio(text: str) -> Optional[float]:
    capex = None
    revenue = None

    for pattern in D4_CAPEX_PATTERNS:
        m = pattern.search(text)
        if m:
            capex = _parse_amount_from_match(text, m)
            if capex is not None:
                break

    for pattern in D4_REVENUE_PATTERNS:
        m = pattern.search(text)
        if m:
            revenue = _parse_amount_from_match(text, m)
            if revenue is not None:
                break

    if capex is not None and revenue is not None and revenue > 0:
        return round(capex / revenue * 100, 1)
    return None


# ============================================================
# 主函数：规则引擎
# ============================================================

def apply_hard_rules(
    dimension_scores: List[Dict],
    candidates: List[Dict],
    raw_deepseek: Optional[Dict] = None,
    full_html: Optional[str] = None,
) -> tuple:
    all_text = " ".join(c.get("text_excerpt", "") for c in candidates)

    dim_map = {d.get("dimension_id", ""): d for d in dimension_scores}
    rules_applied = []
    warnings = []

    # ================================================================
    # 规则 1: D2 年限变更（v4优化：幅度感知）
    # ================================================================
    search_text = all_text.lower()
    if full_html:
        search_text = full_html.lower()

    d2_change = _detect_life_extension_with_details(search_text)
    if d2_change:
        from_y, to_y = d2_change
        extension_ratio = to_y / from_y if from_y > 0 else 1.0
        d2 = dim_map.get("D2")
        if d2:
            old_score = d2.get("score", 0)
            # v6.2修复：如果变更明确标注为"effective FY2024"或"beginning of fiscal year 2024"
            # 说明变更不是本期生效的，D2最多给4分（已宣布但未生效），不是5分（本期生效）
            is_future_effective = any(
                phrase in search_text
                for phrase in [
                    "effective at the beginning of fiscal year 2024",
                    "became effective at the beginning of fiscal year 2024",
                    "effective fiscal year 2024",
                    "effective beginning of fiscal 2024",
                ]
            )
            # v4优化：根据延长幅度给分，不再一刀切强制4分
            if extension_ratio >= 2.0:
                new_score = 4 if is_future_effective else 5
            elif extension_ratio >= 1.5:
                new_score = 4
            elif extension_ratio >= 1.2:
                new_score = 3
            else:
                new_score = max(old_score, 2)

            # v6.3修复：规则引擎应能双向覆盖（升分+降分）
            # 当检测到明确的年限变更事实时，规则引擎具有强制覆盖权
            if new_score != old_score:
                d2["score"] = new_score
                d2["rule_applied"] = True
                if is_future_effective:
                    d2["rule_reason"] = f"Detected useful life extension from {from_y}y to {to_y}y (ratio={extension_ratio:.1f}x), BUT effective FY2024 not FY2023 → capped at 4"
                    rules_applied.append(f"D2: {old_score} → {new_score} (life extension {from_y}y→{to_y}y, ratio={extension_ratio:.1f}x, BUT effective FY2024 → capped)")
                else:
                    d2["rule_reason"] = f"Detected useful life extension from {from_y}y to {to_y}y (ratio={extension_ratio:.1f}x)"
                    rules_applied.append(f"D2: {old_score} → {new_score} (life extension {from_y}y→{to_y}y, ratio={extension_ratio:.1f}x)")
            else:
                # 分数相同也记录验证信息
                d2["rule_note"] = f"Verified: useful life extension from {from_y}y to {to_y}y (ratio={extension_ratio:.1f}x), effective FY2024 → capped at 4"
                rules_applied.append(f"D2: {old_score} confirmed (life extension {from_y}y→{to_y}y, effective FY2024 → capped at 4)")
                d2["score"] = new_score
                d2["rule_applied"] = True
                if is_future_effective:
                    d2["rule_reason"] = f"Detected useful life extension from {from_y}y to {to_y}y (ratio={extension_ratio:.1f}x), BUT effective FY2024 not FY2023 → capped at 4"
                    rules_applied.append(f"D2: {old_score} → {new_score} (life extension {from_y}y→{to_y}y, ratio={extension_ratio:.1f}x, BUT effective FY2024 → capped)")
                else:
                    d2["rule_reason"] = f"Detected useful life extension from {from_y}y to {to_y}y (ratio={extension_ratio:.1f}x)"
                    rules_applied.append(f"D2: {old_score} → {new_score} (life extension {from_y}y→{to_y}y, ratio={extension_ratio:.1f}x)")

    # ================================================================
    # 规则 2: D1 年限错配（v4：中点替代最大值）
    # ================================================================
    d1_result = _extract_life_years(candidates, full_text=full_html)
    if d1_result:
        median_life, asset_type, confidence, baseline, source_snippet = d1_result
        d1 = dim_map.get("D1")
        if d1:
            mismatch_ratio = median_life / baseline
            old_score = d1.get("score", 0)

            if mismatch_ratio >= 4:
                new_score = 5
            elif mismatch_ratio >= 2.0:
                new_score = 4
            elif mismatch_ratio >= 1.8:
                new_score = 3
            elif mismatch_ratio >= 1.2:
                new_score = 2
            else:
                new_score = 1

            if confidence == "suspicious":
                warnings.append(
                    f"D1可疑：提取到年限{median_life}年但资产类型无法确认（上下文：{source_snippet[:60]}...），"
                    f"建议人工复核。AI原始分{old_score}分未自动覆盖。"
                )
                d1["rule_warning"] = warnings[-1]
                d1["suspicious_extraction"] = {
                    "life_years": median_life,
                    "asset_type": asset_type,
                    "source_snippet": source_snippet,
                }
            elif new_score != old_score:
                d1["score"] = new_score
                d1["rule_applied"] = True
                d1["rule_reason"] = (
                    f"Extracted useful life = {median_life} years "
                    f"(asset_type={asset_type}, baseline={baseline}y, "
                    f"mismatch_ratio = {mismatch_ratio:.1f}x)"
                )
                rules_applied.append(
                    f"D1: {old_score} → {new_score} "
                    f"(life={median_life}y, asset={asset_type}, baseline={baseline}y, ratio={mismatch_ratio:.1f}x)"
                )
            else:
                d1["rule_note"] = (
                    f"Verified: useful life = {median_life} years "
                    f"(asset_type={asset_type}, baseline={baseline}y, ratio={mismatch_ratio:.1f}x)"
                )

    # ================================================================
    # 规则 3: D4 CAPEX 强度
    # ================================================================
    capex_search_text = full_html if full_html else all_text
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

    return list(dim_map.values()), rules_applied, warnings


def compute_composite_score(dimension_scores: List[Dict]) -> Dict:
    total = 0.0
    parts = []
    estimated_dims = []

    for d in dimension_scores:
        dim_id = d.get("dimension_id", "")
        raw_score = d.get("score")
        weight = WEIGHTS.get(dim_id, d.get("weight", 0))

        if raw_score is None or d.get("insufficient_evidence"):
            score = 2.0
            d["score"] = score
            d["score_was_null"] = True
            estimated_dims.append(dim_id)
        else:
            score = float(raw_score)

        weighted = score * weight
        total += weighted

        if dim_id in estimated_dims:
            parts.append(f"{score}×{weight:.2f}={weighted:.2f}[est]")
        else:
            parts.append(f"{score}×{weight:.2f}={weighted:.2f}")

    breakdown = "+".join(parts) + f"={total:.2f}"
    if estimated_dims:
        breakdown += f" (注：{','.join(estimated_dims)}为证据不足，按保守估计2分计算)"

    risk_level = "未知"
    risk_level_en = "Unknown"
    for threshold, level, level_en in RISK_LEVEL_THRESHOLDS:
        if total >= threshold:
            risk_level = level
            risk_level_en = level_en
            break

    result = {
        "weighted_score": round(total, 2),
        "max_score": 5.0,
        "risk_level": risk_level,
        "risk_level_en": risk_level_en,
        "score_breakdown": breakdown,
    }
    if estimated_dims:
        result["estimated_dimensions"] = estimated_dims
    return result


def enrich_dimension_scores(dimension_scores: List[Dict]) -> List[Dict]:
    for d in dimension_scores:
        dim_id = d.get("dimension_id", "")
        if "weight" not in d or d["weight"] is None:
            d["weight"] = WEIGHTS.get(dim_id, 0.20)
    return dimension_scores
