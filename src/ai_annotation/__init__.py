"""AI 标注模块

对外统一暴露的接口：annotate_10k() 一键完成智能标注流水线。
"""

from .deepseek_client import DeepSeekClient
from .edgar_fetcher import load_10k_html
from .text_locator import locate_candidates_batch
from .verifier import verify_all
from .scorer_calculator import compute_composite_score, enrich_dimension_scores

__all__ = [
    "DeepSeekClient",
    "load_10k_html",
    "locate_candidates_batch",
    "verify_all",
    "compute_composite_score",
    "enrich_dimension_scores",
]
