import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

print(f"候选数: {len(candidates)}")

# 测试 _extract_life_years（完整路径，和 run_validation.py 一样）
result = _extract_life_years(candidates, html_text)
print(f"_extract_life_years 结果: {result}")

# 检查每个候选的提取结果
from ai_annotation.scorer_calculator import _extract_life_years_from_context

for c in candidates:
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower():
        r = _extract_life_years_from_context(text)
        print(f"useful life 候选提取: {r}")
        break
