import re

content = open('D:/depreciation-risk-detection/data/raw/googl_2022_10k.html', 'r', encoding='latin-1').read()
text = re.sub(r'<[^>]+>', ' ', content)
lines = text.splitlines()

# Search for PP&E note and depreciation figures
for i, line in enumerate(lines, 1):
    l = line.strip()
    if 'depreciation' in l.lower() and ('property' in l.lower() or 'equipment' in l.lower() or 'billion' in l.lower()):
        if any(x in l for x in ['2021', '2022', '15.3', '13.4', '11.6', 'impairment']):
            print(f'{i}: {l}')
