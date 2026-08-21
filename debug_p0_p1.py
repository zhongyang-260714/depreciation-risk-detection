import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years_from_context

for ticker, year in [('MU', 2024), ('MSFT', 2025), ('NVDA', 2025)]:
    print(f"\n=== {ticker} FY{year} ===")
    html_text = load_10k_html(ticker, year, cache_dir='data/raw')
    candidates = locate_candidates_batch(html_text, max_candidates=80)
    
    for c in candidates:
        text = c.get('text_excerpt', '')
        if 'useful life' in text.lower():
            print(f"候选文本前300字符: {text[:300]!r}")
            result = _extract_life_years_from_context(text)
            print(f"提取结果: {result}")
            break
