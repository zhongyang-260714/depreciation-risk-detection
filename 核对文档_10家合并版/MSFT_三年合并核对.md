# Microsoft Corporation（MSFT）折旧风险评分依据与推断链——三年合并核对

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

## 一、Microsoft Corporation 2023（截至 2023-06-30） → 综合 4.40 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**MSFT-FY2023-SIG-001【CRITICAL】** — Item 7. MD&A - Change in Accounting Estimate; Note 1. Accounting Policies (Item 8)（Item 7. MD&A - Change in Accounting Estimate (HTML line 1905); identical disclosure in Note 1. Accounting Policies (HTML line 7235)）
> In July 2022, we completed an assessment of the useful lives of our server and network equipment. Due to investments in software that increased efficiencies in how we operate our server and network equipment, as well as advances in technology, we determined we should increase the estimated useful lives of both server and network equipment from four years to six years. This change in accounting estimate was effective beginning fiscal year 2023. Based on the carrying amount of server and network equipment included in property and equipment, net as of June 30, 2022, the effect of this change in estimate for fiscal year 2023 was an increase in operating income of $3.7 billion and net income of $...

推断链：
- 官方披露：2022 年 7 月评估，服务器与网络设备年限 4→6 年，FY2023 期初生效（L1905、L7235）
- 量化影响：FY2023 营业利润 +$3.7B、净利润 +$3.0B、EPS +$0.40（基于 2022-06-30 账面价值）
- 会计估计变更→未来适用法，FY2022 及以前少提折旧永不修正
- 变更理由为'软件投资提升运营效率+技术进步'，与 AI 硬件 1-2 年迭代的行业现实方向相反
- 结果：FY2023 净利润 $72,361M 中约 4.1% 直接来自年限延长；6 年年限横跨 3-6 个 AI 硬件技术代际

**MSFT-FY2023-SIG-003【CRITICAL】** — Notes to Financial Statements - Note 7. Property and Equipment（Note 7. Property and Equipment (HTML line 13914)）
> During fiscal years 2023, 2022, and 2021, depreciation expense was $ 11.0 billion, $ 12.6 billion, and $ 9.3 billion, respectively. Depreciation expense declined in fiscal year 2023 due to the change in estimated useful lives of our server and network equipment. As of June 30, 2023, we have committed $ 13.5 billion for the construction of new buildings, building improvements, and leasehold improvements, primarily related to datacenters.

推断链：
- 折旧费用：FY2023 $11.0B vs FY2022 $12.6B vs FY2021 $9.3B（L13914）
- 公司原文归因：下降源于服务器及网络设备年限变更
- 同期 capex $23,886M→$28,107M（+17.7%）、PP&E 原值 $134,058M→$163,892M（+22.3%）→ 折旧方向与资产扩张方向背离
- $13.5B 建设承诺（主要数据中心）尚未转固，转固后叠加在现有折旧之上
- 结果：当前折旧线显著低估扩张中资产基数的稳态运行成本

**MSFT-FY2023-SIG-006【CRITICAL】** — Item 7. MD&A - Q2 Charge; Non-GAAP Financial Measures; Segment Reconciliations（Item 7. MD&A (HTML lines 1900, 2326); 分部对账 'Severance, hardware-related impairment, and lease consolidation costs'：毛利层 $152M (L3252)、营业利润层 $1,171M (L3357)、净利润层 $946M (L3462)）
> As a result, we recorded a $1.2 billion charge in the second quarter of fiscal year 2023 (Q2 charge), which included employee severance expenses of $800 million, impairment charges resulting from changes to our hardware portfolio, and costs related to lease consolidation activities. ... Current year gross margin, operating income, net income, and diluted EPS were negatively impacted by the Q2 charge, which resulted in decreases of $152 million, $1.2 billion, $946 million, and $0.13, respectively.

推断链：
- FY2023 Q2：$1.2B charge，含硬件组合变化减值+遣散 $800M+租赁合并（L1900）
- 利润影响：毛利 -$152M、营业利润 -$1.2B、净利润 -$946M、EPS -$0.13（L2326）
- 硬件组合调整→减值的传导链条在本财年实际兑现（非风险假设）
- 同一财年服务器年限 4→6 年延长：会计估计在延长年限，运营现实在触发减记
- 结果：FY2023 同时存在'延长年限增利 $3.0B'与'硬件减值减利'两股方向相反的力量，前者金额约 3 倍于后者

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **5** | 服务器/网络设备折旧年限 6 年（本期 4→6 年变更后生效），按锚点'≥6 年→5 分'给满分档，与 MSFT FY2024 确认版（D1=5）及 GOOGL 2023（6 年）口径完全一致。AI 硬件技术迭代周期仅 1-2 年，错配比 ... |
| D2 政策保守性 | **5** | FY2023 是年限变更生效年，对应锚点'本期延长年限+未来适用法+量化利润影响→5 分档'，对齐 GOOGL 2023（本期变更→5 分）：2022 年 7 月评估、FY2023 期初生效、未来适用不追溯，并量化披露 FY2023 营业利... |
| D3 减值触发 | **4** | FY2023 本期实际发生硬件组合变化减值（Q2 charge $1.2B 内，硬件部分未单独量化；扣除遣散费 $800M 后硬件减值+租赁合并约 $400M），对应锚点'直接信号+历史记录但本期减值小→4'中'本期有实际减值'的较强情形。... |
| D4 CAPEX 强度 | **3** | 现金 capex $28,107M / 收入 $211,915M = 13.26%，落在 8-15% 档→3 分（与 ORCL FY2024 13.0%→3 分锚点一致）；含融资租赁新增 ROU $3,128M 口径 14.7%，仍未越 1... |
| D5 竞争替代 | **5** | FY2023 10-K 明确 Azure 为 OpenAI 独家云服务商、承载其全部负载并加大专用超算投资（L772）——直接运营海量 GPU 集群，竞争替代/技术淘汰暴露为样本最高档，按锚点'直接运营海量 GPU+竞争暴露最高档→5'评分... |

**验算**：5×0.25 + 5×0.20 + 4×0.20 + 3×0.20 + 5×0.15 = 5×0.25=1.25 + 5×0.20=1.00 + 4×0.20=0.80 + 3×0.20=0.60 + 5×0.15=0.75 = **4.40** ✓
**置信度**：0.9 — 全部财务数据与 12 条信号引文经原文逐字核对（含 HTML 行号）。评分锚点与同公司 FY2024 确认版（4.20）及 GOOGL 2023/META 2023 基准显式对齐：D1=5（6 年年限，同 FY2024）、D2=5（本期变更+量化披露，对齐 GOOGL 2023 本期变更档，高于 FY2024 的历史记录档 4）、D3=4（本期实际硬件减值，高于 FY2024 零减值的 3）、D4=3（capex/收入 13.3%，低于 FY2024 的 18.1%→4）、D5=5（OpenAI 独家算力敞口，同 FY2024）。验算 5×0.25+5×0.20+4×0.20+3×0.20+5×0.15=4.40。FY2023 高于 FY2024 的 0.20 分全部来自'本期变更+本期减值'两个真实事件差异，符合跨年锚点一致性要求。

---

## 二、Microsoft Corporation 2024（截至 2024-06-30） → 综合 4.20 🔴 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**MSFT-FY2024-SIG-001【CRITICAL】** — Item 7. MD&A - Change in Accounting Estimate; Note 1. Accounting Policies (Item 8)（Item 7. MD&A - Change in Accounting Estimate (HTML line 1840); identical disclosure in Note 1. Accounting Policies (HTML line 7078)）
> In July 2022, we completed an assessment of the useful lives of our server and network equipment. Due to investments in software that increased efficiencies in how we operate our server and network equipment, as well as advances in technology, we determined we should increase the estimated useful lives of both server and network equipment from four years to six years. This change in accounting estimate was effective beginning fiscal year 2023.

推断链：
- 官方披露：2022 年 7 月评估，服务器与网络设备年限 4→6 年，FY2023 期初生效（L1840、L7078）
- 会计估计变更→未来适用法，FY2022 及以前少提折旧永不修正
- 变更理由为'软件投资提升运营效率+技术进步'，与 AI 硬件 1-2 年迭代的行业现实方向相反
- MD&A 三处'Excluding the impact of the change in accounting estimate, gross margin percentage increased slightly'（L2251、L2578、L2588）→ 变更仍在抬高 FY2024 报告毛利率
- 结果：FY2024 净利润 $88,136M 内嵌年限延长的持续收益；6 年年限横跨 3-6 个 AI 硬件技术代际

**MSFT-FY2024-SIG-005【CRITICAL】** — Consolidated Statements of Cash Flows; Note 14. Leases（Consolidated Statements of Cash Flows (HTML lines 6248-6259); Note 14. Leases (HTML lines 18278-18319)）
> Additions to property and equipment: $(44,477) million FY2024, $(28,107) FY2023, $(23,886) FY2022 (Cash Flows, L6248-6259). Right-of-use assets obtained in exchange for lease obligations - Finance leases: $11,633 million FY2024, $3,128 FY2023, $4,234 FY2022 (Note 14, L18278-18319).

推断链：
- 现金 capex $28,107M→$44,477M（+58.2%）（L6248-6259）
- 融资租赁新增资产 $3,128M→$11,633M（+272%）（L18308-18311）
- 广义 capex/收入 = 56,110/245,122 = 22.9%，为样本最高水平之一
- FY2024 折旧 $15.2B 仅为广义 capex 的 27% → 未来折旧巨额递延
- 结果：AI 军备竞赛的资本投入速度远超折旧确认速度

**MSFT-FY2024-SIG-006【CRITICAL】** — Item 7. MD&A - Non-GAAP Financial Measures; Segment Reconciliations（Item 7. MD&A (HTML line 2245；同一表述见 L3086)；分部对账 FY2024 该行为 $0 (HTML lines 3166-3173)）
> Prior year non-GAAP financial measures exclude the impact of a $1.2 billion charge in the second quarter of fiscal year 2023 (�Q2 charge�), which included employee severance expenses, impairment charges resulting from changes to our hardware portfolio, and costs related to lease consolidation activities.

推断链：
- FY2023 Q2：$1.2B charge，含硬件组合变化减值+遣散+租赁合并（L2245）
- FY2024：同口径费用 $0（L3166-3169），商誉/无形资产亦无减值（L14731、L15042）
- 硬件组合调整→减值的传导链条已被实际验证一次
- 6 年折旧年限不变，而产品组合一年内即可触发减值 → 年限假设与资产实际流转矛盾
- 结果：本期利润干净是事件未发生，而非风险不存在

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **5** | 服务器/网络设备折旧年限 6 年，按锚点'≥6 年→5 分'给满分档（与 GOOGL 6 年→D1=5 口径一致）。AI 硬件技术迭代周期仅 1-2 年，错配比 3-6 倍；公司自认 AI 市场 'rapidly evolving'（L11... |
| D2 政策保守性 | **4** | 年限延长（4→6 年）发生于上一财年（2022 年 7 月评估、FY2023 期初生效），对应锚点'历史有延长记录'档，本期无新延长，故不给满分。未来适用法不追溯，历史少提折旧永不修正；FY2024 MD&A 三处'剔除变更影响后毛利率仅微... |
| D3 减值触发 | **3** | FY2024 固定资产/商誉/无形资产三项零减值（Note 附注明文确认，L14731/L15042/L3166-3169），对应锚点'仅间接信号→3'：间接信号密集（L1165、L1208），上年 FY2023 Q2 $1.2B 费用含硬... |
| D4 CAPEX 强度 | **4** | 现金 capex $44,477M / 收入 $245,122M = 18.14%，同比 +58%，对应 15-25% 档→4 分；含融资租赁新增 ROU $11,633M 口径 22.9%；PP&E 占总资产 26.5%；建设承诺 $35... |
| D5 竞争替代 | **5** | Azure 是 OpenAI 独家算力提供方，直接运营海量 GPU 集群，竞争替代/技术淘汰暴露为样本最高档；自研芯片 Maia/Cobalt 已披露，GPU 代际更替（H100→B100/GB200）直接冲击现役机队残值。（本维度分数采用... |

**验算**：5×0.25 + 4×0.20 + 3×0.20 + 4×0.20 + 5×0.15 = 5×0.25=1.25 + 4×0.20=0.80 + 3×0.20=0.60 + 4×0.20=0.80 + 5×0.15=0.75 = **4.20** ✓
**置信度**：0.9 — 分数为项目负责人人工核对版本（D1=5/D2=4/D3=3/D4=4/D5=5，验算 5×0.25+4×0.20+3×0.20+4×0.20+5×0.15=4.20）：D1 按'≥6 年→5 分'锚点与 GOOGL 口径拉齐；D3 按'本期零 PP&E 减值→3 分'锚点从严；D5 因 Azure+OpenAI 独家算力敞口给最高档。12 条信号引文全部经原文逐字核对（含行号）；财务数据以本 10-K 披露为准（capex $44,477M 现金口径、商誉 $119,220M、FY2024 三项零减值）。

**NA 项**：D2 政策保守性：年限延长（4→6 年）发生于上一财年（2022 年 7 月评估、FY2023 期初生效），对应锚点'历史有延长记录'档，本期无新延长，故不给满分。未来适用法不追溯，历史少提折旧永不修正；FY2024 MD&A 三处'剔除变更影响后毛利率仅微增'（L2251/2578/2588）表明变更红利持续进入本期利润。本文件未量化变更的美元影响（FY2023 10-K 披露约 -$3.7B，不在本文件，记 NA）。（本维度分数采用人工核对版本，见《评分依据与推断核对》第四节；原 AI 草稿分为 4，D1/D3/D5 经核对后修正。）

---

## 三、Microsoft Corporation 2025（截至 2025-06-30） → 综合 4.40 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**MSFT-FY2025-SIG-001【CRITICAL】** — Notes to Financial Statements - Note 6. Property and Equipment（Note 6. Property and Equipment (HTML line 12431)）
> During fiscal years 2025, 2024, and 2023, depreciation expense was $22.0 billion, $15.2 billion, and $11.0 billion, respectively. As of June 30, 2025, 2024, and 2023, purchases of property and equipment remaining in accounts payable were $6.9 billion, $4.3 billion, and $3.8 billion, respectively.

推断链：
- 折旧费用：FY2025 $22.0B vs FY2024 $15.2B vs FY2023 $11.0B（L12431）
- 6 年年限（样本最乐观档）下折旧仍 +44.7% YoY → 资产扩张 > 年限摊薄
- 折旧/收入 = 22,000/281,724 = 7.8%（FY2024 为 6.2%），费用曲线陡峭化
- 应付账款中已购未付 PP&E 亦升至 $6.9B（FY2024 $4.3B）→ 转固队列继续膨胀
- 结果：即便年限不再缩短，现有扩张速度已使利润表开始承压；若按 1-2 年技术寿命重估，费用将数倍于此

**MSFT-FY2025-SIG-004【CRITICAL】** — Consolidated Statements of Cash Flows; Note 13. Leases（Consolidated Statements of Cash Flows (HTML lines 5412-5424); Note 13. Leases (HTML lines 16406-16489, 16654-16695, 16922-16941)）
> Additions to property and equipment: $(64,551) million FY2025, $(44,477) FY2024, $(28,107) FY2023 (Cash Flows, L5412-5424). Right-of-use assets obtained in exchange for lease obligations - Finance leases: $20,511 million FY2025, $11,633 FY2024, $3,128 FY2023 (Note 13, L16654-16695). Finance lease cost FY2025: amortization of ROU assets $3,408M + interest $1,417M = $4,825M (L16406-16489); finance-leased property and equipment at cost $53,876M, accumulated depreciation $(9,861)M (L16922-16941).

推断链：
- 现金 capex $44,477M→$64,551M（+45.1%）（L5412-5424）
- 融资租赁新增资产 $11,633M→$20,511M（+76.3%）（L16684-16695）
- 广义 capex/收入 = 85,062/281,724 = 30.2%，样本最高且首破 25% 阈值
- 融资租赁 PP&E 成本 $53,876M（+67%），租赁渠道扩表与现金采购并行
- FY2025 折旧/广义 capex = 25.9%（FY2024 为 27.1%）→ 投入与费用确认的剪刀差扩大
- 结果：AI 军备竞赛的资本投入速度进一步抛离折旧确认速度

**MSFT-FY2025-SIG-002【HIGH】** — Notes to Financial Statements - Note 1. Accounting Policies - Property and Equipment（Note 1. Accounting Policies - Property and Equipment (HTML line 6256)）
> Property and equipment is stated at cost less accumulated depreciation and depreciated using the straight-line method over the shorter of the estimated useful life of the asset or the lease term. The estimated useful lives of our property and equipment are generally as follows: software developed or acquired for internal use, three years; computer equipment, two to six years; buildings and improvements, five to 15 years; leasehold improvements, three to 15 years; and furniture and equipment, one to 10 years. Land is not depreciated.

推断链：
- 直线法折旧，按估计寿命与租期孰短（L6256）
- 计算机设备年限区间 2-6 年，与 FY2024 完全一致，6 年上限延续
- FY2025 全文无 'change in accounting estimate'/'server and network equipment' 年限叙述 → 年限延长的历史被披露层面'遗忘'
- 同类资产年限裁量达 3 倍（2 vs 6 年），与同业可比性弱
- 结果：年限上限维持在样本最乐观水平（与 GOOGL 并列 6 年），且披露透明度进一步下降

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **5** | 锚点'≥6 年→5 分'，与 FY2024 确认版一致：服务器/网络设备折旧年限维持 6 年（政策表 computer equipment 2-6 年，L6256），2022 年 4→6 年变更继续作为既定政策执行，FY2025 本期无变更... |
| D2 政策保守性 | **4** | 锚点'历史有延长记录本期无变更→4'，与 FY2024 确认版一致：年限延长（4→6 年）发生于 2022 年 7 月、FY2023 期初生效，未来适用不追溯，历史少提折旧永不修正；FY2025 本期无任何年限变更，故不到 5 分。跨年新增... |
| D3 减值触发 | **3** | 锚点'本期零 PP&E 减值→3'，与 FY2024 确认版一致：FY2025 固定资产/商誉/无形资产连续第三年零减值（L13118、L13425），且 FY2024 的 'Severance, hardware-related impa... |
| D4 CAPEX 强度 | **5** | ⚠️本维度为 FY2025 唯一升档维度（4→5），依据锚点'>25%→5'与真实事实变化：含融资租赁新增 ROU 的广义 capex/收入 = (64,551+20,511)/281,724 = 30.2%，首破 25% 阈值（FY202... |
| D5 竞争替代 | **5** | 锚点'直接运营海量 GPU+竞争暴露最高档→5'，与 FY2024 确认版一致：Azure 为 OpenAI 独家算力平台（'The OpenAI API is exclusive to Azure, runs on Azure'，L141... |

**验算**：5×0.25 + 4×0.20 + 3×0.20 + 5×0.20 + 5×0.15 = 5×0.25=1.25 + 4×0.20=0.80 + 3×0.20=0.60 + 5×0.20=1.00 + 5×0.15=0.75 = **4.40** ✓
**置信度**：0.9 — 评分锚点显式对齐 MSFT FY2024 确认版（D1=5/D2=4/D3=3/D4=4/D5=5→4.20）：D1/D2/D3/D5 锚点档位不变，分数维持；仅 D4 因广义 capex/收入 30.2% 突破 >25% 锚点阈值由 4 升至 5（FY2024 版推理中已预告）。验算 5×0.25+4×0.20+3×0.20+5×0.20+5×0.15=4.40。12 条信号引文全部经原文逐字核对（含行号，7 条程序化切片、其余为多行表格转录并标注）；财务数据以本 10-K 披露为准。

**NA 项**：D1 年限错配：锚点'≥6 年→5 分'，与 FY2024 确认版一致：服务器/网络设备折旧年限维持 6 年（政策表 computer equipment 2-6 年，L6256），2022 年 4→6 年变更继续作为既定政策执行，FY2025 本期无变更。AI 硬件迭代周期 1-2 年，错配比 3-6 倍；公司自认 AI 市场 'highly competitive and rapidly evolving'（L863）。新增不利事实：FY2025 10-K 将 4→6 年变更叙事整体移除（'change in accounting estimate' 0 命中），年限乐观假设沉淀为不可见的'既定事实'；leasehold improvements 上限 20→15 年为保守方向但非服务器资产，不改变本维度评分。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2023 | 4.40 | 5 | 5 | 4 | 3 | 5 | draft_pending_review |
| 2024 | 4.20 | 5 | 4 | 3 | 4 | 5 | confirmed |
| 2025 | 4.40 | 5 | 4 | 3 | 5 | 5 | draft_pending_review |

### 政策延续 vs 变化

- **2023 本期延长**：本期发生折旧年限延长
- **2024 历史延长生效中**：无新的年限变更，上期延长政策继续适用
- **2025 历史延长生效中**：无新的年限变更，沿用上期政策

### 分数差异理由

**2023 → 2024（4.40 → 4.20，Δ-0.20）**：
- 维度变化：D2 政策保守性 5→4；D3 减值触发 4→3；D4 CAPEX 强度 3→4

**2024 → 2025（4.20 → 4.40，Δ+0.20）**：
- 维度变化：D4 CAPEX 强度 4→5

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
| MSFT-FY2023-SIG-001 | Item 7. MD&A - Change in Accounting Estimate; Note 1. Accounting Policies (Item 8) | Item 7. MD&A - Change in Accounting Estimate (HTML line 1905); identical disclosure in Note 1. Accounting Policies (HTML line 7235) | ☐ |
| MSFT-FY2023-SIG-002 | Notes to Financial Statements - Note 1. Accounting Policies - Property and Equipment | Note 1. Accounting Policies - Property and Equipment (HTML line 7608) | ☐ |
| MSFT-FY2023-SIG-003 | Notes to Financial Statements - Note 7. Property and Equipment | Note 7. Property and Equipment (HTML line 13914) | ☐ |
| MSFT-FY2023-SIG-004 | Notes to Financial Statements - Note 7. Property and Equipment | Note 7. Property and Equipment 明细表 (HTML lines 13784-13900；Computer equipment and software 行 L13817/13820/13824) | ☐ |
| MSFT-FY2023-SIG-005 | Consolidated Statements of Cash Flows; Note 14. Leases | Consolidated Statements of Cash Flows (HTML lines 6371-6382); Note 14. Leases (HTML lines 18227-18238, 18462-18509) | ☐ |
| MSFT-FY2023-SIG-006 | Item 7. MD&A - Q2 Charge; Non-GAAP Financial Measures; Segment Reconciliations | Item 7. MD&A (HTML lines 1900, 2326); 分部对账 'Severance, hardware-related impairment, and lease consolidation costs'：毛利层 $152M (L3252)、营业利润层 $1,171M (L3357)、净利润层 $946M (L3462) | ☐ |
| MSFT-FY2024-SIG-001 | Item 7. MD&A - Change in Accounting Estimate; Note 1. Accounting Policies (Item 8) | Item 7. MD&A - Change in Accounting Estimate (HTML line 1840); identical disclosure in Note 1. Accounting Policies (HTML line 7078) | ☐ |
| MSFT-FY2024-SIG-002 | Notes to Financial Statements - Note 1. Accounting Policies - Property and Equipment | Note 1. Accounting Policies - Property and Equipment (HTML line 7451) | ☐ |
| MSFT-FY2024-SIG-003 | Notes to Financial Statements - Note 7. Property and Equipment | Note 7. Property and Equipment (HTML line 13766) | ☐ |
| MSFT-FY2024-SIG-004 | Notes to Financial Statements - Note 7. Property and Equipment | Note 7. Property and Equipment 明细表 (HTML lines 13594-13752；Computer equipment and software 行 L13669/13672/13676) | ☐ |
| MSFT-FY2024-SIG-005 | Consolidated Statements of Cash Flows; Note 14. Leases | Consolidated Statements of Cash Flows (HTML lines 6248-6259); Note 14. Leases (HTML lines 18278-18319) | ☐ |
| MSFT-FY2024-SIG-006 | Item 7. MD&A - Non-GAAP Financial Measures; Segment Reconciliations | Item 7. MD&A (HTML line 2245；同一表述见 L3086)；分部对账 FY2024 该行为 $0 (HTML lines 3166-3173) | ☐ |
| MSFT-FY2025-SIG-001 | Notes to Financial Statements - Note 6. Property and Equipment | Note 6. Property and Equipment (HTML line 12431) | ☐ |
| MSFT-FY2025-SIG-002 | Notes to Financial Statements - Note 1. Accounting Policies - Property and Equipment | Note 1. Accounting Policies - Property and Equipment (HTML line 6256) | ☐ |
| MSFT-FY2025-SIG-003 | Notes to Financial Statements - Note 6. Property and Equipment | Note 6. Property and Equipment 明细表 (HTML lines 12259-12417；Computer equipment and software 行 L12334-12341；合计行 L12372-12417) | ☐ |
| MSFT-FY2025-SIG-004 | Consolidated Statements of Cash Flows; Note 13. Leases | Consolidated Statements of Cash Flows (HTML lines 5412-5424); Note 13. Leases (HTML lines 16406-16489, 16654-16695, 16922-16941) | ☐ |
| MSFT-FY2025-SIG-005 | Notes to Financial Statements - Note 13. Leases | Note 13. Leases (HTML line 17404) | ☐ |
| MSFT-FY2025-SIG-006 | Item 7. MD&A - Contractual Obligations / Other Planned Uses of Capital; Note 6 | Note 6 (HTML line 12431); MD&A 合同承诺表 (HTML lines 3005-3046, footnote L3103); MD&A - Other Planned Uses of Capital (HTML line 3107) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
