#!/usr/bin/env python3
"""验证脚本：运行5家公司的AI标注并与人工评分对比

使用方法：
1. 如果已有 .env 文件：直接运行 python run_validation.py
2. 如果没有 .env 文件：运行 python setup_api_key.py 先配置
"""

import sys
import json
import os
from pathlib import Path

REPO_ROOT = Path("D:/depreciation-risk-detection")
CACHE_DIR = REPO_ROOT / "data" / "raw"

sys.path.insert(0, str(REPO_ROOT))

from src.ai_annotation import (
    DeepSeekClient,
    apply_hard_rules,
    compute_composite_score,
    enrich_dimension_scores,
    load_10k_html,
    locate_candidates_batch,
    verify_all,
)

# 5家公司的配置 + 人工评分基准
COMPANIES = [
    {
        "ticker": "META", "fiscal_year": 2024, "name": "Meta Platforms",
        "human": {"D1": 5, "D2": 5, "D3": 3, "D4": 5, "D5": 5, "composite": 4.60}
    },
    {
        "ticker": "MSFT", "fiscal_year": 2025, "name": "Microsoft",
        "human": {"D1": 5, "D2": 4, "D3": 3, "D4": 5, "D5": 5, "composite": 4.40}
    },
    {
        "ticker": "MU", "fiscal_year": 2024, "name": "Micron Technology",
        "human": {"D1": 4, "D2": 3, "D3": 4, "D4": 5, "D5": 4, "composite": 4.00}
    },
    {
        "ticker": "NVDA", "fiscal_year": 2025, "name": "NVIDIA",
        "human": {"D1": 4, "D2": 4, "D3": 4, "D4": 2, "D5": 3, "composite": 3.45}
    },
    {
        "ticker": "ORCL", "fiscal_year": 2025, "name": "Oracle",
        "human": {"D1": 5, "D2": 5, "D3": 3, "D4": 5, "D5": 4, "composite": 4.45}
    },
]


def run_ai_annotation(ticker, fiscal_year, name, human_scores):
    """运行完整的AI标注流程并与人工评分对比"""
    print(f"\n{'='*70}")
    print(f"验证: {name} ({ticker}) FY{fiscal_year}")
    print(f"人工评分: D1={human_scores['D1']} D2={human_scores['D2']} D3={human_scores['D3']} D4={human_scores['D4']} D5={human_scores['D5']} 综合={human_scores['composite']}")
    print(f"{'='*70}")
    
    try:
        # 1. 下载/加载 10-K
        print(f"[1/6] 加载 10-K HTML...")
        html_text = load_10k_html(ticker, fiscal_year, cache_dir=CACHE_DIR)
        print(f"      文本长度: {len(html_text):,} 字符")
        
        # 2. 关键词定位（v6.2优化版）
        print(f"[2/6] 关键词定位（v6.2五级检索体系）...")
        candidates = locate_candidates_batch(html_text, max_candidates=80)
        print(f"      候选段落: {len(candidates)} 个")
        
        # 统计各级别
        core = sum(1 for c in candidates if c.get('keyword_tier') == 'core')
        extended = sum(1 for c in candidates if c.get('keyword_tier') == 'extended')
        regex = sum(1 for c in candidates if c.get('keyword_tier') == 'regex')
        must_include = sum(1 for c in candidates if c.get('keyword_tier') == 'must_include')
        print(f"      分布: core={core}, extended={extended}, regex={regex}, must_include={must_include}")
        
        if not candidates:
            print("      警告: 无候选段落，跳过")
            return None
        
        # 3. DeepSeek 草拟（v6.2增强prompt）
        print(f"[3/6] DeepSeek AI 草拟（v6.2增强锚点prompt）...")
        client = DeepSeekClient()
        company_meta = {
            "ticker": ticker,
            "fiscal_year": fiscal_year,
            "industry": "Technology"
        }
        ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="en")
        n_signals = len(ai_raw.get("risk_signals", []))
        n_dims = len(ai_raw.get("dimension_scores", []))
        print(f"      AI 生成 {n_signals} 条信号，{n_dims} 个维度评分")
        
        # 4. 程序验真
        print(f"[4/6] 程序验真...")
        verification = verify_all(ai_raw, html_text)
        print(f"      通过率: {verification['pass_rate']*100:.0f}% ({verification['passed']}/{verification['total']})")
        
        # 5. 规则引擎（v6.2优化）
        print(f"[5/6] 规则引擎修正（v6.2取上限+多次延长检测）...")
        dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
        composite_before = compute_composite_score(dim_scores_before)
        print(f"      AI 原始分: {composite_before['weighted_score']:.2f}")
        
        dim_scores, rules_triggered, rule_warnings = apply_hard_rules(
            dim_scores_before, candidates, ai_raw, full_html=html_text
        )
        composite = compute_composite_score(dim_scores)
        print(f"      规则修正后: {composite['weighted_score']:.2f}")
        if rules_triggered:
            for rule in rules_triggered:
                print(f"      • {rule}")
        
        # 6. 与人工评分对比
        print(f"[6/6] 对比人工评分...")
        ai_dims = {d.get("dimension_id", ""): d.get("score", 0) for d in dim_scores}
        
        comparison = []
        for dim_id in ["D1", "D2", "D3", "D4", "D5"]:
            ai_score = ai_dims.get(dim_id, 0)
            human_score = human_scores.get(dim_id, 0)
            diff = ai_score - human_score
            comparison.append({
                "dim": dim_id,
                "ai": ai_score,
                "human": human_score,
                "diff": diff,
                "match": "✅" if abs(diff) <= 0.5 else "❌"
            })
        
        print(f"\n{'维度':<6} {'AI评分':<8} {'人工评分':<10} {'差值':<8} {'匹配':<6}")
        print("-" * 40)
        for c in comparison:
            print(f"{c['dim']:<6} {c['ai']:<8} {c['human']:<10} {c['diff']:+0.1f}      {c['match']:<6}")
        
        ai_composite = composite['weighted_score']
        human_composite = human_scores['composite']
        composite_diff = ai_composite - human_composite
        
        print(f"\n{'综合分':<6} {ai_composite:<8.2f} {human_composite:<10.2f} {composite_diff:+.2f}      {'✅' if abs(composite_diff) <= 0.5 else '❌'}")
        
        return {
            "ticker": ticker,
            "fiscal_year": fiscal_year,
            "ai_composite": ai_composite,
            "human_composite": human_composite,
            "composite_diff": composite_diff,
            "dimension_comparison": comparison,
            "n_candidates": len(candidates),
            "n_signals": n_signals,
            "verification_pass_rate": verification['pass_rate'],
            "rules_triggered": rules_triggered,
        }
        
    except Exception as e:
        print(f"      错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 70)
    print("v6.2 AI标注验证：5家公司AI评分 vs 人工评分对比")
    print("=" * 70)
    
    # 检查API key
    try:
        client = DeepSeekClient()
        if client.health_check():
            print("✅ DeepSeek API 连接正常")
        else:
            print("⚠️ DeepSeek API 连接测试失败，将继续尝试...")
    except ValueError as e:
        print(f"❌ {e}")
        print()
        print("请先配置API Key:")
        print("  方法1: 运行 python setup_api_key.py")
        print("  方法2: 设置环境变量 DEEPSEEK_API_KEY=your_key")
        print("  方法3: 在 D:/depreciation-risk-detection/.env 文件中写入 DEEPSEEK_API_KEY=your_key")
        return
    except Exception as e:
        print(f"❌ API 连接错误: {e}")
        return
    
    results = []
    for company in COMPANIES:
        result = run_ai_annotation(
            company["ticker"],
            company["fiscal_year"],
            company["name"],
            company["human"]
        )
        if result:
            results.append(result)
    
    # 汇总
    print(f"\n{'='*70}")
    print("验证汇总")
    print(f"{'='*70}")
    print(f"{'公司':<8} {'AI综合分':<10} {'人工综合分':<12} {'差值':<8} {'结果':<6}")
    print("-" * 50)
    for r in results:
        match = "✅通过" if abs(r['composite_diff']) <= 0.5 else "❌偏差"
        print(f"{r['ticker']:<8} {r['ai_composite']:<10.2f} {r['human_composite']:<12.2f} {r['composite_diff']:+.2f}    {match:<6}")
    
    # 保存结果
    output_path = REPO_ROOT / "data" / "validation_v62_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n详细结果已保存: {output_path}")


if __name__ == "__main__":
    main()
