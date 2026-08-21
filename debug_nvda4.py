import sys
sys.path.insert(0, 'src')

from ai_annotation.scorer_calculator import _extract_life_years, _extract_life_years_from_context
from ai_annotation import load_10k_html

# 加载 NVDA HTML
html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
print(f"HTML 文本长度: {len(html_text)}")

# 测试直接从 HTML 提取（模拟 _extract_life_years 的回退逻辑）
search_text = html_text[:50000]
print(f"搜索文本长度: {len(search_text)}")

import re
matches = list(re.finditer(r"useful\s+(?:life|lives)", search_text, re.I))
print(f"找到 'useful life/lives' 匹配: {len(matches)} 个")

for i, m in enumerate(matches[:5]):
    start = max(0, m.start() - 300)
    end = min(len(search_text), m.end() + 300)
    context = search_text[start:end]
    print(f"\n=== 匹配 {i+1} ===")
    print(context[:500])
    
    # 测试提取
    result = _extract_life_years_from_context(context)
    print(f"提取结果: {result}")

# 测试完整的 _extract_life_years 函数（无候选，只有 full_text）
print("\n\n=== 测试 _extract_life_years（空候选，只有 full_text）===")
result = _extract_life_years([], full_text=html_text)
print(f"结果: {result}")
