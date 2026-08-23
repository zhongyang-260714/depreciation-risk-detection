"""模型训练模块

包含 XGBoost / LightGBM 分类模型、孤立森林异常检测、AutoEncoder 训练，
以及 SHAP 可解释性分析。
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pickle
import yaml

# 机器学习
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, roc_auc_score, precision_recall_curve, 
    average_precision_score, confusion_matrix, f1_score
)

# XGBoost / LightGBM
import xgboost as xgb
import lightgbm as lgb

# 异常检测
from sklearn.ensemble import IsolationForest

# 可解释性
import shap
import matplotlib.pyplot as plt


class RiskModel:
    """风险识别模型主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化模型
        
        Args:
            config_path: 模型配置文件路径
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.shap_explainer = None
    
    def _load_config(self, path: Optional[str]) -> Dict:
        """加载配置"""
        if path is None:
            path = Path(__file__).parent.parent.parent / "config" / "data_config.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def preprocess(self, X: pd.DataFrame) -> np.ndarray:
        """数据预处理（标准化）
        
        Args:
            X: 原始特征DataFrame
        
        Returns:
            np.ndarray: 标准化后的特征矩阵
        """
        self.feature_names = X.columns.tolist()
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled
    
    def train_xgboost(
        self, X_train: np.ndarray, y_train: np.ndarray, 
        X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None
    ) -> xgb.XGBClassifier:
        """训练 XGBoost 分类模型
        
        Args:
            X_train: 训练特征
            y_train: 训练标签（0=正常, 1=高风险）
            X_val: 验证特征
            y_val: 验证标签
        
        Returns:
            xgb.XGBClassifier: 训练好的模型
        """
        params = self.config.get("model", {}).get("models", {}).get("xgboost", {}).get("params", {})
        
        model = xgb.XGBClassifier(
            max_depth=params.get("max_depth", 6),
            learning_rate=params.get("learning_rate", 0.1),
            n_estimators=params.get("n_estimators", 200),
            subsample=params.get("subsample", 0.8),
            colsample_bytree=params.get("colsample_bytree", 0.8),
            eval_metric=params.get("eval_metric", "logloss"),
            random_state=params.get("random_state", 42),
            use_label_encoder=False
        )
        
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))
        
        model.fit(
            X_train, y_train,
            eval_set=eval_set,
            early_stopping_rounds=20 if len(eval_set) > 1 else None,
            verbose=True
        )
        
        self.model = model
        return model
    
    def train_isolation_forest(self, X_train: np.ndarray) -> IsolationForest:
        """训练孤立森林异常检测模型
        
        用于无监督场景（无标签数据时的初步筛选）
        
        Args:
            X_train: 训练特征
        
        Returns:
            IsolationForest: 训练好的模型
        """
        params = self.config.get("model", {}).get("models", {}).get("isolation_forest", {}).get("params", {})
        
        model = IsolationForest(
            contamination=params.get("contamination", 0.05),
            random_state=params.get("random_state", 42),
            n_estimators=200
        )
        
        model.fit(X_train)
        self.model = model
        return model
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """评估模型性能
        
        Args:
            X_test: 测试特征
            y_test: 测试标签
        
        Returns:
            Dict: 包含各项评估指标
        """
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1] if hasattr(self.model, "predict_proba") else None
        
        metrics = {
            "accuracy": (y_pred == y_test).mean(),
            "f1_score": f1_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        if y_prob is not None:
            metrics["roc_auc"] = roc_auc_score(y_test, y_prob)
            metrics["average_precision"] = average_precision_score(y_test, y_prob)
        
        print("=" * 50)
        print("Model Evaluation Results")
        print("=" * 50)
        for k, v in metrics.items():
            if k != "confusion_matrix":
                print(f"{k}: {v:.4f}")
        print(f"\nConfusion Matrix:\n{metrics['confusion_matrix']}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["Normal", "High Risk"]))
        
        return metrics
    
    def explain_with_shap(self, X_sample: np.ndarray, plot: bool = True) -> shap.Explanation:
        """使用 SHAP 解释模型预测
        
        Args:
            X_sample: 样本数据（100个左右）
            plot: 是否绘制 SHAP 图
        
        Returns:
            shap.Explanation: SHAP 解释结果
        """
        if self.shap_explainer is None:
            self.shap_explainer = shap.TreeExplainer(self.model)
        
        shap_values = self.shap_explainer.shap_values(X_sample)
        
        if plot:
            plt.figure(figsize=(10, 8))
            shap.summary_plot(shap_values, X_sample, feature_names=self.feature_names, show=False)
            plt.title("SHAP Feature Importance")
            plt.tight_layout()
            plt.savefig("docs/shap_summary.png", dpi=150)
            plt.close()
        
        return shap_values
    
    def save(self, path: str) -> None:
        """保存模型"""
        with open(path, "wb") as f:
            pickle.dump({
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": self.feature_names,
                "config": self.config
            }, f)
        print(f"Model saved to {path}")
    
    def load(self, path: str) -> None:
        """加载模型"""
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.config = data["config"]
        print(f"Model loaded from {path}")


if __name__ == "__main__":
    # 测试用例
    print("Model training module loaded.")
    print("Config:", RiskModel().config.get("model", {}).get("default", "xgboost"))
