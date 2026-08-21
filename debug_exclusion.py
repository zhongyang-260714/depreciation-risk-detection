import sys
sys.path.insert(0, 'src')
from ai_annotation.scorer_calculator import _has_exclusion_context, _detect_asset_type, _has_confirmation_context

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
print(f"_detect_asset_type: {_detect_asset_type(text)}")
print(f"_has_confirmation_context: {_has_confirmation_context(text)}")

# 找出哪个排除模式匹配了
import re
from ai_annotation.scorer_calculator import D1_EXCLUSION_PATTERNS
for p in D1_EXCLUSION_PATTERNS:
    if p.search(text):
        print(f"排除模式匹配: {p.pattern}")
