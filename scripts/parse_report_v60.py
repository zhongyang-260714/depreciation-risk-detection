import json, sys

JSON_PATH = r"D:\depreciation-risk-detection\tmp\report_v60.json"
OUT_TXT = r"D:\depreciation-risk-detection\tmp\report_v60_text.txt"

d = json.load(open(JSON_PATH, encoding='utf-8'))
blocks = d.get('content', {}).get('blocks', [])
para_count = 0
table_count = 0
image_count = 0
lines = []

for b in blocks:
    t = b.get('type')
    if t == 'paragraph':
        txt = (b.get('text') or '').strip()
        if txt:
            lines.append(txt)
            para_count += 1
    elif t == 'table':
        table_count += 1
        for row in b.get('cells', []):
            cells = [c.get('text', '').strip() for c in row]
            lines.append(' | '.join(cells))
        lines.append('')  # blank after table
    elif t in ('image', 'picture', 'image-block'):
        image_count += 1

text = '\n'.join(lines)
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    f.write(text)

print("paragraphs:", para_count)
print("tables:", table_count)
print("images:", image_count)
print("total chars:", len(text))
print("saved to", OUT_TXT)
