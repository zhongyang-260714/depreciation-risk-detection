# API 接口定义 v1.0（队友直接实现）

> **状态**：草案，待 7月19日 会议确认后定稿
> **负责人**：你定义业务逻辑，队友实现代码
> **技术栈**：FastAPI + Pydantic

---

## 接口清单（共3个）

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 风险分析 | POST | `/api/v1/analyze` | 接收财务数据，返回风险评分 |
| 公司列表 | GET | `/api/v1/companies` | 返回支持分析的公司列表 |
| 健康检查 | GET | `/api/v1/health` | 检查服务是否正常运行 |

---

## 接口 1：风险分析（核心）

### 请求格式（你发给后端的数据）

```json
{
  "ticker": "META",
  "fiscal_year": 2023,
  "total_assets": 185000,
  "intangible_assets": 37000,
  "rd_expense": 38500,
  "revenue": 134900,
  "depreciation_amortization": 8500,
  "net_income": 39000,
  "capex": 28000,
  "risk_factors_text": "可选：粘贴年报风险因素章节文本"
}
```

### 字段说明（队友实现时校验规则）

| 字段 | 类型 | 必填 | 校验规则 | 说明 |
|------|------|------|---------|------|
| ticker | string | 是 | 大写英文字母，2-5位 | 股票代码 |
| fiscal_year | int | 是 | 2000-2024 | 财年 |
| total_assets | float | 是 | > 0 | 总资产（百万美元）|
| intangible_assets | float | 是 | ≥ 0 | 无形资产（百万美元）|
| rd_expense | float | 是 | ≥ 0 | 研发费用（百万美元）|
| revenue | float | 是 | > 0 | 营业收入（百万美元）|
| depreciation_amortization | float | 是 | ≥ 0 | 折旧摊销（百万美元）|
| net_income | float | 否 | 任意 | 净利润（百万美元）|
| capex | float | 否 | ≥ 0 | 资本支出（百万美元）|
| risk_factors_text | string | 否 | 任意 | 年报风险因素文本 |

### 响应格式（后端返回给你的数据）

```json
{
  "success": true,
  "data": {
    "risk_score": 68.5,
    "risk_level": "high",
    "company": "META",
    "fiscal_year": 2023,
    "key_metrics": {
      "depreciation_rate": 0.0459,
      "depreciation_rate_pct": "4.59%",
      "intangible_ratio": 0.20,
      "intangible_ratio_pct": "20.00%",
      "rd_intensity": 0.285,
      "rd_intensity_pct": "28.50%",
      "asset_turnover": 0.73,
      "capex_to_revenue": 0.207,
      "capex_to_revenue_pct": "20.70%"
    },
    "risk_signals": [
      {
        "category": "折旧风险",
        "description": "GPU集群折旧年限5年，但NVIDIA产品周期仅2-3年",
        "severity": "high",
        "metric": "depreciation_rate",
        "threshold": 0.05,
        "actual_value": 0.0459
      },
      {
        "category": "资本支出风险",
        "description": "CAPEX 280亿美元，占收入20.7%，资本化决策空间巨大",
        "severity": "medium",
        "metric": "capex_to_revenue",
        "threshold": 0.15,
        "actual_value": 0.207
      }
    ],
    "shap_explanation": [
      {
        "feature": "rd_intensity",
        "contribution": 18.5,
        "direction": "positive",
        "description": "研发强度28.5%显著偏高，增加风险评分"
      },
      {
        "feature": "depreciation_rate",
        "contribution": 12.3,
        "direction": "positive",
        "description": "折旧率4.59%偏低，可能存在折旧不足"
      },
      {
        "feature": "intangible_ratio",
        "contribution": 8.2,
        "direction": "positive",
        "description": "无形资产占比20%，技术淘汰风险存在"
      }
    ],
    "analysis_summary": "Meta Platforms Inc. 在2023财年表现出中等偏高的资产折旧风险。研发投入强度（28.5%）和资本支出规模（280亿美元）均处于高位，但折旧率（4.59%）相对偏低，可能存在技术迭代导致的资产加速贬值未被充分计提的风险。建议关注GPU集群的实际使用年限与会计折旧年限的匹配度。"
  }
}
```

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "total_assets must be greater than 0",
    "field": "total_assets"
  }
}
```

---

## 接口 2：公司列表

### 请求

```
GET /api/v1/companies
```

### 响应

```json
{
  "success": true,
  "data": {
    "companies": [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "META",
        "name": "Meta Platforms Inc.",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "TSLA",
        "name": "Tesla Inc.",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      },
      {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "available_years": [2020, 2021, 2022, 2023, 2024]
      }
    ]
  }
}
```

---

## 接口 3：健康检查

### 请求

```
GET /api/v1/health
```

### 响应

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-07-15T14:30:00Z"
  }
}
```

---

## 风险等级定义（队友实现时参考）

| 风险等级 | 风险评分 | 颜色 | 说明 |
|---------|---------|------|------|
| low | 0-39 | 🟢 绿色 | 折旧政策合理，风险可控 |
| medium | 40-69 | 🟡 黄色 | 存在潜在风险，需关注 |
| high | 70-100 | 🔴 红色 | 风险显著，建议深入调查 |

---

## 技术实现要求（给队友）

### 必装依赖

```
fastapi==0.111.0
uvicorn==0.30.0
pydantic==2.7.0
python-multipart==0.0.9
```

### 文件结构

```
src/api/
├── __init__.py
├── main.py          # FastAPI 主入口
├── models.py        # Pydantic 数据模型（上面的JSON格式）
├── schemas.py       # 请求/响应模型定义
├── routers/
│   ├── __init__.py
│   ├── analyze.py   # /api/v1/analyze 路由
│   ├── companies.py # /api/v1/companies 路由
│   └── health.py    # /api/v1/health 路由
└── utils/
    ├── __init__.py
    └── calculator.py  # 风险计算工具函数
```

### 启动命令

```bash
cd D:/depreciation-risk-detection
venv/Scripts/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 自动文档

- 启动后访问：http://localhost:8000/docs
- 这是 Swagger UI，可以在线测试所有接口

---

## 注意事项

1. **当前风险评分是占位符**：队友先用固定公式返回评分（如 `rd_intensity * 100 + depreciation_rate * 200`），你后续会替换为真实的 XGBoost 模型
2. **文本分析可选**：如果请求中没有 `risk_factors_text`，直接忽略文本分析部分
3. **SHAP 解释先占位**：队友先用固定规则生成 SHAP 解释（如 `rd_intensity > 0.2` 就贡献 18.5 分），你后续替换为真实的 SHAP 值
4. **分析摘要先用模板**：队友先用固定模板生成摘要，你后续接入 LLM 自动生成

---

> 这份接口定义是**最终版**，可以直接给队友实现。你不需要修改，只需要在 7月19日 会议上确认这些字段是否满足你的需求。

