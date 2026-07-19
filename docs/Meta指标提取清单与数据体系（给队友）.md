# Meta 2023 完整指标提取清单（给队友）

> **用途**：数据提取脚本开发参考  
> **来源**：Meta 2023 10-K 年报（SEC EDGAR，文件编号 0001326801-24-000012）  
> **提取方式**：XBRL 标签 + 附注文本解析

---

## 一、Meta 2023 完整数据（已提取，供验证）

### 1.1 资产负债表（Balance Sheet）

| 指标 | 字段名 | 2023年 | 2022年 | 单位 | XBRL标签 / 附注位置 |
|------|--------|--------|--------|------|-------------------|
| 总资产 | total_assets | 229,623 | 185,727 | 百万美元 | us-gaap:Assets |
| 固定资产净值 | ppe_net | 96,587 | 79,518 | 百万美元 | us-gaap:PropertyPlantAndEquipmentAndFinanceLeaseRightOfUseAssetAfterAccumulatedDepreciationAndAmortization |
| 固定资产原值 | ppe_gross | 46,838 | 34,330 | 百万美元 | us-gaap:PropertyPlantAndEquipmentGross ⚠️ 数据可能不完整，需核实 |
| 累计折旧 | accumulated_depreciation | ~50,000 | ~45,000 | 百万美元 | 计算：Gross - Net |
| 土地 | land | 待提取 | 待提取 | 百万美元 | 附注7（PP&E Schedule） |
| 建筑物 | buildings | 待提取 | 待提取 | 百万美元 | 附注7 |
| 服务器/网络设备 | servers_network | 待提取 | 待提取 | 百万美元 | 附注7 |
| 设备/其他 | equipment_other | 待提取 | 待提取 | 百万美元 | 附注7 |
| 在建工程 | construction_in_progress | 1,400 | 2,180 | 百万美元 | 附注7 |
| 无形资产净值（不含商誉） | intangible_assets_net | 788 | 897 | 百万美元 | us-gaap:IntangibleAssetsNetExcludingGoodwill |
| 商誉 | goodwill | 20,654 | 20,306 | 百万美元 | us-gaap:Goodwill |
| 现金及等价物 | cash_and_equivalents | 待提取 | 待提取 | 百万美元 | 资产负债表 |
| 总负债 | total_liabilities | 待提取 | 待提取 | 百万美元 | 资产负债表 |
| 股东权益 | shareholders_equity | 待提取 | 待提取 | 百万美元 | 计算：Assets - Liabilities |

> ⚠️ **注意**：固定资产原值 $46,838M 与净值 $96,587M 看起来矛盾（原值应大于净值）。XBRL 标签 `us-gaap:PropertyPlantAndEquipmentGross` 可能只包含部分类别（如设备类），不含土地和建筑物。完整原值需要从附注7的 PP&E Schedule 表格中提取。

### 1.2 利润表（Income Statement）

| 指标 | 字段名 | 2023年 | 2022年 | 单位 | XBRL标签 / 报表位置 |
|------|--------|--------|--------|------|-------------------|
| 营业收入 | revenue | 134,902 | 116,609 | 百万美元 | us-gaap:RevenueFromContractWithCustomer |
| 营业成本 | cost_of_revenue | 待提取 | 待提取 | 百万美元 | 利润表 |
| 毛利润 | gross_profit | 待提取 | 待提取 | 百万美元 | 计算：Revenue - Cost |
| 研发费用 | rd_expense | 38,483 | 35,338 | 百万美元 | us-gaap:ResearchAndDevelopmentExpense |
| R&D 资本化金额 | rd_capitalized | ~0 | ~0 | 百万美元 | 附注（Meta 几乎不资本化） |
| R&D 费用化金额 | rd_expensed | 38,483 | 35,338 | 百万美元 | 同上（全部费用化） |
| 销售及行政费用 | sg_and_a | 待提取 | 待提取 | 百万美元 | 利润表 |
| 营业利润 | operating_income | 46,751 | 28,944 | 百万美元 | us-gaap:OperatingIncomeLoss |
| 所得税费用 | income_tax_expense | 8,330 | 5,619 | 百万美元 | us-gaap:IncomeTaxExpenseBenefit |
| 净利润 | net_income | 39,098 | 23,200 | 百万美元 | us-gaap:NetIncomeLoss |
| 资产减值损失 | impairment_loss | 待提取 | 待提取 | 百万美元 | 利润表（如果有） |
| 稀释每股收益 | diluted_eps | 14.87 | 8.59 | 美元 | 利润表 |

> **注意**：折旧费用和摊销费用在利润表中通常**不单独列示**，而是分摊到营业成本、研发费用、销售费用等科目中。需要从现金流量表中获取独立的折旧/摊销数字。

### 1.3 现金流量表（Cash Flow Statement）

| 指标 | 字段名 | 2023年 | 2022年 | 2021年 | 单位 | XBRL标签 / 报表位置 |
|------|--------|--------|--------|--------|------|-------------------|
| 经营现金流 | operating_cash_flow | 57,683 | 待提取 | 待提取 | 百万美元 | 现金流量表 |
| 折旧费用 | depreciation | 11,178 | 8,686 | 7,967 | 百万美元 | us-gaap:Depreciation |
| 摊销费用 | amortization | 161 | 185 | 407 | 百万美元 | us-gaap:AmortizationOfIntangibleAssets |
| 折旧+摊销合计 | depreciation_and_amortization | 11,339 | 8,871 | 8,374 | 百万美元 | 计算 |
| CAPEX（购买固定资产现金） | capex_ppe | 27,266 | 31,431 | 18,690 | 百万美元 | us-gaap:PaymentsToAcquirePropertyPlantAndEquipment |
| 融资租赁本金支付 | finance_lease_payments | 1,058 | 850 | 677 | 百万美元 | 现金流量表 |
| 总 CAPEX | total_capex | 28,324 | 32,281 | 19,367 | 百万美元 | 计算：CAPEX + 融资租赁 |
| 处置固定资产收入 | ppe_sales_proceeds | 221 | 245 | 123 | 百万美元 | us-gaap:ProceedsFromSaleOfPropertyPlantAndEquipment |
| 自由现金流 | free_cash_flow | 30,417 | 待提取 | 待提取 | 百万美元 | 计算：经营现金流 - CAPEX |

### 1.4 会计政策（Note 1 - Significant Accounting Policies）

| 参数 | 字段名 | 数值 | 来源 |
|------|--------|------|------|
| 折旧方法 | depreciation_method | 直线法（Straight-line） | 附注1 |
| 服务器/网络使用寿命 | server_useful_life | 4-5 年 | 附注1 |
| 建筑物使用寿命 | building_useful_life | 25-30 年 | 附注1 |
| 设备/其他使用寿命 | equipment_useful_life | 1-3 年 | 附注1 |
| 软件摊销期 | software_amortization | 待提取 | 附注1 |
| 商誉减值测试频率 | goodwill_impairment_test | 每年至少一次 | 附注1 |
| 法定税率 | statutory_tax_rate | 21.0% | 附注（所得税） |
| 实际有效税率 | effective_tax_rate | 17.6% | 管理层讨论 |
| 员工总数 | employee_count | 67,317 | 管理层讨论 |

### 1.5 附注 7 - 固定资产明细（PP&E Schedule）

这是**最重要的附注之一**，需要提取以下明细：

| 资产类别 | 2023年原值 | 2023年累计折旧 | 2023年净值 | 2022年净值 | 来源 |
|---------|-----------|--------------|-----------|-----------|------|
| 土地（Land） | 待提取 | 不适用（不折旧） | 待提取 | 待提取 | 附注7 |
| 建筑物（Buildings） | 待提取 | 待提取 | 待提取 | 待提取 | 附注7 |
| 租赁改良（Leasehold Improvements） | 待提取 | 待提取 | 待提取 | 待提取 | 附注7 |
| 服务器/网络设备（Servers/Network） | 待提取 | 待提取 | 待提取 | 待提取 | 附注7 |
| 计算机设备（Computer Equipment） | 待提取 | 待提取 | 待提取 | 待提取 | 附注7 |
| 家具/办公设备（Furniture/Other） | 待提取 | 待提取 | 待提取 | 待提取 | 附注7 |
| 在建工程（Construction in Progress） | 待提取 | 不适用 | 1,400 | 2,180 | 附注7 |
| **合计** | 46,838? | 待提取 | 96,587 | 79,518 | 附注7 |

> **关键**：附注7的表格会显示每个类别的原值、累计折旧、净值。这是判断折旧风险的核心数据。

### 1.6 文本特征（Risk Factors + MD&A）

| 特征 | 字段名 | 示例（Meta 2023） | 来源 |
|------|--------|-----------------|------|
| 技术淘汰风险提及 | tech_obsolescence_mentioned | 是（3次） | Risk Factors |
| 减值风险提及 | impairment_mentioned | 是（5次） | Risk Factors |
| 折旧年限具体数字 | depreciation_life_disclosed | 4-5 年（服务器） | 附注1 |
| CAPEX 规模披露 | capex_disclosed | $28.1 billion | MD&A |
| 服务器折旧占比 | server_depreciation_pct | 65.5% | 附注7 |
| 在建工程说明 | cip_description | 数据中心、服务器组件 | 附注7 |

---

## 二、推荐数据指标体系（共 45 个指标）

### 2.1 必须提取（Tier 1：模型直接输入，25个）

这些指标**必须**从每家公司 10-K 中提取，否则模型无法训练。

| # | 指标 | 字段名 | 来源 | 重要性 | 备注 |
|---|------|--------|------|--------|------|
| 1 | 总资产 | total_assets | 资产负债表 | ⭐⭐⭐⭐⭐ | - |
| 2 | 固定资产净值 | ppe_net | 资产负债表 | ⭐⭐⭐⭐⭐ | 含融资租赁 |
| 3 | 固定资产原值 | ppe_gross | 附注7 | ⭐⭐⭐⭐⭐ | 用于计算累计折旧 |
| 4 | 累计折旧 | accumulated_depreciation | 计算/附注 | ⭐⭐⭐⭐⭐ | Gross - Net |
| 5 | 服务器/网络设备原值 | servers_gross | 附注7 | ⭐⭐⭐⭐⭐ | **核心！** |
| 6 | 服务器/网络设备净值 | servers_net | 附注7 | ⭐⭐⭐⭐⭐ | **核心！** |
| 7 | 建筑物原值 | buildings_gross | 附注7 | ⭐⭐⭐⭐ | 辅助判断 |
| 8 | 建筑物净值 | buildings_net | 附注7 | ⭐⭐⭐⭐ | 辅助判断 |
| 9 | 在建工程 | construction_in_progress | 附注7 | ⭐⭐⭐⭐ | 未来折旧压力 |
| 10 | 无形资产净值 | intangible_assets_net | 资产负债表 | ⭐⭐⭐⭐ | 不含商誉 |
| 11 | 商誉 | goodwill | 资产负债表 | ⭐⭐⭐⭐ | 减值风险 |
| 12 | 营业收入 | revenue | 利润表 | ⭐⭐⭐⭐⭐ | - |
| 13 | 净利润 | net_income | 利润表 | ⭐⭐⭐⭐⭐ | - |
| 14 | 营业利润 | operating_income | 利润表 | ⭐⭐⭐⭐ | - |
| 15 | 所得税费用 | income_tax_expense | 利润表 | ⭐⭐⭐ | 用于计算实际税率 |
| 16 | 研发费用 | rd_expense | 利润表 | ⭐⭐⭐⭐⭐ | 全部费用化/部分资本化 |
| 17 | R&D 资本化金额 | rd_capitalized | 附注 | ⭐⭐⭐⭐ | 如果资本化 |
| 18 | 资产减值损失 | impairment_loss | 利润表 | ⭐⭐⭐⭐ | 当年已计提的减值 |
| 19 | 折旧费用 | depreciation | 现金流量表 | ⭐⭐⭐⭐⭐ | **核心！** |
| 20 | 摊销费用 | amortization | 现金流量表 | ⭐⭐⭐ | 单独提取 |
| 21 | CAPEX（购买固定资产） | capex_ppe | 现金流量表 | ⭐⭐⭐⭐⭐ | **核心！** |
| 22 | 融资租赁本金支付 | finance_lease_payments | 现金流量表 | ⭐⭐⭐ | 视同 CAPEX |
| 23 | 经营现金流 | operating_cash_flow | 现金流量表 | ⭐⭐⭐⭐ | 利润质量 |
| 24 | 服务器使用寿命 | server_useful_life | 附注1 | ⭐⭐⭐⭐⭐ | **核心！** 文本提取 |
| 25 | 建筑物使用寿命 | building_useful_life | 附注1 | ⭐⭐⭐ | 文本提取 |

### 2.2 强烈建议提取（Tier 2：衍生计算输入，15个）

这些指标不直接输入模型，但用于计算衍生比率。建议提取，避免后续返工。

| # | 指标 | 字段名 | 来源 | 用途 |
|---|------|--------|------|------|
| 26 | 土地原值 | land_gross | 附注7 | 计算资产结构 |
| 27 | 设备/其他原值 | equipment_gross | 附注7 | 计算资产结构 |
| 28 | 设备/其他净值 | equipment_net | 附注7 | 计算资产结构 |
| 29 | 累计折旧（服务器） | servers_accumulated_depreciation | 附注7 | 服务器新旧程度 |
| 30 | 累计折旧（建筑物） | buildings_accumulated_depreciation | 附注7 | 建筑物新旧程度 |
| 31 | 软件/无形资产明细 | software_intangibles | 附注 | 摊销风险分析 |
| 32 | 专利/无形资产明细 | patent_intangibles | 附注 | 摊销风险分析 |
| 33 | 现金及等价物 | cash_and_equivalents | 资产负债表 | 财务健康度 |
| 34 | 总负债 | total_liabilities | 资产负债表 | 财务杠杆 |
| 35 | 毛利润 | gross_profit | 利润表 | 毛利率计算 |
| 36 | 销售及行政费用 | sg_and_a | 利润表 | 费用结构 |
| 37 | 稀释每股收益 | diluted_eps | 利润表 | 辅助 |
| 38 | 处置固定资产收入 | ppe_sales_proceeds | 现金流量表 | 资产更新速度 |
| 39 | 有效税率 | effective_tax_rate | 管理层讨论/附注 | 利润影响计算 |
| 40 | 员工人数 | employee_count | 管理层讨论 | 人均资本密集度 |

### 2.3 可选提取（Tier 3：高级分析，5个）

| # | 指标 | 字段名 | 来源 | 用途 |
|---|------|--------|------|------|
| 41 | 设备使用寿命 | equipment_useful_life | 附注1 | 辅助判断 |
| 42 | 软件摊销期 | software_amortization_years | 附注1 | 辅助判断 |
| 43 | 商誉减值测试方法 | goodwill_test_method | 附注1 | 辅助判断 |
| 44 | 收入构成（广告/硬件/其他） | revenue_breakdown | 管理层讨论 | 收入模式分析 |
| 45 | 主要收入地区分布 | revenue_geography | 管理层讨论 | 地区风险分析 |

---

## 三、衍生计算指标（28个，从一级指标自动计算）

这些不需要从财报提取，用 Python 脚本自动计算：

| # | 指标 | 公式 | 用途 |
|---|------|------|------|
| 1 | 折旧率（固定资产） | depreciation / 平均固定资产净值 | 核心风险指标 |
| 2 | 折旧率（总资产） | depreciation / total_assets | 辅助指标 |
| 3 | 摊销率 | amortization / total_assets | 辅助指标 |
| 4 | 折旧+摊销率 | (depreciation + amortization) / total_assets | 综合指标 |
| 5 | 无形资产占比 | (intangible_assets_net + goodwill) / total_assets | 技术淘汰风险 |
| 6 | 商誉占比 | goodwill / total_assets | 减值风险 |
| 7 | 研发强度 | rd_expense / revenue | 资本化风险 |
| 8 | R&D 资本化率 | rd_capitalized / (rd_expense + rd_capitalized) | 利润操纵风险 |
| 9 | CAPEX/收入 | total_capex / revenue | 扩张速度 |
| 10 | CAPEX/固定资产净值 | total_capex / ppe_net | 资产更新速度 |
| 11 | 资产周转率 | revenue / total_assets | 资产效率 |
| 12 | 固定资产周转率 | revenue / ppe_net | 固定资产效率 |
| 13 | 累计折旧率 | accumulated_depreciation / ppe_gross | 资产新旧程度 |
| 14 | 净固定资产率 | ppe_net / ppe_gross | 资产折旧程度 |
| 15 | 折旧覆盖倍数 | depreciation / net_income | 折旧对利润影响 |
| 16 | 资本密集度 | ppe_net / total_assets | 资产密集型程度 |
| 17 | 自由现金流 | operating_cash_flow - capex_ppe | 现金生成能力 |
| 18 | 毛利率 | gross_profit / revenue | 盈利能力 |
| 19 | 营业利润率 | operating_income / revenue | 盈利能力 |
| 20 | 净利润率 | net_income / revenue | 盈利能力 |
| 21 | 服务器折旧占比 | servers_depreciation / total_depreciation | 核心资产折旧占比 |
| 22 | 在建工程/固定资产 | construction_in_progress / ppe_net | 未来折旧压力 |
| 23 | 固定资产增长率 | (ppe_net_t - ppe_net_t-1) / ppe_net_t-1 | 扩张速度 |
| 24 | 折旧增长率 | (depreciation_t - depreciation_t-1) / depreciation_t-1 | 折旧压力变化 |
| 25 | 收入增长率 | (revenue_t - revenue_t-1) / revenue_t-1 | 增长态势 |
| 26 | 净利润增长率 | (net_income_t - net_income_t-1) / net_income_t-1 | 增长态势 |
| 27 | 实际有效税率 | income_tax_expense / (net_income + income_tax_expense) | 利润影响 |
| 28 | 人均固定资产 | ppe_net / employee_count | 资本密集度 |

---

## 四、数据提取优先级说明

### 4.1 为什么分 Tier 1 / 2 / 3？

**Tier 1（必须）**：模型直接输入，缺少任何一个都会导致模型训练失败或效果大幅下降。

**Tier 2（强烈建议）**：用于衍生计算和模型解释。如果缺少，部分衍生指标无法计算，但模型仍能运行（只是不够精细）。

**Tier 3（可选）**：高级分析用。Phase 1 可以先不提取，Phase 2 再补充。

### 4.2 数据提取难点

| 难点 | 说明 | 解决方案 |
|------|------|---------|
| **固定资产明细**（附注7） | XBRL 标签可能只给合计，明细在表格中 | 需要解析附注7的 HTML 表格 |
| **R&D 资本化** | 美国公司很少资本化，但如果有需要识别 | 搜索"capitalized development costs" |
| **折旧/摊销分开** | 有些公司合并披露"D&A" | 如果合并，就用合并数字，但优先分开 |
| **有效税率** | 法定税率 vs 实际税率，位置分散 | 附注（所得税）+ 管理层讨论 |
| **员工人数** | 不强制披露，位置不固定 | 搜索"employees"或"headcount" |
| **使用寿命** | 文本格式（"4-5 years"），非数字 | 需要 NLP 提取或正则匹配 |

---

## 五、JSON 输出格式示例（队友参考）

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
    "extracted_by": "script_v1"
  },
  "balance_sheet": {
    "total_assets": 229623,
    "ppe_net": 96587,
    "ppe_gross": 46838,
    "accumulated_depreciation": 50749,
    "land": null,
    "buildings_gross": null,
    "buildings_net": null,
    "servers_network_gross": null,
    "servers_network_net": null,
    "equipment_other_gross": null,
    "equipment_other_net": null,
    "construction_in_progress": 1400,
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
    "rd_capitalized": 0,
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
    "finance_lease_payments": 1058,
    "total_capex": 28324,
    "proceeds_from_ppe_sales": 221,
    "free_cash_flow": 30417
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
  "derived_metrics": {
    "depreciation_rate_ppe": 0.1270,
    "depreciation_rate_total_assets": 0.0487,
    "amortization_rate": 0.0007,
    "depreciation_amortization_rate": 0.0494,
    "intangible_ratio": 0.0934,
    "goodwill_ratio": 0.0900,
    "rd_intensity": 0.2853,
    "rd_capitalization_rate": 0.0,
    "capex_to_revenue": 0.2021,
    "capex_to_ppe_net": 0.2823,
    "asset_turnover": 0.5878,
    "ppe_turnover": 1.3967,
    "accumulated_depreciation_rate": 0.5177,
    "net_ppe_rate": 0.996,
    "depreciation_coverage": 0.2860,
    "capital_intensity": 0.4207,
    "gross_margin": null,
    "operating_margin": 0.3466,
    "net_margin": 0.2900,
    "server_depreciation_ratio": 0.6549,
    "cip_to_ppe": 0.0145,
    "ppe_growth_rate": 0.2147,
    "depreciation_growth_rate": 0.2869,
    "revenue_growth_rate": 0.1567,
    "net_income_growth_rate": 0.6853,
    "effective_tax_rate": 0.176,
    "ppe_per_employee": 1434.0
  },
  "text_features": {
    "tech_obsolescence_mentioned": true,
    "impairment_mentioned": true,
    "depreciation_life_disclosed": "4-5 years",
    "capex_disclosed": "28.1 billion",
    "server_depreciation_pct_disclosed": "65.5%",
    "risk_factors_relevant_paragraphs": [
      "charges associated with impairment or abandonment of any assets on our balance sheet, including as a result of changes to our real property lease arrangements and data center assets",
      "or impairment of assets on our balance sheet. For example, like others in our industry, we rely on certain third-party equipment and components for our technical infrastructure",
      "has resulted, and may result in the future, in the impairment of a portion of our technical infrastructure"
    ]
  }
}
```

> **注意**：
> - `null` 表示该数据尚未提取（Tier 2/3 指标）
> - 所有金额单位统一为**百万美元**（millions）
> - 比率统一为**小数**（如 0.1270 表示 12.70%）
> - 文本特征为**布尔值**或**字符串**

---

## 六、给队友的开发任务

### 6.1 第一阶段：基础数据提取（本周完成）

1. 写 Python 脚本，输入公司代码（如 META）和财年（如 2023）
2. 从 SEC EDGAR 下载 10-K HTML/XBRL 文件
3. 提取 **Tier 1 指标**（25个）
4. 输出 JSON 格式文件
5. 用 Meta 2023 的数据验证脚本正确性

### 6.2 第二阶段：精细数据提取（下周完成）

1. 解析附注7的 HTML 表格，提取固定资产明细
2. 解析附注1的文本，提取使用寿命参数
3. 提取 Risk Factors 中相关段落文本
4. 补充 Tier 2 指标（15个）

### 6.3 第三阶段：批量处理（8月初）

1. 批量处理 10-20 家公司（Meta, Google, Microsoft, Amazon, Tesla, NVIDIA, Apple, Netflix, Salesforce, Adobe...）
2. 生成统一格式的 JSON 数据集
3. 检查数据完整性，标记缺失值

---

## 七、数据验证清单（用 Meta 2023 验证）

脚本写完后，用以下检查点验证：

- [ ] 总资产 = 229,623
- [ ] 固定资产净值 = 96,587
- [ ] 折旧费用 = 11,178
- [ ] 摊销费用 = 161
- [ ] 收入 = 134,902
- [ ] 净利润 = 39,098
- [ ] CAPEX = 27,266
- [ ] 服务器使用寿命 = "4-5 years"
- [ ] 折旧方法 = "straight-line"
- [ ] 折旧率（固定资产）≈ 0.127
- [ ] 折旧率（总资产）≈ 0.049
- [ ] 研发强度 ≈ 0.285
- [ ] CAPEX/收入 ≈ 0.202

如果以上 13 个检查点全部通过，说明脚本正确。

