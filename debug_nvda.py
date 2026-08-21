import re
from bs4 import BeautifulSoup

# 读取 NVDA FY2025 10-K HTML
html_path = 'data/raw/nvda_fy2025_10k.html'
with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()

# 搜索 useful life / depreciat 相关文本
keywords = ['useful life', 'useful lives', 'depreciat']
matches = []
for kw in keywords:
    for m in re.finditer(kw, text, re.I):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        snippet = text[start:end]
        matches.append((kw, snippet))

print(f"找到 {len(matches)} 个匹配\n")

# 打印前20个匹配
for i, (kw, snippet) in enumerate(matches[:20]):
    print(f"=== 匹配 {i+1}: keyword='{kw}' ===")
    print(snippet.replace('\n', ' '))
    print()
