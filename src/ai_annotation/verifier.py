"""验真模块

防止 AI 编造引文/行号。核心防线：
1. 逐字包含：excerpt 是否完整出现在原文中？
2. 行号吻合：按行号定位，检查前后 3 行是否包含 excerpt 的核心子串
3. 模糊匹配：difflib.SequenceMatcher ≥ 0.85 兜底

v6.2修复：增加HTML标签清理，避免AI摘录（纯文本）与原文（HTML）格式不一致导致验真失败。
这是整个方案的灵魂步骤。
"""

import difflib
import re
from typing import List, Dict


def _strip_html(text: str) -> str:
    """去除 HTML 标签和多余空白，保留纯文本。"""
    if not text:
        return ""
    # 去除 HTML 标签
    text = re.sub(r"<[^>]+>", " ", text)
    # 压缩连续空白为单个空格
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_line_number(page_location: str) -> int | None:
    """从 page_location 字段中提取行号数字。"""
    if not page_location:
        return None
    # 匹配 "line 123"、"第 123 行"、"HTML 第 123 行" 等
    m = re.search(r"(?:line|行|Line)\s*[:：]?\s*(\d+)", str(page_location))
    if m:
        return int(m.group(1))
    # 尝试直接匹配纯数字
    m = re.search(r"\b(\d{3,5})\b", str(page_location))
    if m:
        return int(m.group(1))
    return None


def _fuzzy_ratio(a: str, b: str) -> float:
    """计算两段文本的模糊相似度。"""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def verify_signal(signal: dict, full_text: str, line_map: dict | None = None) -> dict:
    """对单条信号进行三级验真。

    Args:
        signal: DeepSeek 返回的信号 dict，必须含 text_excerpt 和 page_location
        full_text: 10-K 完整文本（\n 分割的行列表或整段字符串）
        line_map: {行号: 该行文本} 的映射（可选）

    Returns:
        {"signal_id": str, "passed": bool, "method": str, "confidence": float}
    """
    excerpt = signal.get("text_excerpt", "")
    page_location = signal.get("page_location", "")
    sig_id = signal.get("signal_id", "UNKNOWN")

    if not excerpt:
        return {"signal_id": sig_id, "passed": False, "method": "empty_excerpt", "confidence": 0.0}

    # v6.2修复：去除HTML标签后再比较，避免AI摘录（纯文本）与原文（HTML）格式不一致
    clean_excerpt = _strip_html(excerpt)
    clean_full_text = _strip_html(full_text) if isinstance(full_text, str) else full_text

    # 若 full_text 是字符串，转成行列表（基于原始文本，保留行号映射一致性）
    if isinstance(full_text, str):
        full_lines = full_text.split("\n")
    else:
        full_lines = list(full_text)

    # 策略 1：全文逐字包含（基于清理后的文本）
    if clean_excerpt in clean_full_text:
        return {"signal_id": sig_id, "passed": True, "method": "exact", "confidence": 1.0}

    # 策略 2：行号区域匹配（对region也做HTML清理）
    line_no = _extract_line_number(page_location)
    if line_no is not None and line_map is not None:
        if line_no in line_map:
            # 检查前后 3 行
            start = max(1, line_no - 3)
            end = min(max(line_map.keys()), line_no + 3)
            region = "\n".join(line_map.get(i, "") for i in range(start, end + 1))
            clean_region = _strip_html(region)
            if clean_excerpt in clean_region:
                return {"signal_id": sig_id, "passed": True, "method": "line_region", "confidence": 0.95}
            # 核心子串匹配（取 excerpt 的前 80 个字符作为核心指纹）
            core = clean_excerpt[:80]
            if core in clean_region:
                return {"signal_id": sig_id, "passed": True, "method": "line_core", "confidence": 0.90}

    # 策略 3：模糊匹配兜底（基于清理后的文本）
    ratio = _fuzzy_ratio(clean_excerpt, clean_full_text)
    if ratio >= 0.85:
        return {"signal_id": sig_id, "passed": True, "method": "fuzzy", "confidence": round(ratio, 3)}

    # 策略 4：更宽松的模糊匹配（针对长文本可能被截断的情况）
    if len(clean_excerpt) > 100:
        # 取前 100 字符再试一次
        ratio2 = _fuzzy_ratio(clean_excerpt[:100], clean_full_text)
        if ratio2 >= 0.85:
            return {"signal_id": sig_id, "passed": True, "method": "fuzzy_prefix", "confidence": round(ratio2, 3)}

    return {"signal_id": sig_id, "passed": False, "method": "none", "confidence": round(ratio, 3)}


def verify_all(
    ai_result: dict,
    full_text: str,
) -> dict:
    """对 DeepSeek 返回的所有信号批量验真。

    Args:
        ai_result: DeepSeek 返回的 dict，含 risk_signals 列表
        full_text: 10-K 完整文本

    Returns:
        {
            "total": int,
            "passed": int,
            "failed": int,
            "pass_rate": float,
            "results": [verify_signal() 的结果列表],
            "verified_signals": [通过验真的信号列表],
            "failed_signals": [未通过验真的信号列表],
        }
    """
    signals = ai_result.get("risk_signals", [])
    if not signals:
        return {
            "total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0,
            "results": [], "verified_signals": [], "failed_signals": [],
        }

    # 构建行号映射
    lines = full_text.split("\n")
    line_map = {i + 1: line for i, line in enumerate(lines)}

    results = []
    verified = []
    failed = []

    for sig in signals:
        r = verify_signal(sig, full_text, line_map)
        results.append(r)
        if r["passed"]:
            verified.append(sig)
        else:
            failed.append(sig)

    total = len(signals)
    passed = len(verified)

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 3) if total > 0 else 0.0,
        "results": results,
        "verified_signals": verified,
        "failed_signals": failed,
    }
