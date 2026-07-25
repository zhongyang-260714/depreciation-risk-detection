# Salesforce, Inc.（CRM）折旧风险评分依据与推断链——三年合并核对

> 生成时间：2026-07-24 14:55 ｜ 用途：项目负责人逐条核对评分依据
> 核对方法：打开 `D:\depreciation-risk-detection\data\raw\` 对应 10-K HTML，用 Ctrl+F 搜原文摘录，确认 ①原文存在且逐字一致 ②推断链逻辑成立 ③分数符合锚点
> ⚠️ 本文档为核对用只读文档，**不修改 JSON**；任何分数调整以你的核对结论为准，助手不得自行改分。

---

## 〇、评分锚点（所有公司共用，META=4.0 为基准）

| 维度 | 权重 | 5 分 | 4 分 | 3 分 | 2 分 | 1 分 |
|---|---|---|---|---|---|---|
| D1 折旧年限 vs 技术实际寿命 | 0.25 | ≥6 年 | 4-6 年（vs 迭代 1-2 年） | 3-4 年 | 2-3 年 | ≤2 年/加速折旧 |
| D2 会计政策保守性 | 0.20 | 本期延长年限+未来适用 | 历史有延长记录 | prospectively 无延长 | 有追溯/缩短 | 主动缩短年限 |
| D3 减值风险触发 | 0.20 | 本期大额实际减值+多处直接信号 | 有实际减值或≥3处直接信号 | 仅间接信号 | 稀少间接 | 基本无 |
| D4 CAPEX 强度 | 0.20 | ≥25% | 15-25% | 8-15% | 3-8% | <3% |
| D5 行业竞争/技术替代 | 0.15 | 算力竞赛主力、直接运营海量 GPU | 大量运营 GPU/数据中心 | 部分暴露/跟随竞争 | 间接暴露（卖芯片） | 基本无暴露 |

风险等级映射：≥4 高风险 🔴 ｜ 3–3.9 中高风险 🟠 ｜ 2–2.9 中风险 🟡 ｜ <2 低风险 🟢

---

## 一、Salesforce, Inc. 2023（截至 2023-01-31） → 综合 2.10 🟡 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（11 条信号中最关键的 3 条）

**CRM-FY2023-SIG-001【MEDIUM】** — Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies（Note 1. Property and Equipment (HTML lines 4080-4087)）
> Depreciation is calculated on a straight-line basis over the estimated useful lives of those assets as follows: Buildings and building improvements 10 to 40 years Computers, equipment and software 3 to 5 years Furniture and fixtures 5 years Leasehold improvements Shorter of the estimated lease term or 10 years The Company estimates the useful lives of property and equipment upon initial recognition and periodically evaluates the useful lives and whether events or changes in circumstances warrant a revision to the useful lives.

推断链：
- 官方披露：computers, equipment and software 折旧 3-5 年（直线法），与 FY2024 同文
- 技术迭代周期约 1-2 年，年限错配 1.5-5 倍（弱于 GOOGL 3-6 倍、META 2-2.5 倍）
- PPE 净值 $3,702M 仅占总资产 3.7%；FY2023 固定资产折旧摊销 $903M 仅为收入的 2.9%
- 即使按最悲观 2 年重估，折旧增量对 $1,030M 营业利润的冲击也在低个位数百分比内
- Result: 年限假设存在温和错配，但资产基数太小，折旧操纵空间结构性受限

**CRM-FY2023-SIG-003【MEDIUM】** — Notes to Consolidated Financial Statements - Note 10. Restructuring（Note 10. Restructuring (HTML lines 4541-4552); corroborated in income statement Restructuring line $828M (L3758) and MD&A (L3209-3214)）
> In January 2023, the Company announced a restructuring plan (the Plan) intended to reduce operating costs, improve operating margins, and continue advancing the Company's ongoing commitment to profitable growth. The Plan includes a reduction of the Company's workforce and select real estate exits and office space reductions within certain markets. ... The Company incurred approximately $ 828 million in charges in connection with the Plan in fiscal 2023, which consists of $ 683 million in charges related to employee transition, severance payments, employee benefits and share-based compensation and $ 145 million in exit charges associated with the office space reductions.

推断链：
- FY2023 重组费用 $828M = 裁员相关 $683M + 办公空间削减退出 $145M（FY2022/FY2021 均为 0）
- 计划 2023 年 1 月（FY2023 Q4）宣布：裁员行动预计 FY2024 末基本完成，不动产行动预计 FY2026 全部完成
- 办公空间退出费用 = 对租赁/办公资产原使用计划的修正，属'实际资产冲销'但不在折旧核心资产类别
- computers/equipment/software 未受任何减值（Note 5 无减值科目，原值反增 39.8%）
- Result: 存在小规模'实际减值类'证据，但远离折旧风险的目标资产；跨年口径与 FY2024 确认版 SIG-003 一致

**CRM-FY2023-SIG-007【MEDIUM】** — Notes to Consolidated Financial Statements - Note 7. Business Combinations / Note 8. Intangible Assets and Goodwill（Note 7. Business Combinations - Slack (HTML lines 4463-4474); Note 8. Goodwill table (HTML lines 4517-4518)）
> The acquisition date fair value of the consideration transferred for Slack was approximately $ 27.1 billion... Goodwill 21,410 Intangible assets 6,350... Balance as of January 31, 2022 $ 47,937 Traction on Demand 293 Other acquisitions and adjustments (1) 338 Balance as of January 31, 2023 $ 48,568.

推断链：
- Slack（2021-07 收购，对价 $27.1B）→ 商誉 $21,410M、无形资产 $6,350M
- FY2023 商誉变动：47,937 + Traction 293 + 其他调整 338 = 48,568，无减值
- 同期公司确认重组 $828M、股价承压，商誉仍通过年度测试
- 收购技术开发净值 $2,373M、加权平均剩余摊销期 3.8 年——摊销节奏已贴近技术寿命
- Result: 商誉风险真实存在但 FY2023 未触发；与折旧风险是两条独立敞口

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 计算机设备/软件折旧年限 3-5 年（Note 1，L4083），与 FY2024 确认版逐字一致，落在锚点 3-5 年档→3 分。上限 5 年触及 4-6 年档边缘，但整体短于 GOOGL 的 6 年、与 META 4-5 年相当。错配比... |
| D2 政策保守性 | **3** | 全文 'prospectively'/'change in estimate'/'change in accounting estimate' 零命中：FY2023 本期无折旧年限变更，按锚点'无变更→3 分'，与 FY2024 一致。20... |
| D3 减值触发 | **2** | 本期有真实但小规模的资产相关冲销：重组中办公空间削减退出费用 $145M（含 ROU 相关非现金项目，未单列），性质类似 GOOGL 的 office exit，但规模小于 FY2024 的 $447M 且全部集中在租赁/办公资产；战略投资... |
| D4 CAPEX 强度 | **1** | CAPEX/收入 = $798M / $31,352M = 2.55%，落在锚点 <5% 档→1 分，与 FY2024（2.11%→1）同档。对比：META 20.2%、GOOGL 10.5%。固定资产折旧摊销 $903M 仅为收入的 2.... |
| D5 竞争替代 | **1** | Salesforce 不直接运营 GPU 集群：算力构建在租用的 co-location 机房与公有云合作伙伴（Hyperforce）之上，并明确'continue to move to cloud computing platform p... |

**验算**：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 3×0.25=0.75 + 3×0.20=0.60 + 2×0.20=0.40 + 1×0.20=0.20 + 1×0.15=0.15 = **2.10** ✓
**置信度**：0.85 — 低风险结论三向互证：(1) 定量：CAPEX/收入 2.6%、PPE 占总资产 3.7%；(2) 定性：全文无年限变更、无 obsolescence 表述；(3) 结构性：算力租用模式将技术迭代风险转移给供应商。与 FY2024 确认版逐维对照后保持同分（D1=3/D2=3/D3=2/D4=1/D5=1→2.10），因两年政策与风险事实无实质变化。FY2023 特有事实（1 月重组计划当期确认 $828M、战略投资减值 $491M、Slack 商誉完整）均不改变五维档位。加权计算：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 2.10。

---

## 二、Salesforce, Inc. 2024（截至 2024-01-31） → 综合 2.10 🟡 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（7 条信号中最关键的 3 条）

**CRM-FY2024-SIG-001【MEDIUM】** — Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies（Note 1. Property and Equipment (HTML lines 4160-4167)）
> Depreciation is calculated on a straight-line basis over the estimated useful lives of those assets as follows: Buildings and building improvements 10 to 40 years; Computers, equipment and software 3 to 5 years; Furniture and fixtures 5 years; Leasehold improvements Shorter of the estimated lease term or 10 years. The Company estimates the useful lives of property and equipment upon initial recognition and periodically evaluates the useful lives and whether events or changes in circumstances warrant a revision to the useful lives.

推断链：
- 官方披露：computers, equipment and software 折旧 3-5 年（直线法）
- 技术迭代周期约 1-2 年，年限错配 1.5-5 倍（弱于 GOOGL 3-6 倍、META 2-2.5 倍）
- PPE 净值 $3,689M 仅占总资产 3.7%；FY2024 固定资产折旧摊销 $1.1B 仅为收入的 3.2%
- 即使按最悲观 2 年重估，折旧增量对 $5,011M 营业利润的冲击也在个位数百分比内
- Result: 年限假设存在温和错配，但资产基数太小，折旧操纵空间结构性受限

**CRM-FY2024-SIG-003【MEDIUM】** — Notes to Consolidated Financial Statements - Note 10. Restructuring（Note 10. Restructuring (HTML lines 4565-4580); corroborated in MD&A Highlights (lines 2919-2922) and MD&A Restructuring (lines 3094-3103)）
> In January 2023, the Company announced a restructuring plan (the "Restructuring Plan") intended to reduce operating costs, improve operating margins and continue advancing the Company's ongoing commitment to profitable growth. This plan included a reduction of the Company's workforce and select real estate exits and office space reductions within certain markets... Charges: Workforce Reduction $541 / Office Space Reductions $447 / Total $988 (fiscal 2024); Non-cash items: $(445) fiscal 2024.

推断链：
- FY2024 重组费用 $988M = 裁员 $541M + 办公空间削减 $447M
- 非现金项目 $445M（其中办公空间 $418M）= 租赁 ROU 资产的实际冲销
- 性质与 GOOGL 的 office space exit + accelerated depreciation 相同：承认部分资产原摊销进度过慢
- 但对象全部为办公/租赁资产，computers/equipment/software 未受任何减值
- Result: 存在小规模的'实际减值'证据，但不在折旧风险的核心资产类别上

**CRM-FY2024-SIG-006【MEDIUM】** — Item 1A. Risk Factors - Acquisitions（Item 1A. Risk Factors - Risks related to acquisitions (HTML lines 1011-1014)）
> difficulties in managing, or potential write-offs of, acquired assets, and potential financial and credit risks associated with acquired customers; negative impact to our results of operations because of the depreciation and amortization of acquired intangible assets, fixed assets and operating lease right-of-use assets

推断链：
- 风险因素自认：收购资产可能 write-off，收购无形/固定/ROU 资产摊销拖累利润
- FY2024 收购无形资产摊销 $1,869M（COGS $978M + M&S $891M），是固定资产折旧（$1.1B）的 1.7 倍
- Note 8：收购技术开发净值 $1,416M，加权平均剩余摊销期 2.2 年——摊销已贴近技术寿命
- 商誉 $48.6B 不摊销、仅年度测试，是未来最大一次性减值来源
- Result: 若项目把口径扩展到'广义摊销风险'，Salesforce 的敞口在并购端而非设备折旧端

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 计算机设备/软件折旧年限 3-5 年，落在锚点 3-4 年档（→3 分），上限 5 年虽触及 4-6 年档边缘，但整体短于 GOOGL 的 6 年、与 META 4-5 年相当或略优。错配比约 1.5-5 倍。更重要的是资产基数极小（PPE... |
| D2 政策保守性 | **3** | 全文 'prospectively'/'change in estimate' 零命中：本期无折旧年限变更，按锚点'无变更→3 分'。在 2023 年 AI 军备竞赛中，GOOGL（4→6 年，+$3.0B 净利）与 MSFT（4→6 年）... |
| D3 减值触发 | **2** | 本期有真实但小规模的资产相关冲销：重组中办公空间削减 $447M（含非现金 ROU 冲销约 $418M），性质类似 GOOGL 的 office exit，但规模更小且全部集中在租赁/办公资产；战略投资减值及下调 $465M 非 PP&E。... |
| D4 CAPEX 强度 | **1** | CAPEX/收入 = $736M / $34,857M = 2.11%，落在锚点 <3% 档（→1 分），与预期一致。对比：META 20.2%（4 分）、GOOGL 10.5%（3 分）。固定资产折旧摊销 $1.1B 仅为收入的 3.2%... |
| D5 竞争替代 | **1** | Salesforce 不直接运营 GPU 集群：AI 能力（Einstein/Agentforce）构建在租用的第三方机房与公有云合作伙伴之上，并明确'continue to move to cloud computing platform... |

**验算**：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 3×0.25=0.75 + 3×0.20=0.60 + 2×0.20=0.40 + 1×0.20=0.20 + 1×0.15=0.15 = **2.10** ✓
**置信度**：0.85 — 低风险结论有三向互证：(1) 定量：CAPEX/收入 2.1%、PPE 占总资产 3.7%；(2) 定性：全文无年限变更、无 obsolescence 表述；(3) 结构性：算力租用模式将技术迭代风险转移给供应商。低分是证据支持的结论而非证据缺失。扣分不确定性主要在 D1（3-5 年跨度跨两档锚点）与 D3（重组非现金冲销的规模判断）。加权计算：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 2.10。

---

## 三、Salesforce, Inc. 2025（截至 2025-01-31） → 综合 2.10 🟡 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（10 条信号中最关键的 3 条）

**CRM-FY2025-SIG-001【MEDIUM】** — Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies（Note 1. Property and Equipment (HTML lines 4007-4014)）
> Depreciation is calculated on a straight-line basis over the estimated useful lives of those assets as follows: Buildings and building improvements 10 to 40 years; Computers, equipment and software 3 to 5 years; Furniture and fixtures 5 years; Leasehold improvements Shorter of the estimated lease term or 10 years. The Company estimates the useful lives of property and equipment upon initial recognition and periodically evaluates the useful lives and whether events or changes in circumstances warrant a revision to the useful lives.

推断链：
- 官方披露：computers, equipment and software 折旧 3-5 年（直线法），与 FY2024 逐字一致
- 技术迭代周期约 1-2 年，年限错配 1.5-5 倍（锚点档位不变）
- PPE 净值 $3,236M 仅占总资产 3.1%，较 FY2024（3.7%）进一步下降
- FY2025 固定资产折旧摊销 $1.0B 仅为收入的 2.6%（FY2024 为 3.2%）
- Result: 年限档位不变、基数缩小，D1 锚点维持 3 分

**CRM-FY2025-SIG-007【MEDIUM】** — Item 1A. Risk Factors - Acquisitions; Note 8. Intangible Assets and Goodwill（Item 1A. Risk Factors - Risks related to acquisitions (HTML lines 985-989); Note 8 (HTML lines 4433-4435)）
> difficulties in managing, or potential write-offs of, acquired assets, and potential financial and credit risks associated with acquired customers; negative impact to our results of operations because of the depreciation and amortization of acquired intangible assets, fixed assets and operating lease right-of-use assets

推断链：
- 风险因素自认：收购资产可能 write-off，收购无形/固定/ROU 资产摊销拖累利润
- FY2025 收购无形资产摊销 $1,651M，是固定资产折旧（$1.0B）的 1.65 倍
- Note 8：收购技术开发剩余摊销期 0.9 年（FY2024 为 2.2 年）——摊销已贴近甚至快于技术寿命
- FY2025 三笔新收购（Own/Spiff/Zoomin）新增商誉约 $2.4B，商誉敞口扩大至 $51.3B
- Result: '类折旧'风险继续集中在并购会计端，且摊销假设偏保守而非乐观

**CRM-FY2025-SIG-002【LOW】** — Full-text keyword scan (XBRL noise excluded)（Full document scan of crm_fy2025_10k.html (4,927 lines; plain-text extraction via Python tag-stripping, errors='replace')）
> (Zero hits) FY2025 10-K 全文（去标签纯文本 4,927 行）中 'prospectively'、'change in estimate'、'change in accounting estimate' 均为 0 命中——本期未发生折旧年限估计变更，与 FY2024 确认版扫描结果一致。

推断链：
- 全文 0 命中 'prospectively' / 'change in estimate'（去标签后逐行扫描）
- 固定资产折旧摊销 $1.1B→$1.0B 与 PPE 原值 $6,841M→$6,918M（+1.1%）方向正常，无'资产增、折旧降'异常
- 连续两年（FY2024、FY2025）无变更，排除'偶发遗漏'假设
- Result: D2 按锚点'无变更→3 分'，与 FY2024 确认版一致

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 锚点对照 FY2024 确认版（D1=3）：计算机设备/软件折旧年限 3-5 年逐字未变（Note 1，L4009-4010），落在锚点 3-5 年档→3 分。错配比约 1.5-5 倍不变。资产基数进一步缩小（PPE 净值占总资产由 3.7... |
| D2 政策保守性 | **3** | 锚点对照 FY2024 确认版（D2=3）：全文 'prospectively'/'change in estimate'/'change in accounting estimate' 连续第二年 0 命中，本期无折旧年限变更→3 分。A... |
| D3 减值触发 | **2** | 锚点对照 FY2024 确认版（D3=2）：本期资产相关冲销进一步收缩——重组中办公空间削减仅 $75M（非现金 $75M，FY2024 为 $447M/$418M）；战略投资减值及下调 $583M 仍为非 PP&E。无任何计算设备减值、无... |
| D4 CAPEX 强度 | **1** | 锚点对照 FY2024 确认版（D4=1）：CAPEX/收入 = $658M / $37,895M = 1.74%，落在锚点 <5% 档（→1 分），且较 FY2024（2.11%）进一步下降。固定资产折旧摊销 $1.0B 仅为收入的 2.... |
| D5 竞争替代 | **1** | 锚点对照 FY2024 确认版（D5=1）：任务特别关注的'Agentforce 是否改变基础设施策略'经文件事实检验为否——10-K 未披露任何自有 GPU 集群建设；风险因素自认 AI 部署推高算力需求（SIG-006），但应对路径是 ... |

**验算**：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 3×0.25=0.75 + 3×0.20=0.60 + 2×0.20=0.40 + 1×0.20=0.20 + 1×0.15=0.15 = **2.10** ✓
**置信度**：0.88 — 与 FY2024 确认版（2.10）完全同分，反映文件事实：FY2025 无折旧政策变化、无 PP&E 减值、capex/折旧/PPE 三降。低风险结论四向互证：(1) 定量：CAPEX/收入 1.7%、PPE 占总资产 3.1%；(2) 定性：全文无年限变更、无 obsolescence 表述；(3) 结构性：$17.3B 租用算力承诺将迭代风险转移给供应商；(4) 趋势：Agentforce 放量年资产密集度指标全面下降。置信度略高于 FY2024（0.85→0.88），因连续两年数据排除了单年偶然性。加权计算：3×0.25 + 3×0.20 + 2×0.20 + 1×0.20 + 1×0.15 = 2.10。

**NA 项**：D5 竞争替代：锚点对照 FY2024 确认版（D5=1）：任务特别关注的'Agentforce 是否改变基础设施策略'经文件事实检验为否——10-K 未披露任何自有 GPU 集群建设；风险因素自认 AI 部署推高算力需求（SIG-006），但应对路径是 'continue to move to cloud computing platform providers' + $17.3B 基础设施服务提供商承诺（SIG-009），且 capex/PPE 净值/折旧三指标同向下降（SIG-008）。AI 军备竞赛的算力迭代成本仍由供应商承担，按锚点'算力租用风险转移→1 分'维持。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2023 | 2.10 | 3 | 3 | 2 | 1 | 1 | draft_pending_review |
| 2024 | 2.10 | 3 | 3 | 2 | 1 | 1 | confirmed |
| 2025 | 2.10 | 3 | 3 | 2 | 1 | 1 | draft_pending_review |

### 政策延续 vs 变化

- **2023 基期**：无特别变更记录
- **2024 维持**：无新的年限变更，沿用上期政策
- **2025 维持**：无新的年限变更，沿用上期政策

### 分数差异理由

**2023 → 2024（2.10 → 2.10，Δ+0.00）**：
- 维度无变化

**2024 → 2025（2.10 → 2.10，Δ+0.00）**：
- 维度无变化

---

## 附录：核对清单

### ① 五维评分逐项依据（锚点适用说明）
- [ ] D1 年限档位与 10-K 原文一致（服务器/网络设备年限表）
- [ ] D2 锚点适用正确（本期变更 vs 历史变更 vs 无变更）
- [ ] D3 减值信号数量/金额与原文一致
- [ ] D4 CAPEX/收入 计算正确（注意口径：含/不含融资租赁本金）
- [ ] D5 竞争暴露定性合理（运营型 vs 设计型 vs 租用型）

### ② 每条风险信号的证据链定位
| 信号 ID | 原文章节 | 定位串/行号 | 核对结果 |
|---|---|---|---|
| CRM-FY2023-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies | Note 1. Property and Equipment (HTML lines 4080-4087) | ☐ |
| CRM-FY2023-SIG-002 | Full-text keyword scan (XBRL noise excluded) | Full document scan of crm_fy2023_10k.html (4,975 lines) | ☐ |
| CRM-FY2023-SIG-003 | Notes to Consolidated Financial Statements - Note 10. Restructuring | Note 10. Restructuring (HTML lines 4541-4552); corroborated in income statement Restructuring line $828M (L3758) and MD&A (L3209-3214) | ☐ |
| CRM-FY2023-SIG-004 | Item 7. MD&A - Restructuring / Operating Expenses | Item 7. MD&A - Restructuring (HTML lines 3209-3214); plan description at MD&A Highlights (lines 2940-2948) | ☐ |
| CRM-FY2023-SIG-005 | Item 2. Properties | Item 2. Properties (HTML lines 2523-2526) | ☐ |
| CRM-FY2023-SIG-006 | Notes to Consolidated Financial Statements - Note 1. Impairment Assessment / Goodwill | Note 1. Impairment Assessment / Goodwill (HTML lines 4155-4158, 4166-4170) | ☐ |
| CRM-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies | Note 1. Property and Equipment (HTML lines 4160-4167) | ☐ |
| CRM-FY2024-SIG-002 | Full-text keyword scan (XBRL noise excluded) | Full document scan of crm_fy2024_10k.html (5,002 lines) | ☐ |
| CRM-FY2024-SIG-003 | Notes to Consolidated Financial Statements - Note 10. Restructuring | Note 10. Restructuring (HTML lines 4565-4580); corroborated in MD&A Highlights (lines 2919-2922) and MD&A Restructuring (lines 3094-3103) | ☐ |
| CRM-FY2024-SIG-004 | Notes to Consolidated Financial Statements - Note 1. Impairment Assessment / Goodwill | Note 1. Impairment Assessment / Goodwill (HTML lines 4234-4248) | ☐ |
| CRM-FY2024-SIG-005 | Item 1. Business / Item 1A. Risk Factors / Item 2. Properties | Item 1. Business - Infrastructure (HTML lines 483-487); Item 1A. Risk Factors - Service Disruptions (lines 964-966); Item 2. Properties (line 2665) | ☐ |
| CRM-FY2024-SIG-006 | Item 1A. Risk Factors - Acquisitions | Item 1A. Risk Factors - Risks related to acquisitions (HTML lines 1011-1014) | ☐ |
| CRM-FY2025-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Summary of Business and Significant Accounting Policies | Note 1. Property and Equipment (HTML lines 4007-4014) | ☐ |
| CRM-FY2025-SIG-002 | Full-text keyword scan (XBRL noise excluded) | Full document scan of crm_fy2025_10k.html (4,927 lines; plain-text extraction via Python tag-stripping, errors='replace') | ☐ |
| CRM-FY2025-SIG-003 | Notes to Consolidated Financial Statements - Note 10. Restructuring | Note 10. Restructuring (HTML lines 4448-4463); corroborated in MD&A (line 3210-3214) and income statement (line 3698) | ☐ |
| CRM-FY2025-SIG-004 | Notes to Consolidated Financial Statements - Note 1. Impairment Assessment / Goodwill | Note 1. Impairment Assessment / Goodwill (HTML lines 4079-4093) | ☐ |
| CRM-FY2025-SIG-005 | Item 1. Business - Infrastructure; Item 2. Properties | Item 1. Business - Infrastructure (HTML lines 443-450); Item 2. Properties (line 2532) | ☐ |
| CRM-FY2025-SIG-006 | Item 1A. Risk Factors - Service Disruptions / Infrastructure Capacity | Item 1A. Risk Factors - Service Disruptions (HTML lines 929-943) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
