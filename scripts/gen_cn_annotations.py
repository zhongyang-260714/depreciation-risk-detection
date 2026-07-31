# -*- coding: utf-8 -*-
"""生成 3 份中国科创企业标注 JSON（与美股样例同构）+ 1 份中国验证集 CSV。
金额单位：人民币百万元（RMB mn），与美股样例的美金百万元对齐。
证据链页码/行号统一标注“待团队用年报 PDF 终核”，避免虚构精确行号。
"""
import json, os

OUT_JSON = "D:/depreciation-risk-detection/data/annotated_cn"
OUT_CSV  = "D:/depreciation-risk-detection/data/processed/training_v07_china_validation_3.csv"
os.makedirs(OUT_JSON, exist_ok=True)
os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)

WEIGHTS = {  # 5D-DRS 权重（与美国面板一致）
    "D1": 0.25, "D2": 0.20, "D3": 0.20, "D4": 0.20, "D5": 0.15,
}

def risk_level(score):
    if score >= 4.0: return ("极高风险", "Extremely High Risk", "#DC3545")
    if score >= 3.5: return ("中高风险", "High-Medium Risk", "#FD7E14")
    if score >= 3.0: return ("中风险",   "Medium Risk",     "#FFC107")
    if score >= 2.5: return ("中低风险", "Medium-Low Risk", "#20C997")
    return            ("低风险",   "Low Risk",         "#28A745")

# ----------------------------------------------------------------------------
# 1) 数据港 (603881) — 高有形 / IDC 运营型（对标 META/GOOGL 运营型）
# ----------------------------------------------------------------------------
sh_j = {
    "metadata": {
        "version": "1.0",
        "annotation_schema": "Depreciation Risk Annotation Schema v1.0 (China A-share parity)",
        "annotated_at": "2026-07-27",
        "annotator": "zhongyang-260714 (Project Lead)",
        "review_status": "confirmed",
        "filing_source": "上交所年报 + 《2024年度会计估计变更的公告》(公告编号 2025-012)",
        "review_note": "中国验证集首批三家之一（高有形/IDC 运营型）。核心证据为 2024-10-01 起执行的折旧年限延长，数据来自公司会计估计变更公告原文。页码/行号待团队用年报 PDF 终核。",
        "reviewed_at": "2026-07-27T11:00:00+08:00",
        "reviewed_by": "zhongyang-260714"
    },
    "company": {
        "ticker": "603881.SH",
        "name": "上海数据港股份有限公司",
        "fiscal_year": 2024,
        "filing_date": "2025-03-22",
        "report_period_end": "2024-12-31",
        "industry": "IDC / 算力基础设施运营",
        "primary_assets": "数据中心房屋建筑物、专用设备（暖通/电力/网络）、在建工程",
        "file_path": "data/raw/sh603881_2024_annual_report.pdf",
        "coverage_note": "数据港 2024 年报：营收约 17.21 亿元(+11.57%)，归母净利约 1.32 亿元(+7.49%)，总资产约 75.76 亿元。关键事件：2024-10-01 起将房屋建筑物折旧年限由 20-30 年调整为 20-40 年、专用设备由 5-10 年调整为 5-15 年（未来适用法），增加 2024 年净利润 1,678,038.57 元。该变更是自持廊坊项目后首次调整，方向与美股巨头“延长年限”一致，但资产为 IDC 基建而非 AI 训练芯片。"
    },
    "financial_highlights": {
        "unit_note": "金额单位：人民币百万元（RMB mn）",
        "revenue_millions": 1721,
        "revenue_note": "营业收入约 172,090.92 万元 ≈ 1,721 百万元，同比 +11.57%（2024 年报）",
        "net_income_millions": 132,
        "net_income_note": "归母净利润约 13,219.02 万元 ≈ 132 百万元，同比 +7.49%",
        "operating_income_millions": None,
        "operating_income_note": "待年报 PDF 终核",
        "rd_expense_millions": None,
        "rd_expense_note": "IDC 运营商研发支出较低，不适用为风险主渠道（待年报 PDF 终核）",
        "operating_cash_flow_millions": 1855,
        "operating_cash_flow_note": "EBITDA（近似）约 185,480.13 万元 ≈ 1,855 百万元（2024 年报）",
        "capex_millions": None,
        "capex_note": "购建固定资产等 capex 待年报 PDF 终核；期末在建工程 303 百万元表明持续扩建",
        "depreciation_expense_millions": None,
        "depreciation_expense_note": "折旧费用绝对值待年报 PDF 终核；本次变更仅影响 2024 年净利 +167.8 百万元→实际为 +1.678 百万元（167.8 万元）",
        "ppe_net_millions": 3729,
        "ppe_net_note": "固定资产合计 3,729,315,753.43 元 ≈ 3,729 百万元，占总资产约 50.5%（2024-12-31）",
        "intangible_assets_millions": 32,
        "intangible_assets_note": "无形资产 32,437,463.57 元 ≈ 32 百万元",
        "goodwill_millions": 144,
        "goodwill_note": "商誉 143,809,935.20 元 ≈ 144 百万元",
        "construction_in_progress_millions": 303,
        "construction_in_progress_note": "在建工程 302,716,363.29 元 ≈ 303 百万元（怀来等扩建项目）"
    },
    "accounting_policy": {
        "depreciation_method": "直线法（年限平均法）",
        "estimate_change_2024": "2024-10-01 起：房屋建筑物折旧年限 20-30 年 → 20-40 年；专用设备 5-10 年 → 5-15 年",
        "estimate_change_method": "未来适用法（对以往年度无影响）",
        "estimate_change_impact": "增加 2024 年净利润 1,678,038.57 元（约 1.68 百万元，占 2024 归母净利 0.13%）",
        "estimate_change_reason": "廊坊项目土地与房屋均自有自持，设计使用年限 50 年，结合土地使用权剩余年限适度上调；原基地合作型项目按合作期限(约10年)定年限。变更仅适用于 2024-10-01 后新计提折旧的相关资产。",
        "change_in_estimate_location": "《2024年度会计估计变更的公告》(2025-012) + 2024 年报“重要会计政策/会计估计变更”节（页码/行号待年报 PDF 终核）",
        "impairment_policy": "资产负债表日判断资产是否存在减值迹象，存在时估计可收回金额（公允价值减处置费用 / 未来现金流量现值孰高），低于账面价值则计提减值。",
        "policy_risk_note": "数据港 2024 年延长了房屋建筑物与专用设备折旧年限，方向与美国巨头“延长年限”一致，是本研究在 A 股发现的第一个“年限上行漂移”实证案例。但金额影响极小（占净利 0.13%），且有自持廊坊项目的业务依据（建筑实际寿命长）；且资产为 IDC 基建（暖通/电力/建筑），并非迭代 1-2 年的 AI 训练芯片，故错配烈度远低于美股云厂商。"
    },
    "risk_signals": [
        {
            "signal_id": "SH603881-2024-SIG-001",
            "source": "《2024年度会计估计变更的公告》(2025-012) + 2024 年报",
            "keyword_matched": "折旧年限 20-30年→20-40年；5-10年→5-15年",
            "text_excerpt": "公司将房屋及建筑物折旧年限由原来的 20-30 年调整为 20-40 年，专用设备折旧年限由原来的 5-10 年调整为 5-15 年。本次变更自 2024 年 10 月 1 日起执行，采用未来适用法，增加 2024 年净利润 1,678,038.57 元。",
            "page_location": "会计估计变更公告正文 + 2024 年报相关节（页码/行号待年报 PDF 终核）",
            "risk_type": "useful_life_extension",
            "severity": "medium",
            "relevance_to_depreciation": "数据港在 AI 算力投资高峰期延长了固定资产折旧年限，方向与 Meta/Google 等美股巨头的“年限魔术”一致，是中国样本中出现“折旧乐观上漂”的首个实证。但专用设备上限由 10 年提至 15 年（+50%），若其中含算力相关设备，则与技术迭代周期的错配会随后续智算投入放大。当前金额影响极小（占净利 0.13%），属早期温和信号。",
            "evidence_chain": [
                "2024-10-01 起执行折旧年限变更（未来适用法）",
                "房屋建筑物 20-30 年 → 20-40 年；专用设备 5-10 年 → 5-15 年",
                "影响 2024 净利 +1,678,038.57 元（约占归母净利 0.13%）",
                "变更理由：自持廊坊项目建筑实际寿命长（设计使用年限 50 年）",
                "含义：出现“年限上行漂移”苗头，但幅度温和、有业务依据；需跟踪后续智算设备是否沿用更长年限"
            ]
        },
        {
            "signal_id": "SH603881-2024-SIG-002",
            "source": "2024 年报 资产负债表 / 固定资产明细",
            "keyword_matched": "固定资产 37.29 亿；在建工程 3.03 亿",
            "text_excerpt": "固定资产合计 3,729,315,753.43 元；在建工程 302,716,363.29 元；IDC 业务持续扩建（怀来等）。",
            "page_location": "2024 年报 资产负债表（页码/行号待年报 PDF 终核）",
            "risk_type": "capex_intensity",
            "severity": "high",
            "relevance_to_depreciation": "数据港是典型的重资产 IDC 运营商：固定资产占总资产约 50.5%，且在建工程持续。东数西算与智算中心建设潮下，其折旧基数将持续膨胀；一旦后续将算力设备也套用偏长年限，折旧错配的杠杆效应会放大。当前 capex/折旧绝对值待年报终核。",
            "evidence_chain": [
                "固定资产 37.29 亿（占总资产约 50.5%）",
                "在建工程 3.03 亿（怀来等扩建）",
                "IDC 行业处于算力建设扩张期",
                "重资产敞口高 → 折旧假设偏差的杠杆效应大"
            ]
        }
    ],
    "dimension_scores": [
        {"dimension_id":"D1","dimension_name":"折旧年限 vs 技术实际寿命","dimension_name_en":"Depreciation Life vs Technology Useful Life","weight":0.25,"score":3,"score_max":5,"score_label":"中风险","score_label_en":"Medium Risk",
         "reasoning":"2024-10-01 起延长专用设备 5-10→5-15 年、房屋 20-30→20-40 年，方向与美巨头“延长”一致，但资产为 IDC 基建（建筑+暖通电力）而非 AI 训练芯片；建筑延长有自持廊坊项目“设计使用年限 50 年”的业务依据，设备上限 +50% 值得跟踪。评 3 分（中）。",
         "supporting_signals":["SH603881-2024-SIG-001"],
         "key_metrics":{"building_life_change":"20-30y -> 20-40y","equipment_life_change":"5-10y -> 5-15y","effective_date":"2024-10-01","ai_chip_cycle_years":"1-2","mismatch_ratio":"低（基建非芯片）"}},
        {"dimension_id":"D2","dimension_name":"会计政策保守性","dimension_name_en":"Accounting Policy Conservatism","weight":0.20,"score":3,"score_max":5,"score_label":"中风险","score_label_en":"Medium Risk",
         "reasoning":"单次未来适用法变更，影响净利仅 +167.8 万元（占净利 0.13%），动机温和；但方向为利己延长，与美股“年限魔术”同类。评 3 分（中）。",
         "supporting_signals":["SH603881-2024-SIG-001"],
         "key_metrics":{"change_count":1,"change_method":"未来适用法","impact_on_net_income_mn":1.678,"impact_pct_net_income":0.13}},
        {"dimension_id":"D3","dimension_name":"减值风险触发","dimension_name_en":"Impairment Risk Triggers","weight":0.20,"score":2,"score_max":5,"score_label":"低风险","score_label_en":"Low Risk",
         "reasoning":"2024 年报为标准无保留审计意见，IDC 业务稳定，未见重大长期资产减值迹象。评 2 分（低）。",
         "supporting_signals":[],
         "key_metrics":{"audit_opinion":"标准无保留","ppe_impairment_2024":"无重大"}},
        {"dimension_id":"D4","dimension_name":"资本支出(CAPEX)强度","dimension_name_en":"Capital Expenditure Intensity","weight":0.20,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"IDC 天然重资产：固定资产 37.29 亿（占总资产约 50.5%），在建工程 3.03 亿，东数西算下持续扩建。capex/折旧绝对值待终核，但重资产敞口高。评 4 分（高）。",
         "supporting_signals":["SH603881-2024-SIG-002"],
         "key_metrics":{"ppe_net_mn":3729,"ppe_to_total_assets_pct":50.5,"cip_mn":303}},
        {"dimension_id":"D5","dimension_name":"行业竞争/技术替代","dimension_name_en":"Industry Competition & Technology Substitution","weight":0.15,"score":3,"score_max":5,"score_label":"中风险","score_label_en":"Medium Risk",
         "reasoning":"IDC 行业竞争（运营商、第三方）存在，但资产为长寿命建筑，技术替代慢于芯片；AI 算力需求上行反而利好。评 3 分（中）。",
         "supporting_signals":[],
         "key_metrics":{"competitors":["运营商IDC","第三方IDC","云厂商"],"tech_substitution":"慢（基建）"}}
    ],
    "comparative_context": {
        "same_company_trend": "数据港 2024 为首次出现折旧年限延长（此前无变更记录），属早期信号，需跟踪后续年份是否延续。",
        "cross_company_benchmark": "在 A 股三家验证集中，数据港代表“高有形/运营型”，与美股 META/GOOGL 运营型对应；其年限延长幅度温和（vs 美股巨头多年反复延长），但方向相同。",
        "narrative_significance": "数据港是中国样本里第一个出现“折旧年限上行漂移”的实证，验证了 6.2 节“智算中心建设潮下的会计前瞻”隐患假设——只是当前金额影响极小（占净利 0.13%），属于应纳入监测的早期苗头而非已兑现风险。"
    },
    "annotation_methodology": {
        "source_document": "上海数据港股份有限公司 2024 年年度报告 + 《2024年度会计估计变更的公告》(2025-012)",
        "filing_accessed": "上交所 / 巨潮资讯",
        "text_extraction_method": "公告与年报关键会计估计节人工摘录（页码/行号待 PDF 终核）",
        "scoring_method": "Five-dimension weighted scoring (5D-DRS) with 0-5 scale, weights 0.25/0.20/0.20/0.20/0.15（与美国面板一致）",
        "human_verification": "关键数字（变更前后年限、影响净利 1,678,038.57 元、固定资产 37.29 亿）来自公告/年报原文，已核对；逐字行号待团队用年报 PDF 终核",
        "limitation": "capex/折旧绝对值、精确页码行号待年报 PDF 终核；单一年度，未做多年趋势。"
    }
}

# ----------------------------------------------------------------------------
# 2) 寒武纪 (688256) — 高无形 / AI 芯片设计(Fabless)（对标 NVDA/AMD 设计型）
# ----------------------------------------------------------------------------
cw_j = {
    "metadata": {
        "version": "1.0",
        "annotation_schema": "Depreciation Risk Annotation Schema v1.0 (China A-share parity)",
        "annotated_at": "2026-07-27",
        "annotator": "zhongyang-260714 (Project Lead)",
        "review_status": "confirmed",
        "filing_source": "上交所年报（公司代码 688256）",
        "review_note": "中国验证集首批三家之一（高无形/芯片设计型）。核心风险在存货暴增与持续亏损（D3）及技术替代（D5），而非 PP&E 折旧（D1 极低、D2 最保守）。用于验证 5D-DRS 对轻资产公司的边界。页码/行号待团队用年报 PDF 终核。",
        "reviewed_at": "2026-07-27T11:00:00+08:00",
        "reviewed_by": "zhongyang-260714"
    },
    "company": {
        "ticker": "688256.SH",
        "name": "中科寒武纪科技股份有限公司",
        "fiscal_year": 2024,
        "filing_date": "2025-04-19",
        "report_period_end": "2024-12-31",
        "industry": "AI 芯片设计（Fabless）",
        "primary_assets": "存货、应收账款、无形资产（专利/技术）、少量固定资产（流片/测试设备）",
        "file_path": "data/raw/sh688256_2024_annual_report.pdf",
        "coverage_note": "寒武纪 2024 年报：营收 11.74 亿元(+65.56%)，归母净亏损 4.52 亿元（连续亏损但收窄）；研发投入 10.72 亿元（占营收 91.30%），资本化比重 0%（全部费用化，最保守）。固定资产仅 2.31 亿、在建工程 1.50 亿（Fabless 轻资产）。风险不在折旧而在：存货暴增（年末 17.74 亿，同比+1684%）、连续 8 年亏损、AI 芯片技术替代极快。"
    },
    "financial_highlights": {
        "unit_note": "金额单位：人民币百万元（RMB mn）",
        "revenue_millions": 1174,
        "revenue_note": "营业收入 1,174,464,377.35 元 ≈ 1,174 百万元，同比 +65.56%",
        "net_income_millions": -452,
        "net_income_note": "归母净利润 -452,338,800 元 ≈ -452 百万元（连续亏损，较上年 -848 百万元收窄）",
        "operating_income_millions": None,
        "operating_income_note": "待年报 PDF 终核",
        "rd_expense_millions": 1072,
        "rd_expense_note": "研发投入 1,072 百万元（占营收 91.30%）；资本化比重 0%，全部费用化",
        "operating_cash_flow_millions": -1618,
        "operating_cash_flow_note": "经营活动现金流净额约 -1,618 百万元（2024，同比恶化）",
        "capex_millions": None,
        "capex_note": "Fabless 模式下 capex 低，固定资产仅 231 百万元（待年报 PDF 终核）",
        "depreciation_expense_millions": None,
        "depreciation_expense_note": "折旧费用低（固定资产规模小），非主要风险渠道",
        "ppe_net_millions": 231,
        "ppe_net_note": "固定资产 231 百万元（Fabless 轻资产）",
        "intangible_assets_millions": 183,
        "intangible_assets_note": "无形资产 182,762,964.88 元 ≈ 183 百万元（专利/技术）",
        "goodwill_millions": 0,
        "goodwill_note": "商誉 0（无重大并购）",
        "construction_in_progress_millions": 150,
        "construction_in_progress_note": "在建工程 150 百万元（待年报 PDF 终核）"
    },
    "accounting_policy": {
        "depreciation_method": "直线法（年限平均法）",
        "rd_capitalization_policy": "2024 年研发投入资本化比重为 0%（全部费用化），为验证集中最保守的会计选择",
        "estimate_change_2024": "未见折旧年限变更披露",
        "estimate_change_method": "不适用",
        "impairment_policy": "资产负债表日判断资产（尤其存货、无形资产）减值迹象；存货按成本与可变现净值孰低计量。",
        "policy_risk_note": "寒武纪采用 Fabless 模式，固定资产极少，PP&E 折旧错配几乎不存在；且研发投入 100% 费用化（资本化比重 0%），无通过资本化虚增资产/利润的空间——这是最保守的会计姿态。但轻资产公司的风险从“折旧”迁移到“存货跌价 + 技术替代”：存货一年暴增 1684% 至 17.74 亿，在芯片快速迭代下跌价风险极高；连续 8 年亏损则使持续经营与资产可收回金额承压。"
    },
    "risk_signals": [
        {
            "signal_id": "SH688256-2024-SIG-001",
            "source": "2024 年报 资产重大变化 / 存货",
            "keyword_matched": "存货较上年末增加 1684.66%",
            "text_excerpt": "截至 2024 年末，公司存货余额达 17.74 亿元，较上年末增加 1684.66%；同期营收 11.74 亿元。",
            "page_location": "2024 年报“资产重大变化”节（页码/行号待年报 PDF 终核）",
            "risk_type": "inventory_impairment_risk",
            "severity": "critical",
            "relevance_to_depreciation": "寒武纪风险不在折旧而在存货：一年暴增 1684% 至 17.74 亿（约为全年营收的 1.5 倍），在 AI 芯片迭代极快（H20/新一代架构）背景下，呆滞与跌价风险极高。这是“风险藏存货/摊销”而非“风险藏折旧”的典型——恰好框定 5D-DRS 的适用边界。",
            "evidence_chain": [
                "存货 2024 年末 17.74 亿，同比 +1684.66%",
                "存货/营收 ≈ 1.5x（库存远超年销售规模）",
                "AI 芯片迭代 12-18 个月，呆滞与跌价风险高",
                "连续 8 年亏损，资产可收回金额承压",
                "→ 减值触发（D3）与技术替代（D5）为真实风险通道"
            ]
        },
        {
            "signal_id": "SH688256-2024-SIG-002",
            "source": "2024 年报 关键会计政策 / 研发投入",
            "keyword_matched": "研发投入占营业收入的比例为 91.30%；资本化比重 0%",
            "text_excerpt": "公司持续保持高质量的研发投入，研发投入占营业收入的比例为 91.30%。（2024 年研发投入资本化比重为 0%，全部费用化。）",
            "page_location": "2024 年报 管理层讨论与分析（页码/行号待年报 PDF 终核）",
            "risk_type": "accounting_conservatism_positive",
            "severity": "low",
            "relevance_to_depreciation": "正面信号：研发投入 100% 费用化（资本化比重 0%），是验证集中最保守的会计选择，无通过研发资本化虚增资产/利润的空间。这拉低了 D2（会计政策保守性）风险，使寒武纪在 5D-DRS 下折旧相关风险较低——但企业整体经营/技术风险仍极高，需由 D3/D5 捕捉。",
            "evidence_chain": [
                "研发投入 10.72 亿，占营收 91.30%",
                "资本化比重 0%（全部费用化）",
                "→ D2 最保守（最低风险）",
                "→ 折旧/资本化渠道无虚增，风险转由 D3/D5 表达"
            ]
        }
    ],
    "dimension_scores": [
        {"dimension_id":"D1","dimension_name":"折旧年限 vs 技术实际寿命","dimension_name_en":"Depreciation Life vs Technology Useful Life","weight":0.25,"score":2,"score_max":5,"score_label":"低风险","score_label_en":"Low Risk",
         "reasoning":"Fabless 模式，固定资产仅 2.31 亿，几乎不存在 PP&E 折旧错配；未见折旧年限延长。评 2 分（低）。",
         "supporting_signals":[],
         "key_metrics":{"ppe_net_mn":231,"ai_chip_cycle_years":"1-2","mismatch":"极低（轻资产）"}},
        {"dimension_id":"D2","dimension_name":"会计政策保守性","dimension_name_en":"Accounting Policy Conservatism","weight":0.20,"score":1,"score_max":5,"score_label":"极低风险","score_label_en":"Very Low Risk",
         "reasoning":"研发投入资本化比重 0%（全部费用化），验证集中最保守，无资本化虚增资产/利润。评 1 分（极低）。",
         "supporting_signals":["SH688256-2024-SIG-002"],
         "key_metrics":{"rd_input_mn":1072,"rd_to_revenue_pct":91.30,"capitalization_ratio_pct":0}},
        {"dimension_id":"D3","dimension_name":"减值风险触发","dimension_name_en":"Impairment Risk Triggers","weight":0.20,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"存货暴增 1684% 至 17.74 亿（≈营收 1.5 倍），连续 8 年亏损，芯片迭代下跌价/呆滞风险极高。评 4 分（高）。",
         "supporting_signals":["SH688256-2024-SIG-001"],
         "key_metrics":{"inventory_mn":1774,"inventory_yoy_pct":1684.66,"net_loss_mn":452,"loss_years":8}},
        {"dimension_id":"D4","dimension_name":"资本支出(CAPEX)强度","dimension_name_en":"Capital Expenditure Intensity","weight":0.20,"score":2,"score_max":5,"score_label":"低风险","score_label_en":"Low Risk",
         "reasoning":"Fabless 轻资产，固定资产仅 2.31 亿、在建工程 1.50 亿，capex 低。评 2 分（低）。",
         "supporting_signals":[],
         "key_metrics":{"ppe_net_mn":231,"cip_mn":150}},
        {"dimension_id":"D5","dimension_name":"行业竞争/技术替代","dimension_name_en":"Industry Competition & Technology Substitution","weight":0.15,"score":5,"score_max":5,"score_label":"最高风险","score_label_en":"Highest Risk",
         "reasoning":"AI 芯片国产替代核心战场，受 NVIDIA H20 出口管制催化但亦面临巨头碾压与架构快速迭代，技术替代风险极高。评 5 分（最高）。",
         "supporting_signals":["SH688256-2024-SIG-001"],
         "key_metrics":{"segment":"AI芯片","substitution":"极快(12-18月)","driver":"国产替代+迭代"}}
    ],
    "comparative_context": {
        "same_company_trend": "寒武纪连续多年亏损、存货随营收扩张快速累积，风险集中在经营与技术面，折旧渠道长期稳定。",
        "cross_company_benchmark": "在 A 股三家验证集中代表“高无形/设计型”，对标美股 NVDA/AMD；但其 5D-DRS 折旧相关风险（D1/D2/D4）低，与重资产的 Intel/Meta 形成两极。",
        "narrative_significance": "寒武纪是 5D-DRS 边界的试金石：模型给出中低风险（折旧错配低），但企业整体风险极高——风险从 PP&E 折旧迁移到存货(D3)与技术替代(D5)。这证明模型对轻资产公司需配合 D3/D5 与无形资产维度，既展示判别效度，也诚实标注了适用边界。"
    },
    "annotation_methodology": {
        "source_document": "中科寒武纪科技股份有限公司 2024 年年度报告（上交所 688256）",
        "filing_accessed": "上交所 / 巨潮资讯",
        "text_extraction_method": "年报关键节人工摘录（页码/行号待 PDF 终核）",
        "scoring_method": "Five-dimension weighted scoring (5D-DRS), weights 0.25/0.20/0.20/0.20/0.15（与美国面板一致）",
        "human_verification": "营收 11.74 亿、净亏 4.52 亿、研发 10.72 亿(占91.30%)、资本化0%、存货 17.74 亿(+1684%) 均来自年报原文，已核对；逐字行号待 PDF 终核",
        "limitation": "固定资产/折旧绝对值、精确页码行号待年报 PDF 终核；未做多年趋势；模型对轻资产公司边界需配合 D3/D5。"
    }
}

# ----------------------------------------------------------------------------
# 3) 科大讯飞 (002230) — 混合型（软件+硬件+算力）（对标 CRM 软件型）
# ----------------------------------------------------------------------------
xf_j = {
    "metadata": {
        "version": "1.0",
        "annotation_schema": "Depreciation Risk Annotation Schema v1.0 (China A-share parity)",
        "annotated_at": "2026-07-27",
        "annotator": "zhongyang-260714 (Project Lead)",
        "review_status": "confirmed",
        "filing_source": "深交所年报（公司代码 002230）",
        "review_note": "中国验证集首批三家之一（混合型）。最高分样本：高研发资本化率(43.58%) + 巨额无形资产/商誉堆 + 信用减值损失 9.65 亿，验证‘风险藏摊销/商誉’路径在中国同样成立。页码/行号待团队用年报 PDF 终核。",
        "reviewed_at": "2026-07-27T11:00:00+08:00",
        "reviewed_by": "zhongyang-260714"
    },
    "company": {
        "ticker": "002230.SZ",
        "name": "科大讯飞股份有限公司",
        "fiscal_year": 2024,
        "filing_date": "2025-04-22",
        "report_period_end": "2024-12-31",
        "industry": "AI 软件 + 硬件 + 算力（混合型）",
        "primary_assets": "无形资产（软件/技术）、商誉（并购）、开发支出、固定资产（飞星一号算力集群）、存货",
        "file_path": "data/raw/sz002230_2024_annual_report.pdf",
        "coverage_note": "科大讯飞 2024 年报：营收 233.43 亿元(+18.79%)，归母净利 5.6 亿元；研发投入 45.8 亿元、资本化率 43.58%（资本化额约 19.96 亿），开发支出 16.36 亿、无形资产 29.17 亿、商誉 11.35 亿；固定资产 50.37 亿、在建工程 10.33 亿（飞星一号万卡算力）；2024 信用减值损失 9.65 亿(+42.58%)、资产减值损失 1.07 亿。混合型资产结构，风险横跨折旧(D1/D4)与无形资产摊销/商誉(D2/D3)。"
    },
    "financial_highlights": {
        "unit_note": "金额单位：人民币百万元（RMB mn）",
        "revenue_millions": 23343,
        "revenue_note": "营业收入 23,343,093,018.69 元 ≈ 23,343 百万元，同比 +18.79%",
        "net_income_millions": 560,
        "net_income_note": "归母净利润 560,162,663.16 元 ≈ 560 百万元，同比 -14.78%（扣非 188 百万元 +59.35%）",
        "operating_income_millions": None,
        "operating_income_note": "待年报 PDF 终核",
        "rd_expense_millions": 4580,
        "rd_expense_note": "研发投入 45.8 亿元（约 4,580 百万元），占营收 19.62%；资本化率 43.58%，资本化额约 1,996 百万元",
        "operating_cash_flow_millions": 2495,
        "operating_cash_flow_note": "经营活动现金流净额 2,495 百万元（同比 +613%）",
        "capex_millions": None,
        "capex_note": "算力集群（飞星一号）建设持续，固定资产 5,037 百万元、在建工程 1,033 百万元；精确 capex 待年报 PDF 终核",
        "depreciation_expense_millions": None,
        "depreciation_expense_note": "折旧费用绝对值待年报 PDF 终核；含算力服务器折旧",
        "ppe_net_millions": 5037,
        "ppe_net_note": "固定资产 5,037,418,177.15 元 ≈ 5,037 百万元（含飞星一号算力设备）",
        "intangible_assets_millions": 2917,
        "intangible_assets_note": "无形资产 2,916,651,306.77 元 ≈ 2,917 百万元",
        "goodwill_millions": 1135,
        "goodwill_note": "商誉 1,134,673,186.61 元 ≈ 1,135 百万元（并购形成）",
        "construction_in_progress_millions": 1033,
        "construction_in_progress_note": "在建工程 1,032,764,040.07 元 ≈ 1,033 百万元",
        "development_expenditure_millions": 1636,
        "development_expenditure_note": "开发支出 1,636,081,539.76 元 ≈ 1,636 百万元（资本化研发堆积）"
    },
    "accounting_policy": {
        "depreciation_method": "直线法（年限平均法）",
        "rd_capitalization_policy": "研发投入 45.8 亿元，资本化率 43.58%，资本化额约 19.96 亿元计入开发支出/无形资产（A 股 AI 软件公司偏高）",
        "estimate_change_2024": "未见折旧年限延长披露（服务器折旧政策待年报 PDF 终核）",
        "impairment_policy": "商誉及无形资产每年/出现减值迹象时做减值测试；存货按成本与可变现净值孰低；应收账款按预期信用损失计提。",
        "policy_risk_note": "科大讯飞是‘风险藏摊销/商誉’的中国样板：研发投入 43.58% 资本化（偏高），形成 开发支出 16.36 亿 + 无形资产 29.17 亿 + 商誉 11.35 亿 的巨额无形资产堆；2024 信用减值损失 9.65 亿(+42.58%)、资产减值损失 1.07 亿，减值触发已密集出现。同时自建飞星一号万卡算力集群带来 50 亿级固定资产折旧敞口。折旧与无形资产两条风险通道在此交汇。"
    },
    "risk_signals": [
        {
            "signal_id": "SZ002230-2024-SIG-001",
            "source": "2024 年报 研发投入 / 开发支出",
            "keyword_matched": "研发投入资本化率为 43.58%",
            "text_excerpt": "2024 年公司研发投入金额为 45.8 亿元，同比增长 19.37%；研发投入占营业收入比例为 19.62%；此外，公司全年研发投入资本化率为 43.58%。",
            "page_location": "2024 年报 管理层讨论与分析 / 研发投入节（页码/行号待年报 PDF 终核）",
            "risk_type": "rd_capitalization_aggressive",
            "severity": "high",
            "relevance_to_depreciation": "科大讯飞将 43.58% 的研发投入资本化（约 19.96 亿），计入开发支出/无形资产，递延费用确认、虚增当期资产与利润——这是美股软件巨头‘激进资本化’路径的中国翻版。高资本化率意味着未来摊销压力与减值风险更大，是‘风险藏摊销’的核心证据。",
            "evidence_chain": [
                "研发投入 45.8 亿，占营收 19.62%",
                "资本化率 43.58% → 资本化额约 19.96 亿",
                "开发支出 16.36 亿 + 无形资产 29.17 亿 + 商誉 11.35 亿（巨额无形资产堆）",
                "高资本化 → 未来摊销与减值压力上升",
                "→ 对应 D2（会计保守性）偏高、D3（减值）触发密集"
            ]
        },
        {
            "signal_id": "SZ002230-2024-SIG-002",
            "source": "2024 年度财务决算报告 减值损失",
            "keyword_matched": "信用减值损失 9.65 亿；资产减值损失 1.07 亿",
            "text_excerpt": "信用减值损失 965,333,261.07 元（+42.58%）；资产减值损失 107,071,575.33 元（+26.05%）。",
            "page_location": "2024 年度财务决算报告（页码/行号待年报 PDF 终核）",
            "risk_type": "impairment_trigger",
            "severity": "high",
            "relevance_to_depreciation": "2024 年信用减值损失 9.65 亿（同比 +42.58%）、资产减值损失 1.07 亿，减值触发已密集出现；叠加存货 28.47 亿、应收账款 146.66 亿，在 AI 投入回报不确定下，巨额无形资产/商誉堆的减值风险是真实敞口。",
            "evidence_chain": [
                "信用减值损失 9.65 亿（+42.58%）",
                "资产减值损失 1.07 亿（+26.05%）",
                "存货 28.47 亿、应收账款 146.66 亿",
                "商誉 11.35 亿 + 无形资产 29.17 亿 待减值测试",
                "→ D3（减值触发）高"
            ]
        },
        {
            "signal_id": "SZ002230-2024-SIG-003",
            "source": "2024 年报 固定资产 / 飞星一号",
            "keyword_matched": "固定资产 50.37 亿；飞星一号万卡算力集群",
            "text_excerpt": "固定资产 5,037,418,177.15 元；公司基于全国首个国产万卡智能算力集群‘飞星一号’训练星火大模型。",
            "page_location": "2024 年报 资产负债表 / 管理层讨论（页码/行号待年报 PDF 终核）",
            "risk_type": "capex_intensity",
            "severity": "high",
            "relevance_to_depreciation": "自建万卡算力集群使固定资产达 50.37 亿、在建工程 10.33 亿，带来算力服务器折旧敞口；若服务器折旧年限偏长（待年报终核），将与 AI 硬件 1-2 年迭代周期形成错配，叠加高额无形资产，构成‘折旧+摊销’双通道风险。",
            "evidence_chain": [
                "固定资产 50.37 亿、在建工程 10.33 亿",
                "飞星一号万卡算力集群（自有 GPU 服务器）",
                "算力硬件迭代 1-2 年 vs 会计折旧年限待核",
                "→ D1/D4 敞口"
            ]
        }
    ],
    "dimension_scores": [
        {"dimension_id":"D1","dimension_name":"折旧年限 vs 技术实际寿命","dimension_name_en":"Depreciation Life vs Technology Useful Life","weight":0.25,"score":3,"score_max":5,"score_label":"中风险","score_label_en":"Medium Risk",
         "reasoning":"自建飞星一号万卡算力集群带来 GPU 服务器折旧敞口，但未见延长折旧年限的确证（待年报终核），故评 3 分（中）。",
         "supporting_signals":["SZ002230-2024-SIG-003"],
         "key_metrics":{"ppe_net_mn":5037,"ai_hw_cycle_years":"1-2","server_life_change":"待年报终核"}},
        {"dimension_id":"D2","dimension_name":"会计政策保守性","dimension_name_en":"Accounting Policy Conservatism","weight":0.20,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"研发投入资本化率 43.58%（偏高），资本化额约 19.96 亿计入开发支出/无形资产，递延费用确认、虚增资产与利润，较激进。评 4 分（高）。",
         "supporting_signals":["SZ002230-2024-SIG-001"],
         "key_metrics":{"rd_input_mn":4580,"rd_to_revenue_pct":19.62,"capitalization_ratio_pct":43.58,"capitalized_mn":1996}},
        {"dimension_id":"D3","dimension_name":"减值风险触发","dimension_name_en":"Impairment Risk Triggers","weight":0.20,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"商誉 11.35 亿 + 无形资产 29.17 亿 + 开发支出 16.36 亿 巨额堆；2024 信用减值损失 9.65 亿(+42.58%)、资产减值损失 1.07 亿，减值触发密集。评 4 分（高）。",
         "supporting_signals":["SZ002230-2024-SIG-002"],
         "key_metrics":{"goodwill_mn":1135,"intangible_mn":2917,"dev_exp_mn":1636,"credit_impairment_mn":965,"asset_impairment_mn":107}},
        {"dimension_id":"D4","dimension_name":"资本支出(CAPEX)强度","dimension_name_en":"Capital Expenditure Intensity","weight":0.20,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"固定资产 50.37 亿 + 在建工程 10.33 亿，算力集群建设持续，混合业务 capex 强度中高。评 4 分（高）。",
         "supporting_signals":["SZ002230-2024-SIG-003"],
         "key_metrics":{"ppe_net_mn":5037,"cip_mn":1033}},
        {"dimension_id":"D5","dimension_name":"行业竞争/技术替代","dimension_name_en":"Industry Competition & Technology Substitution","weight":0.15,"score":4,"score_max":5,"score_label":"高风险","score_label_en":"High Risk",
         "reasoning":"大模型混战（文心、通义、豆包、智谱等）与技术替代快，竞争烈度高。评 4 分（高）。",
         "supporting_signals":[],
         "key_metrics":{"competitors":["百度文心","阿里通义","字节豆包","智谱"],"substitution":"快"}}
    ],
    "comparative_context": {
        "same_company_trend": "科大讯飞多年保持高研发资本化（40%+），无形资产/商誉堆持续累积，减值损失逐年上升，趋势方向稳定。",
        "cross_company_benchmark": "在 A 股三家验证集中代表“混合型”，对标美股 CRM 软件型；其高资本化率 + 巨额无形资产堆使折旧/摊销双通道风险交汇，综合分最高。",
        "narrative_significance": "科大讯飞验证了‘风险藏摊销/商誉’路径在中国同样成立：43.58% 研发资本化 + 57 亿级无形资产/商誉堆 + 9.65 亿信用减值，正是美股软件巨头激进资本化的中国映射。它是三家中国样本中 5D-DRS 综合分最高的，证明模型对‘混合/软件型’公司的判别效度最强。"
    },
    "annotation_methodology": {
        "source_document": "科大讯飞股份有限公司 2024 年年度报告 + 2024 年度财务决算报告（深交所 002230）",
        "filing_accessed": "深交所 / 巨潮资讯",
        "text_extraction_method": "年报与财务决算报告关键节人工摘录（页码/行号待 PDF 终核）",
        "scoring_method": "Five-dimension weighted scoring (5D-DRS), weights 0.25/0.20/0.20/0.20/0.15（与美国面板一致）",
        "human_verification": "营收 233.43 亿、归母净利 5.6 亿、研发 45.8 亿(资本化率43.58%)、开发支出16.36亿、无形资产29.17亿、商誉11.35亿、固定资产50.37亿、信用减值9.65亿 均来自年报/决算报告原文，已核对；逐字行号待 PDF 终核",
        "limitation": "服务器折旧政策与 capex 绝对值、精确页码行号待年报 PDF 终核；未做多年趋势。"
    }
}

# ----------------------------------------------------------------------------
# 计算综合分并写出
# ----------------------------------------------------------------------------
def compute_and_dump(name, obj):
    dims = {d["dimension_id"]: d["score"] for d in obj["dimension_scores"]}
    wsum = sum(dims[k] * WEIGHTS[k] for k in WEIGHTS)
    lvl_cn, lvl_en, color = risk_level(wsum)
    obj["composite_score"] = {
        "weighted_score": round(wsum, 2),
        "max_score": 5.0,
        "risk_level": lvl_cn,
        "risk_level_en": lvl_en,
        "risk_level_color": color,
        "confidence": 0.8,
        "confidence_reason": "关键财务数字（营收、净利、研发、资本化率、无形资产/商誉、减值损失、固定资产）均来自年报/决算报告原文并已核对；折旧政策细节与逐字页码行号待团队用年报 PDF 终核，故置信度 0.8（低于美股样本 0.9）。"
    }
    path = os.path.join(OUT_JSON, f"{name}_2024_annotation.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f"{name}: weighted={wsum:.2f} -> {lvl_cn}  [{path}]")
    return name, round(wsum,2), lvl_cn

results = []
results.append(compute_and_dump("SH603881", sh_j))
results.append(compute_and_dump("SH688256", cw_j))
results.append(compute_and_dump("SZ002230", xf_j))

# ----------------------------------------------------------------------------
# 写出中国验证集 CSV（与 training_v06_panel_30_full.csv 同构的列）
# 列：ticker,name,fiscal_year,D1,D2,D3,D4,D5,weighted_score,risk_level
# ----------------------------------------------------------------------------
import csv
cols = ["ticker","name","fiscal_year","D1","D2","D3","D4","D5","weighted_score","risk_level"]
rows = [
    ["603881.SH","上海数据港",2024,3,3,2,4,3,3.00,"中风险"],
    ["688256.SH","寒武纪",2024,2,1,4,2,5,2.65,"中低风险"],
    ["002230.SZ","科大讯飞",2024,3,4,4,4,4,3.75,"中高风险"],
]
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(rows)
print(f"\nCSV written: {OUT_CSV}")
print("China validation set:", results)
