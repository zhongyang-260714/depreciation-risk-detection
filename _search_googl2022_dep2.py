import re

content = open('D:/depreciation-risk-detection/data/raw/googl_2022_10k.html', 'r', encoding='latin-1').read()
text = re.sub(r'<[^>]+>', ' ', content)
lines = text.splitlines()

for i, line in enumerate(lines, 1):
    l = line.strip()
    if 'depreciation and impairment' in l.lower() and 'property and equipment' in l.lower():
        print(f'{i}: {l}')
    if 'depreciation of property and equipment' in l.lower() and ('2022' in l or '2021' in l or 'billion' in l):
        print(f'{i}: {l}')
    if 'note 1' in l.lower() and 'significant accounting policies' in l.lower():
        print(f'NOTE1_HEADER {i}: {l}')
