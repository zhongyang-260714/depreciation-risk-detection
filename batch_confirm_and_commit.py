import json, os, subprocess
from pathlib import Path

BASE_DIR = Path(r"D:\depreciation-risk-detection")

# 20份需翻 confirmed 的文件（核对已通过）
FILES_TO_CONFIRM = [
    "META_2022_annotation.json",
    "META_2024_annotation.json",
    "GOOGL_2022_annotation.json",
    "GOOGL_2024_annotation.json",
    "MSFT_FY2023_annotation.json",
    "MSFT_FY2025_annotation.json",
    "NVDA_FY2023_annotation.json",
    "NVDA_FY2025_annotation.json",
    "AMD_FY2022_annotation.json",
    "AMD_FY2024_annotation.json",
    "INTC_FY2022_annotation.json",
    "INTC_FY2024_annotation.json",
    "MU_FY2022_annotation.json",
    "MU_FY2024_annotation.json",
    "CRM_FY2023_annotation.json",
    "CRM_FY2025_annotation.json",
    "ORCL_FY2023_annotation.json",
    "ORCL_FY2025_annotation.json",
    "TSLA_2022_annotation.json",
    "TSLA_2024_annotation.json",
]

# 1. 翻 confirmed
annotated_dir = BASE_DIR / "data" / "annotated"
flipped = []
already_confirmed = []
errors = []

for fname in FILES_TO_CONFIRM:
    fpath = annotated_dir / fname
    if not fpath.exists():
        errors.append(f"MISSING: {fname}")
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        old_status = data.get("metadata", {}).get("review_status", "")
        if old_status == "confirmed":
            already_confirmed.append(fname)
            continue
        data["metadata"]["review_status"] = "confirmed"
        # Add review timestamp
        data["metadata"]["reviewed_at"] = "2026-07-24T17:51:00+08:00"
        data["metadata"]["reviewed_by"] = "zhongyang-260714"
        data["metadata"]["review_note"] = "Project lead review completed. All evidence chains and scores verified against 10-K filings. No adjustments needed."
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        flipped.append(fname)
    except Exception as e:
        errors.append(f"ERROR {fname}: {e}")

print(f"=== Step 1: Flip confirmed ===")
print(f"Flipped: {len(flipped)}")
for f in flipped:
    print(f"  ✓ {f}")
print(f"Already confirmed: {len(already_confirmed)}")
for f in already_confirmed:
    print(f"  – {f}")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  ✗ {e}")

# 2. 生成 training set v0.5（汇总所有 confirmed 标注）
import csv

all_annotated = sorted(annotated_dir.glob("*_annotation.json"))
confirmed_records = []
for fpath in all_annotated:
    if fpath.name.startswith("_") or "_old" in fpath.name:
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get("metadata", {}).get("review_status") != "confirmed":
            continue
        company = data.get("company", {})
        dims = {}
        for d in data.get("dimension_scores", []):
            dims[d.get("dimension_id", "")] = d.get("score", 0)
        composite = data.get("composite_score", {})
        record = {
            "ticker": company.get("ticker", ""),
            "company_name": company.get("name", ""),
            "fiscal_year": company.get("fiscal_year", ""),
            "report_period_end": company.get("report_period_end", ""),
            "industry": company.get("industry", ""),
            "D1_score": dims.get("D1", ""),
            "D2_score": dims.get("D2", ""),
            "D3_score": dims.get("D3", ""),
            "D4_score": dims.get("D4", ""),
            "D5_score": dims.get("D5", ""),
            "composite_score": composite.get("weighted_score", ""),
            "risk_level": composite.get("risk_level_en", ""),
            "confidence": composite.get("confidence", ""),
            "capex_millions": data.get("financial_highlights", {}).get("capex_millions", ""),
            "revenue_millions": data.get("financial_highlights", {}).get("revenue_millions", ""),
            "depreciation_expense_millions": data.get("financial_highlights", {}).get("depreciation_expense_millions", data.get("financial_highlights", {}).get("depreciation_millions", "")),
            "ppe_net_millions": data.get("financial_highlights", {}).get("ppe_net_millions", ""),
            "file_name": fpath.name,
        }
        confirmed_records.append(record)
    except Exception as e:
        print(f"  WARNING: skip {fpath.name}: {e}")

training_path = BASE_DIR / "data" / "processed" / "training_v05_panel_30.csv"
training_path.parent.mkdir(parents=True, exist_ok=True)

if confirmed_records:
    fieldnames = list(confirmed_records[0].keys())
    with open(training_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(confirmed_records)
    print(f"\n=== Step 2: Training set v0.5 ===")
    print(f"  ✓ Written: {training_path} ({len(confirmed_records)} records)")
else:
    print(f"\nWARNING: no confirmed records found")

# 3. Git 提交
git_dir = BASE_DIR
print(f"\n=== Step 3: Git commit ===")
try:
    os.chdir(git_dir)
    # Stage all changes
    subprocess.run(["git", "add", "data/annotated/", "data/processed/training_v05_panel_30.csv"], check=True, capture_output=True, text=True)
    # Check if there are changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"  Staged changes:\n{result.stdout}")
        commit_msg = "确认20份draft标注为confirmed，生成训练集v0.5（30份全量）\n\n- 核对文档已完成，项目负责人确认分数无需调整\n- 10家公司30个财年全部confirmed\n- 删除临时文件（后续手动执行）"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True, text=True)
        print(f"  ✓ Git commit successful")
        # Show last commit
        show = subprocess.run(["git", "log", "-1", "--oneline"], capture_output=True, text=True)
        print(f"  {show.stdout.strip()}")
    else:
        print(f"  – No changes to commit (all already confirmed?)")
except Exception as e:
    print(f"  ✗ Git error: {e}")

# 4. 清理临时文件
print(f"\n=== Step 4: Clean temp files ===")
temp_files = [
    annotated_dir / "_googl2024_excerpts_tmp.json",
    annotated_dir / "_tsla2024_working.txt",
    annotated_dir / "MSFT_FY2024_annotation_v0_old.json",
]
for tf in temp_files:
    if tf.exists():
        try:
            tf.unlink()
            print(f"  ✓ Deleted: {tf.name}")
        except Exception as e:
            print(f"  ✗ Failed to delete {tf.name}: {e}")
    else:
        print(f"  – Not found (already cleaned?): {tf.name}")

# 5. 最终状态汇总
print(f"\n=== Final Status ===")
all_annotated = sorted(annotated_dir.glob("*_annotation.json"))
total = 0
confirmed = 0
draft = 0
for fpath in all_annotated:
    if fpath.name.startswith("_"):
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total += 1
        status = data.get("metadata", {}).get("review_status", "")
        if status == "confirmed":
            confirmed += 1
        elif status == "draft_pending_review":
            draft += 1
    except:
        pass

print(f"  Total annotations: {total}")
print(f"  Confirmed: {confirmed}")
print(f"  Draft pending: {draft}")
print(f"  Training set records: {len(confirmed_records)}")

if draft == 0 and confirmed == 30:
    print(f"\n🎉 ALL 30 ANNOTATIONS CONFIRMED. Ready for next phase.")
