import sys
sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years

# 加载 NVDA HTML
html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
print(f"HTML 长度: {len(html_text)}")

# 提取候选（和 run_validation.py 一样用 max_candidates=80）
candidates = locate_candidates_batch(html_text, max_candidates=80)
print(f"候选段落: {len(candidates)} 个")

# 检查是否有 useful life 相关的候选
has_useful_life = False
for c in candidates:
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower() or 'two to seven' in text.lower():
        print(f"\n找到 useful life 候选:")
        print(f"  关键词: {c['keyword_matched']}")
        print(f"  级别: {c['keyword_tier']}/{c['keyword_strength']}")
        print(f"  文本: {text[:300]}")
        has_useful_life = True

if not has_useful_life:
    print("\n警告: 80个候选中没有 useful life 相关内容！")

# 直接测试 _extract_life_years
print("\n=== 测试 _extract_life_years ===")
result = _extract_life_years(candidates, html_text)
print(f"结果: {result}")
