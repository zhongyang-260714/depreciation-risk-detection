import re

with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''def _detect_asset_type(text: str) -> str:
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
    if not scores:
        return "unknown"
    return max(scores, key=scores.get)'''

new_func = '''def _detect_asset_type(text: str) -> str:
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

    if not scores:
        return "unknown"
    return max(scores, key=scores.get)'''

if old_func in content:
    content = content.replace(old_func, new_func, 1)
    with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("修复成功：优化 _detect_asset_type 逻辑")
else:
    print("未找到目标函数")
    # 查找实际内容
    idx = content.find('def _detect_asset_type')
    if idx >= 0:
        print("找到的代码:")
        print(content[idx:idx+500])
