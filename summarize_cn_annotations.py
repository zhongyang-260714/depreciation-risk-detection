#!/usr/bin/env python3
"""整理所有A股标注数据为汇总表。"""

import json
import csv
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent
ANNOTATED_CN_DIR = REPO_ROOT / "data" / "annotated_cn"
OUTPUT_CSV = REPO_ROOT / "data" / "annotated_cn_summary.csv"

# Company mapping
COMPANIES = {
    "603019SH": "中科曙光",
    "603881SH": "数据港",
    "688256SH": "寒武纪",
    "000977SZ": "浪潮信息",
    "002230SZ": "科大讯飞",
    "300738SZ": "奥飞数据",
    "300383SZ": "光环新网",
    "688041SH": "海光信息",
    "601138SH": "工业富联",
    "300442SZ": "润泽科技",
}

YEARS = [2022, 2023, 2024]


def load_annotation(ticker: str, year: int):
    """Load annotation JSON for a ticker and year."""
    paths = [
        ANNOTATED_CN_DIR / f"{ticker}_{year}_ai_annotation.json",
        ANNOTATED_CN_DIR / f"SH{ticker}_{year}_annotation.json",
        ANNOTATED_CN_DIR / f"SZ{ticker}_{year}_annotation.json",
    ]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                comp = data.get("composite_score", {})
                dims = data.get("dimension_scores", [])
                signals = data.get("risk_signals", [])
                return {
                    "score": comp.get("weighted_score", 0),
                    "level": comp.get("risk_level", ""),
                    "confidence": comp.get("confidence", ""),
                    "n_signals": len(signals),
                    "d1_score": next((d.get("score", 0) for d in dims if d.get("dimension_id") == "D1" or d.get("id") == "D1"), 0),
                    "d2_score": next((d.get("score", 0) for d in dims if d.get("dimension_id") == "D2" or d.get("id") == "D2"), 0),
                    "d3_score": next((d.get("score", 0) for d in dims if d.get("dimension_id") == "D3" or d.get("id") == "D3"), 0),
                    "d4_score": next((d.get("score", 0) for d in dims if d.get("dimension_id") == "D4" or d.get("id") == "D4"), 0),
                    "d5_score": next((d.get("score", 0) for d in dims if d.get("dimension_id") == "D5" or d.get("id") == "D5"), 0),
                }
            except Exception:
                pass
    return None


def main():
    rows = []
    for ticker, name in COMPANIES.items():
        for year in YEARS:
            ann = load_annotation(ticker, year)
            if ann:
                rows.append({
                    "公司": name,
                    "代码": ticker,
                    "财年": year,
                    "综合得分": ann["score"],
                    "风险等级": ann["level"],
                    "信号数": ann["n_signals"],
                    "D1年限": ann["d1_score"],
                    "D2变更": ann["d2_score"],
                    "D3减值": ann["d3_score"],
                    "D4资本": ann["d4_score"],
                    "D5行业": ann["d5_score"],
                })

    # Write CSV
    if rows:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Summary saved to: {OUTPUT_CSV}")
        print(f"   Total records: {len(rows)}")

        # Print table
        print("\n" + "="*100)
        print(f"{'公司':<8} {'代码':<10} {'财年':<6} {'得分':<6} {'等级':<8} {'信号':<4} {'D1':<4} {'D2':<4} {'D3':<4} {'D4':<4} {'D5':<4}")
        print("="*100)
        for r in rows:
            print(f"{r['公司']:<8} {r['代码']:<10} {r['财年']:<6} {r['综合得分']:<6.2f} {r['风险等级']:<8} {r['信号数']:<4} {r['D1年限']:<4.1f} {r['D2变更']:<4.1f} {r['D3减值']:<4.1f} {r['D4资本']:<4.1f} {r['D5行业']:<4.1f}")
        print("="*100)
    else:
        print("No annotations found!")


if __name__ == "__main__":
    main()
