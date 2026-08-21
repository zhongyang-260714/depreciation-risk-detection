"""EDGAR 10-K 下载模块（v4 — 修复SEC submissions分页问题）

下载策略：
1. 通过 SEC 官方 ticker→CIK 映射 JSON 获取 CIK
2. 通过 data.sec.gov/submissions/CIK{cik}.json 获取 filing 列表
3. **遍历 recent + files 分页**，找到最接近目标财年的 10-K
4. 构造下载 URL 并获取

v4 修复：
- SEC submissions 数据分页存储（recent仅1000条），旧10-K在额外files中
- 新增 _extract_10k_candidates 和 _load_all_candidates 遍历所有分页

无需 API key，但需附合规 User-Agent（SEC 要求）。
"""

import re
import time
from pathlib import Path
from typing import Optional

import requests


SEC_BASE = "https://www.sec.gov"
DATA_SEC = "https://data.sec.gov"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(depreciation-risk-detection research bot; academic use only)"
)
HEADERS = {"User-Agent": USER_AGENT}


def _get_cik(ticker: str) -> Optional[str]:
    """通过 ticker 查询 CIK（补零到 10 位）。

    优先使用 SEC 官方 ticker→CIK 映射 JSON（更稳定），
    失败时回退到旧的 browse-edgar 接口。
    """
    ticker_upper = ticker.upper()

    # 方法1: SEC 官方 ticker 映射文件
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        mapping = resp.json()
        for item in mapping.values():
            if item.get("ticker", "").upper() == ticker_upper:
                cik = str(item["cik_str"]).zfill(10)
                return cik
    except Exception:
        pass

    # 方法2: 回退到旧接口
    url = (
        f"{SEC_BASE}/cgi-bin/browse-edgar?action=getcompany"
        f"&CIK={ticker_upper}&type=10-K&count=1&output=atom"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        m = re.search(r"CIK=(\d{10})", resp.text)
        if m:
            return m.group(1)
    except Exception:
        pass

    return None


def _extract_10k_candidates(filings_data: dict) -> list[dict]:
    """从 filings 数据块中提取所有 10-K 候选。

    filings_data 格式: {"form": [...], "accessionNumber": [...], ...}
    """
    forms = filings_data.get("form", [])
    accs = filings_data.get("accessionNumber", [])
    docs = filings_data.get("primaryDocument", [])
    filing_dates = filings_data.get("filingDate", [])
    report_dates = filings_data.get("reportDate", [])

    candidates = []
    for i, form in enumerate(forms):
        if form != "10-K":
            continue
        if i >= len(accs):
            continue

        acc = accs[i]
        doc = docs[i] if i < len(docs) else None
        fdate = filing_dates[i] if i < len(filing_dates) else ""
        rdate = report_dates[i] if i < len(report_dates) else ""

        # 推断财年
        inferred_fy = None
        if rdate and len(rdate) >= 4:
            try:
                inferred_fy = int(rdate[:4])
            except ValueError:
                pass
        if inferred_fy is None and fdate and len(fdate) >= 4:
            try:
                inferred_fy = int(fdate[:4]) - 1
            except ValueError:
                pass

        if inferred_fy is not None:
            candidates.append({
                "fy": inferred_fy,
                "acc": acc,
                "doc": doc,
                "fdate": fdate,
                "rdate": rdate,
            })
    return candidates


def _find_10k_for_fiscal_year(sub_data: dict, target_fy: int, cik: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
    """从 submissions JSON（含分页 files）中找到最接近目标财年的 10-K。

    Returns:
        (accessionNumber, primaryDocument, actual_fiscal_year)
    """
    filings = sub_data.get("filings", {})
    all_candidates = []

    # 1. 先从 recent 中提取
    recent = filings.get("recent", {})
    all_candidates.extend(_extract_10k_candidates(recent))

    # 2. 如果 recent 中没有精确匹配，遍历 files 数组中的额外 JSON 文件
    #    SEC submissions 分页存储，recent 仅包含最近 1000 条 filings
    #    目标财年可能在 recent 中不存在，但在 files 中存在
    files = filings.get("files", [])
    has_exact_match = any(c["fy"] == target_fy for c in all_candidates)
    if files and not has_exact_match:
        for file_info in files:
            file_name = file_info.get("name", "")
            if not file_name:
                continue
            file_url = f"{DATA_SEC}/submissions/{file_name}"
            try:
                resp = requests.get(file_url, headers=HEADERS, timeout=20)
                resp.raise_for_status()
                file_data = resp.json()
                file_candidates = _extract_10k_candidates(file_data)
                all_candidates.extend(file_candidates)
                # 如果找到了精确匹配，提前停止遍历
                if any(c["fy"] == target_fy for c in file_candidates):
                    break
                # SEC 频率限制
                time.sleep(0.2)
            except Exception:
                # 单个文件加载失败不影响整体流程
                continue
    #    SEC submissions 分页存储，recent 仅包含最近 1000 条 filings
    files = filings.get("files", [])
    if files:
        # 计算当前已有候选的最近财年距离
        recent_best_dist = min(
            (abs(c["fy"] - target_fy) for c in all_candidates),
            default=float("inf"),
        )

        # 如果最近的候选距离目标超过1年，或没有候选，尝试从 files 加载更多历史数据
        if recent_best_dist > 1 or not all_candidates:
            for file_info in files:
                file_name = file_info.get("name", "")
                if not file_name:
                    continue
                file_url = f"{DATA_SEC}/submissions/{file_name}"
                try:
                    resp = requests.get(file_url, headers=HEADERS, timeout=20)
                    resp.raise_for_status()
                    file_data = resp.json()
                    file_candidates = _extract_10k_candidates(file_data)
                    all_candidates.extend(file_candidates)
                    # SEC 频率限制
                    time.sleep(0.2)
                except Exception:
                    # 单个文件加载失败不影响整体流程
                    continue

    if not all_candidates:
        return None, None, None

    best = min(all_candidates, key=lambda c: abs(c["fy"] - target_fy))
    return best["acc"], best["doc"], best["fy"]


def download_10k_html(
    ticker: str,
    fiscal_year: int,
    save_dir: Path | None = None,
    strict: bool = False,
) -> str:
    """下载指定公司、财年的 10-K HTML 全文。

    Args:
        ticker: 股票代码，如 "META"
        fiscal_year: 目标财年，如 2023
        save_dir: 可选的本地缓存目录
        strict: 如果 True，当找不到精确匹配的财年时抛出错误

    Returns:
        10-K HTML 文本字符串（如实际财年不匹配，会在开头插入 <!-- actual_fy: X --> 标记）

    Raises:
        RuntimeError: 下载失败或 strict=True 且找不到精确匹配时抛出
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

    # Step 3: 按财年筛选 10-K（支持分页 files）
    target_acc, target_doc, actual_fy = _find_10k_for_fiscal_year(sub_data, fiscal_year, cik)

    if not target_acc:
        raise RuntimeError(f"未找到 {ticker} 的任何 10-K filing")

    if strict and actual_fy != fiscal_year:
        raise RuntimeError(
            f"未找到 {ticker} FY{fiscal_year} 的精确匹配 10-K，"
            f"最近的是 FY{actual_fy}"
        )

    # Step 4: 构造下载 URL
    acc_no_dashes = target_acc.replace("-", "")
    if target_doc:
        file_url = f"{SEC_BASE}/Archives/edgar/data/{cik}/{acc_no_dashes}/{target_doc}"
    else:
        file_url = f"{SEC_BASE}/Archives/edgar/data/{cik}/{acc_no_dashes}/{acc_no_dashes}.txt"

    # Step 5: 下载
    try:
        resp = requests.get(file_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"无法下载 10-K 文件 ({file_url}): {e}") from e

    html_text = resp.text

    # 简单校验
    if len(html_text) < 50000:
        raise RuntimeError(
            f"下载内容疑似非 10-K 正文（仅 {len(html_text):,} 字符），"
            f"URL: {file_url}"
        )

    # 如果实际财年不匹配，在 HTML 开头插入标记
    if actual_fy != fiscal_year:
        html_text = f"<!-- actual_fiscal_year: {actual_fy} (requested: {fiscal_year}) -->\n" + html_text

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
    """优先读缓存，支持多种缓存文件名格式，没有则下载。"""
    if cache_dir is not None:
        cache_dir = Path(cache_dir)
        # 尝试多种缓存文件名格式（兼容历史数据）
        possible_names = [
            f"{ticker.upper()}_{fiscal_year}_10k.html",      # AMD_2023_10k.html
            f"{ticker.lower()}_fy{fiscal_year}_10k.html",    # amd_fy2023_10k.html
            f"{ticker.lower()}_{fiscal_year}_10k.html",      # amd_2023_10k.html
            f"{ticker.upper()}_FY{fiscal_year}_10k.html",    # AMD_FY2023_10k.html
        ]
        for name in possible_names:
            cache_file = cache_dir / name
            if cache_file.exists():
                return cache_file.read_text(encoding="utf-8", errors="replace")
    return download_10k_html(ticker, fiscal_year, save_dir=cache_dir)
