import re, html, sys

PATH = r"D:\depreciation-risk-detection\data\raw\amd_fy2024_10k.html"

with open(PATH, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print("total lines:", len(lines))

def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

plain = [strip_tags(l) for l in lines]

def find(pattern, ctx=0, flags=re.I):
    pat = re.compile(pattern, flags)
    hits = []
    for i, p in enumerate(plain):
        if pat.search(p):
            hits.append(i + 1)
    return hits

if __name__ == "__main__":
    kw = sys.argv[1] if len(sys.argv) > 1 else "impairment"
    hits = find(kw)
    print(f"keyword {kw!r}: {len(hits)} hits")
    for h in hits:
        txt = plain[h-1]
        print(f"--- line {h} ---")
        print(txt[:1500])
        print()
