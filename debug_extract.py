import sys
sys.path.insert(0, 'src')
from ai_annotation.scorer_calculator import _extract_life_years_from_context

text = """Property
 and equipment are stated at cost less accumulated depreciation. 
Depreciation of property and equipment is computed using the 
straight-line method based on the estimated useful lives of the assets 
of two to seven years .
 Once an asset is identified for retirement or disposition, the related 
cost and accumulated depreciation or amortization are removed, and a 
gain or loss is recorded. The estimated useful lives of our buildings 
are up to thirty years ."""

print("=== 测试文本 ===")
print(text)
print(f"\n文本长度: {len(text)}")
print(f"包含 '\\n': {'Yes' if '\\n' in text else 'No'}")

result = _extract_life_years_from_context(text)
print(f"\n提取结果: {result}")

# 测试去掉换行符后的文本
text2 = text.replace('\n', ' ').replace('\r', ' ')
result2 = _extract_life_years_from_context(text2)
print(f"去掉换行符后: {result2}")

# 只测试核心部分
text3 = "Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets of two to seven years."
result3 = _extract_life_years_from_context(text3)
print(f"核心文本: {result3}")
