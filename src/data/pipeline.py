"""数据清洗流水线

从原始数据（PDF/Excel/CSV）到特征矩阵的完整流程。
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List


class DataPipeline:
    """数据清洗流水线"""
    
    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_financial(self, source: str) -> pd.DataFrame:
        """加载原始财务数据
        
        Args:
            source: 数据源名称（csmar / wrds / compustat）
        
        Returns:
            pd.DataFrame: 原始数据
        """
        # TODO: 实现数据加载
        pass
    
    def clean_financial(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗财务数据
        
        步骤:
        1. 统一列名（小写+下划线）
        2. 处理缺失值（行业均值填充）
        3. 单位标准化（统一为百万美元/人民币）
        4. 异常值检测（3σ法则）
        5. 计算衍生指标
        
        Args:
            df: 原始财务数据
        
        Returns:
            pd.DataFrame: 清洗后数据
        """
        # 统一列名
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        
        # 处理缺失值（按行业/年份分组填充）
        # TODO: 实现更智能的填充策略
        df = df.fillna(df.groupby('fiscal_year').transform('median'))
        
        # 单位标准化（假设原始单位为千元）
        monetary_cols = ['total_assets', 'intangible_assets', 'r_d_expense', 'revenue', 'depreciation_amortization']
        for col in monetary_cols:
            if col in df.columns:
                df[col] = df[col] / 1000  # 转换为百万
        
        # 异常值检测：标记超出3σ的观测
        for col in monetary_cols:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                df[f'{col}_outlier'] = (df[col] < mean - 3*std) | (df[col] > mean + 3*std)
        
        return df
    
    def merge_text_features(self, financial_df: pd.DataFrame, text_df: pd.DataFrame) -> pd.DataFrame:
        """合并财务数据与文本特征
        
        Args:
            financial_df: 财务数据
            text_df: 文本特征数据
        
        Returns:
            pd.DataFrame: 合并后的特征矩阵
        """
        return pd.merge(
            financial_df,
            text_df,
            on=['ticker', 'fiscal_year'],
            how='left'
        )
    
    def build_feature_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """构建最终特征矩阵
        
        Args:
            df: 合并后的数据
        
        Returns:
            pd.DataFrame: 模型可直接输入的特征矩阵
        """
        # 选择数值列，移除标识列和文本列
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 排除已知非特征列
        exclude_cols = ['fiscal_year', 'cik', 'gvkey']  # 添加其他标识列
        feature_cols = [c for c in numeric_cols if c not in exclude_cols]
        
        return df[feature_cols].copy()
    
    def run_pipeline(self, financial_source: str, text_source: Optional[str] = None) -> pd.DataFrame:
        """运行完整流水线
        
        Args:
            financial_source: 财务数据源
            text_source: 文本数据源（可选）
        
        Returns:
            pd.DataFrame: 特征矩阵
        """
        # 1. 加载财务数据
        df = self.load_raw_financial(financial_source)
        
        # 2. 清洗财务数据
        df = self.clean_financial(df)
        
        # 3. 合并文本特征（如有）
        if text_source:
            text_df = pd.read_csv(f"{self.raw_dir}/{text_source}")
            df = self.merge_text_features(df, text_df)
        
        # 4. 构建特征矩阵
        feature_matrix = self.build_feature_matrix(df)
        
        # 5. 保存
        output_path = self.processed_dir / "feature_matrix.csv"
        feature_matrix.to_csv(output_path, index=False)
        print(f"Feature matrix saved to {output_path}")
        
        return feature_matrix


if __name__ == "__main__":
    pipeline = DataPipeline()
    print("Data pipeline module loaded.")
