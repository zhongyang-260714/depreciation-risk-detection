import json, re
from collections import defaultdict

PATH = r"D:\depreciation-risk-detection\tmp\report_v41.json"
OUT  = r"D:\depreciation-risk-detection\tmp\report_v41.txt"
data = json.load(open(PATH, encoding='utf-8'))
blocks = data.get('content', {}).get('blocks', [])

lines = []
para = 0; tables = 0
for b in blocks:
    if b.get('type') == 'paragraph':
        txt = (b.get('text') or '').strip()
        if txt:
            lines.append(txt)
            para += 1
    elif b.get('type') == 'table':
        tables += 1
        cells = b.get('table', {}).get('cells', [])
        grid = defaultdict(dict)
        maxcol = 0
        for c in cells:
            r = c.get('row', 1); col = c.get('col', 1); maxcol = max(maxcol, col)
            grid[r][col] = (c.get('text') or '').strip()
        lines.append('【表%d】' % tables)
        for r in sorted(grid):
            lines.append('  ' + ' | '.join(grid[r].get(c, '') for c in range(1, maxcol+1)))
        lines.append('【/表%d】' % tables)

text = '\n'.join(lines)
open(OUT, 'w', encoding='utf-8').write(text)
print("paragraphs with text:", para, "| tables:", tables, "| total chars:", len(text))
