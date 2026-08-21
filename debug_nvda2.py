import json

# 读取 NVDA 的验证结果
with open('data/validation_v62_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

nvda = results['NVDA']
print("=== NVDA 候选段落 ===")
for i, c in enumerate(nvda.get('candidates', [])[:10]):
    print(f"\n候选 {i+1}: dim={c.get('dimension_id')}")
    text = c.get('text_excerpt', '')
    print(f"文本 ({len(text)} 字符):")
    print(text[:500])
    print("...")

print("\n\n=== NVDA 规则应用 ===")
for r in nvda.get('rules_applied', []):
    print(r)

print("\n=== NVDA AI 原始评分 ===")
for d in nvda.get('ai_raw_scores', []):
    print(f"{d['dimension_id']}: {d['score']}")

print("\n=== NVDA D1 提取调试 ===")
# 手动测试提取
from src.ai_annotation.scorer_calculator import _extract_life_years_from_context

# 从候选段落中提取所有文本
all_text = " ".join(c.get("text_excerpt", "") for c in nvda.get('candidates', []))
print(f"所有候选文本总长度: {len(all_text)}")

# 搜索包含 useful life 的候选
for c in nvda.get('candidates', []):
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower() or 'depreciat' in text.lower():
        print(f"\n相关候选 (dim={c.get('dimension_id')}):")
        print(text[:800])
        result = _extract_life_years_from_context(text)
        print(f"提取结果: {result}")
