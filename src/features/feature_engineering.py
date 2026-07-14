"""特征工程模块

构建传统财务指标 + 科创特有风险指标 + 文本特征。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path


class FeatureEngineer:
    """特征工程器：从原始数据生成模型可用特征"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化特征工程器
        
        Args:
            config_path: 特征配置文件路径
        """
        self.features = {}
        self.config = self._load_config(config_path)
    
    def _load_config(self, path: Optional[str]) -> Dict:
        """加载特征配置"""
        if path is None:
            path = Path(__file__).parent.parent.parent / "config" / "data_config.yaml"
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def build_traditional_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """构建传统财务特征
        
        特征列表:
        - depreciation_rate: 折旧摊销率 = 折旧摊销 / 总资产
        - intangible_ratio: 无形资产占比 = 无形资产 / 总资产
        - rd_intensity: 研发强度 = 研发费用 / 营业收入
        - rd_capitalization_rate: 研发资本化率 = 资本化研发 / 总研发
        - asset_turnover: 资产周转率 = 营业收入 / 总资产
        - goodwill_ratio: 商誉占比 = 商誉 / 总资产
        
        Args:
            df: 清洗后的财务数据
        
        Returns:
            pd.DataFrame: 包含新特征的DataFrame
        """
        df = df.copy()
        
        # 折旧摊销率
        df['depreciation_rate'] = df.get('depreciation_amortization', 0) / df.get('total_assets', 1)
        
        # 无形资产占比
        df['intangible_ratio'] = df.get('intangible_assets', 0) / df.get('total_assets', 1)
        
        # 研发强度
        df['rd_intensity'] = df.get('r_d_expense', 0) / df.get('revenue', 1)
        
        # 研发资本化率
        total_rd = df.get('capitalized_rd', 0) + df.get('expensed_rd', 0)
        df['rd_capitalization_rate'] = df.get('capitalized_rd', 0) / total_rd.replace(0, np.nan)
        
        # 资产周转率
        df['asset_turnover'] = df.get('revenue', 0) / df.get('total_assets', 1)
        
        # 商誉占比
        df['goodwill_ratio'] = df.get('goodwill', 0) / df.get('total_assets', 1)
        
        return df
    
    def build_innovation_features(self, df: pd.DataFrame, patent_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """构建科创特有风险特征
        
        特征列表:
        - tech_half_life: 技术半衰期（基于专利引用网络）
        - patent_citation_velocity: 专利引用速度
        - patent_filing_intensity: 专利申请强度
        - technology_obsolescence_score: 技术淘汰风险得分
        
        Args:
            df: 财务数据
            patent_df: 专利数据（可选）
        
        Returns:
            pd.DataFrame: 包含新特征的DataFrame
        """
        df = df.copy()
        
        # TODO: 实现技术半衰期计算（基于专利引用网络）
        # 参考：NBER 专利引用衰减模型
        df['tech_half_life'] = np.nan  # 占位
        
        # TODO: 实现专利引用速度
        df['patent_citation_velocity'] = np.nan  # 占位
        
        # 技术迭代强度（研发增长率的波动）
        if 'r_d_expense' in df.columns:
            df['rd_growth_volatility'] = df.groupby('ticker')['r_d_expense'].pct_change().rolling(window=3).std()
        
        return df
    
    def build_text_features(self, text_df: pd.DataFrame) -> pd.DataFrame:
        """构建文本特征
        
        特征列表:
        - risk_sentiment_score: 风险情感得分（FinBERT）
        - depreciation_keyword_count: 折旧/减值相关关键词频率
        - uncertainty_word_count: 不确定性词汇数量
        - text_length_risk: 风险章节文本长度异常度
        
        Args:
            text_df: 年报文本数据
        
        Returns:
            pd.DataFrame: 包含新特征的DataFrame
        """
        # TODO: 实现文本特征提取
        # 需调用 src/nlp/text_analyzer.py
        return pd.DataFrame()
    
    def build_all_features(self, financial_df: pd.DataFrame, patent_df: Optional[pd.DataFrame] = None, text_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """构建全部特征
        
        Args:
            financial_df: 财务数据
            patent_df: 专利数据（可选）
            text_df: 文本数据（可选）
        
        Returns:
            pd.DataFrame: 完整特征矩阵
        """
        df = self.build_traditional_features(financial_df)
        df = self.build_innovation_features(df, patent_df)
        
        if text_df is not None:
            text_features = self.build_text_features(text_df)
            if not text_features.empty:
                df = df.merge(text_features, on=['ticker', 'fiscal_year'], how='left')
        
        return df


def get_feature_importance(model, feature_names: List[str]) -> pd.DataFrame:
    """获取特征重要性（用于XGBoost/LightGBM）
    
    Args:
        model: 训练好的模型
        feature_names: 特征名称列表
    
    Returns:
        pd.DataFrame: 特征重要性排序
    """
    importance = model.feature_importances_
    return pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)


if __name__ == "__main__":
    # 测试用例
    engineer = FeatureEngineer()
    print("Feature engineering module loaded.")
