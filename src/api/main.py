"""FastAPI 后端接口（预留）

为后续 REST API 服务提供基础框架。
Phase 3 系统集成时激活此模块。
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np

app = FastAPI(
    title="科创企业资产折旧风险识别 API",
    description="AI驱动的科技企业财报风险识别系统",
    version="0.1.0"
)


class FinancialInput(BaseModel):
    """财务指标输入"""
    ticker: str
    fiscal_year: int
    total_assets: float
    intangible_assets: float
    r_d_expense: float
    revenue: float
    depreciation_amortization: float


class RiskResponse(BaseModel):
    """风险识别响应"""
    ticker: str
    risk_score: float
    risk_level: str
    key_metrics: Dict[str, float]
    warnings: List[str]


@app.get("/")
def root():
    """API 状态检查"""
    return {"status": "ok", "service": "depreciation-risk-detection"}


@app.post("/predict", response_model=RiskResponse)
def predict_risk(input_data: FinancialInput):
    """预测单家公司的折旧风险
    
    Args:
        input_data: 财务指标
    
    Returns:
        RiskResponse: 风险评分与预警
    """
    # TODO: 加载模型并进行预测
    # 当前返回占位数据
    
    risk_score = 50.0  # 占位
    risk_level = "中风险" if risk_score >= 40 else "低风险"
    
    return RiskResponse(
        ticker=input_data.ticker,
        risk_score=risk_score,
        risk_level=risk_level,
        key_metrics={
            "depreciation_rate": input_data.depreciation_amortization / input_data.total_assets,
            "intangible_ratio": input_data.intangible_assets / input_data.total_assets
        },
        warnings=["模型尚未加载，返回占位数据"]
    )


@app.post("/batch_predict")
def batch_predict(inputs: List[FinancialInput]):
    """批量预测"""
    # TODO: 实现批量预测
    return {"status": "placeholder", "count": len(inputs)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
