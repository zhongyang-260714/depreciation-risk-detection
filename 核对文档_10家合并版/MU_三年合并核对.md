# Micron Technology, Inc.（MU）折旧风险评分依据与推断链——三年合并核对

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

## 一、Micron Technology, Inc. 2022（截至 2022-09-01） → 综合 4.00 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**MU-FY2022-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment（Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 2717-2719)）
> Property, plant, and equipment is stated at cost and depreciated using the straight-line method over estimated useful lives of generally 10 to 30 years for buildings, 5 to 7 years for equipment, and 3 to 5 years for software.

推断链：
- Official equipment life: 5-7 years straight-line (lines 2717-2719); upper bound 7 years consistent with FY2023 anchor
- Equipment gross: $61,354M of $81,331M total PP&E gross (line 2870); FY2022 depreciation $7.03B
- Node cadence: 2022 sales on 1x/1y/1z/1-alpha nodes while 1-beta on track to ramp in 2023 (lines 230-232); 232-layer NAND announced (line 643)
- EUV lithography planned on the DRAM node after 1-beta (lines 640-641) - each such transition can strand or devalue pre-EUV tools
- Result: 7-year life assumes multi-node tool reuse; depreciation is back-loaded relative to economic value loss if node turnover accelerates

**MU-FY2022-SIG-002【HIGH】** — MD&A - Critical Accounting Estimates - Property, Plant, and Equipment（Item 7. MD&A - Critical Accounting Estimates (HTML lines 2505-2512)）
> We periodically assess the estimated useful lives of our property, plant, and equipment based on technology node transitions, capital spending, and equipment re-use rates. We also review the carrying value of property, plant, and equipment for impairment when events and circumstances indicate that the carrying value of an asset or group of assets may not be recoverable from the estimated future cash flows expected to result from its use and/or disposition.

推断链：
- Company admits useful lives are a critical estimate driven by node transitions and re-use rates (lines 2505-2508)
- FY2022: Q4 revenue -23% QoQ, gross margin 47%->39% (lines 2102-2124), yet no life revision disclosed
- Undiscounted-cash-flow recoverability test is a weak backstop at asset-group level
- Estimate discretion is inactive at BOTH cycle peak (FY2022) and trough (FY2023) - depreciation lacks cycle adaptivity
- Result: depreciation schedule embeds a normal-utilization, stable-node assumption

**MU-FY2022-SIG-003【HIGH】** — Notes to Consolidated Financial Statements - Property, Plant, and Equipment（Notes - Property, Plant, and Equipment (HTML lines 2870-2871)）
> As of 2022 2021 Land $ 280 $ 280 Buildings 16,676 14,776 Equipment (1) 61,354 51,902 Construction in progress (2) 1,897 1,517 Software 1,124 987 81,331 69,462 Accumulated depreciation ( 42,782 ) ( 36,249 ) $ 38,549 $ 33,213 (1) Includes costs related to equipment not placed into service of $ 3.35 billion as of September 1, 2022 and $ 1.99 billion as of September 2, 2021. ... Depreciation expense was $ 7.03 billion, $ 6.13 billion, and $ 5.57 billion for 2022, 2021, and 2020, respectively.

推断链：
- Equipment gross +18.2% YoY to $61,354M; total PP&E gross $81,331M; net PP&E $38,549M (line 2870)
- $3.35B equipment not yet placed into service (+68% vs $1.99B in 2021) - capex ahead of the downturn
- FY2022 depreciation $7.03B vs FY2021 $6.13B (+14.7%); accumulated depreciation $42,782M = 52.6% of gross PP&E
- Newest, largest equipment cohort enters the 7-year schedule exactly as Q4 FY2022 demand collapses
- Result: depreciation expense is locked to rise into the FY2023 trough regardless of utilization

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与FY2023确认版锚点一致→4分。FY2022披露口径为设备5-7年直线折旧（L2717-2719），上限7年与FY2023的'生产设备7年'锚点一致（FY2023为披露措辞细化，非年限变更，两年均未披露任何调整）。存储节点迭代周期约1-... |
| D2 政策保守性 | **3** | 与FY2023确认版锚点一致→3分（无变更档）。FY2022未发生任何折旧年限变更：全文检索'prospectively'、'change in estimate'正文零命中（已核实）。公司在周期顶部年既未延长年限虚增利润（对照GOOGL/... |
| D3 减值触发 | **4** | 按锚点'直接信号+历史记录本期减值小→4'。FY2022本期实际减值很小：重组及资产减值合计仅$48M，其中$23M为Lehi出售处置损失（FY2021 $435M减值周期的收尾，L2778-2784）；商誉定性测试全部通过、无减值（L24... |
| D4 CAPEX 强度 | **5** | CAPEX/收入=12,067/30,758=39.2%，远超25%锚点上限→5分，与FY2023确认版（49.4%→5）同档。FY2022是三年资本开支超级周期的顶点（FY2020 $8.2B→FY2021 $10.0B→FY2022 $... |
| D5 竞争替代 | **4** | 与FY2023确认版锚点一致→4分（存储行业周期/技术迭代压力档）。FY2022技术替代压力具体且密集：1α DRAM量产、1β定档2023、EUV将在1β后节点导入（资本密集型断点）、全球首发232层NAND、HBM2E高量产启动切入AI... |

**验算**：4×0.25 + 3×0.20 + 4×0.20 + 5×0.20 + 4×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 4×0.20=0.80 + 5×0.20=1.00 + 4×0.15=0.60 = **4.00** ✓
**置信度**：0.85 — 全部关键数据（设备5-7年年限L2717-2719、折旧$7.03B/PP&E明细L2870-2871、capex $12.07B L2342-2343、$48M重组减值L3372、商誉定性测试通过L2429-2432、Q4恶化L2102-2106）均逐字核对于FY2022 10-K正文并附行号；无年限变更经全文关键词检索确认。跨年锚点已与MU FY2023确认版逐项对照：D1/D2/D5同分，D4同档，D3差异（4 vs 5）完全由FY2023实际兑现的大额减记驱动。

**NA 项**：D1 年限错配：与FY2023确认版锚点一致→4分。FY2022披露口径为设备5-7年直线折旧（L2717-2719），上限7年与FY2023的'生产设备7年'锚点一致（FY2023为披露措辞细化，非年限变更，两年均未披露任何调整）。存储节点迭代周期约1-2年一代：FY2022在售1x/1y/1z/1α四至五代、1β定档2023、EUV将在1β之后节点导入（L230-232, L638-641），表面错配比3.5-7倍。制造业口径修正与FY2023相同：晶圆厂设备可跨节点复用，公司在关键会计估计中以'技术节点迁移、资本开支、设备复用率'评估年限（L2505-2508），真实错配小于服务器口径。表面档位5，因设备跨节点复用的真实性下调至4——与FY2023评分逻辑逐项一致。；D5 竞争替代：与FY2023确认版锚点一致→4分（存储行业周期/技术迭代压力档）。FY2022技术替代压力具体且密集：1α DRAM量产、1β定档2023、EUV将在1β后节点导入（资本密集型断点）、全球首发232层NAND、HBM2E高量产启动切入AI驱动的高带宽内存竞赛（L230-238, L638-643）。三强寡头（SK海力士/三星/美光）迫使持续高强度换代资本开支；Q4 FY2022行业急剧恶化显示周期反转风险已在财年内兑现。制造设备跨节点复用程度高于AI服务器，替代压力略低于云厂商GPU代际淘汰，维持4分。

---

## 二、Micron Technology, Inc. 2023（截至 2023-08-31） → 综合 4.20 🔴 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（10 条信号中最关键的 3 条）

**MU-FY2023-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment（Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML line 2789)）
> Property, plant, and equipment is stated at cost and depreciated using the straight-line method over estimated useful lives of generally 10 to 30 years for buildings, 7 years for production equipment, up to 7 years for other equipment, and 3 to 5 years for software.

推断链：
- Official production equipment life: 7 years straight-line (line 2789)
- Equipment gross: $65,555M of $87,585M total PP&E gross (line 2901); FY2023 depreciation $7.67B
- Node cadence: CNBU 2023 sales still on 1x/1y/1z/1-alpha nodes while 1-beta already qualified (lines 164-167); 232-layer NAND ramped in 2023 (line 576)
- Micron plans EUV lithography on the node AFTER 1-beta (line 575) - each such transition can strand or devalue pre-EUV tools
- Result: 7-year life assumes multi-node tool reuse; if HBM/EUV transitions accelerate node turnover, depreciation is systematically back-loaded relative to economic value loss

**MU-FY2023-SIG-003【CRITICAL】** — MD&A - Overview / Inventory NRV write-downs; Cash Flow Statement; Auditor's Report (CAM)（Item 7. MD&A - Overview (HTML lines 2107-2108); Inventory NRV write-downs table (line 2219); Consolidated Statements of Cash Flows (line 2659); Report of Independent Registered Public Accounting Firm - Critical Audit Matter (lines 3610-3613)）
> Due to the challenging pricing environment, we recognized charges of $1.83 billion in 2023 to write down inventories to their estimated net realizable value. ... Provision to write down inventories to net realizable value 1,831 (cash flow statement). ... The Company recorded charges of $1.83 billion to cost of goods sold to write down the carrying value of work in process and finished goods inventories to their estimated net realizable value (Critical Audit Matter).

推断链：
- FY2023 inventory NRV write-down: $1,831M to COGS (vs $0 in 2022/2021); net impact $987M after $844M lower-cost benefit
- PwC designated NRV of inventories as THE Critical Audit Matter (lines 3596-3613)
- Same ASP collapse drove gross margin to negative 9% (line 2205) and SBU goodwill impairment
- PP&E impairment test uses undiscounted cash flows and asset-group pooling - did NOT trigger despite the same price collapse
- Result: current assets are marked to economic reality while $87.6B of gross PP&E continues on a 7-year schedule; depreciation risk is real but absorbed asymmetrically across asset classes

**MU-FY2023-SIG-002【HIGH】** — MD&A - Critical Accounting Estimates - Property, Plant, and Equipment（Item 7. MD&A - Critical Accounting Estimates (HTML lines 2574-2584)）
> We periodically assess the estimated useful lives of our property, plant, and equipment based on technology node transitions, capital spending, and equipment re-use rates. We also review the carrying value of property, plant, and equipment for impairment when events and circumstances indicate that the carrying value of an asset or group of assets may not be recoverable from the estimated future cash flows expected to result from its use and/or disposition.

推断链：
- Company admits useful lives are a critical estimate driven by node transitions and re-use rates
- FY2023: worst down-cycle in memory industry history, wafer starts 'significantly reduced' (lines 2120-2123), yet no life revision disclosed
- Undiscounted-cash-flow recoverability test is a weak backstop at asset-group level
- Estimate discretion operates asymmetrically: lives are not shortened in downturns, only revisited when convenient
- Result: depreciation schedule embeds a normal-utilization, stable-node assumption that FY2023 reality violated

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 生产设备折旧年限7年（建筑物10-30年、软件3-5年），按评分锚点≥6年属最高档。存储节点迭代周期约1-2年一代（1x→1y→1z→1α→1β，五年内五代；232层NAND 2023年量产，EUV将在1β之后节点导入），表面错配比3-5倍... |
| D2 政策保守性 | **3** | FY2023未发生任何折旧年限变更：全文检索'prospectively'、'change in estimate'、'extend/shorten useful life'均无正文命中（已核实）。公司既未像GOOGL/MSFT那样延长年限... |
| D3 减值触发 | **5** | FY2023为本批样本中减值/减记实际触发最重的年份：①存货NRV减记$1,831M（现金流量表与MD&A双重确认，且为审计师唯一关键审计事项，L3596-3613）；②SBU商誉全额减值$101M（Q4定量测试，L2903-2916）；③... |
| D4 CAPEX 强度 | **5** | CAPEX/收入=7,676/15,540=49.4%，远超25%锚点上限。下行年比率有失真成分（收入同比-49%而资本开支仅削减36%），但正常年份同样极端：FY2022为39.2%（12,067/30,758）、FY2021为36.2%... |
| D5 竞争替代 | **4** | AI驱动的HBM竞赛是FY2023行业主线：生成式AI拉动HBM需求'very strong'（L188-190），但Micron FY2023仅处于HBM3E送样阶段、2024日历年年初才量产爬坡，落后于SK海力士（HBM3已规模供货）和... |

**验算**：4×0.25 + 3×0.20 + 5×0.20 + 5×0.20 + 4×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 5×0.20=1.00 + 5×0.20=1.00 + 4×0.15=0.60 = **4.20** ✓
**置信度**：0.85 — All key figures (7-year equipment life, $1.83B inventory write-down, $101M goodwill impairment, $382M underutilization, $7.68B capex, PP&E note breakdown) verified verbatim against filing text with line numbers; absence of any useful-life change confirmed by exhaustive keyword search. Interpretation caveat: FY2023 was a net-loss cyclical-trough year, so high D3/D4 scores reflect realized cycle risk and balance-sheet leverage rather than profit inflation - the risk signature differs in mechanism from cloud-vendor peers (META/GOOGL).

**NA 项**：D1 年限错配：生产设备折旧年限7年（建筑物10-30年、软件3-5年），按评分锚点≥6年属最高档。存储节点迭代周期约1-2年一代（1x→1y→1z→1α→1β，五年内五代；232层NAND 2023年量产，EUV将在1β之后节点导入），表面错配比3-5倍。但制造设备口径需与云厂商服务器区分：晶圆厂设备（光刻/刻蚀/沉积/量测）可跨多个节点复用，公司在关键会计估计中明确以'技术节点迁移、资本开支、设备复用率'评估年限（L2575-2577），说明7年假设内含复用预期，真实错配小于服务器口径。综合：表面档位5，因设备跨节点复用的真实性下调至4。；D5 竞争替代：AI驱动的HBM竞赛是FY2023行业主线：生成式AI拉动HBM需求'very strong'（L188-190），但Micron FY2023仅处于HBM3E送样阶段、2024日历年年初才量产爬坡，落后于SK海力士（HBM3已规模供货）和三星，处于追赶位置。技术迭代同时加速：1β DRAM与232层NAND均于2023年量产、下一节点将导入EUV光刻（L573-576），HBM所需的TSV堆叠与先进封装要求新增设备组合。三强寡头竞争（SK海力士/三星/美光）迫使持续高强度资本开支换代，压缩存量设备经济寿命；但存储行业设备跨节点复用程度高于AI服务器，替代压力略低于GOOGL/META面对的GPU代际淘汰，评4分。

---

## 三、Micron Technology, Inc. 2024（截至 2024-08-29） → 综合 4.00 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（11 条信号中最关键的 3 条）

**MU-FY2024-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment（Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 3038-3041)）
> Property, plant, and equipment is stated at cost and depreciated using the straight-line method over estimated useful lives of generally 10 to 30 years for buildings, 7 years for production equipment, up to 7 years for other equipment, and 3 to 5 years for software.

推断链：
- 官方生产设备年限：7 年直线（L3040），连续三年未变
- 设备总值 $70,813M / PP&E 总值 $96,047M（L3141）；FY2024 折旧 $7.70B
- 节点节奏：FY2024 DRAM 比特产出大部在 1α/1β（L141-142），1γ EUV 节点 2025 年放量（L143-144）
- 公司自认年限依据'技术节点迁移、资本开支、设备复用率'（L2829-2831），且本期实际发生旧节点设备改用于前沿节点（L2407-2408）
- 结论：7 年年限内含跨节点复用假设且有本期证据支撑，但若 HBM/EUV 转换加速节点更替，折旧仍系统性地滞后于经济价值损耗

**MU-FY2024-SIG-002【HIGH】** — MD&A - Critical Accounting Estimates - Property, Plant, and Equipment（Item 7. MD&A - Critical Accounting Estimates (HTML lines 2829-2838)）
> We periodically assess the estimated useful lives of our property, plant, and equipment based on technology node transitions, capital spending, and equipment re-use rates. We also review the carrying value of property, plant, and equipment for impairment when events and circumstances indicate that the carrying value of an asset or group of assets may not be recoverable from the estimated future cash flows expected to result from its use and/or disposition. In cases where undiscounted expected future cash flows are less than the carrying value, an impairment loss is recognized equal to the amount by which the carrying value exceeds the estimated fair value of the assets.

推断链：
- 公司承认年限是关键估计，由节点迁移与复用率驱动（L2829-2831）
- FY2024 经历 1β 量产爬坡与 1γ EUV 准备，但未做任何年限修订
- 不折现现金流测试 + 资产组归集 = 弱兜底（L2836-2838）
- 估计裁量'不作为'贯穿下行与复苏：下行年不缩短、复苏年不修订
- 结论：折旧计划内嵌'正常稼动率+稳定节点'假设，周期与技术的双向波动均不被反映

**MU-FY2024-SIG-003【HIGH】** — Notes to Consolidated Financial Statements - Property, Plant, and Equipment（Notes - Property, Plant, and Equipment (HTML lines 3141-3142)）
> Equipment(1)70,813 65,555 Construction in progress(2)3,444 2,464 Software1,365 1,316 96,047 87,585 Accumulated depreciation(56,298)(49,657) $39,749 $37,928 (1)Includes costs related to equipment not placed into service of $3.10 billion as of August 29, 2024 and $2.91 billion as of August 31, 2023.(2)Primarily includes building-related construction and tool installation.Depreciation expense was $7.70 billion, $7.67 billion, and $7.03 billion for 2024, 2023, and 2022, respectively. [注：表格经过去标签拼接，数字与原文逐字一致；完整表头为 Land/Buildings/Equipment/Construction in progress/Software，列示为 As of August 29, 2024 与 August 31, 2023]

推断链：
- 未投入使用设备 $3.10B（FY2023 $2.91B，+6.5%）——尚未开始折旧的设备群
- 在建工程 $3,444M（+39.8% YoY），主要为厂房建设与装机
- FY2024 折旧 $7.70B 仅占收入 30.7%、占经营现金流 $8,507M 的 90.5%
- FY2025 capex 指引 mid-30% 收入（约 $8-9B），设备基数将继续扩张
- 结论：当前折旧率被人为压低（大量资产未启用+补助冲减），FY2025-2026 折旧阶梯式上升已成定局

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与 FY2023 锚点一致评 4：生产设备 7 年直线折旧（L3040），政策句逐字未变。存储节点节奏 1-2 年/代（FY2024 主产 1α/1β，1γ EUV 2025 放量，L141-144），表面错配 3.5-7 倍。维持 4 而... |
| D2 政策保守性 | **3** | 锚点'本期无年限变更→3'：FY2024 未发生任何折旧年限变更，全文检索 'prospectively'、'change in estimate'、'extend/shorten useful life' 均无正文命中（已核实），折旧政策... |
| D3 减值触发 | **4** | 按锚点'直接信号+历史记录本期减值小→4'，由 FY2023 的 5 降档：本期大额减值消失——存货 NRV 减记 $—（vs FY2023 $1,831M，L2473）、商誉定性评估零减值迹象（vs FY2023 SBU $101M 全额... |
| D4 CAPEX 强度 | **5** | 锚点'capex/收入 >25%→5'：FY2024 capex $8,386M / 收入 $25,111M = 33.4%，维持 5 分。比率自 FY2023 的 49.4% 回落 purely 因收入 +62% 恢复，绝对开支反而增加 ... |
| D5 竞争替代 | **4** | 锚点'存储行业周期/HBM 技术迭代压力→4'，与 FY2023 一致。FY2024 行业主线兑现：AI 部署驱动需求（L2379-2380）、HBM3E 量产供应 AI 生态并实现数据中心收入占比 25%→35%、ASP 全年回升。但竞争... |

**验算**：4×0.25 + 3×0.20 + 4×0.20 + 5×0.20 + 4×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 4×0.20=0.80 + 5×0.20=1.00 + 4×0.15=0.60 = **4.00** ✓
**置信度**：0.85 — 全部关键数据与引文逐字核对于 FY2024 10-K 正文（含 HTML 行号）；'无任何年限变更'经全文关键词检索确认；跨年锚点与 FY2023 确认版逐项对照。解释口径：FY2024 为盈利恢复的周期上行年，综合分 4.00 较 FY2023 的 4.20 下降 0.20，唯一变动维度是 D3（5→4）——反映本期减值/减记真实消失，而非政策或风险结构改善；D1/D2/D5 锚点不变、D4 维持 5 分（33.4%>25%）。风险机制定性不变：7 年直线折旧对周期与技术双向脱敏，复苏年零减值恰是测试结构不对称的镜像证据。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2022 | 4.00 | 4 | 3 | 4 | 5 | 4 | draft_pending_review |
| 2023 | 4.20 | 4 | 3 | 5 | 5 | 4 | confirmed |
| 2024 | 4.00 | 4 | 3 | 4 | 5 | 4 | draft_pending_review |

### 政策延续 vs 变化

- **2022 基期**：无特别变更记录
- **2023 维持**：无新的年限变更，沿用上期政策
- **2024 维持**：无新的年限变更，沿用上期政策

### 分数差异理由

**2022 → 2023（4.00 → 4.20，Δ+0.20）**：
- 维度变化：D3 减值触发 4→5

**2023 → 2024（4.20 → 4.00，Δ-0.20）**：
- 维度变化：D3 减值触发 5→4

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
| MU-FY2022-SIG-001 | Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment | Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 2717-2719) | ☐ |
| MU-FY2022-SIG-002 | MD&A - Critical Accounting Estimates - Property, Plant, and Equipment | Item 7. MD&A - Critical Accounting Estimates (HTML lines 2505-2512) | ☐ |
| MU-FY2022-SIG-003 | Notes to Consolidated Financial Statements - Property, Plant, and Equipment | Notes - Property, Plant, and Equipment (HTML lines 2870-2871) | ☐ |
| MU-FY2022-SIG-004 | Notes to Consolidated Financial Statements - Lehi, Utah Fab and 3D XPoint | Notes - Lehi, Utah Fab and 3D XPoint (HTML lines 2778-2796); corroborated in Business Overview (lines 160-175) | ☐ |
| MU-FY2022-SIG-005 | Notes to Consolidated Financial Statements - Restructure and Asset Impairments; Segment Information | Notes - Restructure and Asset Impairments (HTML lines 3372-3376); income statement (line 2591) | ☐ |
| MU-FY2022-SIG-006 | MD&A - Critical Accounting Estimates - Goodwill; Notes - Segment and Other Information | Item 7. MD&A - Critical Accounting Estimates - Goodwill (HTML lines 2429-2432); Notes - Segment and Other Information (line 3454) | ☐ |
| MU-FY2023-SIG-001 | Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment | Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML line 2789) | ☐ |
| MU-FY2023-SIG-002 | MD&A - Critical Accounting Estimates - Property, Plant, and Equipment | Item 7. MD&A - Critical Accounting Estimates (HTML lines 2574-2584) | ☐ |
| MU-FY2023-SIG-003 | MD&A - Overview / Inventory NRV write-downs; Cash Flow Statement; Auditor's Report (CAM) | Item 7. MD&A - Overview (HTML lines 2107-2108); Inventory NRV write-downs table (line 2219); Consolidated Statements of Cash Flows (line 2659); Report of Independent Registered Public Accounting Firm - Critical Audit Matter (lines 3610-3613) | ☐ |
| MU-FY2023-SIG-004 | Notes to Consolidated Financial Statements - Goodwill | Notes - Goodwill (HTML lines 2903-2916); corroborated in Other Operating (Income) Expense table (line 3413) and cash flow statement | ☐ |
| MU-FY2023-SIG-005 | MD&A - Overview / Consolidated Gross Margin | Item 7. MD&A - Overview (HTML lines 2119-2125); Consolidated Gross Margin (lines 2205-2209) | ☐ |
| MU-FY2023-SIG-006 | Notes to Consolidated Financial Statements - Restructure and Asset Impairments | Notes - Restructure and Asset Impairments (HTML lines 3405-3413) | ☐ |
| MU-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Significant Accounting Policies - Property, Plant, and Equipment | Notes - Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 3038-3041) | ☐ |
| MU-FY2024-SIG-002 | MD&A - Critical Accounting Estimates - Property, Plant, and Equipment | Item 7. MD&A - Critical Accounting Estimates (HTML lines 2829-2838) | ☐ |
| MU-FY2024-SIG-003 | Notes to Consolidated Financial Statements - Property, Plant, and Equipment | Notes - Property, Plant, and Equipment (HTML lines 3141-3142) | ☐ |
| MU-FY2024-SIG-004 | MD&A - Consolidated Gross Margin / Inventory NRV write-downs; Segment Note | Item 7. MD&A - Inventory NRV write-downs (HTML lines 2464-2473); corroborated in Segment and Other Information unallocated table (HTML line 3630) and Consolidated Statements of Cash Flows (HTML line 2919) | ☐ |
| MU-FY2024-SIG-005 | MD&A - Critical Accounting Estimates - Goodwill; Notes - Other Operating (Income) Expense, Net | Item 7. MD&A - Critical Accounting Estimates - Goodwill (HTML lines 2756-2760); Notes - Other Operating (Income) Expense, Net (HTML lines 3550-3551; table 'Goodwill impairment — 101 —' at HTML line 3549) | ☐ |
| MU-FY2024-SIG-006 | Notes to Consolidated Financial Statements - Restructure and Asset Impairments | Notes - Restructure and Asset Impairments (HTML line 3541) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
