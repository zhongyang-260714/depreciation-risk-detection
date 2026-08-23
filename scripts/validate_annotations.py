# -*- coding: utf-8 -*-
"""标注库质量校验：A股 30 份 + 美股 30 份
检查项：
1. 结构完整性（metadata/company/composite_score/dimension_scores/risk_signals）
2. 维度分范围 1-5、权重和≈1、综合分 = Σ(维度分×权重) 复算一致
3. 证据链四要素齐全（原文/位置/会计含义/推断链）
4. review_status 有效性
5. 看板加载结果（load_cases）与公司去重检查
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EXPECTED_WEIGHTS_SUM_TOL = 0.01


def validate_file(path: Path) -> list[str]:
    issues = []
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JSON 解析失败: {e}"]

    for key in ("metadata", "company", "composite_score", "dimension_scores"):
        if key not in d:
            issues.append(f"缺少字段 {key}")
    if issues:
        return issues

    status = d["metadata"].get("review_status", "?")
    if status != "confirmed":
        issues.append(f"review_status={status}（非 confirmed）")

    dims = d.get("dimension_scores") or []
    if len(dims) != 5:
        issues.append(f"维度数={len(dims)}（应为 5）")
    wsum, calc = 0.0, 0.0
    for dim in dims:
        s = dim.get("score")
        w = dim.get("weight")
        if s is None or not (1 <= float(s) <= 5):
            issues.append(f"{dim.get('dimension_id', '?')} 分数越界: {s}")
        if w is None:
            issues.append(f"{dim.get('dimension_id', '?')} 缺权重")
            continue
        wsum += float(w)
        calc += float(s or 0) * float(w)
        if not dim.get("reasoning"):
            issues.append(f"{dim.get('dimension_id', '?')} 缺评分理由")
    if abs(wsum - 1.0) > EXPECTED_WEIGHTS_SUM_TOL:
        issues.append(f"权重和={wsum:.3f}（≠1）")

    comp = d.get("composite_score") or {}
    official = comp.get("weighted_score")
    if official is None:
        issues.append("缺 composite_score.weighted_score")
    elif abs(calc - float(official)) > 0.05:
        issues.append(f"综合分复算不符: Σ={calc:.2f} vs 记录={official}")

    signals = d.get("risk_signals") or []
    if not signals:
        issues.append("无风险信号")
    for i, sig in enumerate(signals):
        quote = sig.get("text_excerpt")
        loc = sig.get("page_location") or sig.get("source")
        meaning = sig.get("accounting_meaning") or sig.get("relevance_to_depreciation")
        infer = sig.get("evidence_chain") or sig.get("inference_chain")
        missing = [n for n, v in (("原文", quote), ("位置", loc), ("会计含义", meaning), ("推断链", infer)) if not v]
        if missing:
            issues.append(f"信号{i+1}({sig.get('signal_id','?')}) 证据链缺: {'/'.join(missing)}")
    return issues


def main():
    total_bad = 0
    for sub, expect in (("annotated", 30), ("annotated_cn", 30)):
        files = sorted(p for p in (ROOT / "data" / sub).glob("*_annotation.json")
                       if not p.name.startswith("_"))
        # 只统计正式命名（ai_annotation 或美股标准命名），旧格式单独列出
        if sub == "annotated_cn":
            formal = [p for p in files if p.stem.endswith("_ai_annotation")]
            legacy = [p for p in files if not p.stem.endswith("_ai_annotation")]
        else:
            formal, legacy = files, []
        print(f"\n=== data/{sub}: 正式标注 {len(formal)} 份（预期 {expect}），旧格式 {len(legacy)} 份 ===")
        for p in legacy:
            print(f"  [旧格式] {p.name}")
        for p in formal:
            issues = validate_file(p)
            if issues:
                total_bad += 1
                print(f"  [问题] {p.name}")
                for it in issues:
                    print(f"         - {it}")
        print(f"  → {len(formal) - sum(1 for p in formal if validate_file(p))}/{len(formal)} 通过全部检查")

    # 看板加载视角
    print("\n=== 看板 load_cases() 实际加载结果 ===")
    from src.dashboard.data_loader import load_cases
    cases = load_cases()
    seen = {}
    for c in cases:
        key = (c["ticker"], c["fiscal_year"])
        seen.setdefault(key, []).append(c.get("source_file", "?"))
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    print(f"加载案例总数: {len(cases)}，唯一公司-年份: {len(seen)}")
    tickers = sorted({c['ticker'] for c in cases})
    print(f"公司清单({len(tickers)}): {', '.join(tickers)}")
    if dups:
        print(f"⚠ 重复键: {dups}")
    print(f"\n校验结束，{total_bad} 份文件存在问题。" if total_bad else "\n全部通过 ✅")


if __name__ == "__main__":
    main()
