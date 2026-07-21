"""
双轨财报数据提取器 v2.0
轨道A：yfinance 快速获取27家公司的结构化财务指标
轨道B：sec-edgar-downloader 下载10-K原文（可选，网络不稳定时跳过）
输出：data/extracted/financial_metrics.json + .csv
作者：zhongyang-260714
日期：2025-07-15
"""

import yfinance as yf
import pandas as pd
import json
import time
import os
from pathlib import Path
from datetime import datetime

# ========== 项目路径配置 ==========
PROJECT_ROOT = Path("D:/depreciation-risk-detection")
RAW_DIR = PROJECT_ROOT / "data/raw"
EXTRACTED_DIR = PROJECT_ROOT / "data/extracted"
ANNOTATED_DIR = PROJECT_ROOT / "data/annotated"

# 确保目录存在
for d in [RAW_DIR, EXTRACTED_DIR, ANNOTATED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ========== 27家目标公司（分层覆盖AI产业链） ==========
# 格式：ticker, name, 财年结束类型, 行业层级, 备注
TARGET_COMPANIES = [
    # === L1：AI 芯片制造层 ===
    {"ticker": "NVDA", "name": "NVIDIA", "fy_end": "Jan", "layer": "L1_Chip", "note": "GPU制造龙头"},
    {"ticker": "AMD", "name": "AMD", "fy_end": "Dec", "layer": "L1_Chip", "note": "CPU/GPU竞争"},
    {"ticker": "INTC", "name": "Intel", "fy_end": "Dec", "layer": "L1_Chip", "note": "传统CPU+AI芯片"},
    {"ticker": "QCOM", "name": "Qualcomm", "fy_end": "Sep", "layer": "L1_Chip", "note": "移动端AI芯片"},
    {"ticker": "AVGO", "name": "Broadcom", "fy_end": "Oct", "layer": "L1_Chip", "note": "AI芯片定制"},
    {"ticker": "MU", "name": "Micron", "fy_end": "Aug", "layer": "L1_Chip", "note": "AI存储芯片"},
    {"ticker": "LRCX", "name": "Lam Research", "fy_end": "Jun", "layer": "L1_Chip", "note": "半导体设备"},
    {"ticker": "AMAT", "name": "Applied Materials", "fy_end": "Oct", "layer": "L1_Chip", "note": "半导体设备"},
    
    # === L2：云服务 + AI 应用层 ===
    {"ticker": "META", "name": "Meta Platforms", "fy_end": "Dec", "layer": "L2_Cloud", "note": "社交媒体+AI"},
    {"ticker": "GOOGL", "name": "Alphabet", "fy_end": "Dec", "layer": "L2_Cloud", "note": "Google Cloud+AI"},
    {"ticker": "MSFT", "name": "Microsoft", "fy_end": "Jun", "layer": "L2_Cloud", "note": "Azure+OpenAI"},
    {"ticker": "AMZN", "name": "Amazon", "fy_end": "Dec", "layer": "L2_Cloud", "note": "AWS云+AI"},
    {"ticker": "ORCL", "name": "Oracle", "fy_end": "May", "layer": "L2_Cloud", "note": "云数据库+AI"},
    {"ticker": "IBM", "name": "IBM", "fy_end": "Dec", "layer": "L2_Cloud", "note": "企业AI+云"},
    {"ticker": "CRM", "name": "Salesforce", "fy_end": "Jan", "layer": "L2_Cloud", "note": "AI CRM"},
    
    # === L3：AI 软件 / 网络安全 ===
    {"ticker": "PLTR", "name": "Palantir", "fy_end": "Dec", "layer": "L3_AI_Software", "note": "AI数据分析"},
    {"ticker": "SNOW", "name": "Snowflake", "fy_end": "Jan", "layer": "L3_AI_Software", "note": "云数据平台"},
    {"ticker": "NET", "name": "Cloudflare", "fy_end": "Dec", "layer": "L3_AI_Software", "note": "边缘AI+网络"},
    {"ticker": "DDOG", "name": "Datadog", "fy_end": "Dec", "layer": "L3_AI_Software", "note": "AI监控"},
    {"ticker": "CRWD", "name": "CrowdStrike", "fy_end": "Jan", "layer": "L3_AI_Software", "note": "AI安全"},
    {"ticker": "ZS", "name": "Zscaler", "fy_end": "Jul", "layer": "L3_AI_Software", "note": "云安全"},
    {"ticker": "OKTA", "name": "Okta", "fy_end": "Jan", "layer": "L3_AI_Software", "note": "身份安全"},
    
    # === L4：其他科技（电动车/半导体/通信） ===
    {"ticker": "TSLA", "name": "Tesla", "fy_end": "Dec", "layer": "L4_Other_Tech", "note": "AI自动驾驶"},
    {"ticker": "TSM", "name": "TSMC", "fy_end": "Dec", "layer": "L4_Other_Tech", "note": "晶圆代工(ADR)"},
    {"ticker": "ADI", "name": "Analog Devices", "fy_end": "Oct", "layer": "L4_Other_Tech", "note": "模拟芯片"},
    {"ticker": "MRVL", "name": "Marvell", "fy_end": "Jan", "layer": "L4_Other_Tech", "note": "数据中心芯片"},
    {"ticker": "NXPI", "name": "NXP Semiconductors", "fy_end": "Dec", "layer": "L4_Other_Tech", "note": "汽车芯片"},
]

# ========== 轨道A：yfinance 财务指标提取 ==========

def safe_get(df, key, col):
    """安全获取DataFrame值，返回百万美元"""
    try:
        if key in df.index and col in df.columns:
            val = df.loc[key, col]
            if pd.isna(val):
                return None
            # yfinance 数据单位是美元，除以1e6转为百万
            return float(val) / 1e6
        return None
    except Exception:
        return None

def safe_div(a, b):
    """安全除法"""
    if a is not None and b is not None and abs(b) > 1e-10:
        return round(float(a) / float(b), 4)
    return None

def extract_financial_metrics(company: dict, max_retries: int = 3) -> dict:
    """
    用 yfinance 获取单家公司的核心财务指标
    失败时自动重试
    """
    ticker = company["ticker"]
    name = company["name"]
    
    for attempt in range(max_retries):
        try:
            print(f"  📊 [{attempt+1}/{max_retries}] 提取 {ticker} ({name})...")
            stock = yf.Ticker(ticker)
            
            # 获取三大报表
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cash_flow
            
            if income_stmt.empty:
                print(f"    ⚠️ {ticker}: 利润表为空，跳过")
                return None
            
            # 获取最近的年度列
            latest_col = income_stmt.columns[0]
            fiscal_year = str(latest_col.year) if hasattr(latest_col, 'year') else str(latest_col)[:4]
            
            # 尝试获取上一年（用于计算同比增长）
            prev_col = income_stmt.columns[1] if len(income_stmt.columns) > 1 else None
            
            # ===== 利润表指标 =====
            revenue = safe_get(income_stmt, "Total Revenue", latest_col)
            net_income = safe_get(income_stmt, "Net Income", latest_col)
            operating_income = safe_get(income_stmt, "Operating Income", latest_col)
            rd_expense = safe_get(income_stmt, "Research Development", latest_col)
            
            # 折旧相关：优先单独折旧，其次D&A
            depreciation = safe_get(income_stmt, "Depreciation", latest_col)
            amortization = safe_get(income_stmt, "Amortization", latest_col)
            da_combined = safe_get(income_stmt, "Depreciation Amortization Depletion", latest_col)
            ebitda = safe_get(income_stmt, "EBITDA", latest_col)
            
            # 如果单独折旧为空，但D&A有值，用D&A近似
            if depreciation is None and da_combined is not None:
                depreciation = da_combined
            
            # ===== 资产负债表指标 =====
            total_assets = safe_get(balance_sheet, "Total Assets", latest_col)
            total_liabilities = safe_get(balance_sheet, "Total Liabilities Net Minority Interest", latest_col)
            total_equity = safe_get(balance_sheet, "Stockholders Equity", latest_col)
            ppe_net = safe_get(balance_sheet, "Net PPE", latest_col)
            ppe_gross = safe_get(balance_sheet, "Gross PPE", latest_col)
            acc_depreciation = safe_get(balance_sheet, "Accumulated Depreciation", latest_col)
            intangible = safe_get(balance_sheet, "Net Intangible Assets", latest_col)
            goodwill = safe_get(balance_sheet, "Goodwill", latest_col)
            total_debt = safe_get(balance_sheet, "Total Debt", latest_col)
            cash = safe_get(balance_sheet, "Cash And Cash Equivalents", latest_col)
            
            # ===== 现金流量表指标 =====
            capex = safe_get(cash_flow, "Capital Expenditure", latest_col)
            ocf = safe_get(cash_flow, "Operating Cash Flow", latest_col)
            fcf = safe_get(cash_flow, "Free Cash Flow", latest_col)
            sbc = safe_get(cash_flow, "Stock Based Compensation", latest_col)
            
            # ===== 计算衍生指标 =====
            metrics = {}
            if revenue and revenue != 0:
                metrics = {
                    "capex_to_revenue": safe_div(capex, revenue),
                    "depreciation_to_revenue": safe_div(depreciation, revenue),
                    "rd_to_revenue": safe_div(rd_expense, revenue),
                    "net_margin": safe_div(net_income, revenue),
                    "operating_margin": safe_div(operating_income, revenue),
                    "asset_turnover": safe_div(revenue, total_assets),
                    "ppe_to_total_assets": safe_div(ppe_net, total_assets),
                    "intangible_to_total_assets": safe_div(intangible, total_assets),
                    "debt_to_equity": safe_div(total_debt, total_equity),
                    "cash_to_revenue": safe_div(cash, revenue),
                    "sbc_to_revenue": safe_div(sbc, revenue),
                    "ocf_to_revenue": safe_div(ocf, revenue),
                    "fcf_to_revenue": safe_div(fcf, revenue),
                }
            
            # ===== 计算折旧相关关键比率 =====
            depreciation_metrics = {}
            if ppe_gross and ppe_gross != 0:
                depreciation_metrics["acc_dep_to_gross_ppe"] = safe_div(acc_depreciation, ppe_gross)
            if ppe_net and ppe_net != 0:
                depreciation_metrics["capex_to_net_ppe"] = safe_div(capex, ppe_net)
            if depreciation and depreciation != 0:
                depreciation_metrics["revenue_per_depreciation"] = safe_div(revenue, depreciation)
                depreciation_metrics["capex_to_depreciation"] = safe_div(capex, depreciation)
            
            result = {
                # 元数据
                "ticker": ticker,
                "company_name": name,
                "fiscal_year": fiscal_year,
                "fiscal_year_end": company["fy_end"],
                "industry_layer": company["layer"],
                "note": company["note"],
                "extraction_timestamp": datetime.now().isoformat(),
                "source": "yfinance",
                "retry_count": attempt,
                
                # 利润表
                "revenue_millions": revenue,
                "net_income_millions": net_income,
                "operating_income_millions": operating_income,
                "rd_expense_millions": rd_expense,
                "depreciation_millions": depreciation,
                "amortization_millions": amortization,
                "depreciation_and_amortization_millions": da_combined,
                "ebitda_millions": ebitda,
                
                # 资产负债表
                "total_assets_millions": total_assets,
                "total_liabilities_millions": total_liabilities,
                "total_equity_millions": total_equity,
                "ppe_net_millions": ppe_net,
                "ppe_gross_millions": ppe_gross,
                "accumulated_depreciation_millions": acc_depreciation,
                "intangible_assets_millions": intangible,
                "goodwill_millions": goodwill,
                "total_debt_millions": total_debt,
                "cash_millions": cash,
                
                # 现金流量表
                "capex_millions": capex,
                "operating_cash_flow_millions": ocf,
                "free_cash_flow_millions": fcf,
                "stock_based_compensation_millions": sbc,
                
                # 计算指标
                "metrics": metrics,
                "depreciation_metrics": depreciation_metrics,
                
                # 数据质量标记
                "data_quality": {
                    "has_depreciation": depreciation is not None,
                    "has_capex": capex is not None,
                    "has_ppe": ppe_net is not None,
                    "income_stmt_columns": len(income_stmt.columns),
                    "missing_fields": []
                }
            }
            
            # 标记缺失字段
            for field, val in [
                ("depreciation", depreciation),
                ("capex", capex),
                ("ppe_net", ppe_net),
                ("revenue", revenue),
                ("total_assets", total_assets)
            ]:
                if val is None:
                    result["data_quality"]["missing_fields"].append(field)
            
            print(f"    ✅ {ticker} 提取完成 (FY{fiscal_year})")
            return result
            
        except Exception as e:
            print(f"    ❌ {ticker} 第{attempt+1}次尝试失败: {str(e)[:80]}")
            if attempt < max_retries - 1:
                time.sleep(2 + attempt * 2)  # 递增等待
            else:
                print(f"    💀 {ticker} 最终失败，跳过")
                return None
    
    return None

def batch_extract(companies: list, delay: float = 1.5) -> list:
    """批量提取，间隔请求避免被封"""
    results = []
    failed = []
    
    print(f"\n🚀 开始批量提取 {len(companies)} 家公司...")
    print("=" * 60)
    
    for i, company in enumerate(companies):
        result = extract_financial_metrics(company)
        if result:
            results.append(result)
        else:
            failed.append(company["ticker"])
        
        # 进度显示
        progress = (i + 1) / len(companies) * 100
        print(f"  📈 进度: {i+1}/{len(companies)} ({progress:.1f}%) | 成功: {len(results)} | 失败: {len(failed)}")
        
        # 间隔请求
        if i < len(companies) - 1:
            time.sleep(delay)
    
    print("=" * 60)
    print(f"✅ 提取完成: {len(results)} 家成功, {len(failed)} 家失败")
    if failed:
        print(f"❌ 失败列表: {', '.join(failed)}")
    
    return results

# ========== 保存结果 ==========

def save_results(results: list):
    """保存为JSON和CSV两种格式"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 1. 完整JSON（保留所有嵌套结构）
    json_path = EXTRACTED_DIR / f"financial_metrics_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 JSON 已保存: {json_path} ({len(results)} 家公司)")
    
    # 2. 扁平CSV（用于Excel/Pandas分析）
    flat_data = []
    for r in results:
        flat = {
            # 标识
            "ticker": r["ticker"],
            "company_name": r["company_name"],
            "fiscal_year": r["fiscal_year"],
            "fiscal_year_end": r["fiscal_year_end"],
            "industry_layer": r["industry_layer"],
            "note": r["note"],
            
            # 核心财务数据
            "revenue_millions": r.get("revenue_millions"),
            "net_income_millions": r.get("net_income_millions"),
            "operating_income_millions": r.get("operating_income_millions"),
            "rd_expense_millions": r.get("rd_expense_millions"),
            "depreciation_millions": r.get("depreciation_millions"),
            "amortization_millions": r.get("amortization_millions"),
            "ebitda_millions": r.get("ebitda_millions"),
            
            # 资产负债表
            "total_assets_millions": r.get("total_assets_millions"),
            "ppe_net_millions": r.get("ppe_net_millions"),
            "ppe_gross_millions": r.get("ppe_gross_millions"),
            "accumulated_depreciation_millions": r.get("accumulated_depreciation_millions"),
            "intangible_assets_millions": r.get("intangible_assets_millions"),
            "goodwill_millions": r.get("goodwill_millions"),
            "total_debt_millions": r.get("total_debt_millions"),
            "cash_millions": r.get("cash_millions"),
            
            # 现金流量
            "capex_millions": r.get("capex_millions"),
            "operating_cash_flow_millions": r.get("operating_cash_flow_millions"),
            "free_cash_flow_millions": r.get("free_cash_flow_millions"),
            "stock_based_compensation_millions": r.get("stock_based_compensation_millions"),
            
            # 关键比率
            "capex_to_revenue": r.get("metrics", {}).get("capex_to_revenue"),
            "depreciation_to_revenue": r.get("metrics", {}).get("depreciation_to_revenue"),
            "rd_to_revenue": r.get("metrics", {}).get("rd_to_revenue"),
            "net_margin": r.get("metrics", {}).get("net_margin"),
            "operating_margin": r.get("metrics", {}).get("operating_margin"),
            "ppe_to_total_assets": r.get("metrics", {}).get("ppe_to_total_assets"),
            "intangible_to_total_assets": r.get("metrics", {}).get("intangible_to_total_assets"),
            "debt_to_equity": r.get("metrics", {}).get("debt_to_equity"),
            "sbc_to_revenue": r.get("metrics", {}).get("sbc_to_revenue"),
            "fcf_to_revenue": r.get("metrics", {}).get("fcf_to_revenue"),
            
            # 折旧专项指标
            "acc_dep_to_gross_ppe": r.get("depreciation_metrics", {}).get("acc_dep_to_gross_ppe"),
            "capex_to_net_ppe": r.get("depreciation_metrics", {}).get("capex_to_net_ppe"),
            "revenue_per_depreciation": r.get("depreciation_metrics", {}).get("revenue_per_depreciation"),
            "capex_to_depreciation": r.get("depreciation_metrics", {}).get("capex_to_depreciation"),
            
            # 数据质量
            "has_depreciation": r.get("data_quality", {}).get("has_depreciation"),
            "missing_fields": ",".join(r.get("data_quality", {}).get("missing_fields", [])),
        }
        flat_data.append(flat)
    
    csv_path = EXTRACTED_DIR / f"financial_metrics_{timestamp}.csv"
    df = pd.DataFrame(flat_data)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"💾 CSV 已保存: {csv_path}")
    
    # 3. 生成数据质量报告
    quality_report = {
        "extraction_time": datetime.now().isoformat(),
        "total_companies": len(TARGET_COMPANIES),
        "successful": len(results),
        "failed": len(TARGET_COMPANIES) - len(results),
        "success_rate": round(len(results) / len(TARGET_COMPANIES) * 100, 1),
        "missing_depreciation_count": sum(1 for r in results if not r.get("data_quality", {}).get("has_depreciation")),
        "missing_capex_count": sum(1 for r in results if not r.get("data_quality", {}).get("has_capex")),
    }
    
    report_path = EXTRACTED_DIR / f"quality_report_{timestamp}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2, ensure_ascii=False)
    print(f"📊 质量报告: {report_path}")
    
    return json_path, csv_path, report_path

# ========== 主程序 ==========

def main():
    print("=" * 70)
    print("🚀 双轨财报数据提取器 v2.0")
    print("   目标: 27家AI产业链公司")
    print("   输出: JSON + CSV + 质量报告")
    print("=" * 70)
    
    # 轨道A：批量提取财务指标
    print("\n【轨道A】yfinance 财务指标提取")
    results = batch_extract(TARGET_COMPANIES, delay=1.5)
    
    if not results:
        print("❌ 所有公司提取失败，请检查网络连接")
        return
    
    # 保存结果
    json_path, csv_path, report_path = save_results(results)
    
    # 打印摘要
    print("\n" + "=" * 70)
    print("📋 提取摘要")
    print("=" * 70)
    
    df = pd.read_csv(csv_path)
    print(f"\n公司列表 ({len(df)} 家):")
    print(df[["ticker", "company_name", "fiscal_year", "fiscal_year_end", "industry_layer"]].to_string(index=False))
    
    print(f"\n关键指标概览:")
    summary_cols = ["ticker", "revenue_millions", "capex_millions", "depreciation_millions", "capex_to_revenue"]
    print(df[summary_cols].to_string(index=False))
    
    print(f"\n💡 下一步建议:")
    print(f"   1. 用 Excel 打开: {csv_path}")
    print(f"   2. 对 'depreciation_millions' 为空的行，手动查找补全")
    print(f"   3. 基于完整数据，开始5维度风险评分")
    print("=" * 70)

if __name__ == "__main__":
    main()
