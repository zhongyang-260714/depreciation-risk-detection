import sys
sys.path.insert(0, 'src')
from ai_annotation import load_10k_html
import re

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')

# 搜索 "useful" 附近的内容
for m in re.finditer(r"useful", html_text, re.I):
    start = max(0, m.start() - 50)
    end = min(len(html_text), m.end() + 100)
    snippet = html_text[start:end]
    print(f"=== useful @ {m.start()} ===")
    print(repr(snippet))
    print()
    break  # 只看第一个

# 也搜索 "life"
for m in re.finditer(r"life", html_text, re.I):
    start = max(0, m.start() - 50)
    end = min(len(html_text), m.end() + 50)
    snippet = html_text[start:end]
    if "useful" in snippet.lower():
        print(f"=== life near useful @ {m.start()} ===")
        print(repr(snippet))
        print()
        break
