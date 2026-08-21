import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years

for ticker, year in [('NVDA', 2025), ('MSFT', 2025), ('META', 2024)]:
    print(f"\n=== {ticker} FY{year} ===")
    html_text = load_10k_html(ticker, year, cache_dir='data/raw')
    candidates = locate_candidates_batch(html_text, max_candidates=80)
    
    result = _extract_life_years(candidates, html_text)
    print(f"_extract_life_years: {result}")
    
    # 检查 useful life 候选
    for c in candidates:
        text = c.get('text_excerpt', '')
        if 'useful life' in text.lower():
            print(f"  候选关键词: {c['keyword_matched']}, 长度: {len(text)}")
            break
