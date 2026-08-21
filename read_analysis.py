#!/usr/bin/env python3
"""读取分析结果JSON，详细查看问题"""
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

print(f"\n候选段落样本 (前3个):")
for i, c in enumerate(msft["candidates"][:3]):
    print(f"\n  [{i+1}] tier={c['tier']}, score={c['score']}")
    print(f"  text: {c['text'][:300]}...")

print(f"\nAI信号详情:")
for i, sig in enumerate(msft["ai_raw"]["risk_signals"][:3]):
    print(f"\n  信号{i+1}:")
    for k, v in sig.items():
        if isinstance(v, str):
            print(f"    {k}: {v[:200]}")
        else:
            print(f"    {k}: {v}")

print(f"\n维度评分详情:")
for d in msft["ai_raw"]["dimension_scores"]:
    print(f"  {d}")

print(f"\n验真详情:")
for check in msft["verification"]["checks"]:
    print(f"  {'✅' if check['passed'] else '❌'} {check['check_name']}: {check['message']}")

# 分析NVDA
print("\n" + "="*70)
print("NVDA 详细分析")
print("="*70)
nvda = load_analysis("NVDA", 2025)

print(f"\n候选段落样本 (前3个):")
for i, c in enumerate(nvda["candidates"][:3]):
    print(f"\n  [{i+1}] tier={c['tier']}, score={c['score']}")
    print(f"  text: {c['text'][:300]}...")

print(f"\nAI信号详情:")
for i, sig in enumerate(nvda["ai_raw"]["risk_signals"][:3]):
    print(f"\n  信号{i+1}:")
    for k, v in sig.items():
        if isinstance(v, str):
            print(f"    {k}: {v[:200]}")
        else:
            print(f"    {k}: {v}")

print(f"\n维度评分详情:")
for d in nvda["ai_raw"]["dimension_scores"]:
    print(f"  {d}")

print(f"\n验真详情:")
for check in nvda["verification"]["checks"]:
    print(f"  {'✅' if check['passed'] else '❌'} {check['check_name']}: {check['message']}")
