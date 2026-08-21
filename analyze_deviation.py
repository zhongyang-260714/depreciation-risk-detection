#!/usr/bin/env python3
"""分析MSFT和NVDA的AI信号，找出偏差原因"""
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

def analyze_company(ticker, fiscal_year, name):
    print(f"\n{'='*70}")
    print(f"深度分析: {name} ({ticker}) FY{fiscal_year}")
    print(f"{'='*70}")
    
    # 1. 加载HTML
    html_text = load_10k_html(ticker, fiscal_year, cache_dir=CACHE_DIR)
    print(f"文本长度: {len(html_text):,} 字符")
    
    # 2. 关键词定位
    candidates = locate_candidates_batch(html_text, max_candidates=80)
    print(f"候选段落: {len(candidates)} 个")
    
    # 打印前10个候选段落的关键信息
    print(f"\n前10个候选段落:")
    for i, c in enumerate(candidates[:10]):
        text_preview = c.get('text', '')[:100].replace('\n', ' ')
        print(f"  [{i+1}] tier={c.get('keyword_tier','?')} score={c.get('score',0):.1f} | {text_preview}...")
    
    # 3. DeepSeek AI草拟
    client = DeepSeekClient()
    company_meta = {"ticker": ticker, "fiscal_year": fiscal_year, "industry": "Technology"}
    ai_raw = client.annotate(candidates, company_meta, temperature=0.2, language="en")
    
    # 4. 打印AI生成的信号
    print(f"\nAI生成的风险信号 ({len(ai_raw.get('risk_signals', []))}条):")
    for i, signal in enumerate(ai_raw.get('risk_signals', [])):
        print(f"\n  信号{i+1}:")
        print(f"    维度: {signal.get('dimension', '?')}")
        print(f"    风险: {signal.get('risk_type', '?')}")
        print(f"    证据: {signal.get('evidence', '?')[:150]}...")
        print(f"    引用: {signal.get('source_ref', '?')}")
        print(f"    严重度: {signal.get('severity', '?')}")
    
    # 5. 打印AI维度评分
    print(f"\nAI维度评分:")
    for d in ai_raw.get("dimension_scores", []):
        print(f"  {d.get('dimension_id','?')}: {d.get('score',0)} - {d.get('justification','')[:100]}...")
    
    # 6. 程序验真
    verification = verify_all(ai_raw, html_text)
    print(f"\n程序验真: {verification['passed']}/{verification['total']} 通过")
    for check in verification.get("checks", []):
        status = "✅" if check.get("passed") else "❌"
        print(f"  {status} {check.get('check_name','?')}: {check.get('message','')}")
    
    # 7. 规则引擎
    dim_scores_before = enrich_dimension_scores(ai_raw.get("dimension_scores", []))
    dim_scores, rules_triggered, rule_warnings = apply_hard_rules(
        dim_scores_before, candidates, ai_raw, full_html=html_text
    )
    
    print(f"\n规则引擎触发: {len(rules_triggered)}条")
    for rule in rules_triggered:
        print(f"  • {rule}")
    
    # 保存完整结果以便分析
    output = {
        "ticker": ticker,
        "fiscal_year": fiscal_year,
        "candidates": [{"tier": c.get("keyword_tier"), "score": c.get("score"), 
                        "text": c.get("text", "")[:200]} for c in candidates[:20]],
        "ai_raw": ai_raw,
        "verification": verification,
        "rules_triggered": rules_triggered,
    }
    
    out_path = REPO_ROOT / "data" / f"analysis_{ticker}_FY{fiscal_year}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n详细分析已保存: {out_path}")

# 分析MSFT和NVDA
analyze_company("MSFT", 2025, "Microsoft")
analyze_company("NVDA", 2025, "NVIDIA")
