import sys
sys.path.insert(0, 'src')
from ai_annotation.text_locator import locate_candidates, _extract_visible_paragraphs, _extract_structured_sections
from ai_annotation import load_10k_html

html_text = load_10k_html('NVDA', 2025, cache_dir='data/raw')
print(f"HTML 长度: {len(html_text)}")

# 提取所有段落
paragraphs = _extract_visible_paragraphs(html_text)
print(f"提取的段落数: {len(paragraphs)}")

# 查找包含 useful life 的段落
for i, p in enumerate(paragraphs):
    text = p['text']
    if 'useful life' in text.lower() or 'two to seven' in text.lower():
        print(f"\n=== 段落 {i} (tag={p['tag']}) ===")
        print(f"长度: {len(text)}")
        print(text[:300])

# 提取结构化章节
structured = _extract_structured_sections(html_text)
print(f"\n结构化章节数: {len(structured)}")
for s in structured:
    print(f"  - {s['section_name']} ({len(s['text'])} 字符)")

# 运行完整定位
candidates = locate_candidates(html_text)
print(f"\n候选总数: {len(candidates)}")

# 检查关键词命中
for c in candidates:
    if 'life' in c['text_excerpt'].lower() or 'depreciat' in c['text_excerpt'].lower():
        print(f"\n=== 命中候选 ===")
        print(f"关键词: {c['keyword_matched']}")
        print(f"级别: {c['keyword_tier']}/{c['keyword_strength']}")
        print(f"文本: {c['text_excerpt'][:200]}")
