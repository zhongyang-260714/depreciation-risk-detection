"""AI 标注模块

对外统一暴露的接口：
- 美股：annotate_10k() → EDGAR下载 + 英文关键词 + DeepSeek英文标注
- A股：annotate_cn_report() → 巨潮下载 + 中文关键词 + DeepSeek中文标注
"""

from .deepseek_client import DeepSeekClient
from .edgar_fetcher import load_10k_html
from .text_locator import locate_candidates_batch
from .verifier import verify_all
from .scorer_calculator import compute_composite_score, enrich_dimension_scores, apply_hard_rules, _extract_life_years

# A股适配模块
from .cn_report_fetcher import fetch_annual_report, load_cn_report_text
from .cn_text_locator import locate_cn_candidates

__all__ = [
    # 美股模块
    "DeepSeekClient",
    "load_10k_html",
    "locate_candidates_batch",
    "verify_all",
    "compute_composite_score",
    "enrich_dimension_scores",
    "apply_hard_rules",
    # A股模块
    "fetch_annual_report",
    "load_cn_report_text",
    "locate_cn_candidates",
]
