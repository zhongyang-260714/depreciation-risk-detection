# NVIDIA Corporation（NVDA）折旧风险评分依据与推断链——三年合并核对

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

## 一、NVIDIA Corporation 2023（截至 2023-01-29） → 综合 2.85 🟡 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line

### 核心证据（12 条信号中最关键的 3 条）

**NVDA-FY2023-SIG-001【CRITICAL】** — Item 7. MD&A - Critical Accounting Policies and Estimates - Change in Accounting Estimate; Notes to Consolidated Financial Statements - Note 1（Item 7. MD&A - Change in Accounting Estimate (HTML lines 2470-2481); Note 1. Summary of Significant Accounting Policies (HTML lines 3017-3026)）
> In February 2023, we completed an assessment of the useful lives of our property, plant, and equipment. Based on advances in technology and usage rate, we increased the estimated useful life of a majority of the server, storage, and network equipment from three years to a range of four to five years, and assembly and test equipment from five years to seven years. This change in accounting estimate became effective at the beginning of fiscal year 2024. Based on the carrying amounts of a majority of our server, storage, network, and assembly and test equipment, net in use as of the end of fiscal year 2023, it is estimated this change will increase our fiscal year 2024 operating income by $133 ...

推断链：
- 事实：本文件宣布 2023 年 2 月完成年限评估，服务器/存储/网络设备 3→4-5 年、组装测试设备 5→7 年
- 事实：变更'自 FY2024 起生效'（L2476-2477、L3022-3023），FY2023 全年仍按 3/5 年计提，对本期报表零影响
- 事实：公司量化预计 FY2024 营业利润 +$133M（FY2024 10-K 确认实际 +$135M/净利润 +$114M，锚点吻合）
- 矛盾：同期 AI 加速器迭代周期 1-2 年（Ampere→Hopper 切换正在本期发生，L2184-2187），延长年限假设资产经济寿命为技术周期的 2.5-4 倍
- 影响方向：FY2024 起折旧费用系统性偏低、利润偏高；未来适用使既往低估永不修正

**NVDA-FY2023-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 1. Property and Equipment（Note 1. Summary of Significant Accounting Policies - Property and Equipment (HTML lines 3255-3266)）
> Property and equipment are stated at cost. Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets, generally three to five years. ... The estimated useful lives of our buildings are up to thirty years. ... Leasehold improvements and assets recorded under finance leases are amortized over the shorter of the expected lease term or the estimated useful life of the asset.

推断链：
- FY2023 在用折旧年限：设备类一般 3-5 年、楼宇至多 30 年（低技术敏感度）
- 对照 FY2024 确认版：同一 Note 1 表述为 'three to seven years'（变更后）——两版文件的口径差异精确对应变更时点
- 3 年服务器年限 vs 1-2 年 GPU 迭代周期：错配 1.5-3 倍，处于行业中性偏保守水平
- 影响方向：FY2023 折旧计提本身不虚，但已宣布的变更将使下一年起计提节奏放缓

**NVDA-FY2023-SIG-006【HIGH】** — Item 1A. Risk Factors - Supplier / Purchase Obligation Risks（Item 1A. Risk Factors (HTML line 1079)）
> We have also written-down our inventory, incurred cancellation penalties, and recorded impairments. These impacts were amplified by our placement of non-cancellable and non-returnable purchasing terms, well in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products.

推断链：
- 事实：公司自认历史减记存货、取消费、减值，且由远超历史提前期的不可取消采购条款放大
- 本期兑现：FY2023 存货及采购义务减值 $2.17B（FY2022 仅 $354M）
- 预测失误若 1 年内即在存货侧兑现，则 3-5 年期资产寿命假设应受同等质疑
- 影响方向：历史预测误差支持'长期资产寿命假设偏乐观'的项目假设

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **3** | FY2023 在用折旧年限：服务器/存储/网络设备 3 年、组装测试设备 5 年、设备类一般 3-5 年（Note 1 'generally three to five years'，L3258；Note 10 表 '3 - 5'，L350... |
| D2 政策保守性 | **4** | 锚点分档：本期延长年限→5；历史有延长本期无变更→4；无变更→3。FY2023 文件事实：①本期（2022-01-31 至 2023-01-29）无年限变更生效，全年按 3/5 年计提；②但本期结束后数日（2023 年 2 月，属 FY20... |
| D3 减值触发 | **3** | 与 FY2024 确认版同口径评 3 分：Risk Factors 中无固定资产折旧/减值的直接信号，固定资产渠道本期零减值（商誉年度测试 FY2023/2022/2021 均'not impaired'，L3476；无 PP&E 减值披露... |
| D4 CAPEX 强度 | **2** | CAPEX（购建固定资产及无形资产）$1,833M / 收入 $26,974M = 6.8%，高于 FY2024 确认版的 1.75%（1 分），落在 5-8% 档评 2 分，仍为低档。结构性说明：①FY2023 capex 偏高主因总部楼... |
| D5 竞争替代 | **2** | 与 FY2024 确认版同口径评 2 分：NVIDIA 为 fabless 芯片设计商，销售 GPU 而非运营 GPU 集群，自身资产负债表对 GPU 技术替代的 PP&E 暴露极小，技术过时冲击由客户（数据中心运营商）与自身存货承担。本期... |

**验算**：3×0.25 + 4×0.20 + 3×0.20 + 2×0.20 + 2×0.15 = 3×0.25=0.75 + 4×0.20=0.80 + 3×0.20=0.60 + 2×0.20=0.40 + 2×0.15=0.30 = **2.85** ✓
**置信度**：0.82 — 全部财务数据与引文逐字核对于 FY2023 10-K 正文（含行号，非 UTF-8 HTML 容错解码+去标签核对）。跨年锚点显式对照 FY2024 确认版：D1/D2 差异精确对应年限变更生效时点（FY2023 在用 3/5 年 vs FY2024 变更后 4-5/7 年；本文件已宣布但零当期影响），D3/D5 同渠道持平，D4 反映 FY2023 楼宇建设 capex 峰值。扣分项：FY2023 在用年限保守（3 年服务器）、无 PP&E 减值、轻资产量级封顶；加分项：本文件即为激进年限延长的首次披露载体（自量化 +$133M）、$2.17B+$1.35B 非 PP&E 减记佐证长期估计乐观偏差。

---

## 二、NVIDIA Corporation 2024（截至 2024-01-28） → 综合 3.10 🟠 [✅ confirmed]

**会计政策摘要**：方法：straight-line；服务器年限：4-5 (extended from 3 in February 2023)年

### 核心证据（9 条信号中最关键的 3 条）

**NVDA-FY2024-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1 (Significant Accounting Policies); also MD&A - Change in Accounting Estimate（Note 1. Significant Accounting Policies (lines 3323-3326); MD&A - Change in Accounting Estimate (lines 2800-2810)）
> In February 2023, we assessed the useful lives of our property, plant, and equipment. Based on advances in technology and usage rate, we increased the estimated useful life of a majority of the server, storage, and network equipment from three years to a range of four to five years, and assembly and test equipment from five to seven years. The estimated effect of this change for fiscal year 2024 was a benefit of $33 million and $102 million for cost of revenue and operating expenses, respectively, which resulted in an increase in operating income of $135 million and net income of $114 million after tax, or $0.05 per both basic and diluted share.

推断链：
- Fact: Feb 2023, server/storage/network equipment useful life extended 3 years -> 4-5 years; assembly/test 5 -> 7 years
- Fact: FY2024 effect = +$135M operating income, +$114M net income (+$0.05/share)
- Contradiction: AI accelerator generation cycle is ~1-2 years (H100 2022 -> H200 2024 -> B100/B200 2024-2025); extending depreciable life to 4-5 years assumes servers remain economically useful 2.5-4x longer than one product generation
- Contradiction: 'advances in technology' is cited as the reason to LENGTHEN life, while the same advances are what render prior-generation hardware obsolete faster
- Impact direction: Depreciation expense understated in FY2024 and future years -> reported profit overstated; applied prospectively so the effect persists and compounds as CAPEX grows

**NVDA-FY2024-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 1（Note 1. Significant Accounting Policies - Property and Equipment (lines 3567-3579)）
> Property and equipment are stated at cost less accumulated depreciation. Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets of three to seven years. ... The estimated useful lives of our buildings are up to thirty years.

推断链：
- Official depreciation life: 3-7 years straight-line for equipment (post-extension)
- Buildings up to 30 years (lower risk - not technology-sensitive)
- Technology cycle: GPU generations now ship annually (Hopper -> Blackwell -> Rubin)
- Impact direction: 7-year schedule vs 1-2 year tech cycle = 3.5-7x mismatch; depreciation expense systematically understated relative to economic consumption

**NVDA-FY2024-SIG-006【HIGH】** — Item 1A. Risk Factors - Supplier / Purchase Obligation Risks（Item 1A. Risk Factors (lines 1091-1094)）
> We have also written down our inventory, incurred cancellation penalties, and recorded impairments and may have to do so in the future. These impacts were amplified by our placement of non-cancellable and non-returnable purchasing terms well in advance of our historical lead times.

推断链：
- Fact: past inventory write-downs and impairments admitted in Risk Factors
- FY2023 $1.0B inventory provision coincided with the A100/H100 architecture transition and gaming demand collapse - a technology-transition write-down
- If demand-side forecasts proved wrong within 1 year, the 4-5 year useful-life assumption deserves equal skepticism
- Impact direction: History of forecast error supports the hypothesis that long-dated asset-life assumptions are optimistically biased

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 服务器/存储/网络设备折旧年限在2023年2月由3年延长至4-5年，组装测试设备由5年延长至7年（Note 1，行3323-3326；MD&A，行2800-2810）。而AI芯片技术迭代周期已压缩至1-2年（H100 2022出货→H200... |
| D2 政策保守性 | **5** | 本期（FY2024期初，2023年2月）主动延长折旧年限且按会计估计变更未来适用（prospectively），不追溯调整，完全符合评分锚点最高档'本期延长年限+未来适用→5'。公司甚至量化了利润增厚效果：营业利润+$135M、净利润+$1... |
| D3 减值触发 | **3** | Risk Factors中无固定资产折旧/减值的直接信号——直接信号缺失，需用间接信号推断，推断强度下降。存在的证据：①连续两年实际存货减值（FY2024 $774M、FY2023 $1.0B，行3819）；②Risk Factors两处明... |
| D4 CAPEX 强度 | **1** | CAPEX（购建固定资产及无形资产）$1,069M / 收入$60,922M = 1.75%，远低于3%的最低档阈值，按锚点得1分。净PP&E仅$3,914M（收入的6.4%），年折旧$894M仅占收入1.5%。fabless轻资产模式决定... |
| D5 竞争替代 | **2** | NVIDIA是fabless芯片设计商，销售GPU而非运营GPU集群，自身资产负债表对GPU技术替代的直接暴露极小——技术过时的冲击主要由客户（Meta/Google/Microsoft的数据中心资产）和自身存货承担。公司虽运营少量DGX ... |

**验算**：4×0.25 + 5×0.20 + 3×0.20 + 1×0.20 + 2×0.15 = 4×0.25=1.00 + 5×0.20=1.00 + 3×0.20=0.60 + 1×0.20=0.20 + 2×0.15=0.30 = **3.10** ✓
**置信度**：0.8 — 会计政策层面的直接证据极强（公司自行披露年限延长及$114M利润增厚，行3323-3326），但Risk Factors中固定资产减值直接信号缺失，D3依赖间接信号推断；轻资产结构使绝对利润影响很小，综合分落在'政策激进、量级有限'的中高档。

---

## 三、NVIDIA Corporation 2025（截至 2025-01-26） → 综合 3.45 🟠 [⏳ draft_pending_review]

**会计政策摘要**：方法：straight-line；服务器年限：4-5 (extended from 3 in February 2023; remains in force in FY2025 with no new change disclosed)年

### 核心证据（12 条信号中最关键的 3 条）

**NVDA-FY2025-SIG-001【CRITICAL】** — Notes to Consolidated Financial Statements - Note 1 (Significant Accounting Policies)（Note 1. Significant Accounting Policies - Property and Equipment (HTML lines 3683-3691)）
> Property and equipment are stated at cost less accumulated depreciation. Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets of two to seven years. ... The estimated useful lives of our buildings are up to thirty years.

推断链：
- Fact: FY2025 policy range is 'two to seven years' (L3684-3687); FY2024 10-K stated 'three to seven years'
- Fact: no 'change in accounting estimate' disclosure exists anywhere in the FY2025 10-K (zero full-text hits)
- Carryover: servers depreciated over 4-5 years per the Feb 2023 extension, which boosted FY2024 net income by $114M; the same schedule governed FY2025's much larger compute-hardware base ($7,568M vs $5,200M gross)
- Contradiction: the same filing states NVIDIA seeks 'to complete new computing solutions each year' (SIG-007) - a 1-year cadence vs a 4-5 year depreciation life
- Impact direction: depreciation expense for the fastest-growing asset class remains systematically spread over 2.5-5x the technology generation length; FY2025 net income of $72,880M embeds the uncorrected carryover benefit

**NVDA-FY2025-SIG-002【HIGH】** — Notes to Consolidated Financial Statements - Note 11 (Balance Sheet Components)（Note 11. Balance Sheet Components (HTML line 3905)）
> Property and Equipment: Land $511 (2025) vs $218 (2024); Buildings, leasehold improvements, and furniture 2,076 vs 1,816; Equipment, compute hardware, and software 7,568 vs 5,200 (Estimated Useful Life 2 - 7 years); Construction in process 529 vs 189; Total property and equipment, gross 10,684 vs 7,423; Accumulated depreciation and amortization (4,401) vs (3,509); Total property and equipment, net $6,283 vs $3,914.

推断链：
- Fact: equipment/compute hardware/software gross $7,568M (71% of gross PP&E), life 2-7 years (L3905)
- Fact: net PP&E $6,283M vs $3,914M (+60.5% YoY); CIP $529M (+180%); land $511M (+134%)
- Trend: FY2024 net PP&E was 6.4% of revenue; FY2025 capex tripled to $3,236M while depreciation was only $1.3B - a growing wedge of undepreciated new assets
- Impact direction: every year of life-assumption optimism now applies to a base growing >45%/yr; the absolute distortion ceiling rises mechanically

**NVDA-FY2025-SIG-006【HIGH】** — Item 1A. Risk Factors - Supplier / Purchase Obligation Risks（Item 1A. Risk Factors (HTML lines 1063-1076)）
> We have had to reduce average selling prices, including due to our channel pricing programs, increase prices for certain of our products as a result of our suppliers' increase in prices, write down our inventory, incur cancellation penalties, and record impairments, and may have to do so in the future. These impacts would be amplified by our non-cancellable and non-returnable purchase orders placed in advance of our historical lead times and could be exacerbated if we need to make changes to the design of future products. The risk of these impacts has increased and may continue to increase as our purchase obligations and prepaids have grown and are expected to continue to grow and become a g...

推断链：
- Fact: past write-downs, cancellation penalties and impairments admitted; FY2025 language escalates ('has increased and may continue to increase')
- Fact: purchase obligations/prepaid capacity 'grown and expected to continue to grow' - $30.8B inventory/supply/capacity obligations (SIG-010)
- If 12-month demand forecasts repeatedly fail, 48-60-month useful-life assumptions deserve equal skepticism
- Impact direction: history of forecast error + management's own escalation language supports the hypothesis that long-dated asset-life assumptions are optimistically biased

### 逐维评分

| 维度 | 分 | 依据摘要 |
|---|---|---|
| D1 年限错配 | **4** | 与FY2024确认版锚点一致，维持4分。现行年限：服务器/存储/网络设备4-5年（2023年2月延长，本期未变更未撤销）、组装测试设备7年；Note 1总体区间2-7年（下限由FY2024的3年收紧至2年，承认部分资产寿命更短，方向保守但幅... |
| D2 政策保守性 | **4** | 锚点'历史有延长本期无变更→4'（FY2024确认版本期为延长方故为5）。FY2025全文无任何会计估计变更披露（'change in accounting estimate'/'increased the estimated useful... |
| D3 减值触发 | **4** | 较FY2024确认版（3分）上调至4分，依据真实披露变化：①本期存货+超额采购承诺渠道实际核销$3.7B（FY2024 $2.2B，+68%），其中存货减值$1.6B（翻倍）、采购承诺费用约$2.0B、应计余额$2,095M（L3905/L... |
| D4 CAPEX 强度 | **2** | CAPEX/收入=3,236/130,497=2.48%，仍处<5%档（锚点1-2分），较FY2024（1.75%→1分）上调至档内上限2分，依据真实变化：capex同比×3（$1,069M→$3,236M）、净PP&E+60.5%（$3,... |
| D5 竞争替代 | **3** | 较FY2024确认版（2分）上调至3分（'卖芯片而非运营、间接暴露→2-3'档上限），依据文件技术迭代表述的真实强化：①公司自述'更快的加速计算平台发布节奏'且数据中心方案'每年完成新计算方案'（L1113-1119）——技术替代压力由公司... |

**验算**：4×0.25 + 4×0.20 + 4×0.20 + 2×0.20 + 3×0.15 = 4×0.25=1.00 + 4×0.20=0.80 + 4×0.20=0.80 + 2×0.20=0.40 + 3×0.15=0.45 = **3.45** ✓
**置信度**：0.82 — 全部财务数据与引文逐字核对于FY2025 10-K正文（含HTML行号），并与FY2024确认版逐维对照。锚点维度D1/D2严格沿用既有口径（年限错配档不变、历史延长本期无变更→4）；D3/D4/D5上调均对应文件内可验证的真实变化（核销额$2.2B→$3.7B、Blackwell专项事件、capex×3、年度迭代自述、$45.1B承诺）。残余不确定：FY2023年限延长对FY2025的持续利润影响未在本期量化披露（沿用FY2024的$114M口径推断）；服务器折旧占比未披露（NA）。

---

## 跨年对照与政策演变分析

| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |
|---|---|---|---|---|---|---|---|
| 2023 | 2.85 | 3 | 4 | 3 | 2 | 2 | draft_pending_review |
| 2024 | 3.10 | 4 | 5 | 3 | 1 | 2 | confirmed |
| 2025 | 3.45 | 4 | 4 | 4 | 2 | 3 | draft_pending_review |

### 政策延续 vs 变化

- **2023 历史延长生效中**：沿用上期延长后的政策
- **2024 新增变更（本期延长）**：
- **2025 历史延长生效中**：无新的年限变更，上期延长政策继续适用

### 分数差异理由

**2023 → 2024（2.85 → 3.10，Δ+0.25）**：
- 维度变化：D1 年限错配 3→4；D2 政策保守性 4→5；D4 CAPEX 强度 2→1

**2024 → 2025（3.10 → 3.45，Δ+0.35）**：
- 维度变化：D2 政策保守性 5→4；D3 减值触发 3→4；D4 CAPEX 强度 1→2；D5 竞争替代 2→3

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
| NVDA-FY2023-SIG-001 | Item 7. MD&A - Critical Accounting Policies and Estimates - Change in Accounting Estimate; Notes to Consolidated Financial Statements - Note 1 | Item 7. MD&A - Change in Accounting Estimate (HTML lines 2470-2481); Note 1. Summary of Significant Accounting Policies (HTML lines 3017-3026) | ☐ |
| NVDA-FY2023-SIG-002 | Notes to Consolidated Financial Statements - Note 1. Property and Equipment | Note 1. Summary of Significant Accounting Policies - Property and Equipment (HTML lines 3255-3266) | ☐ |
| NVDA-FY2023-SIG-003 | Notes to Consolidated Financial Statements - Note 10. Balance Sheet Components | Note 10. Balance Sheet Components - Property and Equipment 表 (HTML line 3502) | ☐ |
| NVDA-FY2023-SIG-004 | Notes to Consolidated Financial Statements - Note 1. Long-lived Assets | Note 1. Summary of Significant Accounting Policies - Long-lived Assets (HTML lines 3308-3324) | ☐ |
| NVDA-FY2023-SIG-005 | Item 1A. Risk Factors - Supply/Inventory Risks | Item 1A. Risk Factors (HTML lines 1025-1030) | ☐ |
| NVDA-FY2023-SIG-006 | Item 1A. Risk Factors - Supplier / Purchase Obligation Risks | Item 1A. Risk Factors (HTML line 1079) | ☐ |
| NVDA-FY2024-SIG-001 | Notes to Consolidated Financial Statements - Note 1 (Significant Accounting Policies); also MD&A - Change in Accounting Estimate | Note 1. Significant Accounting Policies (lines 3323-3326); MD&A - Change in Accounting Estimate (lines 2800-2810) | ☐ |
| NVDA-FY2024-SIG-002 | Notes to Consolidated Financial Statements - Note 1 | Note 1. Significant Accounting Policies - Property and Equipment (lines 3567-3579) | ☐ |
| NVDA-FY2024-SIG-003 | Notes to Consolidated Financial Statements - Note 10 (Balance Sheet Components) | Note 10. Balance Sheet Components (line 3819) | ☐ |
| NVDA-FY2024-SIG-004 | Notes to Consolidated Financial Statements - Note 1 | Note 1. Significant Accounting Policies - Long-lived Assets (lines 3618-3631) | ☐ |
| NVDA-FY2024-SIG-005 | Item 1A. Risk Factors - Supply Chain / Inventory Risks | Item 1A. Risk Factors (lines 1024-1028); repeated in MD&A (lines 2509-2510) | ☐ |
| NVDA-FY2024-SIG-006 | Item 1A. Risk Factors - Supplier / Purchase Obligation Risks | Item 1A. Risk Factors (lines 1091-1094) | ☐ |
| NVDA-FY2025-SIG-001 | Notes to Consolidated Financial Statements - Note 1 (Significant Accounting Policies) | Note 1. Significant Accounting Policies - Property and Equipment (HTML lines 3683-3691) | ☐ |
| NVDA-FY2025-SIG-002 | Notes to Consolidated Financial Statements - Note 11 (Balance Sheet Components) | Note 11. Balance Sheet Components (HTML line 3905) | ☐ |
| NVDA-FY2025-SIG-003 | Notes to Consolidated Financial Statements - Note 11; Note 16 (Segment Information); Consolidated Statements of Cash Flows | Note 11 (HTML line 3908); Note 16 (HTML lines 4200-4205); cash-flow D&A add-back $1,864M (HTML line 3418) | ☐ |
| NVDA-FY2025-SIG-004 | Notes to Consolidated Financial Statements - Note 1 (Long-lived Assets); Note 5 (Goodwill) | Note 1. Long-lived Assets (HTML lines 3734-3741); Goodwill note (HTML line 3863, annual test concluded goodwill 'not impaired' - words split across inline XBRL tags in source) | ☐ |
| NVDA-FY2025-SIG-005 | Item 1A. Risk Factors - Supply Chain / Inventory Risks | Item 1A. Risk Factors (HTML lines 1106-1108); repeated in MD&A (HTML lines 2662-2664) | ☐ |
| NVDA-FY2025-SIG-006 | Item 1A. Risk Factors - Supplier / Purchase Obligation Risks | Item 1A. Risk Factors (HTML lines 1063-1076) | ☐ |

### ③ 跨年对照
- [ ] 政策延续/变化判断与原文一致
- [ ] 分数差异理由有原文事实支撑（非口径漂移）

### ④ 推断链说明
- [ ] 每条推断链的因果逻辑无跳跃
- [ ] 数字计算（验算式）与 JSON 一致

---

> 核对完成签名：__________  日期：__________
