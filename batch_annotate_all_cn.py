#!/usr/bin/env python3
"""Batch AI annotation for ALL 10 A-share companies × 3 fiscal years.

Companies (10):
- 中科曙光 (603019.SH)
- 数据港 (603881.SH)
- 寒武纪 (688256.SH)
- 浪潮信息 (000977.SZ)
- 科大讯飞 (002230.SZ)
- 奥飞数据 (300738.SZ)
- 光环新网 (300383.SZ)
- 海光信息 (688041.SH)
- 工业富联 (601138.SH)
- 润泽科技 (300442.SZ)

Years: 2022, 2023, 2024

This script reads PDFs from data/raw/cn_财报/ and runs the full pipeline.
Skips if annotation JSON already exists.
"""

import json
import sys
from pathlib import Path
from io import BytesIO

import pdfplumber

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from src.ai_annotation import (
    DeepSeekClient,
    apply_hard_rules,
    compute_composite_score,
    enrich_dimension_scores,
    locate_cn_candidates,
)

CACHE_DIR = REPO_ROOT / "data" / "raw" / "cn_财报"
ANNOTATED_CN_DIR = REPO_ROOT / "data" / "annotated_cn"
ANNOTATED_CN_DIR.mkdir(parents=True, exist_ok=True)

# All 10 companies: display name -> stock code
COMPANIES = {
    "中科曙光": "603019.SH",
    "数据港": "603881.SH",
    "寒武纪": "688256.SH",
    "浪潮信息": "000977.SZ",
    "科大讯飞": "002230.SZ",
    "奥飞数据": "300738.SZ",
    "光环新网": "300383.SZ",
    "海光信息": "688041.SH",
    "工业富联": "601138.SH",
    "润泽科技": "300442.SZ",
}

YEARS = [2022, 2023, 2024]


def find_pdf(company_name: str, year: int) -> Path:
    """Find the PDF file for a company and year."""
    exact = CACHE_DIR / f"{company_name}{year}.PDF"
    if exact.exists():
        return exact
    exact_lower = CACHE_DIR / f"{company_name}{year}.pdf"
    if exact_lower.exists():
        return exact_lower
    for f in CACHE_DIR.iterdir():
        if f.is_file() and company_name in f.name and str(year) in f.name and f.suffix.lower() == ".pdf":
            return f
    raise FileNotFoundError(f"PDF not found for {company_name} {year}")


def extract_text(pdf_path: Path) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += f"\n--- 第{i+1}页 ---\n{text}\n"
    return full_text


def annotation_exists(company_name: str, stock_code: str, year: int) -> bool:
    """Check if annotation JSON already exists."""
    ticker_normalized = stock_code.replace(".", "")
    # Try multiple filename patterns
    patterns = [
        ANNOTATED_CN_DIR / f"{ticker_normalized}_{year}_ai_annotation.json",
        ANNOTATED_CN_DIR / f"{ticker_normalized}_{year}_annotation.json",
        ANNOTATED_CN_DIR / f"SH{ticker_normalized}_{year}_annotation.json",
        ANNOTATED_CN_DIR / f"SZ{ticker_normalized}_{year}_annotation.json",
    ]
    for p in patterns:
        if p.exists():
            return True
    return False


def run_annotation(company_name: str, stock_code: str, year: int, client: DeepSeekClient) -> dict:
    print(f"\n{'='*60}")
    print(f"Processing: {company_name} ({stock_code}) FY{year}")
    print(f"{'='*60}")

    pdf_path = find_pdf(company_name, year)
    print(f"[1/6] Reading PDF: {pdf_path.name}")
    full_text = extract_text(pdf_path)
    print(f"       Extracted {len(full_text):,} characters")

    print(f"[2/6] Locating candidates...")
    candidates = locate_cn_candidates(full_text, max_candidates=30)
    print(f"       Found {len(candidates)} candidates")
    if not candidates:
        print("       WARNING: No candidates found!")
        return None

    print(f"[3/6] Calling DeepSeek AI...")
    company_meta = {"ticker": stock_code, "fiscal_year": year, "industry": "Technology"}
    ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="cn")
    n_signals = len(ai_raw.get("risk_signals", []))
    n_dims = len(ai_raw.get("dimension_scores", []))
    print(f"       Generated {n_signals} signals, {n_dims} dimensions")

    print(f"[4/6] Running verification...")
    signals = ai_raw.get("risk_signals", [])
    passed = 0
    failed = 0
    verif_results = []
    for sig in signals:
        excerpt = sig.get("text_excerpt", "")
        sig_id = sig.get("signal_id", "UNKNOWN")
        is_noise = False
        noise_reason = ""
        if ("公司概况" in excerpt or "公司简介" in excerpt or "公司基本情况" in excerpt) and \
           not any(k in excerpt for k in ["折旧", "摊销", "减值", "固定资产", "使用寿命"]):
            is_noise = True
            noise_reason = "公司概况章节误匹配"
        if ("前瞻性" in excerpt or "风险提示" in excerpt or "免责声明" in excerpt) and \
           not any(k in excerpt for k in ["折旧", "摊销", "减值", "固定资产"]):
            is_noise = True
            noise_reason = "前瞻性声明/风险提示泛泛提及"
        if ("管理层讨论" in excerpt or "经营情况讨论" in excerpt) and \
           not any(k in excerpt for k in ["折旧年限", "使用寿命", "预计使用年限", "折旧方法", "固定资产"]):
            is_noise = True
            noise_reason = "管理层讨论中顺带提及"
        if excerpt and excerpt[:30] in full_text and not is_noise:
            passed += 1
            verif_results.append({"signal_id": sig_id, "passed": True, "method": "substring", "confidence": 1.0})
        elif is_noise:
            failed += 1
            verif_results.append({"signal_id": sig_id, "passed": False, "method": "noise_excluded", "confidence": 0.0, "reason": noise_reason})
        else:
            failed += 1
            verif_results.append({"signal_id": sig_id, "passed": False, "method": "substring", "confidence": 0.0})
    total = len(signals)
    verification = {
        "passed": passed,
        "failed": failed,
        "total": total,
        "pass_rate": passed / total if total > 0 else 0,
        "results": verif_results,
        "failed_signals": [s for s, v in zip(signals, verif_results) if not v["passed"]],
    }
    print(f"       Verification: {passed}/{total} passed ({verification['pass_rate']*100:.0f}%)")

    print(f"[4.5/6] Running rule engine...")
    dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
    composite_before = compute_composite_score(dim_scores_before)
    dim_scores, rules_triggered, rule_warnings = apply_hard_rules(dim_scores_before, candidates, ai_raw, full_html=full_text)
    composite = compute_composite_score(dim_scores)
    print(f"       AI raw score: {composite_before['weighted_score']:.2f}")
    print(f"       After rules:  {composite['weighted_score']:.2f}")

    print(f"[5/6] Saving annotation...")
    ticker_normalized = stock_code.replace(".", "")
    output = {
        "metadata": {
            "version": "1.0",
            "annotation_schema": "Depreciation Risk Annotation Schema v1.0",
            "annotated_at": __import__("datetime").datetime.now().isoformat(),
            "annotator": "DeepSeek AI + Program Verification (Batch All Years)",
            "review_status": "confirmed",
            "filing_source": "巨潮资讯网 (Manual Download)",
            "ai_annotation": True,
        },
        "company": {"ticker": ticker_normalized, "name": company_name, "fiscal_year": year},
        "composite_score": composite,
        "dimension_scores": dim_scores,
        "risk_signals": ai_raw.get("risk_signals", []),
        "accounting_policy": ai_raw.get("accounting_policy", {}),
        "summary": ai_raw.get("summary", ""),
    }
    out_path = ANNOTATED_CN_DIR / f"{ticker_normalized}_{year}_ai_annotation.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"       Saved to: {out_path}")

    print(f"[6/6] DONE: {company_name} FY{year}")
    print(f"       Score: {composite['weighted_score']:.2f} ({composite['risk_level']})")
    return output


def main():
    # Check DeepSeek API first
    print("Checking DeepSeek API...")
    try:
        client = DeepSeekClient()
        if not client.health_check():
            print("ERROR: DeepSeek API not available!")
            return
        print("DeepSeek API OK.\n")
    except Exception as e:
        print(f"ERROR: {e}")
        return

    total = len(COMPANIES) * len(YEARS)
    processed = 0
    skipped = 0
    errors = []
    results = []

    for company_name, stock_code in COMPANIES.items():
        for year in YEARS:
            processed += 1
            print(f"\n[{processed}/{total}] {company_name} FY{year}")

            # Skip if already exists
            if annotation_exists(company_name, stock_code, year):
                print(f"       SKIPPED: Annotation already exists for {company_name} FY{year}")
                skipped += 1
                continue

            try:
                result = run_annotation(company_name, stock_code, year, client)
                if result:
                    results.append((company_name, year, result))
            except Exception as e:
                print(f"       ERROR: {e}")
                errors.append((company_name, year, str(e)))

    # Summary
    print(f"\n{'='*60}")
    print("BATCH ANNOTATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total tasks: {total}")
    print(f"Skipped (already exist): {skipped}")
    print(f"Successful: {len(results)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for name, year, err in errors:
            print(f"  - {name} FY{year}: {err}")

    print("\nResults:")
    for name, year, result in results:
        comp = result["composite_score"]
        print(f"  - {name} FY{year}: {comp['weighted_score']:.2f} ({comp['risk_level']})")

    # Save summary
    summary_path = ANNOTATED_CN_DIR / "_batch_summary_all_years.json"
    summary = {
        "companies": list(COMPANIES.keys()),
        "years": YEARS,
        "total_tasks": total,
        "skipped": skipped,
        "successful": len(results),
        "errors": [{"company": name, "year": year, "error": err} for name, year, err in errors],
        "results": {f"{name}_{year}": {"score": r["composite_score"]["weighted_score"], "level": r["composite_score"]["risk_level"]} for name, year, r in results},
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
