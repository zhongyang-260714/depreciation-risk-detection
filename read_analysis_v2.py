#!/usr/bin/env python3
"""读取分析结果JSON，详细查看问题（修复版）"""
import json
from pathlib import Path

REPO_ROOT = Path("D:/depreciation-risk-detection")

def load_analysis(ticker, fy):
    path = REPO_ROOT / "data" / f"analysis_{ticker}_FY{fy}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 分析MSFT
print("="*70)
print("MSFT 详细分析")
print("="*70)
msft = load_analysis("MSFT", 2025)

print(f"\n候选段落样本 (前5个):")
for i, c in enumerate(msft["candidates"][:5]):
    text = c['text'][:400] if c['text'] else "[EMPTY]"
    print(f"\n  [{i+1}] tier={c['tier']}, score={c.get('score', 'N/A')}")
    print(f"  text: {text}")

print(f"\nAI维度评分详情:")
for d in msft["ai_raw"]["dimension_scores"]:
    print(f"\n  {d['dimension_id']}: score={d.get('score', 'N/A')}")
    print(f"    reasoning: {d.get('reasoning', 'N/A')[:300]}")
    print(f"    insufficient_evidence: {d.get('insufficient_evidence', False)}")

# 分析NVDA
print("\n" + "="*70)
print("NVDA 详细分析")
print("="*70)
nvda = load_analysis("NVDA", 2025)

print(f"\n候选段落样本 (前5个):")
for i, c in enumerate(nvda["candidates"][:5]):
    text = c['text'][:400] if c['text'] else "[EMPTY]"
    print(f"\n  [{i+1}] tier={c['tier']}, score={c.get('score', 'N/A')}")
    print(f"  text: {text}")

print(f"\nAI维度评分详情:")
for d in nvda["ai_raw"]["dimension_scores"]:
    print(f"\n  {d['dimension_id']}: score={d.get('score', 'N/A')}")
    print(f"    reasoning: {d.get('reasoning', 'N/A')[:300]}")
    print(f"    insufficient_evidence: {d.get('insufficient_evidence', False)}")

print(f"\n验真结果:")
print(f"  MSFT: {msft['verification'].get('passed', 'N/A')}/{msft['verification'].get('total', 'N/A')} 通过")
print(f"  NVDA: {nvda['verification'].get('passed', 'N/A')}/{nvda['verification'].get('total', 'N/A')} 通过")
