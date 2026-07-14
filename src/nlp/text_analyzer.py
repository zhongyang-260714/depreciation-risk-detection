"""NLP 文本分析模块

用于年报文本的风险信号提取，包括：
- FinBERT 情感分析
- 折旧/减值关键词抽取
- 风险因素章节结构化解析
"""

import re
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from collections import Counter

# 尝试导入 transformers（如果未安装则提示）
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class TextAnalyzer:
    """年报文本风险分析器"""
    
    # 折旧/减值相关关键词
    DEPRECIATION_KEYWORDS = [
        "depreciation", "amortization", "impairment", "write-down", "write-off",
        "折旧", "摊销", "减值", "无形资产", "商誉减值", "资产减值",
        "技术淘汰", "obsolete", "obsolescence", "技术迭代", "技术更新"
    ]
    
    # 不确定性/风险信号词
    RISK_SIGNAL_WORDS = [
        "uncertain", "risk", "volatile", "decline", "deterioration", "pressure",
        "挑战", "风险", "不确定", "下降", "压力", "恶化"
    ]
    
    def __init__(self, use_finbert: bool = True):
        """初始化文本分析器
        
        Args:
            use_finbert: 是否使用 FinBERT 模型（需要 GPU 或较强 CPU）
        """
        self.use_finbert = use_finbert and TRANSFORMERS_AVAILABLE
        self.finbert_pipeline = None
        
        if self.use_finbert:
            try:
                # FinBERT 模型（针对金融文本优化）
                self.finbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="yiyanghkust/finbert-tone",
                    tokenizer="yiyanghkust/finbert-tone"
                )
                print("FinBERT loaded successfully.")
            except Exception as e:
                print(f"FinBERT loading failed: {e}")
                self.use_finbert = False
    
    def extract_risk_section(self, text: str) -> str:
        """从年报全文中提取"风险因素"章节
        
        针对 10-K 格式：识别 ITEM 1A. RISK FACTORS 到 ITEM 1B. 之间的内容
        
        Args:
            text: 年报全文
        
        Returns:
            str: 风险因素章节文本
        """
        # 10-K 风险因素章节正则
        risk_pattern = r"ITEM\s+1A\.\s+[^\n]*RISK\s+FACTORS.*?(?=ITEM\s+1B\.|ITEM\s+2\.|ITEM\s+3\.|$)"
        match = re.search(risk_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(0)
        
        # 备用：搜索关键词定位
        keywords = ["risk factors", "风险因素", "主要风险"]
        for kw in keywords:
            idx = text.lower().find(kw)
            if idx != -1:
                return text[idx:idx+5000]  # 取关键词后 5000 字符
        
        return text[:5000]  # 默认取前 5000 字符
    
    def count_keywords(self, text: str, keywords: List[str]) -> Dict[str, int]:
        """统计关键词出现频率
        
        Args:
            text: 文本内容
            keywords: 关键词列表
        
        Returns:
            Dict[str, int]: 各关键词出现次数
        """
        text_lower = text.lower()
        return {kw: text_lower.count(kw.lower()) for kw in keywords}
    
    def calculate_depreciation_risk_score(self, text: str) -> float:
        """计算文本折旧风险得分
        
        基于关键词频率 + 上下文密度计算
        
        Args:
            text: 年报文本（推荐用风险章节）
        
        Returns:
            float: 风险得分 (0-100)
        """
        keyword_counts = self.count_keywords(text, self.DEPRECIATION_KEYWORDS)
        total_mentions = sum(keyword_counts.values())
        
        # 文本长度归一化
        text_length = len(text.split())
        normalized_score = min(100, (total_mentions / max(text_length / 1000, 1)) * 50)
        
        return normalized_score
    
    def analyze_sentiment_finbert(self, text: str) -> Dict[str, float]:
        """使用 FinBERT 分析情感
        
        Args:
            text: 文本（需分段，FinBERT 最大输入约 512 tokens）
        
        Returns:
            Dict[str, float]: 情感得分
                - positive: 积极概率
                - negative: 消极概率
                - neutral: 中性概率
        """
        if not self.use_finbert or self.finbert_pipeline is None:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        
        # 分段处理（512 token 限制）
        chunks = self._chunk_text(text, max_length=500)
        sentiments = []
        
        for chunk in chunks:
            try:
                result = self.finbert_pipeline(chunk[:500])
                sentiments.append(result[0])
            except Exception:
                continue
        
        if not sentiments:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        
        # 聚合结果
        agg = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        for s in sentiments:
            label = s["label"].lower()
            score = s["score"]
            if label in agg:
                agg[label] += score
        
        total = sum(agg.values())
        if total > 0:
            agg = {k: v/total for k, v in agg.items()}
        
        return agg
    
    def _chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """将长文本分块
        
        Args:
            text: 长文本
            max_length: 每块最大长度（词数）
        
        Returns:
            List[str]: 文本块列表
        """
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_length):
            chunks.append(" ".join(words[i:i+max_length]))
        return chunks
    
    def analyze_report(self, text: str) -> Dict[str, Any]:
        """完整分析单份年报
        
        Args:
            text: 年报全文
        
        Returns:
            Dict: 包含所有文本特征
        """
        risk_section = self.extract_risk_section(text)
        
        # 关键词统计
        dep_counts = self.count_keywords(risk_section, self.DEPRECIATION_KEYWORDS)
        risk_counts = self.count_keywords(risk_section, self.RISK_SIGNAL_WORDS)
        
        # 风险得分
        dep_risk_score = self.calculate_depreciation_risk_score(risk_section)
        
        # 情感分析
        sentiment = self.analyze_sentiment_finbert(risk_section)
        
        return {
            "depreciation_keyword_count": sum(dep_counts.values()),
            "risk_signal_count": sum(risk_counts.values()),
            "depreciation_risk_score": dep_risk_score,
            "sentiment_positive": sentiment["positive"],
            "sentiment_negative": sentiment["negative"],
            "sentiment_neutral": sentiment["neutral"],
            "risk_section_length": len(risk_section.split()),
            "keyword_details": dep_counts
        }


if __name__ == "__main__":
    # 测试用例
    analyzer = TextAnalyzer(use_finbert=False)
    
    test_text = """
    The company faces significant risks related to rapid technological obsolescence.
    Our intangible assets may require substantial impairment charges if market conditions deteriorate.
    The depreciation of our technology assets accelerated due to new AI breakthroughs.
    """
    
    result = analyzer.analyze_report(test_text)
    print("Text Analysis Results:")
    for k, v in result.items():
        print(f"  {k}: {v}")
