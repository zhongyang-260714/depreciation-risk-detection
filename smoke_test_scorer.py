# -*- coding: utf-8 -*-
"""实时评分功能冒烟测试

验证三件事：
1. 评分器加载并对 3 个训练样本回代（|模型分 - 人工分| ≤ 0.3，演示流程通畅）；
2. 部分指标输入（缺失值路由）可正常评分；
3. FastAPI /predict 与 /batch_predict 接口可用（TestClient，无需启动服务）。

运行：venv\\Scripts\\python.exe smoke_test_scorer.py
"""
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from src.scoring.predictor import get_scorer  # noqa: E402

MODEL_DIR = REPO_ROOT / "models"
PANEL = REPO_ROOT / "data" / "processed" / "training_v06_panel_30_full.csv"

scorer = get_scorer(MODEL_DIR)
print(f"[1/3] 模型加载成功：{scorer.meta['model_version']}，{len(scorer.feature_cols)} 个特征")

df = pd.read_csv(PANEL, encoding="utf-8-sig")
ok = True
for _, row in df.sample(3, random_state=7).iterrows():
    feats = {c: float(row[c]) for c in scorer.feature_cols if not pd.isna(row[c])}
    r = scorer.predict(feats)
    diff = abs(r["score"] - row["composite_score"])
    flag = "OK " if diff <= 0.3 else "FAIL"
    ok &= diff <= 0.3
    print(f"  [{flag}] {row['ticker']} {int(row['fiscal_year'])}: "
          f"模型 {r['score']:.2f} vs 人工 {row['composite_score']:.2f} "
          f"（Δ={diff:.2f}，{r['risk_level']}）")
assert ok, "样本内回代偏差超限"

r2 = scorer.predict({"capex_to_revenue": 0.5, "life_extended_current_period": 1.0,
                     "server_life_min_years": 6.0})
print(f"[2/3] 部分指标评分 OK：score={r2['score']}，{r2['risk_level']}，"
      f"提供 {r2['n_features_provided']}/{r2['n_features_total']} 项")
assert 1.0 <= r2["score"] <= 5.0

from fastapi.testclient import TestClient  # noqa: E402
from src.api.main import app  # noqa: E402

client = TestClient(app)
resp = client.post("/predict", json={
    "ticker": "DEMO", "fiscal_year": 2025,
    "features": {"capex_to_revenue": 0.4, "life_extended_current_period": 1.0}})
assert resp.status_code == 200, resp.text
body = resp.json()
print(f"[3/3] /predict OK：{body['ticker']} score={body['score']}（{body['risk_level']}）")
resp_b = client.post("/batch_predict", json=[
    {"features": {"capex_to_revenue": 0.4}},
    {"features": {"capex_to_revenue": 0.05}}])
assert resp_b.status_code == 200 and resp_b.json()["count"] == 2, resp_b.text
print("      /batch_predict OK：2 条")
print("SMOKE TEST PASSED")
