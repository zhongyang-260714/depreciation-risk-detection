# Python 数据提取任务清单（给队友 — 不懂金融版）

> **目标**：用 Python 自动从 SEC EDGAR 下载 10-K 年报，提取 25 个核心财务指标，输出 JSON  
> **难度**：中等（需要 Python 基础 + 网络请求 + HTML 解析）  
> **你的优势**：不需要懂金融！只需要按本清单提取数字，按 JSON 格式输出。  
> **金融知识**：全部写在清单里，你不需要额外学习。  
> **求助方式**：把本清单 + 示例代码发给 ChatGPT/Kimi，说"帮我完善这个代码"。

---

## 一、Phase 1：提取 5 家公司验证（本周完成）

### 1.1 公司列表（含 SEC 代码）

每家公司有一个**CIK 代码**（SEC 唯一标识），你需要用这个代码去 SEC 网站找年报。

| # | 公司 | 股票代码 | CIK 代码 | 10-K 提交日期（2023财年） | 优先级 |
|---|------|---------|---------|----------------------|--------|
| 1 | **Meta** | META | **0001326801** | 2024-02-02 | 🔴 必须先做（验证脚本） |
| 2 | **Google/Alphabet** | GOOGL | **0001652044** | 2024-01-30 | 🟡 高 |
| 3 | **Microsoft** | MSFT | **0000789019** | 2024-07-30 | 🟡 高 |
| 4 | **Amazon** | AMZN | **0001018724** | 2024-02-02 | 🟡 高 |
| 5 | **Tesla** | TSLA | **0001318605** | 2024-01-29 | 🟢 中 |
| 6 | **NVIDIA** | NVDA | **0001013480** | 2024-03-05 | 🟢 中 |
| 7 | **Apple** | AAPL | **0000320193** | 2024-02-02 | 🟢 中 |
| 8 | **Netflix** | NFLX | **0001065280** | 2024-01-26 | 🟢 低 |
| 9 | **Salesforce** | CRM | **0001108524** | 2024-03-07 | 🟢 低 |
| 10 | **Adobe** | ADBE | **0000796433** | 2024-01-12 | 🟢 低 |

> **本周目标**：先完成前 5 家（Meta → Google → Microsoft → Amazon → Tesla）。  
> **验证标准**：用 Meta 2023 的数据验证脚本正确，13 个检查点全部通过（见文末）。

### 1.2 为什么选这 10 家？

- **前 5 家**：AI 投入最大、数据中心资产最多、折旧风险最典型
- **后 5 家**：对比组（不同规模、不同行业、不同折旧政策）
- 全部是美国科技公司，10-K 年报格式统一，适合脚本批量处理

---

## 二、Phase 2：提取 25 个核心指标（Tier 1 指标）

### 2.1 指标列表（按报表分类）

#### A. 资产负债表指标（Balance Sheet）

| # | 指标名 | 字段名 | 说明 | 你不需要懂的金融知识 |
|---|--------|--------|------|---------------------|
| 1 | 总资产 | `total_assets` | 公司所有资产加起来 | 就是"公司有多少家当" |
| 2 | 固定资产净值 | `ppe_net` | 机器设备+房子，扣掉折旧后的值 | PP&E = Property, Plant & Equipment |
| 3 | 无形资产净值 | `intangible_assets_net` | 专利、软件等看不见的值，不含商誉 | 就是"知识产权值多少钱" |
| 4 | 商誉 | `goodwill` | 收购其他公司时多付的钱 | 比如花100亿买只值80亿的公司，多出的20亿就是商誉 |

#### B. 利润表指标（Income Statement）

| # | 指标名 | 字段名 | 说明 | 你不需要懂的金融知识 |
|---|--------|--------|------|---------------------|
| 5 | 营业收入 | `revenue` | 公司卖东西/服务收了多少钱 | 就是"一年卖了多少钱" |
| 6 | 营业利润 | `operating_income` | 卖东西的收入减去成本费用 | 就是"卖东西赚了多少" |
| 7 | 所得税费用 | `income_tax_expense` | 交给政府的税 | 就是"交了多少税" |
| 8 | 净利润 | `net_income` | 最后真正赚的钱 | 就是"最后到手多少钱" |
| 9 | 研发费用 | `rd_expense` | 搞研究花的钱 | 就是"搞研发花了多少钱" |
| 10 | 资产减值损失 | `impairment_loss` | 东西不值钱了，账面上减记 | 比如买了100亿的设备，现在只值50亿了，损失50亿 |

#### C. 现金流量表指标（Cash Flow Statement）

| # | 指标名 | 字段名 | 说明 | 你不需要懂的金融知识 |
|---|--------|--------|------|---------------------|
| 11 | 经营现金流 | `operating_cash_flow` | 卖东西实际收到的现金 | 就是"卖东西实际拿到多少现金"（不是账面上的） |
| 12 | 折旧费用 | `depreciation` | 机器设备每年损耗值 | 就是"机器每年旧了多少，算成钱" |
| 13 | 摊销费用 | `amortization` | 专利/软件每年损耗值 | 就是"专利每年过期了多少，算成钱" |
| 14 | 购买固定资产现金支出 | `capex_ppe` | 买新机器设备花的现金 | 就是"今年买新机器花了多少钱" |
| 15 | 融资租赁本金支付 | `finance_lease_payments` | 租设备分期付款的本金 | 就是"租机器每年还多少钱" |
| 16 | 处置固定资产收入 | `ppe_sales_proceeds` | 卖旧机器收到的钱 | 就是"卖旧机器卖了多少钱" |

#### D. 会计政策（附注1 - Note 1）

| # | 指标名 | 字段名 | 说明 | 你不需要懂的金融知识 |
|---|--------|--------|------|---------------------|
| 17 | 折旧方法 | `depreciation_method` | 直线法还是加速法 | 就是"机器折旧是每年一样多，还是前面多后面少" |
| 18 | 服务器/网络设备使用寿命 | `server_useful_life_years` | 几年 | 就是"服务器能用几年" |
| 19 | 建筑物使用寿命 | `building_useful_life_years` | 几年 | 就是"房子能用几年" |
| 20 | 设备/其他使用寿命 | `equipment_useful_life_years` | 几年 | 就是"其他设备能用几年" |
| 21 | 法定税率 | `statutory_tax_rate` | 美国联邦税率 | 就是"法律规定交多少税" |
| 22 | 实际有效税率 | `effective_tax_rate` | 实际交的税率 | 就是"实际交了多少税" |
| 23 | 员工人数 | `employee_count` | 多少人 | 就是"公司有多少人" |

#### E. 文本特征（Risk Factors 章节）

| # | 指标名 | 字段名 | 说明 | 你不需要懂的金融知识 |
|---|--------|--------|------|---------------------|
| 24 | 技术淘汰风险是否提及 | `tech_obsolescence_mentioned` | true/false | 就是"年报里有没有说'技术淘汰'" |
| 25 | 资产减值风险是否提及 | `impairment_mentioned` | true/false | 就是"年报里有没有说'资产减值'" |

### 2.2 你必须提取 vs 可以让搭档做的

| 指标 | 你负责提取 | 搭档（项目负责人）做 |
|------|----------|-------------------|
| 12个数字指标（A/B/C类） | ✅ 用 Python 脚本提取 | ❌ 不需要做 |
| 6个文本参数（D类使用寿命等） | ⚠️ 提取文字，但需要搭档确认含义 | ✅ 搭档确认 |
| 2个文本布尔（E类） | ⚠️ 搜索关键词，但需要搭档确认 | ✅ 搭档确认 |

> **你的核心任务**：写 Python 脚本，从 10-K 文件中提取所有指标，输出 JSON。  
> **搭档的任务**：读你提取的数据，判断指标含义是否正确，给出风险评分。

---

## 三、Python 提取步骤（分 5 步）

### 第 1 步：下载 10-K 文件（SEC EDGAR）

**输入**：公司 CIK 代码 + 财年  
**输出**：HTML 文件保存到本地

**SEC EDGAR 搜索地址格式**：
```
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K
```

**你需要做的事**：
1. 访问上面的地址（把 CIK 换成目标公司）
2. 找到最新提交的 Annual Report (10-K)
3. 点击 Documents，下载 HTML 文件（通常是 `meta-20231231.htm` 这种格式）
4. 保存到 `data/raw/{ticker}_{year}_10k.html`

**Python 代码框架**（让 AI 帮你完善）：
```python
import requests
import time

def download_10k(cik, ticker, year, save_path):
    """
    从 SEC EDGAR 下载 10-K 文件
    cik: 公司CIK代码（如 '0001326801'）
    ticker: 股票代码（如 'META'）
    year: 财年（如 2023）
    save_path: 保存路径
    """
    # SEC 要求加 User-Agent 头
    headers = {'User-Agent': 'Mozilla/5.0 (Your Name your@email.com)'}
    
    # 1. 搜索 10-K 列表
    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K"
    # ... 解析搜索结果，找到最新的 10-K ...
    
    # 2. 进入 Document 页面，找到 HTML 文件链接
    # ... 解析 HTML ...
    
    # 3. 下载 HTML 文件
    # ... 保存到 save_path ...
    
    time.sleep(0.5)  # SEC 要求限速，不要请求太快
    return save_path
```

> **让 AI 帮你写**：把上面的函数签名 + 注释发给 ChatGPT/Kimi，说"帮我完善这个函数，实现从 SEC EDGAR 下载 10-K HTML 文件"。

**注意事项**：
- SEC 网站需要 `User-Agent` 请求头，否则会返回 403
- 请求间隔至少 0.5 秒（SEC 限速）
- 如果公司没有 2023 财年 10-K（因为提交日期在 2024 年初），就找 2024 年初提交的那份

---

### 第 2 步：提取 XBRL 数字标签（最核心的 12 个指标）

**输入**：下载好的 HTML 文件  
**输出**：12 个数字指标

**方法**：用 `BeautifulSoup` 解析 HTML，找到 `ix:nonfraction` 或 `ix:nonnumeric` 标签，标签的 `name` 属性就是 XBRL 指标名。

**核心 XBRL 标签名**（直接复制粘贴）：

```python
# 资产负债表标签
XBRL_TAGS_BALANCE = {
    'total_assets': 'us-gaap:Assets',
    'ppe_net': 'us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization',
    'intangible_assets_net': 'us-gaap:IntangibleAssetsNetExcludingGoodwill',
    'goodwill': 'us-gaap:Goodwill',
}

# 利润表标签
XBRL_TAGS_INCOME = {
    'revenue': 'us-gaap:RevenueFromContractWithCustomer',
    'operating_income': 'us-gaap:OperatingIncomeLoss',
    'income_tax_expense': 'us-gaap:IncomeTaxExpenseBenefit',
    'net_income': 'us-gaap:NetIncomeLoss',
    'rd_expense': 'us-gaap:ResearchAndDevelopmentExpense',
    'impairment_loss': 'us-gaap:ImpairmentOfLongLivedAssetsHeldAndUsed',
}

# 现金流量表标签
XBRL_TAGS_CASHFLOW = {
    'operating_cash_flow': 'us-gaap:NetCashProvidedByUsedInOperatingActivities',
    'depreciation': 'us-gaap:Depreciation',
    'amortization': 'us-gaap:AmortizationOfIntangibleAssets',
    'capex_ppe': 'us-gaap:PaymentsToAcquirePropertyPlantAndEquipment',
    'finance_lease_payments': 'us-gaap:PrincipalPaymentsOnFinanceLeaseObligations',
    'ppe_sales_proceeds': 'us-gaap:ProceedsFromSaleOfPropertyPlantAndEquipment',
}
```

**提取逻辑**（让 AI 帮你完善）：
```python
from bs4 import BeautifulSoup
import re

def extract_xbrl_values(html_path, xbrl_tags):
    """
    从 HTML 文件中提取 XBRL 标签值
    html_path: 10-K HTML 文件路径
    xbrl_tags: 字典 {字段名: XBRL标签名}
    返回: {字段名: 数值}
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    results = {}
    for field_name, tag_name in xbrl_tags.items():
        # 搜索所有包含该 name 属性的标签
        # ... 用 BeautifulSoup 的 find/find_all ...
        # ... 提取 scale（单位）和 value（数值）...
        # ... 处理不同 scale（6=百万, 9=十亿, 0=个）...
        # ... 如果找不到，标记为 None ...
        pass
    
    return results
```

> **让 AI 帮你写**：把上面的标签字典 + 函数签名发给 AI，说"帮我完善这个函数，用 BeautifulSoup 从 HTML 中提取 XBRL 标签的值，注意 scale 属性决定单位（6=百万, 9=十亿, 0=个），输出统一为数字（单位：百万美元）"。

**Scale 换算规则**：
- `scale="6"` → 数值 × 1,000,000（百万美元）
- `scale="9"` → 数值 × 1,000,000,000（十亿美元）
- `scale="0"` → 数值 × 1（美元）
- `scale="-2"` → 百分比（如 0.21 表示 21%）

**Meta 2023 验证数据**（你的脚本必须匹配这些数字）：

| 字段名 | 期望值 | 说明 |
|--------|--------|------|
| total_assets | 229623 | 百万美元 |
| ppe_net | 96587 | 百万美元 |
| intangible_assets_net | 788 | 百万美元 |
| goodwill | 20654 | 百万美元 |
| revenue | 134902 | 百万美元 |
| operating_income | 46751 | 百万美元 |
| income_tax_expense | 8330 | 百万美元 |
| net_income | 39098 | 百万美元 |
| rd_expense | 38483 | 百万美元 |
| depreciation | 11178 | 百万美元 |
| amortization | 161 | 百万美元 |
| capex_ppe | 27266 | 百万美元 |

**如果标签名不匹配怎么办？**
- 不同公司可能用不同的 XBRL 标签名（如 `us-gaap:Revenue` vs `us-gaap:RevenueFromContractWithCustomer`）
- 解决方案：尝试多个备选标签名，取第一个匹配到的
- 让 AI 帮你写备选标签名列表

---

### 第 3 步：提取文本参数（使用寿命、折旧方法）

**输入**：HTML 文件  
**输出**：6 个文本参数

**方法**：用正则表达式搜索关键词

**搜索关键词表**：

| 字段名 | 搜索关键词 | 示例结果 | 处理说明 |
|--------|----------|---------|---------|
| `depreciation_method` | `straight-line` / `declining balance` / `accelerated` | `"straight-line"` | 找到哪个就填哪个 |
| `server_useful_life_years` | `Servers and network assets` 后面的年份 | `"Four to Five years"` | 文本提取 |
| `building_useful_life_years` | `Buildings` 后面的年份 | `"25 to 30 years"` | 文本提取 |
| `equipment_useful_life_years` | `Equipment` / `Furniture` / `Other` 后面的年份 | `"One to Three years"` | 文本提取 |
| `statutory_tax_rate` | `federal statutory income tax rate` / `21%` | `0.21` | 通常是 21% |
| `effective_tax_rate` | `effective tax rate` / `Effective tax rate` | `0.176` | 搜索百分比数字 |
| `employee_count` | `employees` / `headcount` / `workforce` | `67317` | 搜索数字 |

**提取逻辑**（让 AI 帮你完善）：
```python
import re

def extract_text_parameters(html_path):
    """
    从 HTML 中提取文本参数（使用寿命、折旧方法、税率、员工数）
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {}
    
    # 1. 折旧方法：搜索关键词
    if 'straight-line' in content.lower():
        results['depreciation_method'] = 'straight-line'
    elif 'declining balance' in content.lower():
        results['depreciation_method'] = 'declining-balance'
    elif 'accelerated' in content.lower():
        results['depreciation_method'] = 'accelerated'
    else:
        results['depreciation_method'] = None
    
    # 2. 服务器使用寿命：搜索 "Servers and network assets" 附近的年份
    # ... 用正则表达式匹配 ...
    # 示例："Servers and network assets Four to Five years"
    # 提取："4-5" 或 "Four to Five"
    
    # 3. 建筑物使用寿命：搜索 "Buildings" 附近的年份
    # ...
    
    # 4. 有效税率：搜索 "effective tax rate" 附近的百分比
    # 示例："effective tax rate was 17.6%"
    # 提取：0.176
    
    # 5. 员工人数：搜索 "employees" 或 "workforce" 附近的数字
    # 示例："We had a global workforce of 67,317 employees"
    # 提取：67317
    
    return results
```

> **让 AI 帮你写**：把上面的函数 + 搜索关键词表发给 AI，说"帮我完善正则表达式，从 10-K HTML 中提取这些文本参数"。

**文本参数验证**（Meta 2023）：

| 字段名 | 期望值 | 说明 |
|--------|--------|------|
| depreciation_method | `straight-line` | 直线法 |
| server_useful_life_years | `4-5` | 服务器4-5年 |
| building_useful_life_years | `25-30` | 建筑物25-30年 |
| equipment_useful_life_years | `1-3` | 设备1-3年 |
| statutory_tax_rate | `0.21` | 21% |
| effective_tax_rate | `0.176` | 17.6% |
| employee_count | `67317` | 67317人 |

---

### 第 4 步：提取文本布尔特征（Risk Factors）

**输入**：HTML 文件  
**输出**：2 个布尔值（true/false）

**方法**：搜索 Risk Factors 章节中的关键词

```python
def extract_risk_factors(html_path):
    """
    从 Risk Factors 章节中提取关键词，判断是否存在特定风险
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 Risk Factors 章节（Item 1A）
    # 提取 Risk Factors 章节的文本内容
    # ... 用正则或 BeautifulSoup 定位 Item 1A ...
    
    risk_factors_text = ""  # 提取到的 Risk Factors 文本
    
    # 判断技术淘汰风险
    tech_keywords = ['obsolescence', 'technology obsolescence', 'technological change', 'obsolete']
    tech_obsolescence_mentioned = any(kw in risk_factors_text.lower() for kw in tech_keywords)
    
    # 判断资产减值风险
    impairment_keywords = ['impairment', 'write-down', 'asset impairment', 'impairment of assets']
    impairment_mentioned = any(kw in risk_factors_text.lower() for kw in impairment_keywords)
    
    return {
        'tech_obsolescence_mentioned': tech_obsolescence_mentioned,
        'impairment_mentioned': impairment_mentioned,
        'risk_factors_text': risk_factors_text[:5000]  # 保存前5000字符，供搭档参考
    }
```

> **让 AI 帮你写**：说"帮我写一个函数，从 10-K HTML 文件中提取 Item 1A Risk Factors 章节的文本，然后判断其中是否包含 'obsolescence' 和 'impairment' 关键词"。

**验证**（Meta 2023）：
- `tech_obsolescence_mentioned`: `true`（包含 "obsolescence"）
- `impairment_mentioned`: `true`（包含多次 "impairment"）

---

### 第 5 步：计算衍生指标（28个）

**输入**：提取到的 25 个核心指标  
**输出**：28 个衍生计算指标

**不需要从财报提取，用 Python 直接计算**：

```python
def calculate_derived_metrics(data):
    """
    从核心指标计算衍生指标
    data: 包含所有核心指标的字典
    返回: 衍生指标字典
    """
    derived = {}
    
    # 折旧率
    if data.get('ppe_net') and data.get('depreciation'):
        derived['depreciation_rate_ppe'] = data['depreciation'] / data['ppe_net']
    
    # 折旧率（总资产）
    if data.get('total_assets') and data.get('depreciation'):
        derived['depreciation_rate_total_assets'] = data['depreciation'] / data['total_assets']
    
    # 折旧+摊销率
    if data.get('total_assets') and data.get('depreciation') and data.get('amortization'):
        derived['depreciation_amortization_rate'] = (data['depreciation'] + data['amortization']) / data['total_assets']
    
    # 无形资产占比
    if data.get('total_assets') and data.get('intangible_assets_net') and data.get('goodwill'):
        derived['intangible_ratio'] = (data['intangible_assets_net'] + data['goodwill']) / data['total_assets']
    
    # 商誉占比
    if data.get('total_assets') and data.get('goodwill'):
        derived['goodwill_ratio'] = data['goodwill'] / data['total_assets']
    
    # 研发强度
    if data.get('revenue') and data.get('rd_expense'):
        derived['rd_intensity'] = data['rd_expense'] / data['revenue']
    
    # CAPEX/收入
    if data.get('revenue') and data.get('capex_ppe'):
        derived['capex_to_revenue'] = data['capex_ppe'] / data['revenue']
    
    # 资产周转率
    if data.get('total_assets') and data.get('revenue'):
        derived['asset_turnover'] = data['revenue'] / data['total_assets']
    
    # 固定资产周转率
    if data.get('ppe_net') and data.get('revenue'):
        derived['ppe_turnover'] = data['revenue'] / data['ppe_net']
    
    # 折旧覆盖倍数
    if data.get('net_income') and data.get('depreciation'):
        derived['depreciation_coverage'] = data['depreciation'] / data['net_income']
    
    # 资本密集度
    if data.get('total_assets') and data.get('ppe_net'):
        derived['capital_intensity'] = data['ppe_net'] / data['total_assets']
    
    # 净利润率
    if data.get('revenue') and data.get('net_income'):
        derived['net_margin'] = data['net_income'] / data['revenue']
    
    # 营业利润率
    if data.get('revenue') and data.get('operating_income'):
        derived['operating_margin'] = data['operating_income'] / data['revenue']
    
    # 实际有效税率
    if data.get('net_income') and data.get('income_tax_expense'):
        derived['effective_tax_rate'] = data['income_tax_expense'] / (data['net_income'] + data['income_tax_expense'])
    
    # 自由现金流
    if data.get('operating_cash_flow') and data.get('capex_ppe'):
        derived['free_cash_flow'] = data['operating_cash_flow'] - data['capex_ppe']
    
    # 总CAPEX
    if data.get('capex_ppe') and data.get('finance_lease_payments'):
        derived['total_capex'] = data['capex_ppe'] + data['finance_lease_payments']
    
    # 更多指标...（完整28个见上文）
    
    return derived
```

> **让 AI 帮你写**：把上面的 28 个衍生指标公式表发给 AI，说"帮我写一个 Python 函数，从输入的字典中计算这 28 个衍生指标，注意处理 None 和除以零的情况"。

---

## 四、完整 JSON 输出格式

你的脚本最终输出这个格式的 JSON 文件：

```json
{
  "metadata": {
    "ticker": "META",
    "company_name": "Meta Platforms Inc.",
    "sector": "Technology",
    "fiscal_year": 2023,
    "report_date": "2024-02-02",
    "source_url": "https://www.sec.gov/Archives/edgar/data/1326801/000132680124000012/meta-20231231.htm",
    "extraction_date": "2025-07-19",
    "extracted_by": "script_v1",
    "cik": "0001326801"
  },
  "balance_sheet": {
    "total_assets": 229623,
    "ppe_net": 96587,
    "ppe_gross": null,
    "accumulated_depreciation": null,
    "construction_in_progress": null,
    "intangible_assets_net": 788,
    "goodwill": 20654,
    "cash_and_equivalents": null,
    "total_liabilities": null,
    "shareholders_equity": null
  },
  "income_statement": {
    "revenue": 134902,
    "cost_of_revenue": null,
    "gross_profit": null,
    "rd_expense": 38483,
    "rd_capitalized": null,
    "sg_and_a": null,
    "operating_income": 46751,
    "income_tax_expense": 8330,
    "net_income": 39098,
    "impairment_loss": null,
    "diluted_eps": 14.87
  },
  "cash_flow_statement": {
    "operating_cash_flow": 57683,
    "depreciation": 11178,
    "amortization": 161,
    "depreciation_and_amortization": 11339,
    "capex_ppe": 27266,
    "finance_lease_payments": null,
    "total_capex": null,
    "proceeds_from_ppe_sales": 221,
    "free_cash_flow": null
  },
  "accounting_policies": {
    "depreciation_method": "straight-line",
    "server_useful_life_years": "4-5",
    "building_useful_life_years": "25-30",
    "equipment_useful_life_years": "1-3",
    "software_amortization_years": null,
    "goodwill_impairment_test": "annual",
    "statutory_tax_rate": 0.21,
    "effective_tax_rate": 0.176,
    "employee_count": 67317
  },
  "text_features": {
    "tech_obsolescence_mentioned": true,
    "impairment_mentioned": true,
    "risk_factors_text": "[Risk Factors章节前5000字符]"
  },
  "derived_metrics": {
    "depreciation_rate_ppe": 0.1270,
    "depreciation_rate_total_assets": 0.0487,
    "amortization_rate": 0.0007,
    "depreciation_amortization_rate": 0.0494,
    "intangible_ratio": 0.0934,
    "goodwill_ratio": 0.0900,
    "rd_intensity": 0.2853,
    "rd_capitalization_rate": null,
    "capex_to_revenue": 0.2021,
    "capex_to_ppe_net": null,
    "asset_turnover": 0.5878,
    "ppe_turnover": 1.3967,
    "accumulated_depreciation_rate": null,
    "net_ppe_rate": null,
    "depreciation_coverage": 0.2860,
    "capital_intensity": 0.4207,
    "gross_margin": null,
    "operating_margin": 0.3466,
    "net_margin": 0.2900,
    "server_depreciation_ratio": null,
    "cip_to_ppe": null,
    "ppe_growth_rate": null,
    "depreciation_growth_rate": null,
    "revenue_growth_rate": null,
    "net_income_growth_rate": null,
    "effective_tax_rate": 0.176,
    "ppe_per_employee": null
  }
}
```

> **规则**：
> - 提取到的数值直接填
> - 提取不到的填 `null`（JSON 中的 null）
> - 所有金额统一为**百万美元**（单位：millions）
> - 比率统一为**小数**（如 0.1270 表示 12.70%）
> - 年份/人数等文本提取为**字符串**（如 `"4-5"`）

---

## 五、验证清单（用 Meta 2023 验证脚本）

脚本写完后，用 Meta 2023 的数据跑一遍，检查以下 13 个检查点：

### 5.1 核心数字检查（12个）

| # | 检查项 | 期望值 | 允许误差 | 状态 |
|---|--------|--------|---------|------|
| 1 | 总资产 | 229,623 | ±1 | ☐ |
| 2 | 固定资产净值 | 96,587 | ±1 | ☐ |
| 3 | 无形资产净值 | 788 | ±1 | ☐ |
| 4 | 商誉 | 20,654 | ±1 | ☐ |
| 5 | 收入 | 134,902 | ±1 | ☐ |
| 6 | 营业利润 | 46,751 | ±1 | ☐ |
| 7 | 净利润 | 39,098 | ±1 | ☐ |
| 8 | 研发费用 | 38,483 | ±1 | ☐ |
| 9 | 折旧费用 | 11,178 | ±1 | ☐ |
| 10 | 摊销费用 | 161 | ±1 | ☐ |
| 11 | CAPEX | 27,266 | ±1 | ☐ |
| 12 | 经营现金流 | 57,683 | ±1 | ☐ |

### 5.2 文本参数检查（7个）

| # | 检查项 | 期望值 | 状态 |
|---|--------|--------|------|
| 13 | 折旧方法 | `straight-line` | ☐ |
| 14 | 服务器寿命 | `4-5` 或 `Four to Five` | ☐ |
| 15 | 建筑物寿命 | `25-30` 或 `25 to 30` | ☐ |
| 16 | 法定税率 | `0.21` 或 `21%` | ☐ |
| 17 | 有效税率 | `0.176` 或 `17.6%` | ☐ |
| 18 | 员工人数 | `67317` | ☐ |
| 19 | 技术淘汰风险 | `true` | ☐ |
| 20 | 减值风险 | `true` | ☐ |

### 5.3 衍生指标检查（8个）

| # | 检查项 | 计算方式 | 期望值 | 允许误差 | 状态 |
|---|--------|---------|--------|---------|------|
| 21 | 折旧率（总资产） | 11,178 / 229,623 | 0.0487 | ±0.001 | ☐ |
| 22 | 折旧率（固定资产） | 11,178 / 96,587 | 0.1157 | ±0.001 | ☐ |
| 23 | 无形资产占比 | (788 + 20,654) / 229,623 | 0.0934 | ±0.001 | ☐ |
| 24 | 研发强度 | 38,483 / 134,902 | 0.2853 | ±0.001 | ☐ |
| 25 | CAPEX/收入 | 27,266 / 134,902 | 0.2021 | ±0.001 | ☐ |
| 26 | 资产周转率 | 134,902 / 229,623 | 0.5878 | ±0.001 | ☐ |
| 27 | 净利润率 | 39,098 / 134,902 | 0.2900 | ±0.001 | ☐ |
| 28 | 营业利润率 | 46,751 / 134,902 | 0.3466 | ±0.001 | ☐ |

> **全部 28 个检查点通过 = 脚本正确。** 可以开始批量处理其他 9 家公司。

---

## 六、求助方式（遇到问题怎么问 AI）

### 6.1 通用提问模板

当你遇到任何技术问题，用这个模板问 ChatGPT/Kimi：

```
我正在做一个财务数据提取项目，需要从 SEC EDGAR 的 10-K 年报 HTML 文件中提取 XBRL 数据。

【问题描述】：
[描述你遇到的具体问题]

【相关代码】：
```python
[贴你的代码]
```

【相关数据】：
[贴 HTML 片段或标签内容]

【期望结果】：
[描述你希望输出什么]

【实际结果】：
[描述实际输出什么，如果有错误贴错误信息]

请帮我解决。我不需要金融知识解释，只需要技术实现代码。
```

### 6.2 常见问题快速提问

| 问题 | 提问方式 |
|------|---------|
| SEC 网站返回 403 | "SEC EDGAR 请求返回 403 Forbidden，需要加什么请求头？" |
| XBRL 标签找不到 | "BeautifulSoup 找不到 `ix:nonfraction` 标签，但实际 HTML 中有，怎么解决？" |
| Scale 属性搞不懂 | "XBRL 标签有 scale 属性（6, 9, 0, -2），分别代表什么单位？" |
| 正则表达式写不对 | "从 HTML 文本中提取 'Servers and network assets Four to Five years' 中的 'Four to Five'，用 Python 正则怎么写？" |
| JSON 格式问题 | "Python 字典怎么保存为带缩进的 JSON 文件？" |
| 缺失值处理 | "Python 中 if data.get('x') 返回 None，怎么避免除以零错误？" |
| 多公司批量处理 | "怎么写 Python 循环，依次处理 10 家公司的数据？" |
| 代码结构问题 | "怎么把下载、提取、计算、保存四个步骤写成模块化函数？" |

### 6.3 你也可以直接问项目负责人（你的搭档）

| 问题类型 | 问搭档 | 问 AI |
|---------|------|------|
| 这个指标是什么意思？ | ✅ 问搭档 | ❌ 不需要问 AI |
| 这个标签名对不对？ | ✅ 问搭档 | ⚠️ 可以查 SEC 官网 |
| 这个数字合理吗？ | ✅ 问搭档 | ❌ AI 不懂金融 |
| 这段代码怎么写？ | ❌ 搭档不懂代码 | ✅ 问 AI |
| 这个正则怎么写？ | ❌ 搭档不懂代码 | ✅ 问 AI |
| 这个错误怎么解决？ | ❌ 搭档不懂代码 | ✅ 问 AI |
| 这个 JSON 格式对吗？ | ⚠️ 可以问搭档 | ✅ 也可以问 AI |

---

## 七、开发时间规划

| 阶段 | 任务 | 预计时间 | 交付物 |
|------|------|---------|--------|
| **第 1 天** | 环境搭建 + 下载 Meta 10-K | 2 小时 | `data/raw/META_2023_10k.html` |
| **第 2 天** | 写 XBRL 数字提取脚本 | 4 小时 | 能提取 12 个数字指标 |
| **第 3 天** | 写文本参数提取脚本 | 3 小时 | 能提取 6 个文本参数 |
| **第 4 天** | 写 Risk Factors 提取 + 衍生计算 | 3 小时 | 能输出完整 JSON |
| **第 5 天** | 验证脚本（用 Meta 2023） | 2 小时 | 28 个检查点全部通过 |
| **第 6-7 天** | 批量处理前 5 家公司 | 4 小时 | 5 个 JSON 文件 |
| **第 2 周** | 处理剩余 5 家 + 优化脚本 | 8 小时 | 10 个 JSON 文件 |

> **总时间**：约 2 周（每天 2-3 小时），完成 10 家公司的数据提取。

---

## 八、最终交付物

你完成这个项目后，需要提交：

1. **Python 脚本文件**（`src/data_extractor/extract_10k.py`）
   - 输入：公司 CIK 代码 + 财年
   - 输出：JSON 文件

2. **10 个 JSON 数据文件**（`data/extracted/{ticker}_{year}.json`）
   - 每家公司的完整数据

3. **验证报告**（`docs/validation_report.md`）
   - 28 个检查点的验证结果

4. **使用说明**（`docs/extractor_usage.md`）
   - 搭档可以用你的脚本提取新公司的数据

---

> **最后提醒**：你不需要懂金融，只需要按清单提取数字。有任何技术问题问 AI，有任何指标含义问题问搭档。分工明确，效率最高！

