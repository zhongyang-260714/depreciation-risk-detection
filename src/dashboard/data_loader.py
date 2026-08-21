"""T7 交互看板 · 数据加载层

规则（总指挥约束）：
- 一律动态读取，禁止硬编码任何分数、公司名单、权重
- 草稿/临时文件自动跳过：文件名以 _ 开头，或含 backup / draft / old / tmp
- 草稿状态（review_status != confirmed）只打标，不剔除
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ANNOTATED_DIR = REPO_ROOT / "data" / "annotated"
ANNOTATED_CN_DIR = REPO_ROOT / "data" / "annotated_cn"
PANEL_CSV = REPO_ROOT / "data" / "processed" / "training_v05_panel_30.csv"
ANNOTATED_DIR = REPO_ROOT / "data" / "annotated"
PANEL_CSV = REPO_ROOT / "data" / "processed" / "training_v05_panel_30.csv"

# 文件名里的草稿/备份/临时关键词（不区分大小写）
SKIP_KEYWORDS = ("backup", "draft", "old", "tmp")

# 风险等级 → 颜色（低饱和）
LEVEL_COLORS = {
    "高风险": "#B3402F", "High Risk": "#B3402F", "HIGH": "#B3402F",
    "中高风险": "#C07A1B", "Medium-High Risk": "#C07A1B",
    "中风险": "#D9A62E", "Medium Risk": "#D9A62E", "MEDIUM": "#D9A62E",
    "中低风险": "#7A9E43", "Medium-Low Risk": "#7A9E43",
    "低风险": "#2E7D5B", "Low Risk": "#2E7D5B", "LOW": "#2E7D5B",
}
DEFAULT_COLOR = "#8A877F"


def _color_of(level: str, fallback: str = "") -> str:
    if fallback:
        return fallback
    return LEVEL_COLORS.get(level, DEFAULT_COLOR)


def _normalize_case(raw: dict, fallback_ticker: str) -> dict | None:
    """把一份标注 JSON 归一化成统一结构；不符合规范的返回 None。"""
    comp = raw.get("composite_score")
    if not isinstance(comp, dict):  # 非正式标注（如临时摘录文件）
        return None

    company = raw.get("company", {})
    meta = raw.get("metadata", {})
    review_status = meta.get("review_status", "unknown")

    dimensions = [
        {
            "id": d.get("dimension_id", ""),
            "name": d.get("dimension_name", ""),
            "name_en": d.get("dimension_name_en", ""),
            "weight": float(d.get("weight", 0)),
            "score": float(d.get("score", 0)),
            "max": float(d.get("score_max", 5)),
            "label": d.get("score_label", ""),
            "reasoning": d.get("reasoning", ""),
            "supporting_signals": d.get("supporting_signals", []),
            "key_metrics": d.get("key_metrics", {}),
        }
        for d in raw.get("dimension_scores", [])
    ]

    signals = [
        {
            "id": s.get("signal_id", ""),
            "source": s.get("source", ""),
            "keyword": s.get("keyword_matched", ""),
            "excerpt": s.get("text_excerpt", ""),
            "page_location": s.get("page_location", ""),
            "risk_type": s.get("risk_type", ""),
            "severity": s.get("severity", ""),
            "relevance": s.get("relevance_to_depreciation", ""),
            "evidence_chain": s.get("evidence_chain", ""),
        }
        for s in raw.get("risk_signals", [])
    ]

    level = comp.get("risk_level", "")
    return {
        "ticker": company.get("ticker", fallback_ticker),
        "name": company.get("name", ""),
        "fiscal_year": int(company.get("fiscal_year", 0)),
        "score": float(comp.get("weighted_score", 0)),
        "max_score": float(comp.get("max_score", 5)),
        "risk_level": level,
        "risk_level_en": comp.get("risk_level_en", ""),
        "color": _color_of(level, comp.get("risk_level_color", "")),
        "confidence": comp.get("confidence"),
        "confidence_reason": comp.get("confidence_reason", ""),
        "score_breakdown": comp.get("score_breakdown"),
        "review_status": review_status,
        "is_draft": review_status != "confirmed",
        "version": meta.get("version", ""),
        "annotated_at": meta.get("annotated_at", ""),
        "weights": {d["id"]: d["weight"] for d in dimensions},
        "dimensions": dimensions,
        "signals": signals,
        "accounting_policy": raw.get("accounting_policy", {}),
        "financial_highlights": raw.get("financial_highlights", {}),
        "comparative_context": raw.get("comparative_context", ""),
        "summary": raw.get("summary") or comp.get("confidence_reason", ""),
    }


@st.cache_data(show_spinner="正在加载标注数据……")
def load_cases() -> list[dict]:
    """动态读取 data/annotated/ 下全部正式标注，按公司+财年排序。"""
    """动态读取 data/annotated/ 和 data/annotated_cn/ 下全部正式标注，按公司+财年排序。"""
    cases = []
    for directory in (ANNOTATED_DIR, ANNOTATED_CN_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json")):
            stem = path.stem.lower()
            if path.name.startswith("_") or any(kw in stem for kw in SKIP_KEYWORDS):
                continue  # 跳过临时/备份文件
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue  # 损坏文件不影响整体
            case = _normalize_case(raw, path.stem.split("_")[0])
            if case is not None:
                cases.append(case)
    cases.sort(key=lambda c: (c["ticker"], c["fiscal_year"]))
    return cases
    if not ANNOTATED_DIR.exists():
        return cases
    for path in sorted(ANNOTATED_DIR.glob("*.json")):
        stem = path.stem.lower()
        if path.name.startswith("_") or any(kw in stem for kw in SKIP_KEYWORDS):
            continue  # 跳过临时/备份文件
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue  # 损坏文件不影响整体
        case = _normalize_case(raw, path.stem.split("_")[0])
        if case is not None:
            cases.append(case)
    cases.sort(key=lambda c: (c["ticker"], c["fiscal_year"]))
    return cases


@st.cache_data(show_spinner="正在加载训练面板……")
def load_panel() -> pd.DataFrame:
    """读取 30 行训练面板 CSV（数值特征 + 五维评分 + 政策变更标记）。"""
    df = pd.read_csv(PANEL_CSV)
    df["fiscal_year"] = df["fiscal_year"].astype(int)
    df["color"] = df["risk_level"].map(lambda lv: _color_of(str(lv)))
    return df.sort_values(["ticker", "fiscal_year"]).reset_index(drop=True)


def load_all() -> dict:
    """页面统一入口：{'panel': DataFrame, 'cases': [case, ...]}"""
    return {"panel": load_panel(), "cases": load_cases()}


def find_case(cases: list[dict], ticker: str, fiscal_year: int) -> dict | None:
    for c in cases:
        if c["ticker"] == ticker and c["fiscal_year"] == fiscal_year:
            return c
    return None
