#!/usr/bin/env python
"""
批量重跑16家公司（10家美股+6家A股）的AI标注+规则引擎修正
生成对比报告：AI原始分 vs 规则修正后 vs 人工确认分

运行方式：
    cd depreciation-risk-detection
    python scripts/batch_verify_16companies.py

注意：
- 美股10家需要SEC EDGAR下载，每份约10-30秒
- A股6家需要巨潮下载，每份约10-30秒
- DeepSeek API调用每份约30-60秒
- 总预计时间：16家 × 1-2分钟 = 20-30分钟
"""

import sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_annotation import (
    DeepSeekClient,
    apply_hard_rules,
    compute_composite_score,
    enrich_dimension_scores,
    fetch_annual_report,
    load_10k_html,
    locate_candidates_batch,
    locate_cn_candidates,
    verify_all,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "data" / "batch_verify_v3"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 16家公司清单
# ============================================================

US_COMPANIES = [
    {"ticker": "META", "fy": 2023, "name": "Meta"},
    {"ticker": "META", "fy": 2022, "name": "Meta"},  # 变更年
    {"ticker": "META", "fy": 2024, "name": "Meta"},  # 再次延长披露
    {"ticker": "GOOGL", "fy": 2023, "name": "Alphabet"},
    {"ticker": "MSFT", "fy": 2023, "name": "Microsoft"},
    {"ticker": "INTC", "fy": 2023, "name": "Intel"},
    {"ticker": "NVDA", "fy": 2024, "name": "NVIDIA"},
    {"ticker": "ORCL", "fy": 2024, "name": "Oracle"},
    {"ticker": "ORCL", "fy": 2025, "name": "Oracle"},  # 连续延长
    {"ticker": "MU", "fy": 2023, "name": "Micron"},
    {"ticker": "TSLA", "fy": 2024, "name": "Tesla"},
    {"ticker": "AMD", "fy": 2024, "name": "AMD"},
    {"ticker": "CRM", "fy": 2023, "name": "Salesforce"},
]

# 注意：报告6.1说的是10家公司×3财年=30个观测
# 上面列出了13个，如果需要完整的30个，需要补充所有公司所有年份
# 为验证修复效果，先跑关键观测（变更年+AMD）

CN_COMPANIES = [
    {"code": "002230.SZ", "year": 2024, "name": "科大讯飞"},
    {"code": "688256.SH", "year": 2024, "name": "寒武纪"},
    {"code": "603881.SH", "year": 2024, "name": "数据港"},
    {"code": "000977.SZ", "year": 2024, "name": "浪潮信息"},
    {"code": "603019.SH", "year": 2024, "name": "中科曙光"},
    {"code": "300738.SZ", "year": 2024, "name": "奥飞数据"},
]


def run_us_company(client, ticker, fy):
    """跑一家美股公司。"""
    print(f"\n{'='*60}")
    print(f"[US] {ticker} FY{fy}")
    print(f"{'='*60}")
    try:
        # 下载10-K
        html_text = load_10k_html(ticker, fy, cache_dir=CACHE_DIR)
        print(f"  下载完成: {len(html_text):,} 字符")

        # 关键词定位
        candidates = locate_candidates_batch(html_text, max_candidates=50)
        print(f"  候选段落: {len(candidates)} 个")
        if not candidates:
            print("  ⚠️ 无候选段落，跳过")
            return None

        # DeepSeek草拟
        company_meta = {"ticker": ticker, "fiscal_year": fy, "industry": "Technology"}
        ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="en")
        print(f"  AI信号: {len(ai_raw.get('risk_signals', []))} 条")

        # 程序验真
        verification = verify_all(ai_raw, html_text)
        print(f"  验真: {verification['passed']}/{verification['total']}")

        # 规则引擎v3
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        dim_scores, rules_triggered, rule_warnings = apply_hard_rules(
            dim_scores_before, candidates, ai_raw, full_html=html_text
        )
        composite = compute_composite_score(dim_scores)

        print(f"  AI原始分: {composite_before['weighted_score']:.2f} ({composite_before['risk_level']})")
        print(f"  规则修正后: {composite['weighted_score']:.2f} ({composite['risk_level']})")
        if rules_triggered:
            for r in rules_triggered:
                print(f"    🎯 {r}")
        if rule_warnings:
            for w in rule_warnings:
                print(f"    ⚠️ {w}")

        return {
            "ticker": ticker,
            "fy": fy,
            "ai_raw_score": composite_before["weighted_score"],
            "ai_raw_level": composite_before["risk_level"],
            "final_score": composite["weighted_score"],
            "final_level": composite["risk_level"],
            "rules_triggered": rules_triggered,
            "rule_warnings": rule_warnings,
            "dim_scores": dim_scores,
            "verification": verification,
        }
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None


def run_cn_company(client, code, year):
    """跑一家A股公司。"""
    print(f"\n{'='*60}")
    print(f"[CN] {code} {year}")
    print(f"{'='*60}")
    try:
        import pdfplumber

        # 下载PDF
        pdf_path, company_name = fetch_annual_report(code, year, cache_dir=CACHE_DIR / "cn")
        pdf_bytes = pdf_path.read_bytes()
        print(f"  下载完成: {company_name}")

        # 提取文本
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += f"\n--- 第{i+1}页 ---\n{text}\n"
        print(f"  文本: {len(full_text):,} 字符")

        # 中文关键词定位
        candidates = locate_cn_candidates(full_text, max_candidates=50)
        print(f"  候选段落: {len(candidates)} 个")
        if not candidates:
            print("  ⚠️ 无候选段落，跳过")
            return None

        # DeepSeek中文草拟
        company_meta = {"ticker": code, "fiscal_year": year, "industry": "Technology"}
        ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="cn")
        print(f"  AI信号: {len(ai_raw.get('risk_signals', []))} 条")

        # 规则引擎v3
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        dim_scores, rules_triggered, rule_warnings = apply_hard_rules(
            dim_scores_before, candidates, ai_raw, full_html=full_text
        )
        composite = compute_composite_score(dim_scores)

        print(f"  AI原始分: {composite_before['weighted_score']:.2f} ({composite_before['risk_level']})")
        print(f"  规则修正后: {composite['weighted_score']:.2f} ({composite['risk_level']})")
        if rules_triggered:
            for r in rules_triggered:
                print(f"    🎯 {r}")
        if rule_warnings:
            for w in rule_warnings:
                print(f"    ⚠️ {w}")

        return {
            "code": code,
            "year": year,
            "ai_raw_score": composite_before["weighted_score"],
            "ai_raw_level": composite_before["risk_level"],
            "final_score": composite["weighted_score"],
            "final_level": composite["risk_level"],
            "rules_triggered": rules_triggered,
            "rule_warnings": rule_warnings,
            "dim_scores": dim_scores,
        }
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return None


def main():
    client = DeepSeekClient()
    if not client.health_check():
        print("DeepSeek API 不可用，请检查 DEEPSEEK_API_KEY")
        return

    results = []

    # 跑美股关键公司
    print("\n" + "="*60)
    print("开始批量验证：美股关键观测")
    print("="*60)
    for c in US_COMPANIES:
        r = run_us_company(client, c["ticker"], c["fy"])
        if r:
            results.append(r)
            # 保存单个结果
            out_path = OUT_DIR / f"{c['ticker']}_{c['fy']}_v3.json"
            out_path.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(2)  # 避免API限流

    # 跑A股6家
    print("\n" + "="*60)
    print("开始批量验证：A股六家样本")
    print("="*60)
    for c in CN_COMPANIES:
        r = run_cn_company(client, c["code"], c["year"])
        if r:
            results.append(r)
            out_path = OUT_DIR / f"{c['code'].replace('.', '_')}_{c['year']}_v3.json"
            out_path.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
        time.sleep(2)

    # 生成汇总报告
    report_path = OUT_DIR / "batch_report_v3.json"
    report_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # 打印汇总表
    print("\n" + "="*60)
    print("批量验证完成！汇总表：")
    print("="*60)
    print(f"{'公司':<15} {'AI原始分':>8} {'规则修正后':>10} {'规则触发':>8}")
    print("-" * 45)
    for r in results:
        name = r.get("ticker", r.get("code", "?"))
        rules = len(r.get("rules_triggered", []))
        print(f"{name:<15} {r['ai_raw_score']:>8.2f} {r['final_score']:>10.2f} {rules:>8}")

    print(f"\n详细结果保存在: {OUT_DIR}")


if __name__ == "__main__":
    main()
