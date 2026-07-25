# Advanced Micro Devices, Inc.（AMD）折旧风险评分依据与推断链——三年合并核对

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

## 一、Advanced Micro Devices, Inc. 2022（截至 2022-12-31） → 综合 2.40 🟡 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（11 条信号中最关键的 3 条）

**AMD-FY2022-SIG-001【HIGH】** — Notes to Consolidated Financial Statements - Note 2. Basis of Presentation and Significant Accounting Policies（Note 2. Basis of Presentation and Significant Accounting Policies - Property and Equipment (HTML lines 3477-3482)）
> Property and equipment are stated at cost. Depreciation and amortization are provided on a straight-line basis over the estimated useful lives of one to 15 years for equipment, 34 to 44 years for buildings, and leasehold improvements are measured by the shorter of the remaining terms of the leases or the estimated useful economic lives of the improvements.

推断链：
- Stated equipment depreciation life: 1-15 years, straight-line
- Implied average equipment life approx. 5 years (depreciation $439M / equipment gross $2,163M)
- AMD's own risk factors describe short product lifecycles with rapid obsolescence (see SIG-002)
- Upper-bound 15-year life assumes zero technological displacement for a decade and a half
- Mitigating fact: fabless model means PP&E is tiny ($1.5B net), so even aggressive lives move profit by little
- Result: direction of bias is under-depreciation, but magnitude is limited by the small asset base

**AMD-FY2022-SIG-002【HIGH】** — Item 1A. Risk Factors - Demand/Forecasting Risk（Item 1A. Risk Factors (HTML lines 1657-1659)）
> Many of our markets are characterized by short product lifecycles, which can lead to rapid obsolescence and price erosion.

推断链：
- Company states: short product lifecycles, rapid obsolescence, price erosion
- Semiconductor/AI product generation cycle in the industry is approximately 1-2 years
- Depreciation/amortization schedules assume the same technology generates economic benefit for 5-16 years
- Contradiction: revenue life of the technology (1-2 years) is far shorter than its balance-sheet life
- Result: periodic depreciation/amortization expense is systematically lower than true economic consumption of the asset

**AMD-FY2022-SIG-003【HIGH】** — Item 1A. Risk Factors - Inventory Obsolescence（Item 1A. Risk Factors (HTML lines 1673-1683)）
> Excess or obsolete inventory have and may in the future result in write-downs of the value of our inventory. For example, in the third quarter of 2022, we recorded certain charges primarily for inventory, pricing and related reserves in the Gaming and Client segments. Other factors that may result in excess or obsolete inventory include ... a higher incidence of inventory obsolescence because of rapidly changing technology and customer requirements.

推断链：
- FY2022 Q3 (current year): actual charges for inventory, pricing and related reserves in Gaming and Client
- Cause admitted by company: rapidly changing technology and customer requirements
- Inventory gets marked down quickly; fixed assets and intangibles carrying the same technology risk do not
- Depreciation schedules assume smooth consumption; reality is step-function obsolescence events
- Result: obsolescence losses show up late and lumpy (impairment) instead of early and smooth (higher depreciation), flattering interim profits

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 与FY2023确认版锚点一致（3分）：设备折旧年限披露为1-15年直线法（Note 2，L3477-3482；FY2023版为'2-15年'，仅下限措辞差一年、上限15年一致，无变更披露），按折旧费用$439M/设备原值$2,163M推算隐... |
| D2 政策保守性 | **2** | 与FY2023确认版锚点一致（2分）：全文检索'prospectively'零命中——FY2022没有任何折旧/摊销年限变更披露，既无延长年限+未来适用（Meta式5分情形），也无历史延长记录，属于'无变更→2-3'的相对保守情形，给2分。... |
| D3 减值触发 | **3** | 与FY2023确认版锚点一致（3分）：FY2022可折旧/可摊销资产实际减值为零——商誉在Q2（分部变更前后）与Q4（年度）两次测试均通过（L3819-3826），MD&A确认所有报告单元公允价值超过账面值（L2884-2886），无Met... |
| D4 CAPEX 强度 | **1** | 与FY2023确认版锚点一致（1分）：FY2022 CAPEX（购置不动产与设备）$450M，CAPEX/收入=1.91%，低于3%锚点下限，典型fabless轻资产结构（对比Meta 20.2%；FY2023版为2.41%同档）。折旧费用... |
| D5 竞争替代 | **3** | 与FY2023确认版锚点一致（3分）：AMD直接处于AI/高性能芯片竞争中心（Data Center部门收入$6,043M、+64%），公司在Risk Factors中明言竞争将因'rapid technological changes, ... |

**验算**：3×0.25 + 2×0.20 + 3×0.20 + 1×0.20 + 3×0.15 = 3×0.25=0.75 + 2×0.20=0.40 + 3×0.20=0.60 + 1×0.20=0.20 + 3×0.15=0.45 = **2.40** ✓
**置信度**：0.8 — All key figures verified against filing text (revenue, net income, CAPEX, depreciation, amortization, PP&E, goodwill, intangibles, useful lives, Xilinx/Pensando allocation tables). Direct depreciation-specific signals are inherently limited for a fabless company; scoring relies partly on the amortization schedule of acquired intangibles as the analogous optimistic-lifetime exposure - the same judgment call as the FY2023 confirmed version, with which all five dimension scores are anchored identically.

---

## 二、Advanced Micro Devices, Inc. 2023（截至 2023-12-30） → 综合 2.40 🟡 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（8 条信号中最关键的 3 条）

**AMD-FY2023-SIG-001【HIGH】** — Notes to Consolidated Financial Statements - Note 1（Note 1. Basis of Presentation and Significant Accounting Policies - Property and Equipment (lines 3688-3693)）
> Property and equipment are stated at cost. Depreciation and amortization are provided on a straight-line basis over the estimated useful lives of two to 15 years for equipment, 34 to 44 years for buildings, and leasehold improvements are measured by the shorter of the remaining terms of the leases or the estimated useful economic lives of the improvements.

推断链：
- Stated equipment depreciation life: 2-15 years, straight-line
- Implied average equipment life approx. 5-6 years (depreciation $441M / equipment gross $2,346M)
- AMD's own risk factors describe semiconductor product lifecycles as short with rapid obsolescence (see SIG-002)
- Upper-bound 15-year life assumes zero technological displacement for a decade and a half
- Mitigating fact: fabless model means PP&E is tiny ($1.6B net), so even aggressive lives move profit by little
- Result: direction of bias is under-depreciation, but magnitude is limited by the small asset base

**AMD-FY2023-SIG-002【HIGH】** — Risk Factors - Demand/Forecasting Risk（Item 1A. Risk Factors (lines 1721-1722)）
> Many of our markets are characterized by short product lifecycles, which can lead to rapid obsolescence and price erosion.

推断链：
- Company states: short product lifecycles, rapid obsolescence, price erosion
- AI/GPU product generation cycle in the industry is approximately 1-2 years
- Depreciation/amortization schedules assume the same technology generates economic benefit for 5-16 years
- Contradiction: revenue life of the technology (1-2 years) is far shorter than its balance-sheet life
- Result: periodic depreciation/amortization expense is systematically lower than true economic consumption of the asset

**AMD-FY2023-SIG-003【HIGH】** — Risk Factors - Inventory Obsolescence（Item 1A. Risk Factors (lines 1737-1749)）
> Excess or obsolete inventory have resulted in, and may in the future result in, write-downs of the value of our inventory. For example, in the third quarter of 2022, we recorded certain charges primarily for inventory, pricing and related reserves in the Gaming and Client segments. Factors that may result in excess or obsolete inventory ... include ... a higher incidence of inventory obsolescence because of rapidly changing technology and customer requirements.

推断链：
- FY2022 Q3: actual charges for inventory, pricing and related reserves in Gaming and Client
- Cause admitted by company: rapidly changing technology and customer requirements
- Inventory gets marked down quickly; fixed assets and intangibles carrying the same technology risk do not
- Depreciation schedules assume smooth consumption; reality is step-function obsolescence events
- Result: obsolescence losses show up late and lumpy (impairment) instead of early and smooth (higher depreciation), flattering interim profits

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 设备折旧年限披露为2-15年直线法（Note 1，行3689-3693），按折旧费用$441M/设备原值$2,346M推算隐含平均设备年限约5-6年，处于4-6年锚点区间；但AMD是fabless设计公司，PP&E净额仅$1,589M（占总... |
| D2 政策保守性 | **2** | 全文检索'prospectively'零命中：FY2023没有任何折旧/摊销年限变更披露，既无延长年限+未来适用（Meta式5分情形），也无历史延长记录，属于'无变更'的相对保守情形，给2分。需要注明的抵减项：公司在收购初始计量时给Xili... |
| D3 减值触发 | **3** | FY2023实际减值为零（Note 6：年度商誉定性测试通过，行4002-4005），无Meta式已实现大额减值。直接减值信号数量不少但均指向商誉/无形资产/技术许可/存货而非自有PP&E：①Risk Factors专章警告Xilinx/P... |
| D4 CAPEX 强度 | **1** | FY2023 CAPEX（购置不动产与设备）$546M，CAPEX/收入=2.41%，低于3%锚点下限，典型fabless轻资产结构（对比Meta 20.2%）。折旧费用$441M仅占收入1.9%，即使折旧年限假设严重失真，对利润的杠杆效应... |
| D5 竞争替代 | **3** | AMD直接处于AI芯片军备竞赛中心：Data Center部门以MI300系列GPU正面竞争NVIDIA，公司在Risk Factors中明言竞争将因'rapid technological changes, frequent produc... |

**验算**：3×0.25 + 2×0.20 + 3×0.20 + 1×0.20 + 3×0.15 = 3×0.25=0.75 + 2×0.20=0.40 + 3×0.20=0.60 + 1×0.20=0.20 + 3×0.15=0.45 = **2.40** ✓
**置信度**：0.78 — All key figures verified against filing text (revenue, net income, CAPEX, depreciation, amortization, PP&E, goodwill, intangibles, useful lives). Direct depreciation-specific signals are inherently limited for a fabless company; scoring relies partly on the amortization schedule of acquired intangibles as the analogous optimistic-lifetime exposure, which is a judgment call that lowers confidence vs the Meta benchmark.

---

## 三、Advanced Micro Devices, Inc. 2024（截至 2024-12-28） → 综合 2.60 🟡 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**AMD-FY2024-SIG-003【CRITICAL】** — Notes to Consolidated Financial Statements - Note 6（Note 6. Acquisition-related Intangible Assets and Goodwill (lines 3759-3763)）
> During the fourth quarter of fiscal year 2024, the Company determined that the fair value of certain IPR&D recorded within the Data Center segment was not recoverable resulting from actions related to the 2024 Restructuring Plan, and recorded an impairment charge of $ 58 million within Restructuring charges

推断链：
- Q4 FY2024: Data Center IPR&D fair value not recoverable due to 2024 Restructuring Plan actions
- $58M impairment recorded within Restructuring charges (Note 6); Note 14 shows total asset impairment of $73M
- IPR&D balance fell $220M -> $162M, fully explained by the impairment (no reclassification to developed technology this year)
- FY2023 comparative: zero impairment of any kind
- Impaired asset sat in the segment growing +94% - even the AI growth engine strands technology assets
- Result: obsolescence/strategy-shift losses surface as lumpy impairments, confirming the asymmetric recognition pattern (amortize slowly, impair suddenly)

**AMD-FY2024-SIG-001【HIGH】** — Notes to Consolidated Financial Statements - Note 1（Note 1. Basis of Presentation and Significant Accounting Policies - Property and Equipment (lines 3521-3526)）
> Property and equipment are stated at cost. Depreciation and amortization are provided on a straight-line basis over the estimated useful lives of two to 15 years for equipment, 34 to 44 years for buildings, and leasehold improvements are measured by the shorter of the remaining terms of the leases or the estimated useful economic lives of the improvements.

推断链：
- Stated equipment depreciation life: 2-15 years, straight-line (identical to FY2023 disclosure)
- Implied average equipment life approx. 6 years (depreciation $454M / equipment gross $2,798M)
- AMD's own MD&A now discloses an annual AI accelerator cadence (see SIG-010)
- Upper-bound 15-year life spans 15 product generations at the disclosed cadence
- Mitigating fact: fabless model keeps PP&E tiny ($1.8B net, 2.6% of assets)
- Result: direction of bias is under-depreciation, magnitude limited by small asset base; no policy deterioration vs FY2023

**AMD-FY2024-SIG-002【HIGH】** — Risk Factors - Demand/Forecasting Risk（Item 1A. Risk Factors (lines 1579-1580)）
> Many of our markets are characterized by short product lifecycles, which can lead to rapid obsolescence and price erosion.

推断链：
- Company states: short product lifecycles, rapid obsolescence, price erosion
- FY2024 MD&A: annual cadence of Instinct AI solutions (line 2809)
- Depreciation/amortization schedules assume the same technology generates benefit for 5-16 years
- Contradiction: revenue life of the technology (1 year per disclosed cadence) is far shorter than its balance-sheet life
- Result: periodic depreciation/amortization expense systematically lower than true economic consumption

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 与 FY2023 确认版口径保持一致，维持 3 分：折旧政策文本逐字未变（设备 2-15 年直线法，行 3521-3526），按折旧费用 $454M/设备原值 $2,798M 推算隐含平均设备年限约 6 年，仍处于 4-6 年锚点区间；PP... |
| D2 政策保守性 | **2** | 维持 FY2023 确认版 2 分：FY2024 本期无任何折旧/摊销年限变更披露，无延长年限+未来适用情形，也无历史延长记录，属'无变更→2-3'锚点的下端。全文'prospectively'仅 1 次命中（行 3642），经查证为新披露... |
| D3 减值触发 | **4** | 对照 FY2023 确认版（3 分，'仅间接信号'）上调至 4 分，理由是真实事件变化而非口径变化：FY2024 发生 AMD 样本内首次实际减值——Q4 2024 数据中心分部 IPR&D 因 2024 Restructuring Pla... |
| D4 CAPEX 强度 | **1** | 维持 FY2023 确认版 1 分：FY2024 CAPEX（购置不动产与设备）$636M，CAPEX/收入=2.47%（FY2023 为 2.41%），远低于 5% 锚点下限，典型 fabless 轻资产结构。折旧费用 $454M 仅占收... |
| D5 竞争替代 | **3** | 维持 FY2023 确认版 3 分（'卖芯片而非运营、间接暴露→2-3'区间上限）：FY2024 竞争加剧是事实——Data Center 收入 +94% 至 $12,579M（占总收入 49%），MI300X 大规模部署，公司自我加压至年... |

**验算**：3×0.25 + 2×0.20 + 4×0.20 + 1×0.20 + 3×0.15 = 3×0.25=0.75 + 2×0.20=0.40 + 4×0.20=0.80 + 1×0.20=0.20 + 3×0.15=0.45 = **2.60** ✓
**置信度**：0.8 — All key figures verified against FY2024 10-K body text with line numbers (revenue, net income, capex, depreciation, amortization, PP&E, goodwill, intangibles, IPR&D impairment, restructuring charges, segment revenue). Anchor consistency with FY2023 confirmed version explicitly maintained: only D3 moved (3->4), driven by the realized $58M Data Center IPR&D impairment - a documented real event, not a judgment drift. Residual uncertainty: the $58M impairment amount is disclosed but the specific IPR&D project is not named; whether FY2025 (ZT close) changes the structural profile is forward-looking.

**NA 项**：D3 减值触发：对照 FY2023 确认版（3 分，'仅间接信号'）上调至 4 分，理由是真实事件变化而非口径变化：FY2024 发生 AMD 样本内首次实际减值——Q4 2024 数据中心分部 IPR&D 因 2024 Restructuring Plan 相关行动被判定不可收回，确认减值 $58M 计入重组费用（行 3759-3763），Note 14 重组表显示资产减值合计 $73M（行 4033），重组费用总额 $186M 占净利润 11.3%。锚点适用'直接信号+历史记录本期减值小→4'：①本期减值金额小（占收入 0.2%）但已实现且落在 AI 加速器所在的数据中心分部；②直接信号充足：商誉/无形资产减值风险专章（行 2483-2516）、技术许可减值风险专章（行 2607-2616）、Note 1 长期资产减值政策'changes in any of these factors could necessitate impairment recognition in future periods'（行 3451-3452）；③$24.8B 商誉（占总资产 36%）仍仅通过定性测试，Embedded 报告单元单扛 $21.1B。未达 5 分因无 Meta 式大额减值（$58M vs Meta $2.43B）。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2022 | 2.40 | 3 | 2 | 3 | 1 | 3 | draft_pending_review |
| 2023 | 2.40 | 3 | 2 | 3 | 1 | 3 | confirmed |
| 2024 | 2.60 | 3 | 2 | 4 | 1 | 3 | draft_pending_review |

### 政策延续 vs 变化

- **2022 基期**：无特别变更记录
- **2023 维持**：无新的年限变更，沿用上期政策
- **2024 维持**：无新的年限变更，沿用上期政策

### 分数差异理由

**2022 → 2023（2.40 → 2.40，Δ+0.00）**：
- 维度无变化

**2023 → 2024（2.40 → 2.60，Δ+0.20）**：
- 维度变化：D3 减值触发 3→4

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
| AMD-FY2022-SIG-001 | Notes to Consolidated Financial Statements - Note 2. Basis of Presentation and Significant Accounting Policies | Note 2. Basis of Presentation and Significant Accounting Policies - Property and Equipment (HTML lines 3477-3482) | ☐ |
| AMD-FY2022-SIG-002 | Item 1A. Risk Factors - Demand/Forecasting Risk | Item 1A. Risk Factors (HTML lines 1657-1659) | ☐ |
| AMD-FY2022-SIG-003 | Item 1A. Risk Factors - Inventory Obsolescence | Item 1A. Risk Factors (HTML lines 1673-1683) | ☐ |
| AMD-FY2022-SIG-004 | Item 1A. Risk Factors - Acquisition/Goodwill Impairment | Item 1A. Risk Factors (HTML lines 2237-2269) | ☐ |
| AMD-FY2022-SIG-005 | Item 1A. Risk Factors - Technology Licenses | Item 1A. Risk Factors (HTML lines 2447-2456) | ☐ |
| AMD-FY2022-SIG-006 | Notes to Consolidated Financial Statements - Note 5 (Business Combinations) / Note 6 (Acquisition-related Intangible Assets and Goodwill) | Note 5. Business Combinations - Xilinx intangible allocation (HTML line 3753); Xilinx goodwill $22,784M and purchase consideration $48,793M (line 3744); Note 6 intangibles table and amortization expense (line 3814) | ☐ |
| AMD-FY2023-SIG-001 | Notes to Consolidated Financial Statements - Note 1 | Note 1. Basis of Presentation and Significant Accounting Policies - Property and Equipment (lines 3688-3693) | ☐ |
| AMD-FY2023-SIG-002 | Risk Factors - Demand/Forecasting Risk | Item 1A. Risk Factors (lines 1721-1722) | ☐ |
| AMD-FY2023-SIG-003 | Risk Factors - Inventory Obsolescence | Item 1A. Risk Factors (lines 1737-1749) | ☐ |
| AMD-FY2023-SIG-004 | Risk Factors - Acquisition/Goodwill Impairment | Item 1A. Risk Factors (lines 2496-2529) | ☐ |
| AMD-FY2023-SIG-005 | Risk Factors - Technology Licenses | Item 1A. Risk Factors (lines 2729-2737) | ☐ |
| AMD-FY2023-SIG-006 | Notes to Consolidated Financial Statements - Note 5/Note 6 (Acquisitions) | Note 5. Acquisitions - Xilinx intangible allocation (line 3932); IPR&D reclassification (lines 3952-3955); Note 6 intangibles table (line 3990) | ☐ |
| AMD-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Note 1 | Note 1. Basis of Presentation and Significant Accounting Policies - Property and Equipment (lines 3521-3526) | ☐ |
| AMD-FY2024-SIG-002 | Risk Factors - Demand/Forecasting Risk | Item 1A. Risk Factors (lines 1579-1580) | ☐ |
| AMD-FY2024-SIG-003 | Notes to Consolidated Financial Statements - Note 6 | Note 6. Acquisition-related Intangible Assets and Goodwill (lines 3759-3763) | ☐ |
| AMD-FY2024-SIG-004 | Notes to Consolidated Financial Statements - Note 14; MD&A | Note 14. Restructuring Charges (lines 4022-4033); MD&A Restructuring Charges (lines 3089-3094) | ☐ |
| AMD-FY2024-SIG-005 | Risk Factors - Acquisition/Goodwill Impairment | Item 1A. Risk Factors (lines 2483-2516) | ☐ |
| AMD-FY2024-SIG-006 | Notes to Consolidated Financial Statements - Note 6 | Note 6. Acquisition-related Intangible Assets and Goodwill (lines 3758-3767) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
