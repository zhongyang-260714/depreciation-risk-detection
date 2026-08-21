import re

with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''def _has_exclusion_context(text: str) -> bool:
    for pattern in D1_EXCLUSION_PATTERNS:
        if pattern.search(text):
            return True
    return False'''

new_func = '''def _has_exclusion_context(text: str) -> bool:
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
    return False'''

if old_func in content:
    content = content.replace(old_func, new_func, 1)
    with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("修复成功：优化 _has_exclusion_context 逻辑")
else:
    print("未找到目标函数")
