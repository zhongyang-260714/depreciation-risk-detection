import re

with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 移除 DEBUG 输出
content = content.replace(
    "d1_result = _extract_life_years(candidates, full_text=full_html); print(f'[DEBUG] D1 extraction result: {d1_result}')",
    "d1_result = _extract_life_years(candidates, full_text=full_html)"
)

# 2. 修改 word_pattern 支持阿拉伯数字
old_word_pattern = '''        word_pattern = re.compile(
            r"(?:depreciat\\w+|useful\\s+life|life|lives|server|equipment|machinery).{0,300}?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\\s*years?",
            re.I,
        )'''

new_word_pattern = '''        word_pattern = re.compile(
            r"(?:depreciat\\w+|useful\\s+life|life|lives|server|equipment|machinery).{0,300}?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\\d+(?:\\.\\d+)?)"
            r"\\s*years?",
            re.I,
        )'''

if old_word_pattern in content:
    content = content.replace(old_word_pattern, new_word_pattern, 1)
    print("Fixed word_pattern")
else:
    print("word_pattern not found")

# 3. 修改 word_range_pattern 支持阿拉伯数字
old_word_range = '''        word_range_pattern = re.compile(
            r"(?:useful\\s+lives?|depreciable\\s+life|estimated\\s+life|depreciated|over|of)"
            r".??"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\\s*(?:to|-|–)\\s*"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\\d+)"
            r"\\s*years?",
            re.I,
        )'''

new_word_range = '''        word_range_pattern = re.compile(
            r"(?:useful\\s+lives?|depreciable\\s+life|estimated\\s+life|depreciated|over|of)"
            r".??"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\\d+(?:\\.\\d+)?)"
            r"\\s*(?:to|-|–)\\s*"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\\d+(?:\\.\\d+)?)"
            r"\\s*years?",
            re.I,
        )'''

if old_word_range in content:
    content = content.replace(old_word_range, new_word_range, 1)
    print("Fixed word_range_pattern")
else:
    print("word_range_pattern not found")

# 4. 修改 single_word_pattern 支持阿拉伯数字
old_single = '''        single_word_pattern = re.compile(
            r"(?:useful\\s+lives?|depreciable\\s+life|estimated\\s+life|depreciated|over|of)"
            r".??"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\\s*years?",
            re.I,
        )'''

new_single = '''        single_word_pattern = re.compile(
            r"(?:useful\\s+lives?|depreciable\\s+life|estimated\\s+life|depreciated|over|of)"
            r".??"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|\\d+(?:\\.\\d+)?)"
            r"\\s*years?",
            re.I,
        )'''

if old_single in content:
    content = content.replace(old_single, new_single, 1)
    print("Fixed single_word_pattern")
else:
    print("single_word_pattern not found")

# 5. 添加通用阿拉伯数字年限模式到 D1_LIFE_YEAR_PATTERNS
old_patterns = '''D1_LIFE_YEAR_PATTERNS_EN = [
    re.compile(r"depreciat\\w+\\s+over\\s+(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"depreciat\\w+\\s+(?:on\\s+)?(?:a\\s+)?(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:useful\\s+)?(?:life|lives)\\s+of\\s+(?:our\\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:useful\\s+)?(?:life|lives)\\s+of\\s+(?:our\\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(?:of\\s+|to\\s+|up\\s+to\\s+)(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:estimated\\s+)?(?:useful\\s+)?(?:life|lives)\\s+(?:of\\s+|to\\s+|up\\s+to\\s+)(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
]'''

new_patterns = '''D1_LIFE_YEAR_PATTERNS_EN = [
    re.compile(r"depreciat\\w+\\s+over\\s+(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"depreciat\\w+\\s+(?:on\\s+)?(?:a\\s+)?(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:useful\\s+)?(?:life|lives)\\s+of\\s+(?:our\\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(\\d+(?:\\.\\d+)?)\\s*(?:to|-)\\s+(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:useful\\s+)?(?:life|lives)\\s+of\\s+(?:our\\s+)?(?:server|network|datacenter|equipment|machinery).{0,40}?(?:of\\s+|to\\s+|up\\s+to\\s+)(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:estimated\\s+)?(?:useful\\s+)?(?:life|lives)\\s+(?:of\\s+|to\\s+|up\\s+to\\s+)(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    # v6.2新增：通用折旧年限范围匹配（支持 "10 to 30 years" 等格式）
    re.compile(r"(\\d+(?:\\.\\d+)?)\\s*(?:to|-|–)\\s*(\\d+(?:\\.\\d+)?)\\s*years?\\s+(?:for\\s+)?(?:buildings?|production\\s+equipment|other\\s+equipment|machinery|servers?|network|datacenter)", re.I),
    re.compile(r"(?:buildings?|production\\s+equipment|other\\s+equipment|machinery|servers?|network|datacenter).{0,40}?(\\d+(?:\\.\\d+)?)\\s*(?:to|-|–)\\s*(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
    re.compile(r"(?:buildings?|production\\s+equipment|other\\s+equipment|machinery|servers?|network|datacenter).{0,40}?(?:of\\s+|up\\s+to\\s+)?(\\d+(?:\\.\\d+)?)\\s*years?", re.I),
]'''

if old_patterns in content:
    content = content.replace(old_patterns, new_patterns, 1)
    print("Added generic numeric year patterns")
else:
    print("D1_LIFE_YEAR_PATTERNS_EN not found")

with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("All fixes applied.")
