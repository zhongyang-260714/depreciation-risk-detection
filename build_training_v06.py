# -*- coding: utf-8 -*-
"""
build_training_v06.py — 从 30 份 confirmed 标注 JSON 重建全量面板训练集 v0.6
================================================================================
schema 以 training_v01.csv 为准：4 标识列 + 45 原始指标 + 4 年限解析列
+ 6 扩展特征 + 19 衍生指标 + D1-D5 + composite_score + risk_level = 85 列。

数据来源（唯一）：D:/depreciation-risk-detection/data/annotated/*_annotation.json
（30 份，review_status=confirmed）。禁止外源记忆补数；JSON 无来源的单元格保持 NA。

面板红利：depreciation_growth_rate / revenue_growth_rate / capex_yoy_growth
优先按同公司前一面板年计算；前一面板年缺值时回退到 JSON 自带的 *_prior_year 字段；
两者皆无则 NA（计数汇报）。

输出：D:/depreciation-risk-detection/data/processed/training_v06_panel_30_full.csv (UTF-8-SIG)

兼容处理（相对 v01 硬编码数据，JSON 字段命名差异）详见文末 COMPAT_NOTES。
"""
import csv, glob, json, os, re, sys
from collections import OrderedDict

SRC_DIR = r"D:\depreciation-risk-detection\data\annotated"
OUT_CSV = r"D:\depreciation-risk-detection\data\processed\training_v06_panel_30_full.csv"
V01_CSV = r"D:\科创企业资产折旧算法\training_v01_copy.csv"  # 仅用于表头对齐校验

# ============ 1. v01 85 列 schema（列顺序必须与 v01 完全一致） ============
IND_FIELDS = [  # 45 项原始指标，顺序同 v01 IND 表
 "total_assets","ppe_net","ppe_gross","accumulated_depreciation","servers_gross","servers_net",
 "buildings_gross","buildings_net","construction_in_progress","intangible_assets_net","goodwill",
 "revenue","net_income","operating_income","income_tax_expense","rd_expense","rd_capitalized",
 "impairment_loss","depreciation","amortization","capex_ppe","finance_lease_payments",
 "operating_cash_flow","server_useful_life","building_useful_life",
 "land_gross","equipment_gross","equipment_net","servers_accumulated_depreciation",
 "buildings_accumulated_depreciation","software_intangibles","patent_intangibles",
 "cash_and_equivalents","total_liabilities","gross_profit","sg_and_a","diluted_eps",
 "ppe_sales_proceeds","effective_tax_rate","employee_count",
 "equipment_useful_life","software_amortization_years","goodwill_test_method",
 "revenue_breakdown","revenue_geography",
]
LIFE_COLS  = ["server_life_min_years","server_life_max_years","building_life_min_years","building_life_max_years"]
EXTRA_FEATS = ["life_extended_current_period","life_extension_depreciation_reduction",
               "server_depreciation_ratio","inventory_writedown","accelerated_dep_charges","restructuring_charges"]
DERIVED_COLS = ["depreciation_rate_ppe","depreciation_rate_total_assets","amortization_rate",
 "intangible_ratio","goodwill_ratio","rd_intensity","capex_to_revenue","capex_to_ppe_net",
 "asset_turnover","ppe_turnover","accumulated_depreciation_rate","net_ppe_rate",
 "depreciation_coverage","capital_intensity","net_margin","cip_to_ppe",
 "depreciation_growth_rate","revenue_growth_rate","capex_yoy_growth"]
COLS = (["ticker","company_name","fiscal_year","report_period_end"] + IND_FIELDS + LIFE_COLS
        + EXTRA_FEATS + DERIVED_COLS + ["D1","D2","D3","D4","D5","composite_score","risk_level"])
assert len(COLS) == 85, len(COLS)

# ============ 2. 通用取数：候选键链（fh=financial_highlights, ap=accounting_policy） ============
def g(d, *keys):
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return None

# total_property_equipment_millions 在绝大多数 JSON 中是 PP&E 原值(gross)；
# 唯一例外 META_2023：该键=净值 96319（与 v01 主条目口径一致，v0.2 补丁值 96587 无 JSON 来源）。
TOTAL_PPE_IS_NET = {"META_2023"}

def map_numeric(key, fh):
    """把一份 JSON 的 financial_highlights 映射为 v01 数值字段。"""
    d = {}
    d["total_assets"] = g(fh, "total_assets_millions")
    d["ppe_net"] = g(fh, "ppe_net_millions", "property_equipment_net_millions",
                     "total_property_equipment_net_millions")
    if key in TOTAL_PPE_IS_NET and d["ppe_net"] is None:
        d["ppe_net"] = fh.get("total_property_equipment_millions")
    d["ppe_gross"] = g(fh, "ppe_gross_millions", "total_property_equipment_gross_millions")
    if d["ppe_gross"] is None and key not in TOTAL_PPE_IS_NET:
        d["ppe_gross"] = fh.get("total_property_equipment_millions")  # 其余文件该键=gross
    d["accumulated_depreciation"] = g(fh, "accumulated_depreciation_millions")
    # 服务器/网络设备原值：各家附注口径键名不同（均与 v01 口径注记一致）
    d["servers_gross"] = g(fh,
        "servers_network_assets_gross_millions",            # META（v01: Servers and network assets）
        "information_technology_assets_gross_millions",     # GOOGL（v01: Information technology assets）
        "computer_network_machinery_equipment_gross_millions",  # MSFT/ORCL（v01: Computer/network/machinery）
        "computers_equipment_software_gross_millions",      # CRM（v01: Computers, equipment and software）
        "computer_equipment_hardware_software_gross_millions")  # TSLA（v01: Computer equipment, hardware and software）
    d["buildings_gross"] = g(fh, "buildings_gross_millions",   # MU_FY2024
                             "land_and_buildings_gross_millions")  # INTC（v01: Land and buildings 合并口径）
    # NVDA buildings_leasehold_furniture_gross_millions 为建筑物+租赁改良+家具合并口径，无法拆分 → 不取（同 v01）
    d["construction_in_progress"] = g(fh, "construction_in_progress_millions")
    d["intangible_assets_net"] = g(fh, "intangible_assets_net_millions",
                                   "acquisition_related_intangibles_net_millions")  # AMD（v01: 仅收购相关）
    d["goodwill"] = g(fh, "goodwill_millions")
    d["revenue"] = g(fh, "revenue_millions")
    d["net_income"] = g(fh, "net_income_millions")
    d["operating_income"] = g(fh, "operating_income_millions")
    d["income_tax_expense"] = g(fh, "income_tax_expense_millions", "income_tax_benefit_millions")  # AMD_FY2022
    d["rd_expense"] = g(fh, "rd_expense_millions")
    d["impairment_loss"] = g(fh, "impairment_charges_millions")
    d["depreciation"] = g(fh, "depreciation_millions", "depreciation_expense_millions")
    d["amortization"] = g(fh, "amortization_millions")
    d["capex_ppe"] = g(fh, "capex_millions")
    d["finance_lease_payments"] = g(fh, "finance_lease_payments_millions")
    d["operating_cash_flow"] = g(fh, "operating_cash_flow_millions")
    d["land_gross"] = g(fh, "land_millions")  # NVDA_FY2023/2025
    d["equipment_gross"] = g(fh, "equipment_gross_millions",                      # AMD/MU_FY2024
                             "machinery_and_equipment_gross_millions",          # INTC（v01: Machinery and equipment）
                             "equipment_compute_hardware_software_gross_millions")  # NVDA（v01: 设备/计算硬件/软件）
    d["gross_profit"] = g(fh, "gross_margin_millions")       # MU×3
    d["sg_and_a"] = g(fh, "sga_expense_millions")            # NVDA_FY2023
    d["diluted_eps"] = g(fh, "diluted_eps_dollars")          # META_2022
    d["employee_count"] = g(fh, "headcount_year_end")        # META_2022
    # 以下字段 30 份 JSON 均无来源 → 保持 None：servers_net / buildings_net / equipment_net /
    # servers_accumulated_depreciation / buildings_accumulated_depreciation / software_intangibles /
    # patent_intangibles / cash_and_equivalents / total_liabilities / rd_capitalized /
    # ppe_sales_proceeds / effective_tax_rate / revenue_breakdown / revenue_geography
    return d

# ============ 3. 文本字段：年限 / 商誉测试方法 ============
# 单文件 server_useful_life 文本覆盖（期末生效口径，括号内保留 JSON 变更过程）
SERVER_LIFE_OVR = {
    # ap.server_useful_life_years_disclosed_table = "Four to Five years (Note 1 useful life table, HTML L4988)"
    # after 字段 "4.5 (effective Q2 2022) -> 5 (effective Q4 2022)" 是年内过程，非期末口径
    "META_2022": "4-5(2022年内由4经4.5延至5)",
}

def compose_life(before, after):
    if after is None:
        return None
    if before is not None and str(before) != str(after):
        return f"{after}(由{before}变更)"
    return str(after)

def map_text(key, ap):
    """把 accounting_policy 映射为 v01 文本字段。键名按公司/年份差异做兼容。"""
    t = {}
    # --- 服务器使用寿命 ---
    sv = g(ap, "server_useful_life_years",           # META_2023/NVDA_FY2024/2025
              "servers_useful_life_years",           # GOOGL_2022/2024
              "servers_and_network_assets_useful_life_years",  # META_2024
              "server_useful_life_years_in_effect_fy2023",     # NVDA_FY2023
              "computer_equipment_software_useful_life_years",  # TSLA（v01: 计算机设备与软件 3-10）
              "computers_equipment_software_useful_life_years")  # CRM（v01: 计算机/设备/软件）
    if sv is None:
        sv = compose_life(ap.get("server_useful_life_years_before"),
                          ap.get("server_useful_life_years_after"))  # GOOGL_2023/MSFT/ORCL/META_2022
    # 单文件文本覆盖：META_2022 的 after 字段为过程描述(4.5->5)，期末生效口径为披露表"4-5"
    t["server_useful_life"] = SERVER_LIFE_OVR.get(key, sv)
    # --- 建筑物使用寿命 ---
    t["building_useful_life"] = g(ap, "building_useful_life_years",
                                  "buildings_and_improvements_useful_life_years")  # MSFT/ORCL
    # --- 设备使用寿命 ---
    eq = g(ap, "equipment_useful_life_years",                      # AMD/META_2022/2023/NVDA_FY2024/2025
              "computer_network_machinery_equipment_useful_life_years",  # ORCL
              "machinery_equipment_useful_life_years",           # INTC
              "computer_equipment_useful_life_years",            # MSFT（v01: 计算机设备 2-6）
              "equipment_compute_hardware_software_useful_life_years")   # NVDA_FY2023
    if eq is None and "production_equipment_useful_life_years" in ap:  # MU
        eq = g(ap, "equipment_useful_life_years") or ap["production_equipment_useful_life_years"]
    if eq is None and "machinery_equipment_vehicles_office_furniture_useful_life_years" in ap:  # TSLA
        base = ap["machinery_equipment_vehicles_office_furniture_useful_life_years"]
        tool = ap.get("tooling_useful_life_years")
        eq = f"{base}(机器/设备/车辆/家具;tooling {tool})" if tool else base
    if eq is None and "furniture_fixtures_useful_life_years" in ap:  # CRM（v01: 5(家具);租赁改良≤10）
        eq = f"{ap['furniture_fixtures_useful_life_years']}(家具)"
    t["equipment_useful_life"] = eq
    # --- 软件摊销期 ---
    t["software_amortization_years"] = g(ap,
        "software_useful_life_years",                 # MU
        "internal_use_software_useful_life_years",    # MSFT
        "internal_use_software_amortization_years",   # TSLA
        "intangible_assets_useful_life_years")        # ORCL（1-10，收购无形）
    # --- 商誉减值测试方法 ---
    gw = g(ap, "goodwill_impairment_testing", "goodwill_impairment_test",
              "goodwill_impairment_statement", "goodwill_impairment_assessment_fy2024")
    t["goodwill_test_method"] = (gw[:200] if isinstance(gw, str) else gw)
    return t

# ============ 4. 扩展特征：年限变更标记与减提额（逐文件核对 JSON 键后显式给出） ============
# life_extended_current_period: 1=本期发生折旧年限延长并适用；0=本期无变更（含"已宣布但下期生效"）
LIFE_EXT = {
 "AMD_FY2022":0,"AMD_FY2023":0,"AMD_FY2024":0,
 "CRM_FY2023":0,"CRM_FY2024":0,"CRM_FY2025":0,        # CRM_FY2025: no_useful_life_change_in_fiscal_2025=True
 "GOOGL_2022":0,   # change_in_estimate: 2023-01 生效，本期未适用
 "GOOGL_2023":1,   # change_effective=2023-01，本期生效
 "GOOGL_2024":0,   # change_in_estimate: None in FY2024
 "INTC_FY2022":0,  # no_useful_life_change_in_fiscal_2022=True；2023-01 宣布生效
 "INTC_FY2023":1,  # change_effective=2023-01 applied prospectively beginning Q1 2023
 "INTC_FY2024":0,  # no_useful_life_change_in_fiscal_2024=True
 "META_2022":1,    # change_effective=Q2 2022 (4->4.5) and Q4 2022 (4.5->5)，本期两次变更
 "META_2023":0,    # 无变更键；v01 同
 "META_2024":1,    # change_in_estimate: 2024-01 servers 5->5.5，FY2024 期初生效
 "MSFT_FY2023":1,  # no_useful_life_change_in_fiscal_2023=False；FY2023 为变更生效年
 "MSFT_FY2024":0,  # no_useful_life_change_in_fiscal_2024=True
 "MSFT_FY2025":0,  # no_useful_life_change_in_fiscal_2025=True
 "MU_FY2022":0,"MU_FY2023":0,"MU_FY2024":0,           # MU_FY2024: no_useful_life_change_in_fiscal_2024=True
 "NVDA_FY2023":0,  # change_effective=beginning of FY2024，本期未适用
 "NVDA_FY2024":1,  # server 3->4-5 / assembly-test 5->7，2023-02 生效
 "NVDA_FY2025":0,  # no_useful_life_change_in_fiscal_2025=True
 "ORCL_FY2023":1,  # useful_life_change_is_current_period=True；FY2023 Q1 生效
 "ORCL_FY2024":0,  # no_useful_life_change_in_fiscal_2024=True
 "ORCL_FY2025":1,  # no_useful_life_change_in_fiscal_2025=False；FY2025 Q1 生效(5->6)
 "TSLA_2022":0,"TSLA_2023":0,"TSLA_2024":0,           # change_in_estimate 均为 None
}
# life_extension_depreciation_reduction: 本期已实现的减提额（百万$）；"announced/expected" 未实现 → None
LIFE_RED = {
 "META_2022": 860,    # fh.useful_life_change_depreciation_reduction_millions
 "GOOGL_2023": 3900,  # fh.useful_life_change_depreciation_reduction_millions
 "INTC_FY2023": 4200, # fh.useful_life_change_depreciation_reduction_millions
 "MSFT_FY2023": 3700, # fh.useful_life_change_opex_reduction_millions_fy2023
 "ORCL_FY2023": 434,  # fh.useful_life_change_opex_reduction_millions_fy2023（本期）
 "ORCL_FY2025": 733,  # fh.useful_life_change_opex_reduction_millions_fy2025（本期）
 # INTC_FY2022 announced_useful_life_change_expected_* = 预期值 → None
 # GOOGL_2022 change 2023-01 才生效 → None；META_2024 "Expected to reduce" → None
 # ORCL_FY2024 仅列 fy2023=434（上期）→ 本期 None
}
# inventory_writedown 的 INTC 特例：FY2022 Optane 存货减值 723（v01 口径：记入发生年）
INV_WR_OVR = {"INTC_FY2022": 723}  # fh.optane_inventory_impairment_2022_millions

# ============ 5. 年限文本解析（v01 同款，扩展支持小数与 -> 连接符） ============
def parse_life(s):
    if not s:
        return (None, None)
    s = str(s).replace("->", "-").replace("–", "-")
    def _n(x):
        f = float(x)
        return int(f) if f.is_integer() else f
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s)
    if m:
        return (_n(m.group(1)), _n(m.group(2)))
    m = re.match(r"\s*(\d+(?:\.\d+)?)", s)
    if m:
        a = _n(m.group(1))
        return (a, a)
    return (None, None)

# ============ 6. 衍生指标（公式与 v01 完全一致） ============
def div(a, b):
    return round(a / b, 4) if (a is not None and b not in (None, 0)) else None

def derived(d):
    r = OrderedDict()
    r["depreciation_rate_ppe"] = div(d["depreciation"], d["ppe_net"])
    r["depreciation_rate_total_assets"] = div(d["depreciation"], d["total_assets"])
    r["amortization_rate"] = div(d["amortization"], d["total_assets"])
    r["intangible_ratio"] = (div((d["intangible_assets_net"] or 0) + (d["goodwill"] or 0), d["total_assets"])
                             if d["intangible_assets_net"] is not None and d["goodwill"] is not None else None)
    r["goodwill_ratio"] = div(d["goodwill"], d["total_assets"])
    r["rd_intensity"] = div(d["rd_expense"], d["revenue"])
    r["capex_to_revenue"] = div(d["capex_ppe"], d["revenue"])
    r["capex_to_ppe_net"] = div(d["capex_ppe"], d["ppe_net"])
    r["asset_turnover"] = div(d["revenue"], d["total_assets"])
    r["ppe_turnover"] = div(d["revenue"], d["ppe_net"])
    r["accumulated_depreciation_rate"] = div(d["accumulated_depreciation"], d["ppe_gross"])
    r["net_ppe_rate"] = div(d["ppe_net"], d["ppe_gross"])
    # TSLA 特例（v01 口径）：净利润被一次性递延税收益扭曲 → 折旧覆盖率用营业利润。
    # v01 仅 TSLA_2023；TSLA_2024 JSON net_income_note 同样注明含一次性税收益 → 沿用同一口径。
    base = d.get("coverage_income_base", d["net_income"])
    r["depreciation_coverage"] = div(d["depreciation"], base)
    r["capital_intensity"] = div(d["ppe_net"], d["total_assets"])
    r["net_margin"] = div(d["net_income"], d["revenue"])
    r["cip_to_ppe"] = div(d["construction_in_progress"], d["ppe_net"])
    # YoY 三个在面板阶段填充（见第 8 节）
    r["depreciation_growth_rate"] = None
    r["revenue_growth_rate"] = None
    r["capex_yoy_growth"] = None
    return r

# ============ 7. 逐 JSON 组装行 ============
def load_rows():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "*_annotation.json")))
    assert len(files) == 30, f"预期30份JSON，实际{len(files)}"
    rows, priors = [], {}
    for fp in files:
        key = os.path.basename(fp).replace("_annotation.json", "")
        J = json.load(open(fp, encoding="utf-8"))
        assert J["metadata"].get("review_status") == "confirmed", f"{key} 非 confirmed"
        co, fh, ap = J["company"], J.get("financial_highlights", {}), J.get("accounting_policy", {})
        d = {f: None for f in IND_FIELDS}
        d.update(map_numeric(key, fh))
        d.update(map_text(key, ap))
        # 扩展特征
        d["life_extended_current_period"] = LIFE_EXT[key]
        d["life_extension_depreciation_reduction"] = LIFE_RED.get(key)
        d["server_depreciation_ratio"] = g(fh, "server_depreciation_pct_of_total")
        d["inventory_writedown"] = INV_WR_OVR.get(key, g(fh, "inventory_writedown_millions",
                                                         "inventory_provision_millions"))
        d["accelerated_dep_charges"] = g(fh,
            "accelerated_depreciation_and_rent_millions",              # GOOGL_2023
            "manufacturing_accelerated_depreciation_component_millions",  # INTC_FY2024
            "excess_capacity_charges_millions",                        # INTC_FY2024(次选)
            "excess_capacity_charges_2023_millions",                   # INTC_FY2023（v01: 411）
            "excess_capacity_charges_2022_millions")                   # INTC_FY2022
        d["restructuring_charges"] = g(fh,
            "restructuring_charges_millions", "restructuring_expense_millions",
            "restructuring_and_other_charges_millions", "restructure_charges_millions",
            "restructuring_total_charges_millions")
        # TSLA 折旧覆盖率口径（v01 特例 + FY2024 同情形）
        if key in ("TSLA_2023", "TSLA_2024"):
            d["coverage_income_base"] = d["operating_income"]
        # 标签
        scores = {x["dimension_id"]: x.get("score") for x in J.get("dimension_scores", [])}
        comp = J.get("composite_score", {})
        row = OrderedDict()
        row["ticker"] = co["ticker"]; row["company_name"] = co["name"]
        row["fiscal_year"] = co["fiscal_year"]; row["report_period_end"] = co.get("report_period_end")
        for f in IND_FIELDS:
            row[f] = d[f]
        smin, smax = parse_life(d["server_useful_life"])
        bmin, bmax = parse_life(d["building_useful_life"])
        row["server_life_min_years"], row["server_life_max_years"] = smin, smax
        row["building_life_min_years"], row["building_life_max_years"] = bmin, bmax
        for f in EXTRA_FEATS:
            row[f] = d[f]
        row.update(derived(d))
        for k in ["D1", "D2", "D3", "D4", "D5"]:
            row[k] = scores.get(k)
        row["composite_score"] = comp.get("weighted_score")
        row["risk_level"] = comp.get("risk_level")
        rows.append(row)
        # JSON 自带的上年值（面板首年 YoY 回退用；按 ticker+fiscal_year 键控，
        # 文件名含 FY 前缀差异不影响匹配）
        priors[(co["ticker"], co["fiscal_year"])] = {
            "depreciation": g(fh, "depreciation_prior_year_millions"),
            "capex_ppe": g(fh, "capex_prior_year_millions"),
            "revenue": None,  # 30 份 JSON 均无全公司口径 revenue_prior 字段
        }
    return rows, priors

# ============ 8. 面板 YoY：同公司前一面板年优先，JSON prior 字段回退 ============
def fill_yoy(rows, priors):
    stats = {"depreciation_growth_rate": {"panel": 0, "json_prior": 0, "na": 0},
             "revenue_growth_rate": {"panel": 0, "json_prior": 0, "na": 0},
             "capex_yoy_growth": {"panel": 0, "json_prior": 0, "na": 0}}
    base_of = {"depreciation_growth_rate": "depreciation",
               "revenue_growth_rate": "revenue",
               "capex_yoy_growth": "capex_ppe"}
    by_co = {}
    for r in rows:
        by_co.setdefault(r["ticker"], []).append(r)
    for t, rs in by_co.items():
        rs.sort(key=lambda r: r["fiscal_year"])
        for i, r in enumerate(rs):
            for ycol, bcol in base_of.items():
                cur = r[bcol]
                prev = rs[i - 1][bcol] if i > 0 else None
                if cur is not None and prev not in (None, 0):
                    r[ycol] = div(cur - prev, prev); stats[ycol]["panel"] += 1
                else:
                    jp = priors.get((t, r["fiscal_year"]), {}).get(bcol)
                    if cur is not None and jp not in (None, 0):
                        r[ycol] = div(cur - jp, jp); stats[ycol]["json_prior"] += 1
                    else:
                        stats[ycol]["na"] += 1
    return stats

# ============ 9. 主流程 + 校验 ============
def main():
    rows, priors = load_rows()
    yoy_stats = fill_yoy(rows, priors)
    rows.sort(key=lambda r: (r["ticker"], r["fiscal_year"]))

    # --- 校验1：表头与 v01 完全对齐 ---
    with open(V01_CSV, encoding="utf-8-sig") as f:
        v01_header = next(csv.reader(f))
    assert list(COLS) == v01_header, "列与 v01 不一致:\n" + \
        "\n".join(f"{i}: v01={a} v06={b}" for i, (a, b) in enumerate(zip(v01_header, COLS)) if a != b)

    # --- 校验2：行数/公司×年份 ---
    assert len(rows) == 30
    by_co = {}
    for r in rows:
        by_co.setdefault(r["ticker"], []).append(r["fiscal_year"])
    assert len(by_co) == 10 and all(len(v) == 3 for v in by_co.values()), by_co

    # --- 校验3：整列为空检查（应填而未填） ---
    NO_SOURCE = {  # 30 份 JSON 中确认无数据来源的列（如实保持 NA）
        "servers_net","buildings_net","equipment_net","servers_accumulated_depreciation",
        "buildings_accumulated_depreciation","software_intangibles","patent_intangibles",
        "cash_and_equivalents","total_liabilities","rd_capitalized","ppe_sales_proceeds",
        "effective_tax_rate","revenue_breakdown","revenue_geography",
    }
    empty_cols = [c for c in COLS if all(r[c] is None for r in rows)]
    unexpected = [c for c in empty_cols if c not in NO_SOURCE]
    missing_expected = [c for c in NO_SOURCE if c not in empty_cols]
    assert not unexpected, f"意外整列为空: {unexpected}"
    if missing_expected:
        print(f"[提示] 无来源清单中的列出现了数据（好事）: {missing_expected}")

    # --- 校验4：数值抽查 5 处（与 JSON 原文一致） ---
    def cell(t, y, c):
        return next(r[c] for r in rows if r["ticker"] == t and r["fiscal_year"] == y)
    spot = [
        ("MSFT", 2025, "capex_ppe", 64551, "MSFT_FY2025 fh.capex_millions"),
        ("ORCL", 2025, "servers_gross", 30345, "ORCL_FY2025 fh.computer_network_machinery_equipment_gross_millions"),
        ("INTC", 2024, "depreciation", 9951, "INTC_FY2024 fh.depreciation_millions"),
        ("MU", 2024, "gross_profit", 5613, "MU_FY2024 fh.gross_margin_millions"),
        ("META", 2022, "employee_count", 86482, "META_2022 fh.headcount_year_end"),
    ]
    for t, y, c, exp, src in spot:
        got = cell(t, y, c)
        assert got == exp, f"抽查失败 {t} {y} {c}: {got} != {exp} ({src})"

    # --- 写 CSV ---
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as fh_out:
        w = csv.DictWriter(fh_out, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})

    # --- 汇报 ---
    print(f"CSV: {OUT_CSV} ({os.path.getsize(OUT_CSV)} bytes, {len(COLS)}列 × {len(rows)}行)")
    print("列对齐: 85列与 v01 表头逐位一致 ✓")
    print("公司×年份:", {t: sorted(v) for t, v in sorted(by_co.items())})
    print("整列为空(无JSON来源,共%d列): %s" % (len(empty_cols), sorted(empty_cols)))
    print("YoY 填充: ",
          {k: f"panel={v['panel']} json_prior={v['json_prior']} NA={v['na']}" for k, v in yoy_stats.items()})
    print("数值抽查5处 ✓")
    # 已知数据质量提示（不阻断输出）
    print("[数据质量提示] GOOGL_2022 fh.depreciation_expense_millions=10200 与 GOOGL_2023 "
          "fh.depreciation_prior_year_millions=13475 冲突；YoY 按面板口径(10200)计算。")
    print("[数据质量提示] TSLA_2024 fh.net_income_millions=71000 疑似量级错误(实际约7,130)，"
          "JSON note 注明含一次性税收益；net_margin 按原文保留，depreciation_coverage 已用营业利润口径。")

if __name__ == "__main__":
    main()

# ============ COMPAT_NOTES（兼容处理清单） ============
# 1. depreciation: depreciation_millions | depreciation_expense_millions（GOOGL_2022/2024、META_2024、TSLA_2022/2024）
# 2. ppe_net: ppe_net_millions | property_equipment_net_millions | total_property_equipment_net_millions；
#    META_2023 特例：total_property_equipment_millions=净值96319（v01主条目口径）
# 3. ppe_gross: ppe_gross_millions | total_property_equipment_gross_millions | total_property_equipment_millions(除META_2023)
# 4. intangible_assets_net: intangible_assets_net_millions | acquisition_related_intangibles_net_millions(AMD)
# 5. income_tax_expense: income_tax_expense_millions | income_tax_benefit_millions(AMD_FY2022=-122)
# 6. servers_gross 五套公司口径键（META/GOOGL/MSFT+ORCL/CRM/TSLA）；NVDA equipment_compute_hardware_software 归入 equipment_gross（同v01）
# 7. buildings_gross: buildings_gross_millions(MU_FY2024) | land_and_buildings_gross_millions(INTC合并口径，同v01)；
#    NVDA buildings_leasehold_furniture 合并无法拆分→NA（同v01）
# 8. restructuring_charges 五套键名；accelerated_dep_charges 五套键名（INTC_FY2024 取制造加速折旧组件992）
# 9. inventory_writedown: inventory_writedown_millions(MU) | inventory_provision_millions(NVDA) | Optane特例(INTC_FY2022=723)
# 10. 年限文本键名：before/after 对、in-effect 键、公司专属键；compose 为 "after(由before变更)"；
#     parse_life 扩展支持小数(4.5/5.5)与 "->" 连接符（META_2022 年内两次变更）
# 11. life_extended/life_reduction 逐文件显式表（LIFE_EXT/LIFE_RED），依据 JSON 的 no_useful_life_change_in_fiscal_* /
#     useful_life_change_is_current_period / change_effective 等旗标核对；announced/expected 未实现减提→None
# 12. depreciation_coverage：TSLA_2023 沿用 v01 营业利润口径；TSLA_2024 JSON 同样注明净利润含一次性税收益→同口径
# 13. YoY：面板前值优先 → JSON *_prior_year 回退 → NA；revenue 全公司口径 prior 字段 30 份均无→首年 NA
