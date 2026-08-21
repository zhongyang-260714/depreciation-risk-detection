import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years_from_context

for ticker, year in [('MU', 2024), ('MSFT', 2025), ('NVDA', 2025)]:
    print(f"\n{'='*60}")
    print(f"=== {ticker} FY{year} ===")
    print(f"{'='*60}")
    html_text = load_10k_html(ticker, year, cache_dir='data/raw')
    candidates = locate_candidates_batch(html_text, max_candidates=80)
    
    count = 0
    for i, c in enumerate(candidates):
        text = c.get('text_excerpt', '')
        if 'useful life' in text.lower() or 'depreciat' in text.lower():
            count += 1
            result = _extract_life_years_from_context(text)
            print(f"\n--- 候选 {i}: {c['keyword_matched']} ({c['keyword_tier']}) ---")
            print(f"文本: {text[:250]!r}")
            print(f"提取: {result}")
            if count >= 3:
                break
