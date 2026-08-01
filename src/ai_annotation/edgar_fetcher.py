"""EDGAR 10-K 下载模块

极简封装 SEC EDGAR 免费下载接口。无需 API key，但需附 User-Agent。
"""

import time
from pathlib import Path
from typing import Optional

import requests


SEC_BASE = "https://www.sec.gov"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {"User-Agent": USER_AGENT}


def _get_cik(ticker: str) -> Optional[str]:
    """通过 ticker 查询 CIK。"""
    url = f"{SEC_BASE}/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-K&dateb=&owner=exclude&count=1&output=atom"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        # 简单正则提取 CIK
        import re
        m = re.search(r"CIK\.(\d{10})", resp.text)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def download_10k_html(ticker: str, fiscal_year: int, save_dir: Path | None = None) -> str:
    """下载指定公司、财年的最新 10-K HTML 全文。

    策略：
    1. 通过 EDGAR 搜索 10-K 列表
    2. 取第一条结果的 filing detail page
    3. 找到完整 submission 文件的 URL（通常以 .htm 结尾）
    4. 下载并返回 HTML 文本

    Args:
        ticker: 股票代码，如 "META"
        fiscal_year: 财年，如 2023
        save_dir: 可选的本地缓存目录

    Returns:
        10-K HTML 文本字符串

    Raises:
        RuntimeError: 下载失败时抛出
    """
    import re
    from bs4 import BeautifulSoup

    ticker_upper = ticker.upper()

    # Step 1: 搜索 filing 列表
    search_url = (
        f"{SEC_BASE}/cgi-bin/browse-edgar?action=getcompany"
        f"&CIK={ticker_upper}&type=10-K&dateb=&owner=exclude&count=40&output=atom"
    )
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"无法获取 {ticker} 的 filing 列表: {e}") from e

    # 解析 Atom feed，找 filing detail URL
    soup = BeautifulSoup(resp.content, "xml")
    entries = soup.find_all("entry")
    if not entries:
        raise RuntimeError(f"未找到 {ticker} 的任何 10-K filing")

    detail_url = None
    for entry in entries:
        link = entry.find("link")
        if link and link.get("href"):
            detail_url = link.get("href")
            break

    if not detail_url:
        raise RuntimeError(f"无法解析 {ticker} 的 filing 链接")

    # Step 2: 访问 detail page，找到完整文件链接
    try:
        resp = requests.get(detail_url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"无法访问 filing detail 页面: {e}") from e

    detail_soup = BeautifulSoup(resp.content, "html.parser")
    # 找 "Complete submission text file" 链接
    file_url = None
    for table in detail_soup.find_all("table", class_="tableFile"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                desc = cells[1].get_text(strip=True).lower()
                if "complete submission" in desc or "10-k" in desc:
                    link = cells[2].find("a")
                    if link and link.get("href"):
                        href = link.get("href")
                        if href.startswith("http"):
                            file_url = href
                        else:
                            file_url = f"{SEC_BASE}{href}"
                        break
        if file_url:
            break

    # 备选：直接找 .htm 链接
    if not file_url:
        for a in detail_soup.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".htm") or href.endswith(".html"):
                if href.startswith("http"):
                    file_url = href
                else:
                    file_url = f"{SEC_BASE}{href}"
                break

    if not file_url:
        raise RuntimeError(f"无法在 detail 页面找到 10-K 文件链接")

    # Step 3: 下载完整文件
    try:
        resp = requests.get(file_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"无法下载 10-K 文件: {e}") from e

    html_text = resp.text

    # 可选：保存到本地缓存
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        cache_file = save_dir / f"{ticker_upper}_{fiscal_year}_10k.html"
        cache_file.write_text(html_text, encoding="utf-8")

    # SEC 频率限制：每次请求后间隔 0.5 秒
    time.sleep(0.5)

    return html_text


def load_10k_html(ticker: str, fiscal_year: int, cache_dir: Path | None = None) -> str:
    """优先读缓存，没有则下载。"""
    if cache_dir is not None:
        cache_file = Path(cache_dir) / f"{ticker.upper()}_{fiscal_year}_10k.html"
        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")
    return download_10k_html(ticker, fiscal_year, save_dir=cache_dir)
