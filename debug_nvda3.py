import json
import sys
sys.path.insert(0, 'src')

from ai_annotation.scorer_calculator import _extract_life_years_from_context

# 读取 NVDA 分析结果
with open('data/analysis_NVDA_FY2025.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

candidates = data.get('candidates', [])
print(f"总候选段落: {len(candidates)}")

# 查找包含 useful life / depreciat 的候选
found = []
for i, c in enumerate(candidates):
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower() or 'depreciat' in text.lower() or 'life' in text.lower():
        found.append((i, c))

print(f"包含 life/depreciat 的候选: {len(found)}")

for i, c in found[:15]:
    text = c.get('text_excerpt', '')
    dim = c.get('dimension_id', 'N/A')
    print(f"\n=== 候选 {i} (dim={dim}, {len(text)} 字符) ===")
    print(text[:600])
    
    # 测试提取
    result = _extract_life_years_from_context(text)
    print(f"提取结果: {result}")
