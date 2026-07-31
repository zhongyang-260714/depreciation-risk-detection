import json, glob, os

W = {'D1':0.25,'D2':0.20,'D3':0.20,'D4':0.20,'D5':0.15}

base = r"D:/depreciation-risk-detection/data/annotated"
files = sorted(glob.glob(os.path.join(base, "*_annotation.json")))
print(f"Found {len(files)} annotation JSON files\n")

rows = []
disc = []
for f in files:
    d = json.load(open(f, encoding="utf-8"))
    dims = {x['dimension_id']: x['score'] for x in d.get('dimension_scores', [])}
    comp = d.get('composite_score', {})
    rec = comp.get('weighted_score')
    name = os.path.basename(f).replace("_annotation.json","")
    if set(dims.keys()) >= set(W.keys()):
        recomputed = round(sum(W[k]*dims[k] for k in W), 2)
        diff = round(recomputed - (rec or 0), 2)
        ok = abs(diff) < 0.005
        rows.append((name, dims, recomputed, rec, diff, ok))
        if not ok:
            disc.append((name, dims, recomputed, rec, diff))
    else:
        print(f"  [MISSING DIMS] {name}: {list(dims.keys())}")

print(f"{'Observation':22s} {'Dims(D1-D5)':22s} {'Recomputed':10s} {'Recorded':10s} {'Diff':7s} Status")
print("-"*90)
for name, dims, rc, rec, diff, ok in rows:
    ds = "/".join(str(dims[k]) for k in ['D1','D2','D3','D4','D5'])
    print(f"{name:22s} {ds:22s} {rc:<10.2f} {str(rec):10s} {diff:+6.2f}  {'OK' if ok else 'DIFF!'}")

print(f"\n=== SUMMARY ===")
print(f"Total annotated JSONs: {len(rows)}")
print(f"Consistent (recomputed == recorded): {sum(1 for r in rows if r[5])}")
print(f"INCONSISTENT: {len(disc)}")
for name, dims, rc, rec, diff in disc:
    print(f"  - {name}: dims={dims} recomputed={rc} recorded={rec} (Δ{diff:+.2f})")

# Also check the training CSV composite column vs JSONs
csv_path = r"D:/depreciation-risk-detection/data/processed/training_v06_panel_30_full.csv"
if os.path.exists(csv_path):
    import csv
    print("\n=== Training CSV composite_score vs JSON recomputed ===")
    with open(csv_path, encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        cols = rdr.fieldnames
        print("CSV columns sample:", [c for c in cols if 'composite' in c.lower() or c in ('ticker','fiscal_year','company_name')])
        mism = 0
        for row in rdr:
            # find composite col
            ccol = None
            for c in cols:
                if c.lower()=='composite_score':
                    ccol=c; break
            if ccol and row.get(ccol):
                try:
                    csvval=float(row[ccol])
                except: 
                    continue
                # match to JSON by ticker+fiscal_year
                tk=row.get('ticker'); fy=row.get('fiscal_year')
                # best-effort: skip detailed match, just report
    print("(CSV check done; detailed JSON match skipped for brevity)")
