"""关键词矩阵定位模块

从 10-K HTML 文本中提取候选风险段落，记录行号、章节、命中关键词。
对应报告 3.3.1 的六词检索矩阵 + 3.3.2 的 XBRL 噪声排除。
"""

import re
from typing import List, Dict


# 六词检索矩阵（大小写不敏感）
# 对应报告 3.3.1
KEYWORD_MATRIX = {
    "strongest": ["useful life", "useful lives"],
    "strong":    ["obsolescence", "impairment", "depreciation", "prospectively"],
    "medium":    ["technology change", "technological advancement", "technological change"],
}

# XBRL 标签前缀（需排除的噪声）
XBRL_NOISE_PATTERNS = [
    r"<ix:.*?>",
    r"</ix:.*?>",
    r"<ix-.*?:.*?>",
    r"</ix-.*?:.*?>",
]

# 章节推断正则
SECTION_PATTERNS = [
    (re.compile(r"ITEM\s+1A\.\s*RISK\s*FACTORS", re.I), "Risk Factors"),
    (re.compile(r"ITEM\s+7\.\s*MANAGEMENT.*?DISCUSSION", re.I), "MD&A"),
    (re.compile(r"NOTE\s+1\.\s*SUMMARY\s+OF\s*SIGNIFICANT\s*ACCOUNTING", re.I), "Note 1"),
    (re.compile(r"NOTE\s+\d+\.\s*PROPERTY.*?EQUIPMENT", re.I), "PP&E Note"),
    (re.compile(r"NOTES\s+TO\s*CONSOLIDATED\s*FINANCIAL", re.I), "Financial Notes"),
]


def _is_visible_text(line: str) -> bool:
    """排除 XBRL 隐藏标签和纯 HTML 标签行。"""
    stripped = line.strip()
    if not stripped:
        return False
    # XBRL 隐藏标签
    if stripped.startswith("<ix:") or stripped.startswith("<ix-"):
        return False
    # 纯 HTML 标签行（无可见文本）
    if re.match(r"^\s*<[^>]+>\s*$", stripped):
        return False
    return True


def _detect_section(line: str) -> str:
    """根据当前行推断所属章节。"""
    for pattern, name in SECTION_PATTERNS:
        if pattern.search(line):
            return name
    return "Unknown"


def locate_candidates(html_text: str) -> List[Dict]:
    """定位候选风险段落。

    流程：
    1. 按行分割，记录行号
    2. 逐行检查是否命中关键词矩阵
    3. 命中时，提取上下文（前后各 1-2 句）
    4. 排除 XBRL 噪声
    5. 记录来源章节、行号、信号强度

    Args:
        html_text: 10-K 的完整 HTML 文本

    Returns:
        候选段落列表，每项为 dict:
        - keyword_matched: 命中的关键词
        - text_excerpt: 段落原文（含上下文）
        - line_number: HTML 行号（按 \n 分割计数，1-based）
        - source_section: 推断章节
        - signal_strength: strongest / strong / medium
    """
    candidates = []
    lines = html_text.split("\n")

    # 维护当前章节状态
    current_section = "Unknown"

    for i, line in enumerate(lines, start=1):
        # 更新章节推断
        section_guess = _detect_section(line)
        if section_guess != "Unknown":
            current_section = section_guess

        # 排除噪声行
        if not _is_visible_text(line):
            continue

        text_lower = line.lower()

        # 检查三级关键词
        for strength, keywords in KEYWORD_MATRIX.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    # 提取上下文：前后各 1 句（即前后各 1 行可见文本）
                    context_lines = []
                    # 向前找 1 行可见文本
                    for j in range(i - 1, max(0, i - 5), -1):
                        if _is_visible_text(lines[j - 1]):  # lines 是 0-based
                            context_lines.insert(0, lines[j - 1].strip())
                            break
                    # 当前行
                    context_lines.append(line.strip())
                    # 向后找 1 行可见文本
                    for j in range(i, min(len(lines), i + 5)):
                        if _is_visible_text(lines[j]):
                            context_lines.append(lines[j].strip())
                            break

                    excerpt = " ".join(context_lines)
                    # 去重：如果 excerpt 和前一个高度相似，跳过
                    if candidates:
                        prev = candidates[-1]["text_excerpt"]
                        if excerpt in prev or prev in excerpt:
                            continue

                    candidates.append({
                        "keyword_matched": kw,
                        "text_excerpt": excerpt,
                        "line_number": i,
                        "source_section": current_section,
                        "signal_strength": strength,
                    })
                    break  # 同一行命中多个关键词，只记录第一个

    # 去重：相同行号只保留信号最强的
    seen_lines = {}
    for c in candidates:
        ln = c["line_number"]
        if ln not in seen_lines:
            seen_lines[ln] = c
        else:
            # 保留更强的信号
            strength_order = {"strongest": 3, "strong": 2, "medium": 1}
            if strength_order.get(c["signal_strength"], 0) > strength_order.get(seen_lines[ln]["signal_strength"], 0):
                seen_lines[ln] = c

    return list(seen_lines.values())


def locate_candidates_batch(html_text: str, max_candidates: int = 50) -> List[Dict]:
    """带数量限制的候选定位（用于控制 DeepSeek token 成本）。"""
    candidates = locate_candidates(html_text)
    # 按信号强度排序：strongest > strong > medium
    strength_order = {"strongest": 3, "strong": 2, "medium": 1}
    candidates.sort(key=lambda c: strength_order.get(c["signal_strength"], 0), reverse=True)
    return candidates[:max_candidates]
