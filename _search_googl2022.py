import re

text = open("data/raw/googl_2022_10k.html", "r", encoding="latin-1").read()

# Find the exact context around "$11.6 billion and $15.3 billion"
print("=== Context around 11.6 billion ===")
idx = text.find("$11.6 billion")
if idx >= 0:
    context = text[max(0, idx-300):idx+300]
    clean = re.sub(r'<[^>]+>', ' ', context)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(clean)

print("\n=== Context around 15.3 billion ===")
idx = text.find("$15.3 billion")
if idx >= 0:
    context = text[max(0, idx-300):idx+300]
    clean = re.sub(r'<[^>]+>', ' ', context)
    clean = re.sub(r'\s+', ' ', clean).strip()
    print(clean)

# Also search for Note 7 or Note 1 with complete table
print("\n=== Full Note 7 search ===")
for m in re.finditer(r'[Nn]ote\s*7[^<]{0,2000}', text):
    snippet = m.group(0)
    clean = re.sub(r'<[^>]+>', ' ', snippet)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if 'depreciation' in clean.lower() and ('2022' in clean or '2021' in clean):
        print(clean[:400])
        print("---")
