import re

# Search TSLA 2024 10-K for net income
text = open("data/raw/tsla_2024_10k_text.txt", "r", encoding="utf-8").read()

print("=== TSLA 2024 Net Income Search ===")

# Search consolidated statements of income
patterns = [
    r"[Nn]et income.*?[0-9,]+(?:\.[0-9]+)?",
    r"[Cc]onsolidated[^\n]{0,100}[Ii]ncome",
    r"[Nn]et\s+income\s*\(?loss\)?.*?[0-9,]+",
]

for p in patterns:
    matches = re.findall(p, text)
    if matches:
        print(f"\nPattern: {p}")
        for m in matches[:10]:
            clean = re.sub(r'\s+', ' ', m).strip()
            print(f"  >> {clean}")

# More targeted: search lines with "Net income" and dollar amounts
print("\n=== Lines with 'Net income' ===")
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'net income' in line.lower() or 'net loss' in line.lower():
        clean = re.sub(r'\s+', ' ', line).strip()
        if len(clean) > 10 and len(clean) < 300:
            print(f"  L{i}: {clean}")
