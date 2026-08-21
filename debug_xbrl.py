from bs4 import BeautifulSoup
import re

# 读取 NVDA HTML
with open('data/raw/nvda_fy2025_10k.html', 'r', encoding='utf-8', errors='replace') as f:
    html = f.read()

# 测试：查找包含 "two to seven years" 的 ix:nonnumeric 标签
soup = BeautifulSoup(html, 'html.parser')

# 先不处理任何标签，直接搜索
raw_matches = re.findall(r'two\s+to\s+seven\s+years', html, re.I)
print(f"原始 HTML 中 'two to seven years' 出现次数: {len(raw_matches)}")

# 检查这些文本是否在 ix:nonnumeric 标签内
for m in re.finditer(r'two\s+to\s+seven\s+years', html, re.I):
    start = max(0, m.start() - 200)
    end = min(len(html), m.end() + 200)
    snippet = html[start:end]
    print(f"\n=== 原始 HTML 中的上下文 ===")
    print(snippet)
    break  # 只看第一个

# 现在模拟 _extract_visible_paragraphs 的处理流程
soup2 = BeautifulSoup(html, 'html.parser')

# 第一步：unwrap ix:nonnumeric
for tag in soup2.find_all(["ix:nonnumeric", "ix:numeric", "ix:nonfraction"]):
    tag.unwrap()

text_after_unwrap = soup2.get_text(separator="\n", strip=True)
unwrap_matches = re.findall(r'two\s+to\s+seven\s+years', text_after_unwrap, re.I)
print(f"\nunwrap 后 'two to seven years' 出现次数: {len(unwrap_matches)}")

# 第二步：decompose ix:nonnumeric（这是当前代码中的问题！）
for tag in soup2.find_all(["ix:header", "ix:hidden", "ix:nonnumeric", "ix:numeric",
                          "ix:nonfraction", "ix:references", "ix:resources"]):
    tag.decompose()

text_after_decompose = soup2.get_text(separator="\n", strip=True)
decompose_matches = re.findall(r'two\s+to\s+seven\s+years', text_after_decompose, re.I)
print(f"decompose 后 'two to seven years' 出现次数: {len(decompose_matches)}")

# 验证：只 unwrap 不 decompose 的结果
soup3 = BeautifulSoup(html, 'html.parser')
for tag in soup3.find_all(["ix:nonnumeric", "ix:numeric", "ix:nonfraction"]):
    tag.unwrap()
for tag in soup3.find_all(["ix:header", "ix:hidden", "ix:references", "ix:resources"]):
    tag.decompose()
for tag in soup3.find_all(True):
    if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
        tag.unwrap()

text_correct = soup3.get_text(separator="\n", strip=True)
correct_matches = re.findall(r'two\s+to\s+seven\s+years', text_correct, re.I)
print(f"正确做法（只unwrap ix内容标签）后 'two to seven years' 出现次数: {len(correct_matches)}")
