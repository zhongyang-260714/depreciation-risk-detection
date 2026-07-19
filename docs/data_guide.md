# 数据获取指南

## 一、数据目录结构

```
data/
├── raw/              # 原始数据（不提交到Git）
│   ├── sec_edgar/    # SEC 10-K 年报
│   ├── csmar/        # CSMAR 财务数据
│   ├── patents/      # 专利数据
│   └── macro/        # 宏观经济数据
├── processed/        # 清洗后数据
│   ├── financial_features.csv
│   ├── text_features.csv
│   └── patent_features.csv
└── final/             # 模型输入数据
    └── feature_matrix.csv
```

> ⚠️ `data/` 目录已被 `.gitignore` 忽略，**不要将数据文件上传到 GitHub**。

---

## 二、数据源详细说明

### 1. 财务报表数据（优先级：高）

| 来源 | 范围 | 获取方式 | 备注 |
|-----|------|---------|------|
| **CSMAR** | 中国 A 股上市公司 | 学校图书馆数据库 | 需校内网或 VPN |
| **WRDS / Compustat** | 全球上市公司 | 学校图书馆数据库 | 需申请账号 |
| **巨潮资讯** | 中国公司年报 PDF | 爬虫/API | 免费，需解析 PDF |
| **SEC EDGAR** | 美国上市公司 | 公开 API | 需设置 User-Agent |

**关键字段清单**：
- `ticker`：股票代码
- `fiscal_year`：财年
- `total_assets`：总资产
- `intangible_assets`：无形资产
- `r_d_expense`：研发费用
- `capitalized_rd`：资本化研发
- `expensed_rd`：费用化研发
- `depreciation_amortization`：折旧摊销
- `goodwill`：商誉
- `revenue`：营业收入
- `net_income`：净利润

### 2. 年报文本数据（优先级：高）

| 来源 | 格式 | 获取方式 |
|-----|------|---------|
| **SEC EDGAR** | 10-K HTML/TXT | 官方 API / 爬虫 |
| **巨潮资讯** | PDF | 爬虫 |
| **CNRDS** | 结构化文本 | 学校数据库 |

**关键章节**：
- ITEM 1A: Risk Factors（风险因素）
- ITEM 7: Management's Discussion and Analysis（管理层讨论）
- ITEM 8: Financial Statements（财务报表）

### 3. 专利数据（优先级：中）

| 来源 | 范围 | 获取方式 | 限制 |
|-----|------|---------|------|
| **USPTO** | 美国专利 | 开放 API | 需申请 Key |
| **Google Patents** | 全球专利 | 公开 | 无 API，需爬虫 |
| **PatentsView** | 美国专利 | 免费 API | 调用频率限制 |
| **CNIPA** | 中国专利 | 官方查询 | 批量下载困难 |

**关键字段**：
- `patent_id`：专利号
- `assignee`：专利权人
- `filing_date`：申请日期
- `grant_date`：授权日期
- `citation_count`：被引用次数
- `technology_class`：技术分类

### 4. 宏观经济数据（优先级：低）

- **国家统计局**：GDP、工业增加值、CPI
- **工信部**：高技术产业产值、IT行业投资
- **世界银行**：全球科技投资指标

---

## 三、数据获取优先级（Phase 1）

### 本周（7.14-7.20）优先获取：

1. ✅ **SEC EDGAR 10-K 年报**（5-10家美国 AI/科技巨头）
   - 候选：AAPL, MSFT, GOOGL, META, NVDA, AMZN, TSLA, AMD, INTC, IBM
   - 目标年份：2020-2024
   - 用途：手动标注风险信号 + 构建文本分析数据集

2. ✅ **CSMAR 财务数据**（通过学校图书馆）
   - 中国科创板/创业板上市公司
   - 目标：2020-2024年，研发密集型企业

3. ⏳ **PatentsView API**（技术半衰期计算）
   - 上述公司的专利数据
   - 引用网络构建（后续 Phase 2）

---

## 四、SEC EDGAR 数据获取脚本示例

```python
import requests
import os

# 设置 SEC 要求的 User-Agent（环境变量或代码中）
headers = {
    "User-Agent": "YourName (your@email.com)"
}

# 获取公司 CIK（SEC 内部编号）
company_tickers_url = "https://www.sec.gov/files/company_tickers.json"
response = requests.get(company_tickers_url, headers=headers)
tickers = response.json()

# 查找 AAPL 的 CIK
for item in tickers.values():
    if item['ticker'] == 'AAPL':
        cik = str(item['cik_str']).zfill(10)
        print(f"AAPL CIK: {cik}")

# 获取提交历史
submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
submissions = requests.get(submissions_url, headers=headers).json()

# 筛选 10-K 文件
for i, form in enumerate(submissions['filings']['recent']['form']):
    if form == '10-K':
        accession = submissions['filings']['recent']['accessionNumber'][i]
        print(f"10-K: {accession}")
```

> ⚠️ 注意：SEC 有速率限制，请设置合理的延迟（每秒不超过 10 次请求）。

---

## 五、数据标注规范（手动标注风险信号）

| 风险信号 | 描述 | 示例 |
|---------|------|------|
| **资产加速减值** | 无形资产大幅减值或核销 | 商誉减值超过总资产 5% |
| **研发资本化异常** | 资本化率显著高于同行 | 资本化率 > 80% |
| **技术淘汰风险** | 核心技术面临替代 | 年报提及技术迭代压力 |
| **折旧政策激进** | 摊销周期过长 | 软件摊销 > 10 年 |
| **专利价值骤降** | 专利引用量断崖下降 | 引用量同比下降 > 50% |

---

## 六、数据存储规范

1. **原始数据**：`data/raw/`（Excel/CSV/JSON/PDF）
2. **清洗数据**：`data/processed/`（统一 CSV，列名小写+下划线）
3. **特征矩阵**：`data/final/`（模型可直接输入）

**命名规范**：
- `{source}_{entity}_{year}.csv`（如 `csmar_aapl_2023.csv`）
- `feature_matrix_v{version}.csv`（特征矩阵带版本号）
