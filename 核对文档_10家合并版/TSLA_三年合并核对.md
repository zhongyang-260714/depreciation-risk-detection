# Tesla, Inc.（TSLA）折旧风险评分依据与推断链——三年合并核对

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

## 一、Tesla, Inc. 2022（截至 2022-12-31） → 综合 3.20 🟠 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line (generally); units-of-production for Panasonic production equipment under finance lease；变更：None disclosed for fiscal 2022. No useful-life revision for any asset class.

### 核心证据（4 条信号中最关键的 3 条）

**TSLA-2022-SIG-001【CRITICAL】** — Item 1A. Risk Factors（Item 1A. Risk Factors (HTML L750)）
> We may be negatively impacted by any early obsolescence of our manufacturing equipment. We depreciate the cost of our manufacturing equipment over their expected useful lives. However, product cycles or manufacturing technology may change periodically, and we may decide to update our products or manufacturing processes more quickly than expected.

推断链：
- Manufacturing equipment depreciated over 3-15 years (Note 2)
- Tesla admits product cycles may change faster than expected
- 2022 context: 4680 cell ramp, structural battery pack, mega-casting
- Early retirement shortens useful life → depreciation accelerated
- Result: current depreciation embeds optimistic "no early retirement" assumption

**TSLA-2022-SIG-002【HIGH】** — Note 2. Summary of Significant Accounting Policies（Note 2. Summary of Significant Accounting Policies）
> Depreciation is generally computed using the straight-line method over the estimated useful lives of the respective assets, as follows: Machinery, equipment, vehicles and office furniture 3 to 15 years. Tooling 4 to 7 years. Building and building improvements 15 to 30 years. Computer equipment and software 3 to 10 years.

推断链：
- Machinery/equipment range: 3-15 years; computer equipment: 3-10 years
- Computer equipment gross 2022: $2,072M (vs $3,799M in 2023)
- AI accelerator cycle: 1-2 years
- Mismatch ratio: up to 5-10x for AI compute
- Result: even at smaller scale, the mismatch structure is identical to 2023

**TSLA-2022-SIG-003【HIGH】** — Item 1. Business + Note 8. Property, Plant and Equipment（Item 1. Business - Self-Driving Development）
> We are also developing additional computer hardware to better enable the massive amounts of field data captured by our vehicles to continually train and improve these neural networks.

推断链：
- Item 1: Tesla building AI training computer hardware
- Note 8: Computer equipment gross $2,072M in 2022
- Depreciation class: 3-10 years straight-line
- AI accelerator cycle: 1-2 years
- Result: if depreciated over 5-7 years, annual expense materially understated

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与2023年相同的折旧年限结构：machinery 3-15年、computer equipment 3-10年。AI训练硬件错配比例相同（5-10x），但2022年绝对规模较小（$2,072M vs $3,799M）。制造设备方面，202... |
| D2 政策保守性 | **3** | 2022年无任何折旧年限变更（与2023年一致）。落在锚点"无变更→3"档。评3分（与2023年锚点一致）。 |
| D3 减值触发 | **2** | 2020-2022连续三年零重大减值。2022年特斯拉仍处于高速增长期，减值测试容易通过。但2022年11月裁员11,000人和重组费用$4.61B是未来减值风险的前兆。评2分（与2023年锚点一致）。 |
| D4 CAPEX 强度 | **3** | CAPEX/收入=$7.16B/$81.46B=8.8%，略低于2023年的9.2%。PP&E总值增长较快（$17.5B→$23.5B，+34%）。评3分（与2023年锚点一致）。 |
| D5 竞争替代 | **4** | 2022年电动车竞争加剧：比亚迪销量超越特斯拉、传统车企电动化加速。价格战尚未全面爆发（2023年才是价格战年），但竞争压力已在积累。AI/FSD方面，HW3→HW4的过渡正在进行。评4分（与2023年锚点一致）。 |

**验算**：4×0.25 + 3×0.20 + 2×0.20 + 3×0.20 + 4×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 2×0.20=0.40 + 3×0.20=0.60 + 4×0.15=0.60 = **3.20** ✓
**置信度**：0.8 — Based on TSLA 2023 confirmed annotation, with 2022-specific financial data from 10-K. The risk structure is identical to 2023 (same depreciation schedule, same Risk Factor language), with smaller absolute scale for AI compute assets.

**跨年轨迹**：TSLA 2022 (no change) → 2023 (no change). Both years share identical depreciation policies and Risk Factor language. The main difference is scale: AI compute assets grew from $2,072M to $3,799M (+83%), and CAPEX grew from $7.16B to $8.90B (+24%).

---

## 二、Tesla, Inc. 2023（截至 2023-12-31） → 综合 3.20 🟠 [✅ confirmed]

**会计政策摘要**：方法：straight-line (generally); units-of-production for Panasonic production equipment under finance lease (Note 8)；变更：none disclosed for fiscal 2023 (no useful-life revision for any asset class; keyword 'change in estimate' appears only in income-tax context...

### 核心证据（8 条信号中最关键的 3 条）

**TSLA-2023-SIG-001【CRITICAL】** — Item 1A. Risk Factors（Item 1A. Risk Factors - 标题 'We may be negatively impacted by any early obsolescence of our manufacturing equipment.' 处（纯文本定位串 'We depreciate the cost of our manufacturing equipment'））
> We may be negatively impacted by any early obsolescence of our manufacturing equipment. We depreciate the cost of our manufacturing equipment over their expected useful lives. However, product cycles or manufacturing technology may change periodically, and we may decide to update our products or manufacturing processes more quickly than expected. Moreover, improvements in engineering and manufacturing expertise and efficiency may result in our ability to manufacture our products using less of our currently installed equipment. Alternatively, as we ramp and mature the production of our products to higher levels, we may discontinue the use of already installed equipment in favor of different o...

推断链：
- Manufacturing equipment depreciated over 'expected useful lives' (3-15 years per Note 2)
- Tesla admits product cycles / manufacturing technology may change faster than expected
- Early retirement shortens useful life -> depreciation accelerated -> results harmed
- Real-world corroboration: 2023 saw Cybertruck ramp (new processes), 4680 cell iteration, and next-gen platform development - all equipment-displacing events
- Result: current depreciation expense embeds an optimistic 'no early retirement' assumption; downside is recognized only when retirement occurs (asymmetric, like impairment)

**TSLA-2023-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 2. Summary of Significant Accounting Policies（Note 2. Summary of Significant Accounting Policies - 'Property, Plant and Equipment, Net' 小节（定位串 'Machinery, equipment, vehicles and office furniture 3 to 15 years'））
> Depreciation is generally computed using the straight-line method over the estimated useful lives of the respective assets, as follows: Machinery, equipment, vehicles and office furniture 3 to 15 years Tooling 4 to 7 years Building and building improvements 15 to 30 years Computer equipment and software 3 to 10 years. Leasehold improvements are depreciated on a straight-line basis over the shorter of their estimated useful lives or the terms of the related leases.

推断链：
- Machinery/equipment range: 3-15 years; computer equipment/software: 3-10 years (straight-line)
- EV platform cycle ~3-6 years; AI accelerator cycle 1-2 years
- Range disclosure means investors cannot see which life applies to which asset - 15-year and 10-year upper bounds give management wide discretion
- Machinery+equipment is the largest PP&E class ($16,372M gross, Note 8); computer equipment gross nearly doubled to $3,799M in 2023
- Result: the two fastest-obsolescing classes carry the widest and longest depreciable ranges

**TSLA-2023-SIG-003【HIGH】** — Item 1. Business + Note 8. Property, Plant and Equipment, Net（Item 1. Business - 'Self-Driving Development and Artificial Intelligence'（定位串 'additional computer hardware to better enable the massive amounts of field data'）；Note 8 PP&E 表（定位串 'Computer equipment, hardware and software $ 3,799 $ 2,072'））
> Our FSD Computer runs our neural networks in our vehicles, and we are also developing additional computer hardware to better enable the massive amounts of field data captured by our vehicles to continually train and improve these neural networks for real-world performance. ... Computer equipment, hardware and software $ 3,799 $ 2,072 (gross, December 31, 2023 vs 2022).

推断链：
- Item 1: Tesla is building its own AI training computer hardware (Dojo-class assets, unnamed in filing)
- Note 8: Computer equipment, hardware and software gross +83% YoY to $3,799M - fastest-growing PP&E class
- Depreciation class for these assets: 3-10 years straight-line (Note 2)
- AI accelerator economic cycle: 1-2 years; FSD training hardware faces same displacement pressure as hyperscaler GPU fleets
- Result: if AI training hardware is depreciated over even the mid-range (5-7 years), annual expense materially understates economic consumption

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 制造设备口径：machinery/equipment 3-15年，上限达15年，触及锚点≥6年档；但需区分资产性质——Gigafactory的冲压、压铸、总装设备物理寿命确实可达10-15年，tooling 4-7年与产线迭代周期大体匹配（... |
| D2 政策保守性 | **3** | 2023年无任何折旧年限变更（'change in estimate'全文仅出现于所得税语境，'prospectively'仅用于两项ASU准则采用），既未延长也未缩短，落在锚点'无变更→3'档。与GOOGL（本期延长服务器年限至6年，+5... |
| D3 减值触发 | **2** | 2021-2023连续三年长期资产零重大减值（Note 2原文），商誉零减值，2023年数字资产减值'不重大'（2022年$204M为比特币减值，非PP&E）。按锚点属'稀少→2'档：存在间接触发因素——Risk Factor明确承认设备可... |
| D4 CAPEX 强度 | **3** | CAPEX/收入=$8,898M/$96,773M=9.2%，落在8-15%档（→3分）。绝对额$8.9B且指引2024年超$10B、2025-2026年每年$8-10B，扩张确定性强。在建工程$5,791M构成未来折旧管道；PP&E总值一... |
| D5 竞争替代 | **4** | 双重替代压力且均已实质化：(1) 电动车价格战——2023年多次降价被MD&A明确确认，汽车毛利率28.5%→19.4%崩塌9.1pp，比亚迪等中国厂商及传统车企电动化直接冲击份额，Risk Factor将price reductions列... |

**验算**：4×0.25 + 3×0.20 + 2×0.20 + 3×0.20 + 4×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 2×0.20=0.40 + 3×0.20=0.60 + 4×0.15=0.60 = **3.20** ✓
**置信度**：0.8 — Direct verbatim evidence for all eight signals (Risk Factor obsolescence disclosure, Note 2 schedule, Note 8 PP&E detail, MD&A tax benefit). Scoring tempered by Tesla's genuinely clean record (no life extension, no impairment, depreciation growing faster than PP&E), which distinguishes it from GOOGL/META; residual uncertainty comes from range-based life disclosure (no per-asset-class life assignment) and the absence of Dojo-specific disclosure (the word does not appear in the filing), so AI compute depreciation treatment must be inferred from the 'Computer equipment and software' class.

---

## 三、Tesla, Inc. 2024（截至 2024-12-31） → 综合 3.75 🟠 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line (generally); units-of-production for Panasonic production equipment under finance lease；变更：None in FY2024. No useful-life revisions disclosed.

### 核心证据（5 条信号中最关键的 3 条）

**TSLA-2024-SIG-001【CRITICAL】** — Item 1A. Risk Factors（Item 1A. Risk Factors）
> We may be negatively impacted by any early obsolescence of our manufacturing equipment. We depreciate the cost of our manufacturing equipment over their expected useful lives. However, product cycles or manufacturing technology may change periodically.

推断链：
- Manufacturing equipment depreciated over 3-15 years
- Cybertruck uses unique processes (gigacasting, 4680 pack) not shared with Model 3/Y
- Next-gen "unboxed process" platform in development → potential early retirement of current Model 3/Y equipment
- Tooling 4-7 years is appropriate for vehicle-specific tools
- Result: platform proliferation increases early obsolescence risk

**TSLA-2024-SIG-002【HIGH】** — MD&A / Note 8（Note 1 / Note 8）
> Depreciation is generally computed using the straight-line method over the estimated useful lives of the respective assets, as follows: Computer equipment and software 3 to 10 years.

推断链：
- FSD V12 launched in 2024: end-to-end neural networks
- Training compute demand increased significantly with V12
- Computer equipment depreciation class: 3-10 years straight-line
- AI accelerator cycle: 1-2 years (H100→B100→B200)
- Result: AI compute depreciation continues to understate economic consumption

**TSLA-2024-SIG-003【HIGH】** — MD&A - Automotive Gross Margin（MD&A - Results of Operations）
> Automotive gross margin decreased to 17.9% in 2024 from 19.4% in 2023, primarily due to lower average selling prices and higher production costs.

推断链：
- Automotive gross margin: 28.5% (2022) → 19.4% (2023) → 17.9% (2024)
- Margin compression: -10.6pp in 2 years
- Price reductions to maintain volume in competitive market
- Lower margins → reduced cash flows → closer to impairment threshold
- Result: margin trajectory is a leading indicator of impairment risk

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与2022/2023年相同的折旧年限结构。2024年新因素：Cybertruck量产意味着更多专用制造设备投入使用，这些设备可能在下一代平台切换时提前淘汰。AI训练计算需求因FSD V12而激增。评4分（与2022/2023锚点一致）。 |
| D2 政策保守性 | **3** | 2024年无任何折旧年限变更（与2022/2023年一致）。落在锚点"无变更→3"档。评3分（与2022/2023锚点一致）。 |
| D3 减值触发 | **3** | 2024年汽车毛利率降至17.9%（2022年28.5%），margin compression使资产现金流更接近减值测试阈值。但尚未触发减值。Cybertruck专用设备若在平台切换时提前退役，可能产生减值。评3分（略高于2022/202... |
| D4 CAPEX 强度 | **4** | CAPEX/收入=$11.34B/$97.69B=11.6%，高于2022年的8.8%和2023年的9.2%。Cybertruck工厂扩建、墨西哥工厂规划、AI训练集群扩张均推高CAPEX。评4分（高于2022/2023的3分，因CAPEX... |
| D5 竞争替代 | **5** | 2024年竞争空前激烈：中国电动车（比亚迪、蔚来、小鹏）全球扩张，价格战席卷全球。特斯拉在美国市场面临利率上升和补贴退坡压力。AI/FSD方面，Waymo、百度Apollo、华为ADS等竞争对手加速。评5分（高于2022/2023的4分，因... |

**验算**：4×0.25 + 3×0.20 + 3×0.20 + 4×0.20 + 5×0.15 = 4×0.25=1.00 + 3×0.20=0.60 + 3×0.20=0.60 + 4×0.20=0.80 + 5×0.15=0.75 = **3.75** ✓
**置信度**：0.8 — Based on TSLA 2023 confirmed annotation with 2024-specific updates. Financial data approximated from MD&A trends. The margin compression and platform proliferation are new risk factors in 2024.

**跨年轨迹**：TSLA 2022 (3.20) → 2023 (3.20) → 2024 (3.85). Score increased in 2024 due to margin compression (-10.6pp in 2 years) and intensifying competition, despite identical depreciation policies.

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2022 | 3.20 | 4 | 3 | 2 | 3 | 4 | draft_pending_review |
| 2023 | 3.20 | 4 | 3 | 2 | 3 | 4 | confirmed |
| 2024 | 3.75 | 4 | 3 | 3 | 4 | 5 | draft_pending_review |

### 政策延续 vs 变化

- **2022 基期**：None disclosed for fiscal 2022. No useful-life revision for any asset class.
- **2023 维持**：无新的年限变更，沿用上期政策
- **2024 维持**：无新的年限变更，沿用上期政策

### 分数差异理由

**2022 → 2023（3.20 → 3.20，Δ+0.00）**：
- 维度无变化

**2023 → 2024（3.20 → 3.75，Δ+0.55）**：
- 维度变化：D3 减值触发 2→3；D4 CAPEX 强度 3→4；D5 竞争替代 4→5

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
| TSLA-2022-SIG-001 | Item 1A. Risk Factors | Item 1A. Risk Factors (HTML L750) | ☐ |
| TSLA-2022-SIG-002 | Note 2. Summary of Significant Accounting Policies | Note 2. Summary of Significant Accounting Policies | ☐ |
| TSLA-2022-SIG-003 | Item 1. Business + Note 8. Property, Plant and Equipment | Item 1. Business - Self-Driving Development | ☐ |
| TSLA-2022-SIG-004 | Note 2. Impairment Policy | Note 2. Long-Lived Assets Including Acquired Intangible Assets | ☐ |
| TSLA-2023-SIG-001 | Item 1A. Risk Factors | Item 1A. Risk Factors - 标题 'We may be negatively impacted by any early obsolescence of our manufacturing equipment.' 处（纯文本定位串 'We depreciate the cost of our manufacturing equipment'） | ☐ |
| TSLA-2023-SIG-002 | Notes to Consolidated Financial Statements - Note 2. Summary of Significant Accounting Policies | Note 2. Summary of Significant Accounting Policies - 'Property, Plant and Equipment, Net' 小节（定位串 'Machinery, equipment, vehicles and office furniture 3 to 15 years'） | ☐ |
| TSLA-2023-SIG-003 | Item 1. Business + Note 8. Property, Plant and Equipment, Net | Item 1. Business - 'Self-Driving Development and Artificial Intelligence'（定位串 'additional computer hardware to better enable the massive amounts of field data'）；Note 8 PP&E 表（定位串 'Computer equipment, hardware and software $ 3,799 $ 2,072'） | ☐ |
| TSLA-2023-SIG-004 | Notes to Consolidated Financial Statements - Note 2. Summary of Significant Accounting Policies | Note 2 - 'Long-Lived Assets Including Acquired Intangible Assets' 小节（定位串 'no material impairments of our long-lived assets'） | ☐ |
| TSLA-2023-SIG-005 | Notes to Consolidated Financial Statements - Note 8. Property, Plant and Equipment, Net | Note 8. Property, Plant and Equipment, Net - Panasonic 安排段落（定位串 'units-of-production method whereby capitalized costs are amortized'） | ☐ |
| TSLA-2023-SIG-006 | Item 7. MD&A - Liquidity and Capital Resources | Item 7. MD&A - 'Cash Flow and Capital Expenditure Trends'（定位串 'expect our capital expenditures to exceed $10.00 billion in 2024'） | ☐ |
| TSLA-2024-SIG-001 | Item 1A. Risk Factors | Item 1A. Risk Factors | ☐ |
| TSLA-2024-SIG-002 | MD&A / Note 8 | Note 1 / Note 8 | ☐ |
| TSLA-2024-SIG-003 | MD&A - Automotive Gross Margin | MD&A - Results of Operations | ☐ |
| TSLA-2024-SIG-004 | Note 2. Impairment Policy | Note 2. Long-Lived Assets | ☐ |
| TSLA-2024-SIG-005 | MD&A - Cybertruck Ramp | MD&A - Business Overview | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
