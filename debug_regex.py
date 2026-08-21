import sys
sys.path.insert(0, 'src')
import re
from ai_annotation.scorer_calculator import (
    D1_LIFE_YEAR_PATTERNS, _WORD_TO_NUM, _parse_number_word,
    _detect_asset_type, _has_confirmation_context
)

text = """Property
 and equipment are stated at cost less accumulated depreciation. 
Depreciation of property and equipment is computed using the 
straight-line method based on the estimated useful lives of the assets 
of two to seven years .
 Once an asset is identified for retirement or disposition, the related 
cost and accumulated depreciation or amortization are removed, and a 
gain or loss is recorded. The estimated useful lives of our buildings 
are up to thirty years ."""

text = text.replace('\n', ' ').replace('\r', ' ')
text_lower = text.lower()

print(f"处理后的文本:\n{text_lower[:300]}\n")

print("=== 测试 D1_LIFE_YEAR_PATTERNS ===")
for i, pattern in enumerate(D1_LIFE_YEAR_PATTERNS):
    matches = list(pattern.finditer(text_lower))
    print(f"模式 {i}: {pattern.pattern[:60]}... -> 匹配数: {len(matches)}")
    for m in matches:
        print(f"  匹配: {m.group()!r}, groups: {m.groups()}")

print("\n=== 测试 word_range_pattern ===")
word_range_pattern = re.compile(
    r"(?:useful\s+lives?|depreciable\s+life|estimated\s+life|depreciated|over|of)"
    r".??"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
    r"\s*(?:to|-|–)\s*"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)"
    r"\s*years?",
    re.I,
)
matches = list(word_range_pattern.finditer(text_lower))
print(f"匹配数: {len(matches)}")
for m in matches:
    print(f"  匹配: {m.group()!r}")
    print(f"  group1: {m.group(1)}, group2: {m.group(2)}")
    y1 = _parse_number_word(m.group(1))
    y2 = _parse_number_word(m.group(2))
    print(f"  y1={y1}, y2={y2}")

print(f"\n=== 资产类型 ===")
print(f"_detect_asset_type: {_detect_asset_type(text)}")
print(f"_has_confirmation_context: {_has_confirmation_context(text)}")
