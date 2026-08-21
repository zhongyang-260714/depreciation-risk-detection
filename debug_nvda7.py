import sys
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
        print(f"包含 '\\n': {chr(10) in text}")
        print(f"包含 '\\r': {chr(13) in text}")
        print(f"_has_exclusion_context: {_has_exclusion_context(text)}")
        
        result = _extract_life_years_from_context(text)
        print(f"_extract_life_years_from_context: {result}")
        
        # 打印前500字符的repr
        print(f"\n文本repr: {repr(text[:500])}")
        break
else:
    print("没有找到 useful life 候选！")
