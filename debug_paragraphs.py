from bs4 import BeautifulSoup
import re

with open('data/raw/nvda_fy2025_10k.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# 完整模拟 _extract_visible_paragraphs
soup = BeautifulSoup(html, "html.parser")

# v2.4修复：对包含财务数据的XBRL标签，unwrap保留内容而非decompose删除
for tag in soup.find_all(["ix:nonnumeric", "ix:numeric", "ix:nonfraction"]):
    tag.unwrap()  # 只删除标签，保留内容
for tag in soup.find_all(["ix:header", "ix:hidden", "ix:references", "ix:resources"]):
    tag.decompose()  # 元数据标签直接删除
# 移除所有以 ix- 命名空间开头的标签
for tag in soup.find_all(True):
    if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
        tag.unwrap()
for tag in soup.find_all(["ix:header", "ix:hidden", "ix:nonnumeric", "ix:numeric",
                          "ix:nonfraction", "ix:references", "ix:resources"]):
    tag.decompose()
# 移除所有以 ix- 命名空间开头的标签
for tag in soup.find_all(True):
    if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
        tag.decompose()

# 移除 script、style、head、noscript
for tag_name in ["script", "style", "head", "noscript", "meta", "link"]:
    for tag in soup.find_all(tag_name):
        tag.decompose()

# 移除 display:none 的元素
for tag in soup.find_all(style=re.compile(r"display:\s*none", re.I)):
    tag.decompose()

# 提取段落
paragraphs = []
for p in soup.find_all("p"):
    text = p.get_text(separator=" ", strip=True)
    if len(text) > 30:
        paragraphs.append(text)

if len(paragraphs) < 10:
    for div in soup.find_all("div"):
        text = div.get_text(separator=" ", strip=True)
        if len(text) > 50 and len(text) < 5000:
            paragraphs.append(text)

for td in soup.find_all(["td", "th"]):
    text = td.get_text(separator=" ", strip=True)
    if len(text) > 20:
        paragraphs.append(text)

# 搜索包含 useful life / depreciat / two to seven years 的段落
print(f"总段落数: {len(paragraphs)}")
found = []
for i, text in enumerate(paragraphs):
    if 'useful life' in text.lower() or 'depreciat' in text.lower() or 'two to seven' in text.lower():
        found.append((i, text))

print(f"包含相关关键词的段落: {len(found)}")
for i, text in found[:10]:
    print(f"\n=== 段落 {i} ({len(text)} 字符) ===")
    print(text[:500])
