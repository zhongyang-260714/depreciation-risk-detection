# Oracle Corporation（ORCL）折旧风险评分依据与推断链——三年合并核对

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

## 一、Oracle Corporation 2023（截至 2023-05-31） → 综合 4.00 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（10 条信号中最关键的 3 条）

**ORCL-FY2023-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies - Use of Estimates（Note 1. Organization and Significant Accounting Policies - Use of Estimates (HTML line 7442)）
> During the first quarter of fiscal 2023, we completed an assessment of the useful lives of our servers and increased the estimate of the useful lives from four years to five years effective at the beginning of fiscal 2023. Based on the carrying value of our servers as of May 31, 2022, this change in accounting estimate decreased our total operating expenses by $ 434 million during fiscal 2023.

推断链：
- Official disclosure: servers 4->5 years, effective beginning of fiscal 2023, Note 1 Use of Estimates (L7442)
- Quantified effect: -$434M total operating expenses during fiscal 2023 (~5.1% of FY2023 net income $8,503M)
- Change in accounting estimate => prospective application, prior-period under-depreciation never corrected
- Same fiscal year: capex up 93% ($4,511M -> $8,695M) for cloud/AI infrastructure build-out (MD&A L4094-4100)
- AI hardware iteration cycle is 1-2 years (NVIDIA A100 2020 -> H100 2022); a 5-year life spans 2.5-5 technology generations
- Result: FY2023 reported net income of $8,503M directly embeds the $434M expense reduction; the lengthened 5-year life governs all server depreciation from FY2023 onward

**ORCL-FY2023-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 5. Property, Plant and Equipment（Note 5. Property, Plant and Equipment (HTML lines 8211-8331; policy text at Note 1, line 7448: 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.')）
> Computer, network, machinery and equipment: Useful Life 1 - 5 years: $17,258 million (May 31, 2023) vs $12,844 million (May 31, 2022). Total property, plant and equipment: $28,674 million (2023) vs $19,674 million (2022); Accumulated depreciation: $(11,605) vs $(9,958); Total property, plant and equipment, net: $17,069 vs $9,716. (1) Amounts primarily consist of computer equipment to be built and deployed at our data centers. [construction in progress footnote]

推断链：
- Computer/network/equipment gross: $17,258M at FY2023 end (+34.4% YoY), depreciated over 1-5 years
- Total PP&E gross grew $19,674M -> $28,674M (+45.7%); net PP&E up 75.7% to $17,069M
- Server life (5 years, just extended from 4) vs AI accelerator economic cycle (1-2 years) = 2.5-5x mismatch
- Accumulated depreciation ($11,605M) = only 40.5% of gross PP&E, consistent with a young, rapidly expanding asset base
- Result: the newest, largest asset cohort is depreciated under the newly-lengthened life assumption

**ORCL-FY2023-SIG-003【HIGH】** — Notes to Consolidated Financial Statements - Note 1. Property, Plant and Equipment（Note 1. Organization and Significant Accounting Policies - Property, Plant and Equipment (HTML line 7448)）
> Property, plant and equipment are stated at cost, less accumulated depreciation. Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years. Leasehold improvements are amortized over the lesser of the estimated useful lives of the improvements or the lease terms, as appropriate. Property, plant and equipment are periodically reviewed for impairment whenever events or changes in circumstances indicate that the carrying amount of an asset may not be recoverable. We did not recognize any significant property impairment charges in fiscal 2023, 2022 or 2021.

推断链：
- Impairment test triggered only by 'events or changes in circumstances'
- FY2021-FY2023: no significant property impairment despite AI hardware generation turnover beginning in FY2023
- Same period: server life extended 4->5 years (expense down $434M), never shortened
- Accounting asymmetry: good news (longer life) recognized immediately, bad news (obsolescence) absorbed silently
- Result: FY2023 margins are structurally flattered relative to economic consumption of the server fleet

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 服务器折旧年限本期由4年延长至5年（L7442），Note 5明细表'Computer, network, machinery and equipment 1-5年'（L8218-8220）上限5年，落在锚点'5年左右且与技术迭代错配→4'... |
| D2 政策保守性 | **5** | 锚点'本期延长年限+未来适用法+量化影响→5'：FY2023正是变更发生年——FY2023 Q1将服务器年限4→5年、自财年初生效、按会计估计变更处理（基于2022-05-31账面价值、未来适用不追溯；注：正文未用'prospectivel... |
| D3 减值触发 | **3** | FY2023无任何已确认固定资产减值：Note 1声明FY2023/2022/2021连续三年无重大property减值（L7448）；FY2024 MD&A出现的'certain asset impairment charges'（$31... |
| D4 CAPEX 强度 | **4** | CAPEX/收入=8,695/49,954=17.4%，落在15-25%档→4分（CAPEX同比+93%，MD&A L4094-4100，为AI/OCI扩张启动年）。结构性低估同样存在：$9.1B数据中心经营租赁承诺未上表（L10875），... |
| D5 竞争替代 | **4** | 锚点'云基础设施直接运营+AI迭代压力→4'：Oracle以OCI（第二代云基础设施，L3603）直接运营AI云，FY2023承接Cerner并表+资本开支+93%激进扩张，管理层自认ML/AI正驱动技术革新（L880）并投入'第二代云基础... |

**验算**：4×0.25 + 5×0.20 + 3×0.20 + 4×0.20 + 4×0.15 = 4×0.25=1.00 + 5×0.20=1.00 + 3×0.20=0.60 + 4×0.20=0.80 + 4×0.15=0.60 = **4.00** ✓
**置信度**：0.85 — 全部财务数据与引文逐字核对于FY2023 10-K正文（含HTML行号）。FY2023为年限变更本期发生年，D2按本期变更锚点评5（对齐GOOGL 2023）；D4按实际17.4%资本强度评4；D1/D3/D5与FY2024确认版完全一致。扣分项：无任何已确认固定资产减值、AI风险措辞尚温和；加分项：本期变更+$434M量化影响、capex +93%、在建工程+651%、$9.1B表外租赁承诺起点。

---

## 二、Oracle Corporation 2024（截至 2024-05-31） → 综合 3.60 🟠 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（8 条信号中最关键的 3 条）

**ORCL-FY2024-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies（Note 1. Organization and Significant Accounting Policies - Critical Accounting Policies (HTML line 7317)）
> During the first quarter of fiscal 2023, we completed an assessment of the useful lives of our servers and increased the estimate of the useful lives from four years to five years effective at the beginning of fiscal 2023. Based on the carrying value of our servers as of May 31, 2022, this change in accounting estimate decreased our total operating expenses by $ 434 million during fiscal 2023.

推断链：
- Official disclosure: servers 4->5 years, effective beginning FY2023, disclosed in FY2024 10-K Note 1
- Quantified effect: -$434M total operating expenses during fiscal 2023 (prospectively, no restatement)
- Change direction is lengthening (expense-reducing) precisely while Oracle was ramping AI/OCI infrastructure investment
- AI hardware iteration cycle is 1-2 years (NVIDIA H100 2022 -> B100 2024); a 5-year life spans 2.5-5 technology generations
- All servers on Oracle's books during FY2024 (computer/network/equipment gross $20,989M) are depreciated under the extended life
- Result: FY2024 reported net income of $10,467M embeds the ongoing benefit of the extended server life; historical FY2022-and-earlier under-depreciation permanently uncorrected

**ORCL-FY2024-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 5. Property, Plant and Equipment（Note 5. Property, Plant and Equipment (HTML lines 7888, 7923-8023); policy text at Note 1 (line 7323): 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.'）
> Computer, network, machinery and equipment: Useful Life 1 - 5 years: $20,989 million (May 31, 2024) vs $17,258 million (May 31, 2023). Total property, plant and equipment: $34,818 million (2024) vs $28,674 million (2023); Accumulated depreciation: $(13,282) vs $(11,605); Total property, plant and equipment, net: $21,536 vs $17,069.

推断链：
- Computer/network/equipment gross: $20,989M at FY2024 end (+21.6% YoY), depreciated over 1-5 years
- Total PP&E gross grew $34,818M from $28,674M (+21.4%); net PP&E up 26.2% to $21,536M
- Server life (5 years) vs AI accelerator economic cycle (1-2 years) = 2.5-5x mismatch
- Accumulated depreciation ($13,282M) = only 38.1% of gross PP&E, consistent with a young, rapidly expanding asset base
- Result: the newest, largest asset cohort is depreciated under the most optimistic life assumption

**ORCL-FY2024-SIG-003【HIGH】** — Notes to Consolidated Financial Statements - Note 1. Property, Plant and Equipment（Note 1. Organization and Significant Accounting Policies - Property, Plant and Equipment (HTML line 7323)）
> Property, plant and equipment are periodically reviewed for impairment whenever events or changes in circumstances indicate that the carrying amount of an asset may not be recoverable at an appropriate asset or asset group level. We did not recognize any significant property impairment charges in fiscal 2024, 2023 or 2022.

推断链：
- Impairment test triggered only by 'events or changes in circumstances', measured at asset-group level
- FY2022-FY2024: no significant property impairment despite AI hardware generation turnover
- Same period: server life extended 4->5 years (expense down), never shortened
- Accounting system is asymmetric: good news (longer life) recognized immediately, bad news (obsolescence) absorbed silently
- Result: FY2024 margins are structurally flattered relative to economic consumption of the server fleet

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 服务器折旧年限经FY2023 Q1变更后现行5年（Note 5明细表'Computer, network, machinery and equipment 1-5年'，L7923-7925），落在锚点4-6年档→4分。⚠️前提修正：外部信息... |
| D2 政策保守性 | **4** | 锚点'历史有延长→4'：FY2023 Q1将服务器年限4→5年、按未来适用法处理（基于2022-05-31账面价值、不追溯），减少FY2023经营费用$434M（约占FY2023净利润$8,503M的5.1%），该估计变更的持续效应贯穿FY... |
| D3 减值触发 | **3** | FY2024有实际减值但很小：MD&A两处（L1780、L3482）披露acquisition related and other费用（$314M）含'certain asset impairment charges'，未单独量化；Note... |
| D4 CAPEX 强度 | **3** | CAPEX/收入=6,866/52,961=13.0%，落在8-15%档→3分（FY2023为8,695/49,954=17.4%，FY2024表观回落）。但需注意结构性低估：Oracle大量数据中心容量通过经营租赁获得（FY2024租赁费... |
| D5 竞争替代 | **4** | Oracle以OCI直接运营AI云基础设施，是算力竞赛主力之一：承接大规模AI训练/推理负载（与NVIDIA深度合作、参股ARM服务器芯片商Ampere约29%），管理层自述AI'highly competitive and rapidly... |

**验算**：4×0.25 + 4×0.20 + 3×0.20 + 3×0.20 + 4×0.15 = 4×0.25=1.00 + 4×0.20=0.80 + 3×0.20=0.60 + 3×0.20=0.60 + 4×0.15=0.60 = **3.60** ✓
**置信度**：0.85 — 全部财务数据与引文逐字核对于FY2024 10-K正文（含行号）。前提修正已落实：外部假设的'FY2024 5→8年'在文件中不存在，实际为FY2023 Q1 4→5年（-$434M费用，L7317），本标注按文件事实评分。扣分项：FY2024本期无年限变更、无重大PP&E减值，故D2/D3不及GOOGL/META；加分项：$32.2B表外数据中心租赁承诺与在建工程+46.5%显示风险正在向后累积。

---

## 三、Oracle Corporation 2025（截至 2025-05-31） → 综合 4.45 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（10 条信号中最关键的 3 条）

**ORCL-FY2025-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies（Note 1. Organization and Significant Accounting Policies - Critical Accounting Policies (HTML line 6755); same change re-disclosed as footnote (2) to Note 4 PP&E table (HTML line 7507)）
> During the first quarter of fiscal 2025, we completed an assessment of the useful lives of our servers and networking equipment and increased the estimate of the useful lives from five years to six years, effective at the beginning of fiscal 2025. Based on the carrying value of our servers and networking equipment as of May 31, 2024, this change in accounting estimate decreased our total operating expenses by $733 million and increased our net income by $573 million, or $0.21 per basic and $0.20 per diluted share, during fiscal 2025.

推断链：
- Official disclosure: servers AND networking equipment 5->6 years, effective beginning FY2025 (Note 1, L6755; Note 4 footnote (2), L7507)
- Quantified effect: -$733M operating expenses, +$573M net income, +$0.21/$0.20 EPS during fiscal 2025 (prospective, no restatement)
- Second consecutive extension: 4->5 (FY2023) then 5->6 (FY2025); cumulative 50% life extension in three years
- Change enacted in the same year capex tripled to $21.2B and CIP nearly tripled to $16.5B - depreciation step-up mechanically suppressed
- AI hardware iteration cycle is 1-2 years (NVIDIA H100 2022 -> B100/GB200 2024 -> Rubin 2026); a 6-year life spans 3-6 technology generations
- Result: FY2025 reported net income of $12,443M embeds +$573M (4.6%) from the extended life; prior-period under-depreciation permanently uncorrected

**ORCL-FY2025-SIG-008【CRITICAL】** — Consolidated Statements of Cash Flows; Note 4 - Construction in Progress（Consolidated Statements of Cash Flows (HTML lines 6206-6217, 6440-6452); Note 4 (HTML lines 7456-7465, footnote (1) at line 7507)）
> Depreciation: $3,867 (FY2025), $3,129 (FY2024), $2,526 (FY2023). Capital expenditures: $(21,215) (FY2025), $(6,866) (FY2024), $(8,695) (FY2023). Construction in progress: $16,510 (May 31, 2025) vs $5,634 (May 31, 2024). (1) Amounts primarily consist of computer equipment to be built and deployed at our data centers.

推断链：
- CIP (data center computer equipment) up 193% YoY to $16,510M - none of it depreciating yet
- FY2025 depreciation $3,867M = only 18.2% of FY2025 capex $21,215M (down from 45.6% in FY2024)
- Capex/revenue jumped to 36.9% from 13.0%; two-year capex (FY2024+FY2025 = $28.1B) dwarfs FY2025 depreciation
- The FY2025 life extension removed $733M of operating expenses in the very year the capex wave landed - timing is not coincidental
- Result: current depreciation massively understates the run-rate cost of the AI capacity being deployed; the gap is deferred, not eliminated

**ORCL-FY2025-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 4. Property, Plant and Equipment（Note 4. Property, Plant and Equipment (HTML lines 7369, 7404-7504); policy text at Note 1 (line 6785): 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.'）
> Computer, network, machinery and equipment: Useful Life 1 - 6 years (footnote 2): $30,345 million (May 31, 2025) vs $20,989 million (May 31, 2024). Total property, plant and equipment: $59,554 million (2025) vs $34,818 million (2024); Accumulated depreciation: $(16,032) vs $(13,282); Total property, plant and equipment, net: $43,522 vs $21,536.

推断链：
- Computer/network/equipment gross: $30,345M at FY2025 end (+44.6% YoY), depreciated over 1-6 years (upper bound raised from 5)
- Total PP&E gross $59,554M (+71.0%); net PP&E $43,522M (+102.1% YoY)
- Server/network life (6 years) vs AI accelerator economic cycle (1-2 years) = 3-6x mismatch, worsening from FY2024's 2.5-5x
- Accumulated depreciation ($16,032M) = only 26.9% of gross PP&E (down from 38.1% in FY2024), consistent with a very young, explosively expanding asset base
- Result: the newest, largest asset cohort is depreciated under the most optimistic life assumption in Oracle's history

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **5** | 锚点'≥6年→5'：FY2025 Q1服务器及网络设备年限经变更后现行6年（Note 1 L6755；Note 4明细表'Computer, network, machinery and equipment 1-6年'，L7406），达到6... |
| D2 政策保守性 | **5** | 锚点'本期延长年限→5'：FY2025 Q1本期将服务器及网络设备年限5→6年、按未来适用法处理（基于2024-05-31账面价值、不追溯），减少FY2025经营费用$733M、增加净利润$573M（占FY2025净利润$12,443M的4... |
| D3 减值触发 | **3** | 与FY2024锚点一致维持3分：FY2025仍有大额减值缺失与小额未量化减值并存的格局——Note 1声明FY2025/2024/2023连续三年无重大固定资产减值（L6785）；MD&A（L3035）显示acquisition relat... |
| D4 CAPEX 强度 | **5** | 锚点'>25%→5'：CAPEX/收入=21,215/57,399=37.0%，远超25%档→5分（FY2024为13.0%→3分，分数变化反映OCI扩张的真实跳升：capex同比3.1倍）。且仍有结构性低估：另有$43.4B未上表租赁承诺... |
| D5 竞争替代 | **4** | 锚点'云基础设施直接运营+AI迭代压力→4'，与FY2024一致维持4分：Oracle以OCI直接运营AI云基础设施且强度升级——云服务收入占比43%（FY2024 37%）、capex $21.2B、$43.4B租赁承诺、新增AI加速器/... |

**验算**：5×0.25 + 5×0.20 + 3×0.20 + 5×0.20 + 4×0.15 = 5×0.25=1.25 + 5×0.20=1.00 + 3×0.20=0.60 + 5×0.20=1.00 + 4×0.15=0.60 = **4.45** ✓
**置信度**：0.85 — 全部财务数据与引文逐字核对于FY2025 10-K正文（含HTML行号）。与FY2024确认版锚点一致：D3/D5维持原分（无质变），D1/D2/D4上调均由文件事实驱动——本期年限5→6年（L6755，-$733M费用/+$573M净利）、capex/收入13.0%→37.0%（L6440、L4547）。扣分项：连续三年无重大PP&E减值、小额减值同比减少，故D3维持3；加分项：三年内第二次延长年限、$43.4B表外租赁承诺近乎翻倍、在建工程+193%，风险从FY2024的'向后递延'转为'当期兑现'。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2023 | 4.00 | 4 | 5 | 3 | 4 | 4 | draft_pending_review |
| 2024 | 3.60 | 4 | 4 | 3 | 3 | 4 | confirmed |
| 2025 | 4.45 | 5 | 5 | 3 | 5 | 4 | draft_pending_review |

### 政策延续 vs 变化

- **2023 本期延长**：本期发生折旧年限延长
- **2024 历史延长生效中**：无新的年限变更，上期延长政策继续适用
- **2025 新增变更（本期延长）**：

### 分数差异理由

**2023 → 2024（4.00 → 3.60，Δ-0.40）**：
- 维度变化：D2 政策保守性 5→4；D4 CAPEX 强度 4→3

**2024 → 2025（3.60 → 4.45，Δ+0.85）**：
- 维度变化：D1 年限错配 4→5；D2 政策保守性 4→5；D4 CAPEX 强度 3→5

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
| ORCL-FY2023-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies - Use of Estimates | Note 1. Organization and Significant Accounting Policies - Use of Estimates (HTML line 7442) | ☐ |
| ORCL-FY2023-SIG-002 | Notes to Consolidated Financial Statements - Note 5. Property, Plant and Equipment | Note 5. Property, Plant and Equipment (HTML lines 8211-8331; policy text at Note 1, line 7448: 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.') | ☐ |
| ORCL-FY2023-SIG-003 | Notes to Consolidated Financial Statements - Note 1. Property, Plant and Equipment | Note 1. Organization and Significant Accounting Policies - Property, Plant and Equipment (HTML line 7448) | ☐ |
| ORCL-FY2023-SIG-004 | Item 1A. Risk Factors - Oracle Cloud Strategy / Data Center Capacity | Item 1A. Risk Factors (HTML line 899) | ☐ |
| ORCL-FY2023-SIG-005 | Item 1A. Risk Factors - Supply Chain | Item 1A. Risk Factors - Supply Chain (HTML line 920) | ☐ |
| ORCL-FY2023-SIG-006 | Item 1A. Risk Factors - Cloud Products / AI | Item 1A. Risk Factors (HTML line 880) | ☐ |
| ORCL-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies | Note 1. Organization and Significant Accounting Policies - Critical Accounting Policies (HTML line 7317) | ☐ |
| ORCL-FY2024-SIG-002 | Notes to Consolidated Financial Statements - Note 5. Property, Plant and Equipment | Note 5. Property, Plant and Equipment (HTML lines 7888, 7923-8023); policy text at Note 1 (line 7323): 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.' | ☐ |
| ORCL-FY2024-SIG-003 | Notes to Consolidated Financial Statements - Note 1. Property, Plant and Equipment | Note 1. Organization and Significant Accounting Policies - Property, Plant and Equipment (HTML line 7323) | ☐ |
| ORCL-FY2024-SIG-004 | Item 1A. Risk Factors - Data Center Capacity; Note 10. Leases | Item 1A. Risk Factors (HTML line 894); Note 10. Leases, Other Commitments and Certain Contingencies (HTML lines 10623, 10695) | ☐ |
| ORCL-FY2024-SIG-005 | Item 1A. Risk Factors - Supply Chain | Item 1A. Risk Factors - Supply Chain (HTML line 911) | ☐ |
| ORCL-FY2024-SIG-006 | Item 1A. Risk Factors - AI Products | Item 1A. Risk Factors - AI Products (HTML line 887) | ☐ |
| ORCL-FY2025-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Organization and Significant Accounting Policies | Note 1. Organization and Significant Accounting Policies - Critical Accounting Policies (HTML line 6755); same change re-disclosed as footnote (2) to Note 4 PP&E table (HTML line 7507) | ☐ |
| ORCL-FY2025-SIG-002 | Notes to Consolidated Financial Statements - Note 4. Property, Plant and Equipment | Note 4. Property, Plant and Equipment (HTML lines 7369, 7404-7504); policy text at Note 1 (line 6785): 'Depreciation is computed using the straight-line method based on estimated useful lives of the assets, which range from one to 40 years.' | ☐ |
| ORCL-FY2025-SIG-003 | Notes to Consolidated Financial Statements - Note 1. Property, Plant and Equipment | Note 1. Organization and Significant Accounting Policies - Property, Plant and Equipment (HTML line 6785) | ☐ |
| ORCL-FY2025-SIG-004 | Item 1A. Risk Factors - Data Center Capacity; Note 9. Leases | Item 1A. Risk Factors (HTML line 699); Note 9. Leases, Other Commitments and Certain Contingencies (HTML line 10592) | ☐ |
| ORCL-FY2025-SIG-005 | Item 1A. Risk Factors - Supply Chain | Item 1A. Risk Factors - Supply Chain (HTML line 709) | ☐ |
| ORCL-FY2025-SIG-006 | Item 1A. Risk Factors - AI Products | Item 1A. Risk Factors - AI Products (HTML lines 694, 699) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
