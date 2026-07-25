# Intel Corporation（INTC）折旧风险评分依据与推断链——三年合并核对

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

## 一、Intel Corporation 2022（截至 2022-12-31） → 综合 3.90 🟠 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**INTC-FY2022-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1/2. Accounting Policies - Long-Lived Assets / Property, Plant and Equipment（Note 2. Accounting Policies - Property, Plant and Equipment (HTML lines 4218-4220)）
> Based on our latest evaluation, effective January 2023, the estimated useful life of certain machinery and equipment in our wafer fabrication facilities will increase from 5 to 8 years. This change in estimate will be applied prospectively beginning in the first quarter of 2023.

推断链：
- Official disclosure in FY2022 10-K: certain wafer-fab machinery useful life 5 -> 8 years, effective January 2023, prospective
- Decision basis: 'Based on our latest evaluation' - i.e., the annual useful-life evaluation conducted during FY2022
- Same-year operating reality: revenue fell 20.2% ($79,024M -> $63,054M), operating income fell 88.0% ($19,456M -> $2,334M)
- Same-year asset stress signals: $423M excess capacity charges, $723M Optane inventory impairment, $151M restructuring asset impairments
- Prospective application means prior-period under-depreciation (if any) is never corrected
- Result: FY2022 报表是变更前最后一年按 5 年计提的报表，但本期文件已预告自下一年起的费用减负

**INTC-FY2022-SIG-002【CRITICAL】** — Item 7. MD&A - Liquidity / Capital Investments and Useful Life Change discussion（Item 7. MD&A (HTML lines 1810-1827)）
> Effective January 2023, we increased the estimated useful life of certain production machinery and equipment from 5 years to 8 years. We made this change to better reflect the economic value of our machinery and equipment over time. We considered several factors in making this determination, including current usage and expected re-use of machinery and equipment, changes in machinery and equipment technology, future planned cadence between node transitions, a shift to longer duration on trailing-edge technologies, and overall changes in our technology roadmap. Our analysis supported a change in useful life and is consistent with the execution of our IDM 2.0 strategy. This change in estimate w...

推断链：
- Expected effect quantified in MD&A: -$4.2B 2023 depreciation, +$2.6B gross margin, -$400M R&D, -$1.2B ending inventory
- FY2022 operating income was only $2,334M; expected annual P&L benefit (~$3.0B) exceeds it
- Stated rationale includes 'future planned cadence between node transitions' - company's own cadence framework invoked to justify lengthening
- Change consistent with IDM 2.0 strategy per management - depreciation policy subordinated to strategy execution
- Result: FY2022 filing pre-announces a profit-manufacturing assumption change whose benefit dwarfs current-year operating profit

**INTC-FY2022-SIG-003【HIGH】** — Notes to Consolidated Financial Statements - Note 6. Other Financial Statement Details - Property, Plant and Equipment（Note 6. Other Financial Statement Details - Property, Plant and Equipment (HTML lines 4732-4734)）
> Land and buildings $44,808 ($40,039); Machinery and equipment 92,711 (86,955); Construction in progress 36,727 (21,545); Total property, plant and equipment, gross 174,246 (148,539); Less: Accumulated depreciation (93,386) (85,294); Total property, plant and equipment, net $80,860 ($63,245). Our depreciable property, plant and equipment assets are depreciated over the following estimated useful lives: machinery and equipment, 3 to 5 years; and buildings, 10 to 25 years.

推断链：
- Machinery and equipment gross: $92,711M (2022), up $5,756M YoY, depreciated over 3-5 years
- Gross PP&E grew 17.3% YoY; net PP&E up 27.8% to $80,860M
- Accumulated depreciation $93,386M = 53.6% of gross PP&E
- FY2022 depreciation $11,128M vs capex $24,844M (ratio 0.45) - book consumption far below cash build-out
- Result: the asset pool subject to the soon-to-be-extended life assumption is the company's largest and fastest-growing

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | 锚点一致性：FY2023 确认版对变更后 8 年年限评 4（'≥6 年触及最高档，但跨代复用制造业现实部分缓释'）。FY2022 现行年限为机器设备 3-5 年、生产设备 5 年（Note 6，L4733-4734），按任务锚点'变更前 5... |
| D2 政策保守性 | **3** | 锚点'本期延长年限→5；本期无变更→2-3'：FY2022 本期未适用任何折旧年限变更（5→8 变更 2023 年 1 月生效，FY2023 确认版因此评 5），故落在无变更档。但取档内上限 3 而非 2，原因有二：（1）本 10-K 明确... |
| D3 减值触发 | **4** | 按 FY2022 文件事实评分并与 FY2023 确认版（D3=4）锚点一致：'本期大额 PP&E 减值→5；直接信号+历史记录本期减值小→4'。FY2022 有实际减值但需区分性质：重组项下资产减值 $151M（Note 7，L4736）... |
| D4 CAPEX 强度 | **5** | CAPEX/收入=24,844/63,054=39.4%，远超'>25%→5'锚点（FY2023 确认版 47.5% 同评 5，两年同档，锚点一致）。机器设备总值 $92.7B、在建工程 $36.7B（占净 PP&E 45%，同比 +70.... |
| D5 竞争替代 | **5** | 锚点'制造业技术节点竞争压力→4-5'，与 FY2023 确认版（D5=5）一致取 5：FY2022 正是竞争替代在报表层面兑现的年份。（1）先进制程竞赛落后——自认 10nm 重大延误、Intel 4（原 7nm）缺陷模式延误、2022 ... |

**验算**：3×0.25 + 3×0.20 + 4×0.20 + 5×0.20 + 5×0.15 = 3×0.25=0.75 + 3×0.20=0.60 + 4×0.20=0.80 + 5×0.20=1.00 + 5×0.15=0.75 = **3.90** ✓
**置信度**：0.88 — 全部财务数据与引文逐字核对于 FY2022 10-K 正文（含 HTML 行号）。跨年锚点显式对齐 FY2023 确认版：D1/D2 低于 FY2023 系真实政策时点差异（FY2022 为变更前最后一年），D3/D4/D5 与 FY2023 同档系风险实质相同。扣分项：本期无年限变更适用、无大额 PP&E 减值（$723M 为存货减值已区分）；加分项：本期文件已宣布并量化 5→8 年延长（预期 2023 年折旧 -$4.2B），capex 强度 39.4%、CIP +70.5% 显示风险向后累积。

---

## 二、Intel Corporation 2023（截至 2023-12-30） → 综合 4.55 🔴 [✅ confirmed]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**INTC-FY2023-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1. Basis of Presentation / Long-Lived Assets（Note 1. Summary of Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 4247-4249)）
> Effective January 2023, the estimated useful lives of certain machinery and equipment in our wafer fabrication facilities were increased from 5 to 8 years. This change in estimate was applied prospectively beginning in the first quarter of 2023.

推断链：
- Official disclosure: certain wafer-fab production machinery useful life 5 -> 8 years, effective January 2023, prospective
- Same-period revenue fell 14% ($63,054M -> $54,228M) and operating income collapsed to $93M from $2,334M
- 8-year accounting life vs ~1-1.25-year node cadence (Intel 4 shipped Q3 2023; Intel 3/20A/18A to follow by 2025) = ~6 node generations per depreciation life
- Prospective application means prior-period under-depreciation (if any) is never corrected
- Result: 2023 cost of sales and R&D materially understated relative to prior-year depreciation policy

**INTC-FY2023-SIG-002【CRITICAL】** — MD&A - Gross Margin / Liquidity discussion（Item 7. MD&A (HTML lines 1774-1791); corroborated in Note 6 (lines 4744-4750)）
> Effective January 2023, we increased the estimated useful life of certain production machinery and equipment from 5 to 8 years. When compared to the estimated useful life in place as of the end of 2022, we estimate total depreciation expense in 2023 was reduced by $4.2 billion. We estimate this change resulted in an approximately $2.5 billion increase to gross margin, $400 million decrease in R&D expenses, and $1.3 billion decrease in ending inventory values.

推断链：
- Disclosed effect: total 2023 depreciation reduced by $4.2B vs 2022 life assumptions
- +$2.5B gross margin and -$400M R&D expense hit the 2023 income statement; $1.3B remained in ending inventory (deferred to future COGS)
- 2023 operating income was $93M; without the change, operating result would have been a loss of roughly $2.8B
- Management states the precise YoY impact is 'impractical to individually and specifically quantify' because depreciation sits in overhead pools absorbed into inventory (lines 1784-1791) - limiting auditability
- Result: reported 2023 profitability is substantially manufactured by an accounting assumption change

**INTC-FY2023-SIG-003【HIGH】** — MD&A - IDM 2.0 capital investments（Item 7. MD&A (HTML lines 1763-1774)）
> As of December 30, 2023, our capital investments classified as construction in progress totaled $43.4 billion ($36.7 billion as of December 31, 2022). These assets have not yet been placed into service and have not yet begun depreciating... Additionally, we could incur asset impairments on property, plant, and equipment assets if our IDM 2.0 strategy is not successful.

推断链：
- CIP $43,442M as of Dec 30, 2023 (up from $36,727M), not yet depreciating
- Management: as CIP enters service, depreciation will hit production costs and gross margin unless revenue grows
- Management: IDM 2.0 failure could trigger PP&E impairments
- 2023 revenue fell 14% and DCAI/NEX segments shrank, contradicting the revenue-growth assumption
- Result: both legs of the risk (higher future depreciation, or impairment) are management-acknowledged

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 变更后机器设备折旧年限3-8年、生产设备顶格8年，按锚点'≥6年→5'触及最高档。但必须区分制造设备与AI服务器：晶圆厂设备物理磨损寿命确实长达8-15年，且Intel明确以'设备跨代复用'（re-use of machinery and ... |
| D2 政策保守性 | **5** | 本期（2023年1月/Q1）刚刚延长折旧年限并采用未来适用法（prospectively），为锚点最高档'本期延长→5'。变更量化影响：折旧减少$4.2B、毛利率增加~$2.5B、研发费用减少~$400M、期末存货减少~$1.3B。关键背景... |
| D3 减值触发 | **4** | 2023年有实际资产减值但规模小（重组内资产减值$45M），按'本期实际减值→4-5'与'仅间接→3'之间取4。减值触发信号密集且多为直接信号：MD&A明示'IDM 2.0战略不成功可能导致PP&E减值'（L1773-1774）；风险因素明... |
| D4 CAPEX 强度 | **5** | CAPEX/收入=25,750/54,228=47.5%，远超'≥25%→5'锚点，为本批样本中资本强度最高者（META 20.2%、GOOGL 10.5%）。机器设备总值$100.0B、在建工程$43.4B（占净PP&E 45%，尚未开始... |
| D5 竞争替代 | **5** | Intel面临三线竞争替代且均为公司自认：（1）先进制程竞赛落后——自认10nm/7nm延误使'使用TSMC等第三方代工厂的竞争对手受益'（L2410-2414），IFS代工须与TSMC正面竞争，四年五节点是追赶型军备竞赛；（2）AI芯片竞... |

**验算**：4×0.25 + 5×0.20 + 4×0.20 + 5×0.20 + 5×0.15 = 4×0.25=1.00 + 5×0.20=1.00 + 4×0.20=0.80 + 5×0.20=1.00 + 5×0.15=0.75 = **4.55** ✓
**置信度**：0.9 — Strongest evidence class: the 10-K itself quantifies the exact target behavior (production machinery life 5->8 years, -$4.2B depreciation, +$2.5B gross margin) in both MD&A and Note 6, corroborated by the anomalous YoY depreciation decline (-29.5%) amid record capex and PP&E growth, plus direct Risk Factor language on manufacturing-asset write-downs, forced life-shortening, and IDM 2.0 impairment. All figures verified against original filing text with line numbers. Caveat reflected in D1: fab-equipment cross-node reuse means the life-vs-tech-cycle mismatch is structurally weaker than for cloud server fleets.

---

## 三、Intel Corporation 2024（截至 2024-12-28） → 综合 4.55 🔴 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**INTC-FY2024-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 6. Other Financial Statement Details / Property, Plant, and Equipment（Note 6. Other Financial Statement Details - Property, Plant, and Equipment (HTML lines 4532-4544)）
> In connection with the preparation of our Consolidated Financial Statements for the third quarter of 2024, we evaluated our current process technology node capacities relative to projected market demand for our products and services, and concluded that our manufacturing asset portfolio, primarily for our Intel 7 process node, exceeded manufacturing capacity requirements. Upon performing a re-use assessment, we impaired and accelerated depreciation for certain manufacturing assets. In total, we recorded non-cash impairments and accelerated depreciation charges of $2.3 billion and $992 million, respectively, in 2024, substantially all of which were recognized in cost of sales within our Intel ...

推断链：
- Q3 2024 评估结论：制造资产组合（主要 Intel 7 节点）超出产能需求
- 会计后果：非现金减值 $2.3B + 加速折旧 $992M，绝大部分计入 Intel Foundry 成本
- 对照：2023 年 1 月同一资产池刚执行 5→8 年年限延长（-折旧 $4.2B）
- Intel 7 是 2021-2023 年量产主力节点，其资产在 8 年寿命假设下远未折旧完毕即被减值/加速
- 结论：年限延长所依据的'跨代复用'假设在 Intel 7 上被公司自己的复用评估否定，FY2023 的高折旧风险判断被本期事实验证

**INTC-FY2024-SIG-002【CRITICAL】** — MD&A - Consolidated Gross Margin（Item 7. MD&A - Consolidated Gross Margin (HTML lines 1451-1459)）
> Our consolidated gross margin in 2024 decreased by $4.4 billion, or 20%, compared to 2023 due primarily to higher 2024 impairment charges and accelerated depreciation. During Q3 2024, we concluded that our manufacturing asset portfolio, primarily for our Intel 7 process node, exceeded manufacturing capacity requirements. Upon completing an asset re-use assessment, we impaired certain construction-in-progress assets and accelerated depreciation for certain in-use manufacturing assets that resulted in $3.3 billion of charges in 2024.

推断链：
- 2024 毛利率下降 $4.4B（20%），主因是减值与加速折旧
- $3.3B 费用 = CIP 减值 + 在用制造资产加速折旧
- 未转固的 CIP 被减值说明部分产能投资决策在建设中途即被否定
- 2023 年毛利率曾受益 +$2.5B 年限延长；2024 年同一张利润表吞回 $3.3B 现实
- 结论：折旧政策制造的利润修饰开始逆转，且规模与 FY2023 的修饰量同量级

**INTC-FY2024-SIG-003【CRITICAL】** — Item 1A. Risk Factors - Demand / Capacity Utilization（Item 1A. Risk Factors (HTML lines 2002-2010)）
> To the extent the demand decrease is prolonged, our manufacturing or assembly and test capacity could be underutilized, and we may be required to write down our long-lived assets, which would increase our expenses. We may also be required to shorten the useful lives of under-used facilities and equipment and accelerate depreciation. For example, in the third quarter of 2024 we recorded $3.1 billion of charges related to non-cash impairments and the accelerated depreciation for certain manufacturing assets, a substantial majority of which related to the Intel 7 process node.

推断链：
- 风险因素原文承认：需求下滑→产能利用率不足→减记长期资产+缩短年限+加速折旧
- 同段以 FY2024 实际事件为例：Q3 2024 $3.1B 费用，绝大部分 Intel 7 节点
- FY2023 确认版 SIG-008 曾指出年限延长与该风险方向相反；本期该矛盾以加速折旧形式爆发
- 结论：风险因素与会计处理形成完整闭环（警告→兑现），直接信号强度最高

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与 FY2023 确认版锚点一致：机器设备 3-8 年、生产设备顶格 8 年的政策未变，维持 4 分。锚点逻辑复核：8 年年限仍横跨约 6 代节点（18A 2025 量产、14A 开发中，节奏未放缓），错配客观存在；但制造业跨节点复用的缓释... |
| D2 政策保守性 | **4** | FY2023 确认版为 5（本期延长年限+未来适用）。FY2024 本期无任何折旧年限变更（全文检索确认），5→8 年延长作为历史变更继续生效，按锚点'历史有延长本期无变更→4'降 1 分。存量风险仍在：未来适用法下历史期间永不追溯；折旧进... |
| D3 减值触发 | **5** | FY2023 确认版为 4（直接信号充足但本期 PP&E 纯减值仅 $45M）。FY2024 按锚点'本期大额 PP&E 减值→5'顶格：Q3 2024 制造资产非现金减值 $2.3B + 加速折旧 $992M（主要 Intel 7 节点，... |
| D4 CAPEX 强度 | **5** | 与 FY2023 确认版锚点一致：capex/收入 = 23,944/53,101 = 45.1%，远超'≥25%→5'，维持 5 分。绝对额从 $25.75B 降至 $23.9B、资本承诺从 $27.5B 收缩至 $20.0B、五地建厂推... |
| D5 竞争替代 | **5** | 与 FY2023 确认版锚点一致维持 5 分，且证据进一步强化：竞争替代已从利润表压力升级为资产端实际减记——Intel 7（上一代主力节点）资产因需求不足被减值，公司自认产品/技术'can become uncompetitive or ... |

**验算**：4×0.25 + 4×0.20 + 5×0.20 + 5×0.20 + 5×0.15 = 4×0.25=1.00 + 4×0.20=0.80 + 5×0.20=1.00 + 5×0.20=1.00 + 5×0.15=0.75 = **4.55** ✓
**置信度**：0.92 — 本期证据强度为全样本最高：10-K 在 MD&A、Note 6、Note 7、风险因素四处交叉量化同一事件（Intel 7 节点制造资产 $2.3B 减值 + $992M 加速折旧 + 重组减值 $3.6B + 商誉减值 $2.8B），且风险因素文本从假设升级为实指。综合分 4.55 与 FY2023 确认版持平是锚点结构的自然结果而非巧合掩盖：D2 降 1（本期无新年限变更）与 D3 升 1（本期大额减值兑现）精确对冲，反映风险形态从'会计假设虚高风险'转化为'风险已部分兑现、剩余资产仍承压'。所有引文经去标签后逐字核对原文行号。

**NA 项**：D1 年限错配：与 FY2023 确认版锚点一致：机器设备 3-8 年、生产设备顶格 8 年的政策未变，维持 4 分。锚点逻辑复核：8 年年限仍横跨约 6 代节点（18A 2025 量产、14A 开发中，节奏未放缓），错配客观存在；但制造业跨节点复用的缓释理由本期被公司自己的复用评估（re-use assessment）部分否定——Intel 7 资产被认定超出产能需求并减值/加速折旧，说明对上一代节点资产，8 年寿命假设已被证明偏乐观。然而 18A/14A 新节点设备（含 EUV/High-NA）的跨代复用仍可能成立，且年限表本身未变，故不上调至 5。分数不变反映政策未变，而非风险消失。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2022 | 3.90 | 3 | 3 | 4 | 5 | 5 | draft_pending_review |
| 2023 | 4.55 | 4 | 5 | 4 | 5 | 5 | confirmed |
| 2024 | 4.55 | 4 | 4 | 5 | 5 | 5 | draft_pending_review |

### 政策延续 vs 变化

- **2022 基期**：无特别变更记录
- **2023 新增变更（本期延长）**：
- **2024 历史延长生效中**：无新的年限变更，上期延长政策继续适用

### 分数差异理由

**2022 → 2023（3.90 → 4.55，Δ+0.65）**：
- 维度变化：D1 年限错配 3→4；D2 政策保守性 3→5

**2023 → 2024（4.55 → 4.55，Δ+0.00）**：
- 维度变化：D2 政策保守性 5→4；D3 减值触发 4→5

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
| INTC-FY2022-SIG-001 | Notes to Consolidated Financial Statements - Note 1/2. Accounting Policies - Long-Lived Assets / Property, Plant and Equipment | Note 2. Accounting Policies - Property, Plant and Equipment (HTML lines 4218-4220) | ☐ |
| INTC-FY2022-SIG-002 | Item 7. MD&A - Liquidity / Capital Investments and Useful Life Change discussion | Item 7. MD&A (HTML lines 1810-1827) | ☐ |
| INTC-FY2022-SIG-003 | Notes to Consolidated Financial Statements - Note 6. Other Financial Statement Details - Property, Plant and Equipment | Note 6. Other Financial Statement Details - Property, Plant and Equipment (HTML lines 4732-4734) | ☐ |
| INTC-FY2022-SIG-004 | Item 7. MD&A - IDM 2.0 capital investments | Item 7. MD&A (HTML lines 1800-1810) | ☐ |
| INTC-FY2022-SIG-005 | Notes to Consolidated Financial Statements - Note 3. Operating Segments | Note 3. Operating Segments (HTML lines 4674-4682); 非 GAAP 调节表同页佐证 Optane inventory impairment 影响毛利率 1.1 个百分点（L2190） | ☐ |
| INTC-FY2022-SIG-006 | Notes to Consolidated Financial Statements - Note 7. Restructuring and Other Charges; Item 7. MD&A | Note 7. Restructuring and Other Charges (HTML line 4736); MD&A Restructuring and Other Charges (HTML line 1837) | ☐ |
| INTC-FY2023-SIG-001 | Notes to Consolidated Financial Statements - Note 1. Basis of Presentation / Long-Lived Assets | Note 1. Summary of Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 4247-4249) | ☐ |
| INTC-FY2023-SIG-002 | MD&A - Gross Margin / Liquidity discussion | Item 7. MD&A (HTML lines 1774-1791); corroborated in Note 6 (lines 4744-4750) | ☐ |
| INTC-FY2023-SIG-003 | MD&A - IDM 2.0 capital investments | Item 7. MD&A (HTML lines 1763-1774) | ☐ |
| INTC-FY2023-SIG-004 | Notes to Consolidated Financial Statements - Note 6. Other Financial Statement Details | Note 6. Other Financial Statement Details - Property, Plant, and Equipment (HTML lines 4742-4747) | ☐ |
| INTC-FY2023-SIG-005 | Notes to Consolidated Financial Statements - Note 1. Long-Lived Assets | Note 1. Summary of Significant Accounting Policies - Property, Plant, and Equipment (HTML lines 4236-4247) | ☐ |
| INTC-FY2023-SIG-006 | Item 1. Business - Process Technology Roadmap | Item 1. Business (HTML lines 580-610) | ☐ |
| INTC-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Note 6. Other Financial Statement Details / Property, Plant, and Equipment | Note 6. Other Financial Statement Details - Property, Plant, and Equipment (HTML lines 4532-4544) | ☐ |
| INTC-FY2024-SIG-002 | MD&A - Consolidated Gross Margin | Item 7. MD&A - Consolidated Gross Margin (HTML lines 1451-1459) | ☐ |
| INTC-FY2024-SIG-003 | Item 1A. Risk Factors - Demand / Capacity Utilization | Item 1A. Risk Factors (HTML lines 2002-2010) | ☐ |
| INTC-FY2024-SIG-004 | Item 1A. Risk Factors - Process Technology Development | Item 1A. Risk Factors (HTML lines 2045-2052) | ☐ |
| INTC-FY2024-SIG-005 | MD&A / Note 7. Restructuring and Other Charges | MD&A Restructuring and Other Charges (HTML line 1497); Note 7 (HTML line 4593) | ☐ |
| INTC-FY2024-SIG-006 | MD&A / Note 7. Restructuring and Other Charges - Asset impairment charges detail | MD&A Restructuring and Other Charges (HTML lines 1529-1540) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
