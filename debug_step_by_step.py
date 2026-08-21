import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
import re
from ai_annotation.scorer_calculator import (
    _has_exclusion_context, _detect_asset_type, _has_confirmation_context,
    _parse_number_word, D1_LIFE_YEAR_PATTERNS
)

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

# 找到 useful life 候选
for c in candidates:
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower():
        print("=== 手动模拟 _extract_life_years_from_context ===")
        
        # Step 1: 处理文本
        processed = text.replace('\n', ' ').replace('\r', ' ')
        text_lower = processed.lower()
        print(f"Step 1 - _has_exclusion_context: {_has_exclusion_context(processed)}")
        
        # Step 2: 检测资产类型
        asset_type = _detect_asset_type(processed)
        print(f"Step 2 - asset_type: {asset_type}")
        
        # Step 3: 遍历 D1_LIFE_YEAR_PATTERNS
        years = []
        for i, pattern in enumerate(D1_LIFE_YEAR_PATTERNS):
            for m in pattern.finditer(text_lower):
                groups = m.groups()
                print(f"  D1 pattern {i} matched: {groups}")
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
        print(f"Step 3 - years after D1 patterns: {years}")
        
        # Step 4: word_pattern
        if not years:
            word_pattern = re.compile(
                r"(?:depreciat\w+|useful\s+life|life|lives|server|equipment|machinery).{0,300}?"
                r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
                r"\s*years?",
                re.I,
            )
            for m in word_pattern.finditer(text_lower):
                y = _parse_number_word(m.group(1))
                print(f"  word_pattern matched: group1={m.group(1)}, y={y}")
                if y is not None and 1.5 <= y <= 30:
                    years.append(y)
        print(f"Step 4 - years after word_pattern: {years}")
        
        # Step 5: word_range_pattern
        if not years:
            word_range_pattern = re.compile(
                r"(?:useful\s+lives?|depreciable\s+life|estimated\s+life|depreciated|over|of)"
                r".??"
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
                print(f"  word_range_pattern matched: y1={y1}, y2={y2}")
                if y1 is not None and y2 is not None:
                    upper_y = max(y1, y2)
                    if 1.5 <= upper_y <= 30:
                        years.append(upper_y)
        print(f"Step 5 - years after word_range_pattern: {years}")
        
        # Step 6: 最终判断
        if not years:
            print("Step 6 - RETURN None (no years found)")
        else:
            max_life = max(years)
            has_conf = _has_confirmation_context(processed)
            print(f"Step 6 - max_life={max_life}, has_conf={has_conf}")
            if asset_type in ("building", "land"):
                print("Step 6 - RETURN None (building/land)")
            elif asset_type in ("intangible", "software", "patent", "lease", "employee_benefit", "debt"):
                print("Step 6 - RETURN None (excluded asset type)")
            else:
                baseline = 1.5 if asset_type == "unknown" else {"server": 1.5, "datacenter_equipment": 1.5, "gpu_cluster": 1.5, "wafer_fab_equipment": 3.5, "manufacturing_equipment": 3.5, "general_equipment": 4.0}.get(asset_type, 1.5)
                conf = "high" if has_conf else "medium"
                print(f"Step 6 - RETURN ({max_life}, {asset_type}, {conf}, {baseline})")
        
        # 现在调用实际函数
        from ai_annotation.scorer_calculator import _extract_life_years_from_context
        result = _extract_life_years_from_context(text)
        print(f"\n实际函数返回: {result}")
        break
