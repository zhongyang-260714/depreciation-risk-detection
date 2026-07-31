# -*- coding: utf-8 -*-
"""训练并序列化折旧风险评分模型（PoC 演示版）

与 xgboost_poc_v3.py 完全一致的特征筛选与超参数，
在全量 30 样本（10 家 × 3 年）上拟合后序列化，供 Streamlit / FastAPI 实时评分演示使用。

定位：可行性验证（PoC）演示模型，不构成预测能力声明。
运行：python train_scorer.py（在仓库根目录执行）
"""
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

REPO_ROOT = Path(__file__).resolve().parent
SRC = REPO_ROOT / "data" / "processed" / "training_v06_panel_30_full.csv"

df = pd.read_csv(SRC, encoding="utf-8-sig")
print(f"shape = {df.shape}")

# ---------- 特征筛选（与 xgboost_poc_v3.py 完全一致） ----------
ID_COLS = ["ticker", "company_name", "fiscal_year", "report_period_end"]
LABEL_COLS = ["D1", "D2", "D3", "D4", "D5", "composite_score", "risk_level"]
TEXT_COLS = [c for c in df.columns
             if c not in ID_COLS + LABEL_COLS and df[c].dtype not in ("int64", "float64")]
candidates = [c for c in df.columns if c not in ID_COLS + LABEL_COLS + TEXT_COLS]
EMPTY_COLS = [c for c in candidates if df[c].isna().all()]
feature_cols = [c for c in candidates if c not in EMPTY_COLS]
print(f"n_features = {len(feature_cols)}")

X = df[feature_cols].astype(float)
y = df["composite_score"].astype(float).values

PARAMS = dict(n_estimators=200, max_depth=3, learning_rate=0.05,
              subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
              random_state=42, n_jobs=4)

model = xgb.XGBRegressor(**PARAMS)
model.fit(X, y)

# 训练集内回代误差（仅供演示页参考，不作性能声明）
in_sample = model.predict(X)
mae_in = float(np.mean(np.abs(in_sample - y)))
print(f"in-sample MAE = {mae_in:.3f}（仅参考；方法学指标见附录 F：LOGO MAE 0.418）")

# ---------- 序列化 ----------
model_dir = REPO_ROOT / "models"
model_dir.mkdir(parents=True, exist_ok=True)
model_path = model_dir / "depreciation_scorer_v03.joblib"
joblib.dump(model, model_path)

meta = dict(
    model_version="depreciation_scorer_v03",
    trained_at=str(date.today()),
    trained_on="training_v06_panel_30_full.csv（10 家公司 × 3 财年 = 30 行，55 个数值特征）",
    params={k: v for k, v in PARAMS.items() if k != "n_jobs"},
    feature_cols=feature_cols,
    dropped_empty_cols=EMPTY_COLS,
    text_cols_excluded=TEXT_COLS,
    score_range=[1.0, 5.0],
    risk_bands=[
        {"min": 4.0, "level": "高风险", "note": "对应报告 4.3 高风险组（≥4.0）"},
        {"min": 3.0, "level": "中高风险", "note": "对应报告 4.4 中高风险组（3.0–3.9）"},
        {"min": 0.0, "level": "低风险", "note": "对应报告 4.5 低分对照组（<3.0）"},
    ],
    in_sample_mae=round(mae_in, 4),
    reference_metrics="LOGO（留一公司法）MAE 0.418，较朴素基线改善 46.6%（附录 F，PoC 示意性证据）",
    disclaimer="本评分为 30 样本可行性验证（PoC）模型的演示输出，不构成预测能力声明或投资建议。",
)
meta_path = model_dir / "depreciation_scorer_v03_meta.json"
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"saved: {model_path}")
print(f"saved: {meta_path}")
print("DONE")
