import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years_from_context

html_text = load_10k_html('MSFT', 2025, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

for i, c in enumerate(candidates):
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower():
        result = _extract_life_years_from_context(text)
        if result:
            print(f"\n=== MSFT 候选 {i}: {result} ===")
            print(text)
            print("-" * 60)
