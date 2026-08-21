import sys
import importlib

# 强制重新加载模块
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation.scorer_calculator import _extract_life_years_from_context, _has_exclusion_context

text = """Property
 and equipment are stated at cost less accumulated depreciation. 
Depreciation of property and equipment is computed using the 
straight-line method based on the estimated useful lives of the assets 
of two to seven years .
 Once an asset is identified for retirement or disposition, the related 
cost and accumulated depreciation or amortization are removed, and a 
gain or loss is recorded. The estimated useful lives of our buildings 
are up to thirty years ."""

print(f"_has_exclusion_context: {_has_exclusion_context(text)}")
print(f"_extract_life_years_from_context: {_extract_life_years_from_context(text)}")

# 也测试核心文本
text2 = "Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets of two to seven years."
print(f"核心文本: {_extract_life_years_from_context(text2)}")
