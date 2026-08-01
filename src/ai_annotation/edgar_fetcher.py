"""EDGAR 10-K 下载模块（v2 — 使用 SEC data.sec.gov JSON API）

更可靠的下载方式：
1. 通过 EDGAR browse 获取 CIK
2. 通过 data.sec.gov/submissions/CIK{cik}.json 获取 filing 元数据
3. 直接构造主文档下载 URL

无需 API key，但需附合规 User-Agent（SEC 要求）。
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

import requests


SEC_BASE = "https://www.sec.gov"
DATA_SEC = "https://data.sec.gov"
# SEC 要求所有请求必须附带合规 User-Agent（含联系邮箱）
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(depreciation-risk-detection research bot; academic use only)"
)
HEADERS = {"User-Agent": USER_AGENT}


def _get_cik(ticker: str) -> Optional[str]:
    """通过 ticker 查询 CIK（补零到 10 位）。"""
    url = (
        f"{SEC_BASE}/cgi-bin/browse-edgar?action=getcompany"
        f"&CIK={ticker.upper()}&type=10-K&count=1&output=atom"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        # CIK 格式: CIK=0001326801
        m = re.search(r"CIK=(\d{10})", resp.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def download_10k_html(
    ticker: str,
    fiscal_year: int,
    save_dir: Path | None = None,
) -> str:
    """下载指定公司、财年的最新 10-K HTML 全文。

    策略（v2）：
    1. 获取 CIK
    2. 调用 data.sec.gov/submissions/CIK{cik}.json 获取最近 filing 列表
    3. 找到 10-K 的主文档文件名（primaryDocument）
    4. 构造下载 URL 并获取

    Args:
        ticker: 股票代码，如 "META"
        fiscal_year: 财年，如 2023（用于缓存文件名，不影响下载）
        save_dir: 可选的本地缓存目录

    Returns:
        10-K HTML 文本字符串

    Raises:
        RuntimeError: 下载失败时抛出
    """
    ticker_upper = ticker.upper()

    # Step 1: 获取 CIK
    cik = _get_cik(ticker_upper)
    if not cik:
        raise RuntimeError(f"无法查询 {ticker} 的 CIK")

    # Step 2: 获取 submissions JSON
    sub_url = f"{DATA_SEC}/submissions/CIK{cik}.json"
    try:
        resp = requests.get(sub_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        sub_data = resp.json()
    except Exception as e:
        raise RuntimeError(f"无法获取 {ticker} 的 submissions 数据: {e}") from e

    # Step 3: 找到最近的 10-K
    filings = sub_data.get("filings", {})
    recent = filings.get("recent", {})
    forms = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])

    target_acc = None
    target_doc = None
    for i, form in enumerate(forms):
        if form == "10-K":
            target_acc = accs[i]
            target_doc = docs[i] if i < len(docs) else None
            break

    if not target_acc:
        raise RuntimeError(f"未找到 {ticker} 的 10-K filing")

    # Step 4: 构造下载 URL
    # URL 格式: https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primaryDocument}
    acc_no_dashes = target_acc.replace("-", "")
    if target_doc:
        file_url = f"{SEC_BASE}/Archives/edgar/data/{cik}/{acc_no_dashes}/{target_doc}"
    else:
        # 备选：直接下载完整 submission
        file_url = f"{SEC_BASE}/Archives/edgar/data/{cik}/{acc_no_dashes}/{acc_no_dashes}.txt"

    # Step 5: 下载
    try:
        resp = requests.get(file_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"无法下载 10-K 文件 ({file_url}): {e}") from e

    html_text = resp.text

    # 简单校验：10-K 应该至少有 5 万字符
    if len(html_text) < 50000:
        raise RuntimeError(
            f"下载内容疑似非 10-K 正文（仅 {len(html_text):,} 字符），"
            f"URL: {file_url}"
        )

    # 保存到本地缓存
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        cache_file = save_dir / f"{ticker_upper}_{fiscal_year}_10k.html"
        cache_file.write_text(html_text, encoding="utf-8")

    # SEC 频率限制
    time.sleep(0.5)

    return html_text


def load_10k_html(ticker: str, fiscal_year: int, cache_dir: Path | None = None) -> str:
    """优先读缓存，没有则下载。"""
    if cache_dir is not None:
        cache_file = Path(cache_dir) / f"{ticker.upper()}_{fiscal_year}_10k.html"
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")
    return download_10k_html(ticker, fiscal_year, save_dir=cache_dir)
