import sys
import importlib

# 强制重新加载模块
if 'src.ai_annotation.scorer_calculator' in sys.modules:
    del sys.modules['src.ai_annotation.scorer_calculator']
if 'src.ai_annotation' in sys.modules:
    del sys.modules['src.ai_annotation']

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years_from_context, _has_exclusion_context

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

# 找到 useful life 候选
for c in candidates:
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower():
        print(f"=== 候选文本分析 ===")
        print(f"长度: {len(text)}")
        print(f"_has_exclusion_context: {_has_exclusion_context(text)}")
        
        result = _extract_life_years_from_context(text)
        print(f"_extract_life_years_from_context: {result}")
        
        # 如果返回 None，进一步调试
        if result is None:
            import re
            text_processed = text.replace('\n', ' ').replace('\r', ' ')
            text_lower = text_processed.lower()
            
            # 测试 word_pattern
            word_pattern = re.compile(
                r"(?:depreciat\w+|useful\s+life|life|lives|server|equipment|machinery).{0,300}?"
                r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
                r"\s*years?",
                re.I,
            )
            matches = list(word_pattern.finditer(text_lower))
            print(f"word_pattern 匹配数: {len(matches)}")
            for m in matches:
                print(f"  匹配: {m.group()!r}, group1={m.group(1)}")
        break
