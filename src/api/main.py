"""FastAPI 后端接口 · 折旧风险实时评分（PoC 演示版）

加载 depreciation_scorer_v03 模型（30 样本可行性验证模型），
提供单条 / 批量实时评分接口，返回评分、风险等级与 SHAP 单项贡献。

定位：竞赛演示与方法论验证接口，输出不构成预测能力声明或投资建议。
运行：uvicorn src.api.main:app --port 8000
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.scoring.predictor import get_scorer  # noqa: E402

MODEL_DIR = REPO_ROOT / "models"

app = FastAPI(
    title="科创企业资产折旧风险识别 API",
    description="AI 驱动的科创企业财报折旧风险识别系统（PoC 演示版）",
    version="0.3.0",
)


class ScoreRequest(BaseModel):
    """评分请求：features 为 {指标名: 数值}，缺失指标由模型自动处理。"""
    ticker: Optional[str] = Field(default="", description="公司代码（可选，仅作标记）")
    fiscal_year: Optional[int] = Field(default=None, description="财年（可选，仅作标记）")
    features: Dict[str, float] = Field(default_factory=dict, description="财务指标键值对")


class Contributor(BaseModel):
    feature: str
    label: str
    value: Optional[float]
    shap: float
    direction: str


class ScoreResponse(BaseModel):
    ticker: str
    fiscal_year: Optional[int]
    score: float
    risk_level: str
    top_contributors: List[Contributor]
    n_features_provided: int
    n_features_total: int
    model_version: str
    reference_metrics: str
    disclaimer: str


def _score_one(req: ScoreRequest) -> dict:
    try:
        scorer = get_scorer(MODEL_DIR)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"模型文件缺失：{e}") from e
    if not req.features:
        raise HTTPException(status_code=422, detail="features 不能为空，至少提供一个财务指标")
    result = scorer.predict(req.features)
    result["ticker"] = req.ticker or ""
    result["fiscal_year"] = req.fiscal_year
    return result


@app.get("/")
def root():
    """API 状态检查"""
    model_ok = (MODEL_DIR / "depreciation_scorer_v03.joblib").exists()
    return {
        "status": "ok",
        "service": "depreciation-risk-detection",
        "model_loaded": model_ok,
        "version": "0.3.0",
        "note": "PoC 演示模型，输出不构成预测能力声明",
    }


@app.post("/predict", response_model=ScoreResponse)
def predict_risk(req: ScoreRequest):
    """实时评分：输入财务指标，输出折旧风险评分与贡献解释"""
    return _score_one(req)


@app.post("/batch_predict")
def batch_predict(reqs: List[ScoreRequest]):
    """批量实时评分"""
    if not reqs:
        raise HTTPException(status_code=422, detail="请求列表不能为空")
    return {"count": len(reqs), "results": [_score_one(r) for r in reqs]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
