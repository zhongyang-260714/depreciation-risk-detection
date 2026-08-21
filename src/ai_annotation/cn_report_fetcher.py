"""A股年报下载器 — 巨潮资讯网(cninfo.com.cn)

支持从巨潮资讯网自动下载上市公司年度报告PDF。
"""

import json
import re
import time
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urljoin

import requests

# 巨潮资讯网API
CNINFO_ANNOUNCE_API = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
CNINFO_PDF_BASE = "http://static.cninfo.com.cn/"

# 交易所代码映射
EXCHANGE_MAP = {
    "SH": "sse",      # 上交所
    "SZ": "szse",     # 深交所
    "BJ": "bse",      # 北交所
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
}


def _normalize_stock_code(code: str) -> Tuple[str, str]:
    """标准化股票代码，返回(纯数字代码, 交易所后缀)。
    
    支持格式：603881.SH / 603881 / 300738.SZ / 000977
    """
    code = code.strip().upper()
    # 匹配 6位数字.交易所 或 纯6位数字
    m = re.match(r"^(\d{6})(?:\.(SH|SZ|BJ))?$", code)
    if not m:
        raise ValueError(f"股票代码格式错误: {code}，应为 6位数字[.SH/.SZ/.BJ] 格式")
    
    num = m.group(1)
    exchange = m.group(2)
    
    # 如果未指定交易所，根据代码前缀推断
    if not exchange:
        if num.startswith(("600", "601", "603", "605", "688")):
            exchange = "SH"
        elif num.startswith(("000", "001", "002", "003", "300", "301")):
            exchange = "SZ"
        else:
            exchange = "SH"  # 默认上交所
    
    return num, exchange


def _detect_column(exchange: str) -> str:
    """根据交易所返回column参数。"""
    return EXCHANGE_MAP.get(exchange, "sse")


def fetch_annual_report(
    stock_code: str,
    year: int,
    cache_dir: Optional[Path] = None,
    timeout: int = 30,
) -> Tuple[Path, str]:
    """下载指定公司指定年份的年度报告PDF。
    
    Args:
        stock_code: 股票代码，如 "603881.SH" 或 "603881"
        year: 报告年份（如2024表示2024年年报）
        cache_dir: 缓存目录，默认 data/raw/cn_财报/
        timeout: 请求超时秒数
    
    Returns:
        (pdf_path, company_name) — 下载后的PDF路径和公司简称
    
    Raises:
        ValueError: 代码格式错误
        RuntimeError: 下载失败
    """
    num, exchange = _normalize_stock_code(stock_code)
    column = _detect_column(exchange)
    
    if cache_dir is None:
        cache_dir = Path(__file__).resolve().parents[2] / "data" / "raw" / "cn_财报"
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # 缓存文件名
    cache_path = cache_dir / f"{num}_{year}_annual_report.pdf"
    if cache_path.exists():
        # 从缓存读取公司名（简单处理：从文件名推断）
        return cache_path, ""
    
    # 构建查询参数 — 巨潮公告查询API
    # 年报的category是年报类别，我们用公告标题关键词匹配
    stock_param = f"{num},{exchange}"
    
    payload = {
        "stock": stock_param,
        "tabName": "fulltext",
        "pageSize": 30,
        "pageNum": 1,
        "column": column,
        # 关键字筛选年报
        "searchkey": "年度报告",
        "secid": stock_param,
    }
    
    # Step 1: 查询公告列表
    try:
        resp = requests.post(
            CNINFO_ANNOUNCE_API,
            data=payload,
            headers=HEADERS,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"巨潮公告查询失败: {e}") from e
    
    if data.get("announcements") is None or not data["announcements"]:
        raise RuntimeError(f"未找到 {num}.{exchange} 的公告列表")
    
    # Step 2: 从公告列表中筛选目标年份的年度报告
    target_announcement = None
    company_name = ""
    
    for ann in data["announcements"]:
        title = ann.get("announcementTitle", "")
        # 匹配年份和"年度报告"，排除"摘要""修订""更正""补充"
        if "年度报告" in title and "摘要" not in title:
            # 提取标题中的年份
            year_match = re.search(r"20\d{2}", title)
            if year_match and int(year_match.group()) == year:
                # 排除修订/更正版，优先选原版
                if "修订" not in title and "更正" not in title and "补充" not in title:
                    target_announcement = ann
                    company_name = ann.get("secName", "")
                    break
                elif target_announcement is None:
                    target_announcement = ann
                    company_name = ann.get("secName", "")
    
    if target_announcement is None:
        # 放宽条件：只要包含目标年份即可
        for ann in data["announcements"]:
            title = ann.get("announcementTitle", "")
            year_match = re.search(r"20\d{2}", title)
            if year_match and int(year_match.group()) == year and "年度报告" in title:
                target_announcement = ann
                company_name = ann.get("secName", "")
                break
    
    if target_announcement is None:
        raise RuntimeError(f"未找到 {num}.{exchange} {year} 年年度报告")
    
    # Step 3: 下载PDF
    adjunct_url = target_announcement.get("adjunctUrl", "")
    if not adjunct_url:
        raise RuntimeError(f"公告无PDF链接: {target_announcement}")
    
    pdf_url = urljoin(CNINFO_PDF_BASE, adjunct_url)
    
    try:
        pdf_resp = requests.get(pdf_url, headers=HEADERS, timeout=timeout)
        pdf_resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"PDF下载失败: {e}") from e
    
    # 验证是PDF
    if not pdf_resp.content[:4] == b"%PDF":
        raise RuntimeError(f"下载内容不是PDF，可能是验证码或反爬拦截")
    
    cache_path.write_bytes(pdf_resp.content)
    time.sleep(0.5)  # 礼貌延迟
    
    return cache_path, company_name


def load_cn_report_text(stock_code: str, year: int, cache_dir: Optional[Path] = None) -> Tuple[str, str]:
    """一键获取A股年报文本。
    
    Returns:
        (full_text, company_name)
    """
    pdf_path, company_name = fetch_annual_report(stock_code, year, cache_dir)
    
    # 用pdfplumber提取文本
    import pdfplumber
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    return full_text, company_name
