# -*- coding: utf-8 -*-
"""XGBoost PoC v0.3 — 附录 F 复现脚本
生成：summary.json、shap_importance.csv、logo_scatter.png、shap_bar.png
与 train_scorer.py 完全一致的特征筛选与超参数，补充 LOO/LOGO 交叉验证与 SHAP 可视化。
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import LeaveOneOut, LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error, mean_squared_error
import shap

# 字体设置（兼容中文标签）
plt.rcParams["font.sans-serif"] = ["SimHei", "Noto Sans SC"]
plt.rcParams["axes.unicode_minus"] = False

SRC = Path(r"D:\depreciation-risk-detection\data\processed\training_v06_panel_30_full.csv")
OUT = Path(r"D:\depreciation-risk-detection\报告图表")
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SRC, encoding="utf-8-sig")
print(f"Loaded: shape={df.shape}")

# ---------- 特征筛选（与附录 F 描述完全一致） ----------
ID_COLS = ["ticker", "company_name", "fiscal_year", "report_period_end"]
LABEL_COLS = ["D1", "D2", "D3", "D4", "D5", "composite_score", "risk_level"]
TEXT_COLS = [c for c in df.columns
             if c not in ID_COLS + LABEL_COLS and df[c].dtype not in ("int64", "float64")]
candidates = [c for c in df.columns if c not in ID_COLS + LABEL_COLS + TEXT_COLS]
EMPTY_COLS = [c for c in candidates if df[c].isna().all()]
feature_cols = [c for c in candidates if c not in EMPTY_COLS]

print(f"n_features={len(feature_cols)}, empty_dropped={len(EMPTY_COLS)}, text_excluded={len(TEXT_COLS)}")

X = df[feature_cols].astype(float)
y = df["composite_score"].astype(float).values
groups = df["ticker"].values  # LOGO 按公司留一

PARAMS = dict(n_estimators=200, max_depth=3, learning_rate=0.05,
              subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
              random_state=42, n_jobs=4)

# ---------- 朴素基线 ----------
naive_pred = np.full_like(y, y.mean())
naive_mae = float(np.mean(np.abs(naive_pred - y)))
naive_rmse = float(np.sqrt(np.mean((naive_pred - y)**2)))

# ---------- LOO ----------
loo = LeaveOneOut()
loo_preds = np.zeros_like(y, dtype=float)
for train_idx, test_idx in loo.split(X):
    model = xgb.XGBRegressor(**PARAMS)
    model.fit(X.iloc[train_idx], y[train_idx])
    loo_preds[test_idx] = model.predict(X.iloc[test_idx])

loo_mae = float(mean_absolute_error(y, loo_preds))
loo_rmse = float(np.sqrt(mean_squared_error(y, loo_preds)))

# ---------- LOGO ----------
logo = LeaveOneGroupOut()
logo_preds = np.zeros_like(y, dtype=float)
for train_idx, test_idx in logo.split(X, y, groups):
    model = xgb.XGBRegressor(**PARAMS)
    model.fit(X.iloc[train_idx], y[train_idx])
    logo_preds[test_idx] = model.predict(X.iloc[test_idx])

logo_mae = float(mean_absolute_error(y, logo_preds))
logo_rmse = float(np.sqrt(mean_squared_error(y, logo_preds)))

# ---------- 全量拟合 + SHAP ----------
full_model = xgb.XGBRegressor(**PARAMS)
full_model.fit(X, y)

explainer = shap.TreeExplainer(full_model)
shap_vals = explainer.shap_values(X)

# 全局重要性（平均 |SHAP|）
mean_abs_shap = np.abs(shap_vals).mean(axis=0)
shap_df = pd.DataFrame({
    "feature": feature_cols,
    "mean_abs_shap": mean_abs_shap,
})
# 方向：特征值与 SHAP 值的 Pearson 相关符号
shap_df["direction"] = [np.sign(np.corrcoef(X.iloc[:, i].fillna(0), shap_vals[:, i])[0, 1]) if np.std(X.iloc[:, i].fillna(0)) > 0 else 0 for i in range(len(feature_cols))]
shap_df["category"] = shap_df["feature"].apply(
    lambda f: "政策/比率/事件类" if any(k in f for k in ["capex", "revenue", "rate", "ratio", "turnover", "intensity", "life_extended", "growth"]) else "规模类"
)
shap_df = shap_df.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
shap_df["rank"] = shap_df.index + 1

# ---------- 保存 CSV ----------
csv_path = OUT / "xgboost_poc_v3_shap_importance.csv"
shap_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"saved: {csv_path}")

# ---------- 保存 summary.json ----------
summary = {
    "version": "v0.3",
    "sample": "30 rows = 10 companies x 3 fiscal years",
    "features": {"total_candidates": len(candidates), "final_numeric": len(feature_cols), "empty_dropped": len(EMPTY_COLS)},
    "naive_baseline": {"mae": round(naive_mae, 3), "rmse": round(naive_rmse, 3)},
    "loo": {"mae": round(loo_mae, 3), "rmse": round(loo_rmse, 3), "relative_improvement": round((naive_mae - loo_mae) / naive_mae * 100, 1)},
    "logo": {"mae": round(logo_mae, 3), "rmse": round(logo_rmse, 3), "relative_improvement": round((naive_mae - logo_mae) / naive_mae * 100, 1)},
    "top10_features": shap_df.head(10)[["rank", "feature", "mean_abs_shap", "direction", "category"]].to_dict(orient="records"),
}
json_path = OUT / "xgboost_poc_v3_summary.json"
json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"saved: {json_path}")

# ---------- 图 F-1：LOGO 散点图 ----------
fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(y, logo_preds, alpha=0.7, edgecolors="k", linewidths=0.5)
# 标注公司
for i, txt in enumerate(df["ticker"]):
    ax.annotate(txt, (y[i], logo_preds[i]), fontsize=7, alpha=0.7)
ax.plot([1, 5], [1, 5], "r--", lw=1, label="完美预测 y=x")
ax.set_xlabel("实际综合评分", fontsize=11)
ax.set_ylabel("LOGO 预测值", fontsize=11)
ax.set_title(f"LOGO 交叉验证：预测值 vs 实际值\nMAE={logo_mae:.3f}（基线={naive_mae:.3f}，改善={(naive_mae-logo_mae)/naive_mae*100:.1f}%）", fontsize=11)
ax.legend(loc="lower right")
ax.set_xlim(1.5, 5)
ax.set_ylim(1.5, 5)
fig.tight_layout()
f1_path = OUT / "xgboost_poc_v3_logo_scatter.png"
fig.savefig(f1_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"saved: {f1_path}")

# ---------- 图 F-2：SHAP 条形图（Top 20） ----------
top20 = shap_df.head(20).sort_values("mean_abs_shap", ascending=True)
colors = ["#ff7f0e" if "政策" in c else "#1f77b4" for c in top20["category"]]
fig, ax = plt.subplots(figsize=(7, 8))
ax.barh(top20["feature"], top20["mean_abs_shap"], color=colors, edgecolor="k", linewidth=0.3)
ax.set_xlabel("平均 |SHAP|", fontsize=11)
ax.set_title("SHAP 全局特征重要性 Top 20\n（橙=政策/比率/事件类；蓝=规模类）", fontsize=11)
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#ff7f0e", label="政策/比率/事件类"),
                   Patch(facecolor="#1f77b4", label="规模类")]
ax.legend(handles=legend_elements, loc="lower right")
fig.tight_layout()
f2_path = OUT / "xgboost_poc_v3_shap_bar.png"
fig.savefig(f2_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"saved: {f2_path}")

print("\n全部产出完成。")
