# -*- coding: utf-8 -*-
"""看板冒烟测试：验证系统数据链路与六个页面模块可用

验证三件事：
1. 标注库完整：data/annotated/ 下 30 份 confirmed 标注全部可加载；
2. 六个页面模块（P1-P6）均可正常导入；
3. 实时评分链路就绪：模型文件与 v06 面板就位，评分器可加载。

运行：python smoke_test_app.py（在仓库根目录执行）
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DASHBOARD = REPO_ROOT / "src" / "dashboard"
sys.path.insert(0, str(DASHBOARD))
sys.path.insert(0, str(REPO_ROOT))

# [1/3] 标注库完整性
ANN = REPO_ROOT / "data" / "annotated"
skip = ("backup", "draft", "old", "tmp")
files = [p for p in ANN.glob("*.json")
         if not p.name.startswith("_") and not any(k in p.name.lower() for k in skip)]
assert len(files) == 30, f"预期 30 份正式标注，实际 {len(files)} 份"
n_confirmed = 0
for p in files:
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(raw.get("composite_score"), dict), f"{p.name} 缺少 composite_score"
    if raw.get("metadata", {}).get("review_status") == "confirmed":
        n_confirmed += 1
assert n_confirmed == 30, f"预期 30 份 confirmed，实际 {n_confirmed} 份"
print(f"[1/3] 标注库 OK：30 份标注全部 confirmed")

# [2/3] 六个页面模块可导入
import importlib

import data_loader  # noqa: F401,E402

for name in ["p1_overview", "p2_company", "p3_trajectory",
             "p4_sensitivity", "p5_methodology", "p6_live_scoring"]:
    mod = importlib.import_module(f"views.{name}")
    assert hasattr(mod, "render"), f"views.{name} 缺少 render()"
print("[2/3] 页面模块 OK：P1-P6 均可导入且含 render()")

# [3/3] 实时评分链路
for rel in ["models/depreciation_scorer_v03.joblib",
            "models/depreciation_scorer_v03_meta.json",
            "data/processed/training_v06_panel_30_full.csv"]:
    assert (REPO_ROOT / rel).exists(), f"缺少 {rel}"
from src.scoring.predictor import get_scorer  # noqa: E402

scorer = get_scorer(REPO_ROOT / "models")
assert len(scorer.feature_cols) == 55
print(f"[3/3] 评分链路 OK：{scorer.meta['model_version']}，55 个特征就位")

print("SMOKE TEST PASSED")
