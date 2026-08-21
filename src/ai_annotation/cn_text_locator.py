"""中文年报文本关键词定位器

针对中国A股年报文本，定位折旧/减值/资本化等风险相关段落。
设计思路与英文版text_locator完全同构，但使用中文关键词。
"""

import re
from typing import List, Dict


# ============================================================
# 中文关键词矩阵（三级信号强度）
# ============================================================

CN_KEYWORDS_STRONGEST = [
    r"折旧年限",
    r"使用寿命",
    r"预计使用年限",
    r"会计估计变更",
    r"未来适用法",
]

CN_KEYWORDS_STRONG = [
    r"固定资产折旧",
    r"无形资产摊销",
    r"资产减值",
    r"减值准备",
    r"可变现净值",
    r"资本化",
    r"费用化",
]

CN_KEYWORDS_MEDIUM = [
    r"研发投入",
    r"研发支出",
    r"资本性支出",
    r"商誉",
    r"存货跌价",
    r"技术替代",
    r"技术迭代",
    r"设备更新",
]


# 排除噪声（XBRL标签、页眉页脚等）
CN_NOISE_PATTERNS = [
    re.compile(r"^\s*第\s*\d+\s*页"),  # 页码
    re.compile(r"^\s*\d+\s*[/\\]\s*\d+\s*$"),  # 页码 1/200
    re.compile(r"^\s*第[一二三四五六七八九十百]+节"),  # 章节标题行
    re.compile(r"^\s*\d+\.\d+\.\d+\s+"),  # 编号标题
]

# 强制注入模式 = 即使未命中关键词，也必须送入LLM的高价值折旧/减值指纹
MUST_INCLUDE_PATTERNS_CN = [
    # 折旧年限带具体数字（如"折旧年限3-5年"）
    (re.compile(r"折旧年限.*?(?:\d+\s*[-～~至]\s*\d+|\d+)\s*年", re.I), "strongest", "折旧年限数字指纹"),
    (re.compile(r"预计使用年限.*?(?:\d+\s*[-～~至]\s*\d+|\d+)\s*年", re.I), "strongest", "预计使用年限数字指纹"),
    # 会计估计变更与折旧/摊销相关
    (re.compile(r"会计估计变更.*?(?:折旧|摊销|使用年限|预计净残值)", re.I), "strongest", "会计估计变更折旧关联"),
    (re.compile(r"(?:折旧|摊销).*?会计估计变更", re.I), "strongest", "折旧会计估计变更"),
    # 固定资产减值带金额
    (re.compile(r"固定资产.*?减值.*?(?:\d+(?:\.\d+)?\s*(?:万|亿|元|千元|万元))", re.I), "strong", "固定资产减值金额"),
    # 研发资本化率
    (re.compile(r"研发.*?资本化率.*?(?:\d+(?:\.\d+)?\s*%)", re.I), "strong", "研发资本化率"),
    (re.compile(r"资本化率.*?(?:\d+(?:\.\d+)?\s*%)", re.I), "strong", "资本化率"),
    # 期后变更/后续调整
    (re.compile(r"期后.*?变更.*?(?:折旧|摊销|年限)", re.I), "strong", "期后折旧变更"),
    (re.compile(r"(?:自|从)\s*20\d{2}\s*年.*?起.*?(?:折旧|摊销|年限)", re.I), "strong", "未来生效折旧变更"),
    # 资本开支/购建固定资产
    (re.compile(r"购建固定资产.*?支付.*?(?:\d+(?:\.\d+)?\s*(?:万|亿|元))", re.I), "medium", "购建固定资产支付金额"),
    (re.compile(r"资本性支出.*?(?:\d+(?:\.\d+)?\s*(?:万|亿|元))", re.I), "medium", "资本性支出金额"),
]


def _is_noise(text: str) -> bool:
    """判断文本是否为噪声（页眉页脚等）。"""
    for pattern in CN_NOISE_PATTERNS:
        if pattern.match(text):
            return True
    return False


def _extract_context(text: str, match_start: int, match_end: int, window: int = 300) -> str:
    """提取关键词上下文。"""
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)
    return text[start:end].strip()


def locate_cn_candidates(text: str, max_candidates: int = 30) -> List[Dict]:
    """在中文年报文本中定位候选风险段落。
    
    Args:
        text: 中文年报全文文本
        max_candidates: 最大返回候选数
    
    Returns:
        候选段落列表，每个元素包含:
        - text_excerpt: 原文摘录（含上下文）
        - keyword_matched: 命中的关键词
        - signal_strength: strongest/strong/medium
        - page_location: 行号/页码（中文年报中提取近似位置）
    """
    candidates = []
    seen_positions = set()  # 去重：避免同一位置重复命中
    
    # 按强度顺序扫描（最强优先）
    keyword_groups = [
        ("strongest", CN_KEYWORDS_STRONGEST),
        ("strong", CN_KEYWORDS_STRONG),
        ("medium", CN_KEYWORDS_MEDIUM),
    ]
    
    for strength, keywords in keyword_groups:
        for kw in keywords:
            pattern = re.compile(kw, re.I)
            for m in pattern.finditer(text):
                # 去重：同一位置300字符范围内只保留一个
                pos_key = m.start() // 200  # 200字符为一个bucket
                if pos_key in seen_positions:
                    continue
                seen_positions.add(pos_key)
                
                context = _extract_context(text, m.start(), m.end())
                
                # 噪声排除
                if _is_noise(context.split("\n")[0]):
                    continue
                
                candidates.append({
                    "text_excerpt": context,
                    "keyword_matched": kw,
                    "signal_strength": strength,
                    "page_location": f"字符位置 {m.start()}",
                })
                
                if len(candidates) >= max_candidates:
                    return candidates
    
    # 强制注入：即使未命中关键词，MUST_INCLUDE 模式匹配的高价值段落也必须送入LLM
    seen_positions_forced = set(seen_positions)  # 复用已有的位置去重
    for pattern, strength, pattern_name in MUST_INCLUDE_PATTERNS_CN:
        for m in pattern.finditer(text):
            pos_key = m.start() // 200
            if pos_key in seen_positions_forced:
                continue
            seen_positions_forced.add(pos_key)
            
            context = _extract_context(text, m.start(), m.end())
            if _is_noise(context.split("\n")[0]):
                continue
            
            candidates.append({
                "text_excerpt": context,
                "keyword_matched": pattern_name,
                "signal_strength": strength,
                "page_location": f"字符位置 {m.start()} [强制注入]",
            })
            
            if len(candidates) >= max_candidates:
                return candidates

    return candidates
