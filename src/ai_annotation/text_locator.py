"""关键词矩阵定位模块 v2.3

从 10-K HTML 文本中提取候选风险段落，按 HTML 段落块定位，
保留完整上下文。使用 BeautifulSoup 正确解析可见文本。
v2.3: 
- 大幅扩充关键词覆盖（新增财务数据、技术迭代、租赁承诺等）
- 增加结构化章节提取（强制提取Note 1/4/6、Item 1A/7等）
- 提取表格内容（td/th标签）
- MUST_INCLUDE模式增加CAPEX趋势、租赁承诺、技术迭代节奏等
"""

import re
from typing import List, Dict


# ============================================================
# 三级关键词体系
# ============================================================

# 核心级 = 人工标注六词矩阵（报告 3.3.1）
KEYWORD_CORE = {
    "strongest": ["useful life", "useful lives"],
    "strong":    ["obsolescence", "impairment", "depreciation", "prospectively"],
    "medium":    ["technology change", "technological advancement", "technological change"],
}

# 扩展级 = 语义包含词（机器独有，需人工复核）
KEYWORD_EXTENDED = {
    "strongest": [
        "estimated useful life", "depreciable life", "economic life",
        "useful life estimate", "estimated life",
        "years for production equipment", "years for servers",
        "straight-line", "accounting policy", "property and equipment",
    ],
    "strong": [
        "depreciation expense", "accumulated depreciation",
        "change in accounting estimate", "accounting estimate change",
        "write-down", "write down",
        "future applicable", "applied prospectively",
        "capital expenditures", "capex", "purchases of property",
        "construction in progress", "lease commitment",
        "data center", "cloud infrastructure", "gpu cluster",
        "technology obsolescence", "rapidly evolving",
        "impairment charge", "impairment loss",
    ],
    "medium": [
        "technology cycle", "product life cycle",
        "rapidly changing technology", "technology obsolescence",
        "competition", "market conditions", "supply chain",
        "inventory provision", "excess inventory",
        "goodwill impairment", "intangible assets",
    ],
}

# 正则级 = 模式捕获（机器独有，需人工复核）
KEYWORD_REGEX = [
    (re.compile(r"(\d+)\s*years?\s*(?:to|→)\s*(\d+)\s*years?", re.I), "strongest", "年限变更模式"),
    (re.compile(r"increased\s+(?:from\s+)?(\d+)\s*(?:to|→)\s*(\d+)\s*years?", re.I), "strongest", "年限延长模式"),
    (re.compile(r"extended\s+(?:from\s+)?(\d+)\s*(?:to|→)\s*(\d+)\s*years?", re.I), "strongest", "年限延长模式"),
    (re.compile(r"(?:applied|accounted\s+for)\s+prospectively", re.I), "strong", "未来适用模式"),
    (re.compile(r"(?:recorded|recognized|incurred)\s+(?:an?\s+)?impairment\s+(?:charge|loss|of)", re.I), "strong", "减值确认模式"),
    (re.compile(r"depreciation\s+expense\s+(?:was|of|decreased|increased)", re.I), "strong", "折旧费用模式"),
    # 新增：财务数据模式
    (re.compile(r"depreciation\s+expense\s+\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?", re.I), "strong", "折旧费用金额"),
    (re.compile(r"capital\s+expenditures?\s+\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?", re.I), "strong", "CAPEX金额"),
    (re.compile(r"property\s+and\s+equipment.*\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?", re.I), "strong", "PPE金额"),
]

# 强制注入模式 = 即使未命中关键词，也必须送入LLM的高价值折旧指纹
MUST_INCLUDE_PATTERNS = [
    # 折旧年限指纹（捕获具体年限数字 + 资产类型）
    (re.compile(r"(?:servers?|network\s+equipment|data\s+center|property|plant|equipment).*?(?:\d+)\s*-?\s*(?:to|–)?\s*(?:\d+)\s*years?", re.I), "strongest", "折旧年限指纹"),
    (re.compile(r"(?:useful\s+life|depreciable\s+life).*?(?:\d+)\s*-?\s*(?:to|–)?\s*(?:\d+)\s*years?", re.I), "strongest", "使用年限指纹"),
    # 变更量化（捕获折旧费用变动金额）
    (re.compile(r"depreciation\s+expense.*?(?:increased|decreased).*?(?:\$?\d+(?:\.\d+)?\s*(?:million|billion|M|B)?)", re.I), "strong", "折旧费用变更量化"),
    (re.compile(r"(?:change|increase|decrease).*?(?:depreciation|amortization).*?(?:\$?\d+(?:\.\d+)?\s*(?:million|billion|M|B)?)", re.I), "strong", "折旧变更金额"),
    # 期后变更/估计变更
    (re.compile(r"(?:subsequent|after\s+the\s+(?:balance\s+sheet|reporting)\s+date|post[-\s]?balance\s+sheet).*?(?:change\s+in\s+estimate|accounting\s+estimate|depreciation|useful\s+life)", re.I), "strong", "期后折旧估计变更"),
    (re.compile(r"(?:effective|beginning|starting)\s+(?:in\s+)?(?:FY|fiscal\s+year|January|April|July|October)?\s*20\d{2}.*?(?:depreciation|useful\s+life|estimated\s+life)", re.I), "strong", "未来生效的折旧变更"),
    # 资产减值与折旧关联
    (re.compile(r"(?:impairment|write[-\s]?down|write[-\s]?off).*?(?:remaining|residual|remaining\s+useful|adjusted)\s+(?:life|depreciation)", re.I), "strong", "减值后折旧调整"),
    # 资本开支强度（用于D4验证）
    (re.compile(r"capital\s+expenditures?.*?(?:\$?\d+(?:\.\d+)?\s*(?:million|billion|M|B)?)", re.I), "medium", "资本开支金额"),
    (re.compile(r"(?:purchases?|acquisitions?)\s+of\s+(?:property|plant|equipment|PPE).*?(?:\$?\d+(?:\.\d+)?\s*(?:million|billion|M|B)?)", re.I), "medium", "PPE购置金额"),
    # 新增：技术迭代节奏
    (re.compile(r"(?:new\s+product|new\s+architecture|new\s+generation|new\s+computing).*?(?:each\s+year|every\s+year|annual|12\s*months?)", re.I), "strong", "年度技术迭代"),
    (re.compile(r"(?:complete|introduce|launch).*?(?:new|next)\s+(?:product|architecture|generation|solution).*?(?:each|every|annual|yearly)", re.I), "strong", "年度发布节奏"),
    # 新增：租赁承诺
    (re.compile(r"(?:lease\s+commitment|lease\s+obligation|finance\s+lease|operating\s+lease).*?(?:\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?)", re.I), "strong", "租赁承诺金额"),
    (re.compile(r"(?:datacenter|data\s+center).*?(?:lease|commitment|obligation).*?(?:\$?\d+(?:\.\d+)?\s*(?:billion|million|B|M)?)", re.I), "strong", "数据中心租赁"),
    # 新增：毛利率/利润影响
    (re.compile(r"(?:gross\s+margin|operating\s+margin|net\s+income).*?(?:decreased|increased|impact|driven\s+by).*?(?:depreciation|infrastructure|AI)", re.I), "medium", "利润率折旧影响"),
]

# 扁平化所有关键词（用于遍历）
ALL_KEYWORDS = []
for strength, kws in KEYWORD_CORE.items():
    for kw in kws:
        ALL_KEYWORDS.append(("core", strength, kw))
for strength, kws in KEYWORD_EXTENDED.items():
    for kw in kws:
        ALL_KEYWORDS.append(("extended", strength, kw))


# ============================================================
# 章节推断
# ============================================================

SECTION_PATTERNS = [
    (re.compile(r"ITEM\s+1A\.\s*RISK\s*FACTORS", re.I), "Risk Factors"),
    (re.compile(r"ITEM\s+7\.\s*MANAGEMENT.*?DISCUSSION", re.I), "MD&A"),
    (re.compile(r"NOTE\s+1\.\s*SUMMARY\s+OF\s*SIGNIFICANT\s*ACCOUNTING", re.I), "Note 1"),
    (re.compile(r"NOTE\s+\d+\.\s*PROPERTY.*?EQUIPMENT", re.I), "PP&E Note"),
    (re.compile(r"NOTES\s+TO\s*CONSOLIDATED\s*FINANCIAL", re.I), "Financial Notes"),
    (re.compile(r"NOTE\s+\d+\.\s*INTANGIBLE\s*ASSETS", re.I), "Intangible Assets Note"),
    (re.compile(r"NOTE\s+\d+\.\s*LEASES", re.I), "Leases Note"),
    (re.compile(r"NOTE\s+\d+\.\s*GOODWILL", re.I), "Goodwill Note"),
]


def _detect_section(text_upper: str) -> str:
    """根据文本内容推断所属章节。"""
    for pattern, name in SECTION_PATTERNS:
        if pattern.search(text_upper):
            return name
    return "Unknown"


# ============================================================
# HTML 可见文本提取（BeautifulSoup）
# ============================================================

def _extract_visible_paragraphs(html_text: str) -> List[Dict]:
    """用 BeautifulSoup 提取可见文本段落，彻底排除 XBRL 噪声。

    策略：
    1. 用 BeautifulSoup 解析 HTML
    2. 移除所有 <ix:...> 和 <ix-...> XBRL 标签及其内容
    3. 移除 <script>、<style>、<head> 等非内容标签
    4. 提取 <p>、<div>、<span>、<td> 等标签内的文本
    5. 按原始行号记录段落位置
    """
    from bs4 import BeautifulSoup, NavigableString

    soup = BeautifulSoup(html_text, "html.parser")

    # v2.4修复：对包含财务数据的XBRL标签，unwrap保留内容而非decompose删除
    for tag in soup.find_all(["ix:nonnumeric", "ix:numeric", "ix:nonfraction"]):
        tag.unwrap()  # 只删除标签，保留内容
    for tag in soup.find_all(["ix:header", "ix:hidden", "ix:references", "ix:resources"]):
        tag.decompose()  # 元数据标签直接删除
    # 移除所有以 ix- 命名空间开头的标签
    for tag in soup.find_all(True):
        if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
            tag.unwrap()
    for tag in soup.find_all(["ix:header", "ix:hidden", "ix:nonnumeric", "ix:numeric",
                              "ix:nonfraction", "ix:references", "ix:resources"]):
        tag.decompose()
    # 移除所有以 ix- 命名空间开头的标签
    for tag in soup.find_all(True):
        if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
            tag.decompose()

    # 移除 script、style、head、noscript
    for tag_name in ["script", "style", "head", "noscript", "meta", "link"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # 移除 display:none 的元素
    for tag in soup.find_all(style=re.compile(r"display:\s*none", re.I)):
        tag.decompose()

    # 提取段落：优先 <p>，其次是 <div>、<td>、<span> 等
    paragraphs = []

    # 先尝试提取所有 <p> 标签
    p_tags = soup.find_all("p")
    for p in p_tags:
        text = p.get_text(separator=" ", strip=True)
        if len(text) > 30:
            paragraphs.append({"text": text, "tag": "p"})

    # 如果 <p> 太少，补充 <div> 中的文本块
    if len(paragraphs) < 10:
        for div in soup.find_all("div"):
            text = div.get_text(separator=" ", strip=True)
            # 过滤掉过短或已经被 <p> 覆盖的内容
            if len(text) > 50 and len(text) < 5000:
                # 检查是否已被包含
                already_covered = any(text[:100] in p["text"] or p["text"][:100] in text for p in paragraphs)
                if not already_covered:
                    paragraphs.append({"text": text, "tag": "div"})

    # 补充：提取表格内容（td/th标签），这些通常包含财务数据
    for td in soup.find_all(["td", "th"]):
        text = td.get_text(separator=" ", strip=True)
        if len(text) > 20:
            paragraphs.append({"text": text, "tag": "td"})

    # 按文本长度排序，优先取信息量大的段落
    paragraphs.sort(key=lambda x: len(x["text"]), reverse=True)

    # 去重：文本相似度高的只保留一个
    filtered = []
    for p in paragraphs:
        is_dup = False
        for existing in filtered:
            # 如果新段落是已有段落的子串，跳过
            if p["text"] in existing["text"]:
                is_dup = True
                break
            # 如果已有段落是新段落的子串，替换
            if existing["text"] in p["text"]:
                existing["text"] = p["text"]
                is_dup = True
                break
        if not is_dup:
            filtered.append(p)

    # 限制总数，避免过大
    MAX_PARAS = 300
    filtered = filtered[:MAX_PARAS]

    # 重新按文本中的行号近似排序（用于后续展示）
    # 在原始 HTML 中查找每个段落首次出现的位置
    for p in filtered:
        idx = html_text.find(p["text"][:80])
        p["approx_line"] = html_text[:idx].count("\n") + 1 if idx > 0 else 0

    filtered.sort(key=lambda x: x["approx_line"])

    return filtered


# ============================================================
# 结构化章节提取：强制提取关键章节全文
# ============================================================

def _extract_structured_sections(html_text: str) -> List[Dict]:
    """强制提取关键章节的结构化内容。
    
    提取以下高价值章节：
    1. Note 1 - 会计政策（特别是折旧政策部分）
    2. Note 4/6/11 - PP&E明细
    3. Item 1A - 风险因素（技术过时、竞争相关）
    4. Item 7 MD&A - 关键会计估计、CAPEX讨论
    5. Note 9/13 - 租赁承诺
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_text, "html.parser")
    
    # v2.4修复：对包含财务数据的XBRL标签，unwrap保留内容而非decompose删除
    for tag in soup.find_all(["ix:nonnumeric", "ix:numeric", "ix:nonfraction"]):
        tag.unwrap()  # 只删除标签，保留内容
    for tag in soup.find_all(["ix:header", "ix:hidden", "ix:references", "ix:resources", "script", "style", "head", "noscript", "meta", "link"]):
        tag.decompose()  # 元数据/脚本标签直接删除
    # 移除所有以 ix- 命名空间开头的标签
    for tag in soup.find_all(True):
        if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
            tag.unwrap()
    for tag in soup.find_all(["ix:header", "ix:hidden", "ix:nonnumeric", "ix:numeric",
                              "ix:nonfraction", "script", "style", "head", "noscript", "meta", "link"]):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
            tag.decompose()
    
    structured = []
    full_text = soup.get_text(separator="\n", strip=True)
    lines = full_text.split("\n")
    
    # 关键章节标记模式（v2.4修复：更宽松匹配，跳过引用）
    section_markers = [
        # Note 1 - 会计政策（支持多种格式：点号、连字符、特殊字符、任意间隔）
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*(?:SUMMARY\s+OF\s*)?SIGNIFICANT\s+ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*ORGANIZATION\s+AND\s*(?:SUMMARY\s+OF\s*)?SIGNIFICANT\s+ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        # PP&E Note（支持Note 4/6/11）
        (re.compile(r"NOTE\s+[46]\s*.{0,3}\s*PROPERTY.*?EQUIPMENT", re.I), "PP&E Note", 8000),
        (re.compile(r"NOTE\s+11\s*.{0,3}\s*BALANCE\s+SHEET\s+COMPONENTS", re.I), "Balance Sheet Components", 6000),
        # Item 1A / Item 7
        (re.compile(r"ITEM\s+1A\s*.{0,3}\s*RISK\s*FACTORS", re.I), "Item 1A - Risk Factors", 12000),
        (re.compile(r"ITEM\s+7\s*.{0,3}\s*MANAGEMENT.*?DISCUSSION", re.I), "Item 7 - MD&A", 12000),
        # 其他关键Note
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*LEASES", re.I), "Leases Note", 6000),
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*COMMITMENTS", re.I), "Commitments Note", 5000),
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*INTANGIBLE\s+ASSETS", re.I), "Intangible Assets Note", 5000),
    ]
    
    for pattern, section_name, max_chars in section_markers:
        # v2.4修复：查找所有匹配，跳过引用
        all_matches = list(pattern.finditer(full_text))
        for match in all_matches:
            start = match.start()
            # 检查前面100字符是否是引用
            before_text = full_text[max(0, start-100):start]
            is_reference = any(ref_word in before_text.lower() for ref_word in 
                              ["refer to", "see", "reference", "for further information", 
                               "for more information", "as discussed in", "described in"])
            
            if is_reference:
                continue  # 跳过引用，找下一个匹配
            
            # 找到实际的章节内容
            end = start + max_chars
            # 尝试找到下一个主要章节作为结束点
            for other_pattern, _, _ in section_markers:
                if other_pattern != pattern:
                    next_matches = list(other_pattern.finditer(full_text, start + 200))
                    for next_match in next_matches:
                        next_start = next_match.start()
                        next_before = full_text[max(0, next_start-100):next_start]
                        if not any(ref_word in next_before.lower() for ref_word in 
                                  ["refer to", "see", "reference", "for further information"]):
                            if next_start < end:
                                end = min(end, next_start)
                            break
            
            section_text = full_text[start:end].strip()
            if len(section_text) > 300:  # 至少300字符才是有效章节
                structured.append({
                    "text": section_text,
                    "tag": "structured_section",
                    "section_name": section_name,
                    "approx_line": full_text[:start].count("\n") + 1,
                })
            break  # 找到第一个非引用匹配就停止
    
    return structured



def locate_candidates(html_text: str) -> List[Dict]:
    """定位候选风险段落（段落级，BeautifulSoup 解析）。

    流程：
    1. 用 BeautifulSoup 提取可见文本段落
    2. 强制提取结构化章节（Note 1, PP&E Note, Risk Factors等）
    3. 对每个段落检查三级关键词命中
    4. 记录关键词级别、强度、完整段落原文
    5. 去重：相同段落只保留信号最强的
    6. MUST_INCLUDE 强制注入：捕获关键词矩阵遗漏的折旧指纹

    Args:
        html_text: 10-K 的完整 HTML 文本

    Returns:
        候选段落列表，每项为 dict:
        - keyword_matched: 命中的关键词/模式
        - keyword_tier: core / extended / regex / must_include / structured
        - keyword_strength: strongest / strong / medium
        - signal_strength: strongest / strong / medium  (兼容P7渲染，与keyword_strength同值)
        - text_excerpt: 完整段落原文
        - line_number: 近似 HTML 行号（1-based）
        - source_section: 推断章节
        - requires_human_review: 是否需要人工复核
    """
    # 1. 提取普通段落
    paragraphs = _extract_visible_paragraphs(html_text)
    
    # 2. 提取结构化章节
    structured_sections = _extract_structured_sections(html_text)
    
    # 合并所有段落源
    all_paragraphs = paragraphs + structured_sections
    
    candidates = []
    seen_texts = {}  # 去重：按段落文本指纹（前80字符）

    for para in all_paragraphs:
        para_text = para["text"]
        para_lower = para_text.lower()
        para_upper = para_text.upper()
        approx_line = para.get("approx_line", 0)
        section = para.get("section_name") or _detect_section(para_upper)

        # 文本指纹用于去重
        text_fingerprint = para_text[:80].lower().strip()

        # 检查核心关键词
        for strength, kws in KEYWORD_CORE.items():
            for kw in kws:
                if kw.lower() in para_lower:
                    if text_fingerprint not in seen_texts or _strength_rank(strength) > _strength_rank(seen_texts[text_fingerprint]["keyword_strength"]):
                        seen_texts[text_fingerprint] = {
                            "keyword_matched": kw,
                            "keyword_tier": "core",
                            "keyword_strength": strength,
                            "signal_strength": strength,
                            "keyword_category": "人工标准关键词",
                            "text_excerpt": para_text,
                            "line_number": approx_line,
                            "source_section": section,
                            "requires_human_review": False,
                        }
                    break

        # 检查扩展关键词（如果核心没命中该段落）
        if text_fingerprint not in seen_texts:
            for strength, kws in KEYWORD_EXTENDED.items():
                for kw in kws:
                    if kw.lower() in para_lower:
                        seen_texts[text_fingerprint] = {
                            "keyword_matched": kw,
                            "keyword_tier": "extended",
                            "keyword_strength": strength,
                            "signal_strength": strength,
                            "keyword_category": "机器扩展关键词",
                            "text_excerpt": para_text,
                            "line_number": approx_line,
                            "source_section": section,
                            "requires_human_review": True,
                        }
                        break
                if text_fingerprint in seen_texts:
                    break

        # 检查正则模式（如果前面都没命中）
        if text_fingerprint not in seen_texts:
            for pattern, strength, pattern_name in KEYWORD_REGEX:
                if pattern.search(para_text):
                    seen_texts[text_fingerprint] = {
                        "keyword_matched": pattern_name,
                        "keyword_tier": "regex",
                        "keyword_strength": strength,
                        "signal_strength": strength,
                        "keyword_category": "机器正则模式",
                        "text_excerpt": para_text,
                        "line_number": approx_line,
                        "source_section": section,
                        "requires_human_review": True,
                    }
                    break

    # 强制注入：即使未命中关键词，MUST_INCLUDE 模式匹配的高价值段落也必须送入LLM
    for para in all_paragraphs:
        para_text = para["text"]
        text_fingerprint = para_text[:80].lower().strip()
        # 如果该段落已被关键词命中，跳过（避免重复）
        if text_fingerprint in seen_texts:
            continue
        approx_line = para.get("approx_line", 0)
        section = para.get("section_name") or _detect_section(para_text.upper())
        for pattern, strength, pattern_name in MUST_INCLUDE_PATTERNS:
            if pattern.search(para_text):
                seen_texts[text_fingerprint] = {
                    "keyword_matched": pattern_name,
                    "keyword_tier": "must_include",
                    "keyword_strength": strength,
                    "signal_strength": strength,
                    "keyword_category": "强制注入折旧指纹",
                    "text_excerpt": para_text,
                    "line_number": approx_line,
                    "source_section": section,
                    "requires_human_review": False,
                }
                break

    # 转换为列表，按行号排序
    candidates = list(seen_texts.values())
    candidates.sort(key=lambda c: c["line_number"])

    return candidates


def locate_candidates_batch(html_text: str, max_candidates: int = 30) -> List[Dict]:
    """带数量限制的候选定位（用于控制 DeepSeek token 成本）。

    v6.2优化：从默认80降到30，只保留最强信号，避免prompt超限。

    优先级：core > extended > regex > must_include；同 tier 按 strongest > strong > medium
    """
    candidates = locate_candidates(html_text)

    # 分级排序
    tier_order = {"core": 4, "extended": 3, "regex": 2, "must_include": 1}
    strength_order = {"strongest": 3, "strong": 2, "medium": 1}

    candidates.sort(
        key=lambda c: (
            tier_order.get(c["keyword_tier"], 0),
            strength_order.get(c["keyword_strength"], 0),
        ),
        reverse=True,
    )

    return candidates[:max_candidates]


def _strength_rank(strength: str) -> int:
    """信号强度排序辅助。"""
    return {"strongest": 3, "strong": 2, "medium": 1}.get(strength, 0)


def get_keyword_summary(candidates: List[Dict]) -> Dict:
    """返回关键词命中统计，供人工复核参考。"""
    summary = {"core": 0, "extended": 0, "regex": 0, "must_include": 0, "needs_review": 0, "total_paragraphs": 0}
    for c in candidates:
        summary[c["keyword_tier"]] += 1
        if c.get("requires_human_review"):
            summary["needs_review"] += 1
    summary["total_paragraphs"] = len(candidates)
    return summary
