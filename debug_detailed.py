import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch
from ai_annotation.scorer_calculator import _extract_life_years_from_context, _has_exclusion_context
import re

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

# 找到 useful life 候选并详细分析
for c in candidates:
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower():
        print(f"文本长度: {len(text)}")
        print(f"包含 '\\n': {chr(10) in text}")
        print(f"_has_exclusion_context: {_has_exclusion_context(text)}")
        
        # 手动模拟 _extract_life_years_from_context 的每一步
        text_processed = text.replace('\n', ' ').replace('\r', ' ')
        text_lower = text_processed.lower()
        print(f"处理后的 text_lower 前300字符: {text_lower[:300]!r}")
        
        # 检查 word_pattern
        word_pattern = re.compile(
            r"(?:depreciat\w+|useful\s+life|life|lives|server|equipment|machinery).{0,300}?"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty)"
            r"\s*years?",
            re.I,
        )
        matches = list(word_pattern.finditer(text_lower))
        print(f"word_pattern 匹配数: {len(matches)}")
        for m in matches:
            print(f"  匹配: {m.group()!r}, group1={m.group(1)}")
        
        # 调用完整函数
        result = _extract_life_years_from_context(text)
        print(f"_extract_life_years_from_context: {result}")
        break
else:
    print("No useful life candidate found")
