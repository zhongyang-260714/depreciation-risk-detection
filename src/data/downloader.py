"""数据获取与清洗模块

负责从各数据源获取原始数据并进行初步清洗。
当前阶段：优先使用 SEC EDGAR 公开数据跑通流程。
"""

import os
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import yaml


# 加载配置
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "data_config.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


def download_sec_filings(
    tickers: List[str],
    years: List[int],
    filing_type: str = "10-K",
    output_dir: str = "data/raw/sec_edgar"
) -> Dict[str, pd.DataFrame]:
    """下载 SEC EDGAR 年报文件
    
    Args:
        tickers: 股票代码列表（如 ['AAPL', 'MSFT', 'GOOGL']）
        years: 年份列表
        filing_type: 文件类型，默认 10-K
        output_dir: 输出目录
    
    Returns:
        Dict[str, pd.DataFrame]: 各公司年报元数据
    
    Note:
        需要设置 SEC_EDGAR_USER_AGENT 环境变量（SEC要求）
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}
    
    headers = {
        "User-Agent": os.getenv("SEC_EDGAR_USER_AGENT", "depreciation-risk-detection@example.com")
    }
    
    for ticker in tqdm(tickers, desc="Downloading SEC filings"):
        # TODO: 实现 SEC EDGAR 下载逻辑
        # 参考: https://www.sec.gov/edgar/sec-apis
        pass
    
    return results


def parse_10k_text(filing_path: str) -> Dict[str, str]:
    """解析 10-K 年报文本，提取关键章节
    
    Args:
        filing_path: 年报文件路径
    
    Returns:
        Dict[str, str]: 各章节文本
            - full_text: 全文
            - risk_factors: 风险因素章节
            - management_discussion: 管理层讨论与分析
            - financial_statements: 财务报表
    """
    # TODO: 实现文本解析逻辑
    # 可参考: BeautifulSoup + 正则提取 ITEM 1A, ITEM 7 等
    return {
        "full_text": "",
        "risk_factors": "",
        "management_discussion": "",
        "financial_statements": ""
    }


def load_financial_data(
    source: str = "csmar",
    ticker: Optional[str] = None,
    years: Optional[List[int]] = None
) -> pd.DataFrame:
    """加载财务数据
    
    Args:
        source: 数据源，可选 csmar / wrds / compustat
        ticker: 股票代码过滤
        years: 年份过滤
    
    Returns:
        pd.DataFrame: 财务数据
    """
    # TODO: 实现数据加载逻辑
    # 优先从本地 data/processed/ 加载已清洗数据
    pass


def clean_financial_data(df: pd.DataFrame) -> pd.DataFrame:
    """清洗财务数据
    
    清洗步骤:
    1. 处理缺失值（行业均值填充或前向填充）
    2. 检测异常值（3σ法则或IQR）
    3. 标准化币种和单位
    4. 计算衍生指标（如折旧率、无形资产占比）
    
    Args:
        df: 原始财务数据
    
    Returns:
        pd.DataFrame: 清洗后的数据
    """
    # TODO: 实现数据清洗逻辑
    return df


if __name__ == "__main__":
    # 测试用例
    print("Data module loaded. Configuration:")
    print(CONFIG)
