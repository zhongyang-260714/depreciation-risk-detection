import sys
sys.path.insert(0, 'src')
import re
from ai_annotation.scorer_calculator import _parse_number_word

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

# 测试 word_pattern（第一个英文单词匹配模式）
word_pattern = re.compile(
    r"(?:depreciat\w+|useful\s+life|life|lives|server|equipment|machinery).{0,300}?"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
    r"\s*years?",
    re.I,
)

print("=== 测试 word_pattern ===")
matches = list(word_pattern.finditer(text_lower))
print(f"匹配数: {len(matches)}")
for m in matches:
    print(f"  匹配: {m.group()!r}")
    print(f"  group1: {m.group(1)}")
    y = _parse_number_word(m.group(1))
    print(f"  y={y}")

# 测试 word_range_pattern
word_range_pattern = re.compile(
    r"(?:useful\s+lives?|depreciable\s+life|estimated\s+life|depreciated|over|of)"
    r".*?"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
    r"\s*(?:to|-|–)\s*"
    r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\d+)"
    r"\s*years?",
    re.I,
)

print("\n=== 测试 word_range_pattern ===")
matches = list(word_range_pattern.finditer(text_lower))
print(f"匹配数: {len(matches)}")
for m in matches:
    print(f"  匹配: {m.group()!r}")
    print(f"  group1: {m.group(1)}, group2: {m.group(2)}")
    y1 = _parse_number_word(m.group(1))
    y2_str = m.group(2)
    y2 = _parse_number_word(y2_str) if not y2_str.isdigit() else float(y2_str)
    print(f"  y1={y1}, y2={y2}")
