import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')

from ai_annotation import load_10k_html, locate_candidates_batch

html_text = load_10k_html('MU', 2024, cache_dir='data/raw')
candidates = locate_candidates_batch(html_text, max_candidates=80)

print(f"MU candidates: {len(candidates)}")

# 查找包含 useful life / depreciat / life 的候选
found = []
for i, c in enumerate(candidates):
    text = c.get('text_excerpt', '')
    if 'useful life' in text.lower() or 'depreciat' in text.lower():
        found.append((i, c))

print(f"useful life / depreciat candidates: {len(found)}")
for i, c in found[:10]:
    print(f"\n=== {i}: {c['keyword_matched']} ({c['keyword_tier']}) ===")
    print(c['text_excerpt'][:400])
