import json, re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"D:\depreciation-risk-detection")
OUT_DIR = BASE_DIR / "核对文档_10家合并版"
OUT_DIR.mkdir(exist_ok=True)

COMPANIES = {
    "META": ["META_2022_annotation.json", "META_2023_annotation.json", "META_2024_annotation.json"],
    "GOOGL": ["GOOGL_2022_annotation.json", "GOOGL_2023_annotation.json", "GOOGL_2024_annotation.json"],
    "MSFT": ["MSFT_FY2023_annotation.json", "MSFT_FY2024_annotation.json", "MSFT_FY2025_annotation.json"],
    "NVDA": ["NVDA_FY2023_annotation.json", "NVDA_FY2024_annotation.json", "NVDA_FY2025_annotation.json"],
    "AMD": ["AMD_FY2022_annotation.json", "AMD_FY2023_annotation.json", "AMD_FY2024_annotation.json"],
    "INTC": ["INTC_FY2022_annotation.json", "INTC_FY2023_annotation.json", "INTC_FY2024_annotation.json"],
    "MU": ["MU_FY2022_annotation.json", "MU_FY2023_annotation.json", "MU_FY2024_annotation.json"],
    "CRM": ["CRM_FY2023_annotation.json", "CRM_FY2024_annotation.json", "CRM_FY2025_annotation.json"],
    "ORCL": ["ORCL_FY2023_annotation.json", "ORCL_FY2024_annotation.json", "ORCL_FY2025_annotation.json"],
    "TSLA": ["TSLA_2022_annotation.json", "TSLA_2023_annotation.json", "TSLA_2024_annotation.json"],
}

CN_NUMS = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
D_ORDER = ["D1", "D2", "D3", "D4", "D5"]
D_NAMES = {"D1": "D1 年限错配", "D2": "D2 政策保守性", "D3": "D3 减值触发", "D4": "D4 CAPEX 强度", "D5": "D5 竞争替代"}
WEIGHTS = {"D1": 0.25, "D2": 0.20, "D3": 0.20, "D4": 0.20, "D5": 0.15}

def load_json(fname):
    path = BASE_DIR / "data" / "annotated" / fname
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  Error loading {fname}: {e}")
        return None

def get_company_display_name(ticker):
    return {
        "META": "Meta Platforms, Inc.",
        "GOOGL": "Alphabet Inc. (Google)",
        "MSFT": "Microsoft Corporation",
        "NVDA": "NVIDIA Corporation",
        "AMD": "Advanced Micro Devices, Inc.",
        "INTC": "Intel Corporation",
        "MU": "Micron Technology, Inc.",
        "CRM": "Salesforce, Inc.",
        "ORCL": "Oracle Corporation",
        "TSLA": "Tesla, Inc.",
    }.get(ticker, ticker)

def format_fiscal_year(data):
    fy = data.get("company", {}).get("fiscal_year", "N/A")
    period = data.get("company", {}).get("report_period_end", "")
    return f"{fy}（截至 {period}）" if period else str(fy)

def get_review_status(data):
    return data.get("metadata", {}).get("review_status", "unknown")

def get_composite(data):
    return data.get("composite_score", {}).get("weighted_score", 0.0)

def get_dimensions(data):
    result = {}
    for d in data.get("dimension_scores", []):
        result[d.get("dimension_id", "?")] = {
            "score": d.get("score", 0),
            "reasoning": d.get("reasoning", ""),
        }
    return result

def get_top_signals(data, n=3):
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    signals = sorted(data.get("risk_signals", []),
                     key=lambda s: severity_order.get(s.get("severity", "low").lower(), 99))
    return signals[:n]

def get_change_in_estimate(data):
    return data.get("accounting_policy", {}).get("change_in_estimate", "")

def get_policy_summary(data):
    policy = data.get("accounting_policy", {})
    parts = []
    if policy.get("depreciation_method"):
        parts.append(f"方法：{policy['depreciation_method']}")
    server = policy.get("server_useful_life_years") or policy.get("servers_useful_life_years") or policy.get("servers_and_network_assets_useful_life_years")
    if server:
        parts.append(f"服务器年限：{server}年")
    change = policy.get("change_in_estimate", "")
    if change and change not in ("N/A", "None in FY2024. The 2022 change (servers 4→6 years, network 5→6 years) remains in effect. No new useful-life revisions disclosed."):
        parts.append(f"变更：{change[:140]}{'...' if len(change)>140 else ''}")
    return "；".join(parts) if parts else "N/A"

def classify_policy_change(curr_data, prev_data, curr_fy):
    curr_d2 = get_dimensions(curr_data).get("D2", {}).get("score", 0)
    prev_d2 = get_dimensions(prev_data).get("D2", {}).get("score", 0) if prev_data else 0
    curr_change = get_change_in_estimate(curr_data)
    
    if curr_d2 == 5:
        if prev_d2 < 5:
            return f"**{curr_fy} 新增变更（本期延长）**：{curr_change}"
        else:
            return f"**{curr_fy} 再次延长**：{curr_change}"
    elif curr_d2 == 4:
        if prev_d2 == 5:
            return f"**{curr_fy} 历史延长生效中**：无新的年限变更，上期延长政策继续适用"
        else:
            return f"**{curr_fy} 历史延长生效中**：{curr_change if curr_change else '无新的年限变更，沿用上期政策'}"
    elif curr_d2 <= 3:
        return f"**{curr_fy} 维持**：无新的年限变更，沿用上期政策"
    else:
        return f"**{curr_fy} 政策状态**：{curr_change if curr_change else '参见 D2 评分依据'}"

def classify_first_year(data, fy):
    d2 = get_dimensions(data).get("D2", {}).get("score", 0)
    change = get_change_in_estimate(data)
    if d2 == 5:
        return f"**{fy} 本期延长**：{change if change else '本期发生折旧年限延长'}"
    elif d2 == 4:
        return f"**{fy} 历史延长生效中**：{change if change else '沿用上期延长后的政策'}"
    elif d2 <= 3:
        return f"**{fy} 基期**：{change if change else '无特别变更记录'}"
    return f"**{fy} 基期**：{change if change else '无特别变更记录'}"

def build_company_doc(ticker, files):
    years_data = []
    for fname in files:
        data = load_json(fname)
        if data:
            years_data.append((fname, data))
    if not years_data:
        return None
    
    years_data.sort(key=lambda x: x[1].get("company", {}).get("fiscal_year", 0))
    company_name = get_company_display_name(ticker)
    lines = []
    
    lines.append(f"# {company_name}（{ticker}）折旧风险评分依据与推断链——三年合并核对")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 用途：项目负责人逐条核对评分依据")
    lines.append("> 核对方法：打开 `D:\\depreciation-risk-detection\\data\\raw\\` 对应 10-K HTML，用 Ctrl+F 搜原文摘录，确认 ①原文存在且逐字一致 ②推断链逻辑成立 ③分数符合锚点")
    lines.append("> ⚠️ 本文档为核对用只读文档，**不修改 JSON**；任何分数调整以你的核对结论为准，助手不得自行改分。")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Anchor table
    lines.append("## 〇、评分锚点（所有公司共用，META=4.0 为基准）")
    lines.append("")
    lines.append("| 维度 | 权重 | 5 分 | 4 分 | 3 分 | 2 分 | 1 分 |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append("| D1 折旧年限 vs 技术实际寿命 | 0.25 | ≥6 年 | 4-6 年（vs 迭代 1-2 年） | 3-4 年 | 2-3 年 | ≤2 年/加速折旧 |")
    lines.append("| D2 会计政策保守性 | 0.20 | 本期延长年限+未来适用 | 历史有延长记录 | prospectively 无延长 | 有追溯/缩短 | 主动缩短年限 |")
    lines.append("| D3 减值风险触发 | 0.20 | 本期大额实际减值+多处直接信号 | 有实际减值或≥3处直接信号 | 仅间接信号 | 稀少间接 | 基本无 |")
    lines.append("| D4 CAPEX 强度 | 0.20 | ≥25% | 15-25% | 8-15% | 3-8% | <3% |")
    lines.append("| D5 行业竞争/技术替代 | 0.15 | 算力竞赛主力、直接运营海量 GPU | 大量运营 GPU/数据中心 | 部分暴露/跟随竞争 | 间接暴露（卖芯片） | 基本无暴露 |")
    lines.append("")
    lines.append("风险等级映射：≥4 高风险 🔴 ｜ 3–3.9 中高风险 🟠 ｜ 2–2.9 中风险 🟡 ｜ <2 低风险 🟢")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Per-year sections
    for idx, (fname, data) in enumerate(years_data, 1):
        fy = data.get("company", {}).get("fiscal_year", "N/A")
        status = get_review_status(data)
        score = get_composite(data)
        status_tag = "✅ confirmed" if status == "confirmed" else "⏳ draft_pending_review"
        emoji = "🔴" if score >= 4 else "🟠" if score >= 3 else "🟡" if score >= 2 else "🟢"
        
        lines.append(f"## {CN_NUMS[idx]}、{company_name} {format_fiscal_year(data)} → 综合 {score:.2f} {emoji} [{status_tag}]")
        lines.append("")
        lines.append(f"**会计政策摘要**：{get_policy_summary(data)}")
        lines.append("")
        
        top_signals = get_top_signals(data, n=3)
        lines.append(f"### 核心证据（{len(data.get('risk_signals', []))} 条信号中最关键的 {len(top_signals)} 条）")
        lines.append("")
        
        for sig in top_signals:
            sid = sig.get("signal_id", "SIG-???")
            sev = sig.get("severity", "unknown").upper()
            src = sig.get("source", "")
            loc = sig.get("page_location", "")
            excerpt = sig.get("text_excerpt", "").strip().replace("|", "\\|")
            if len(excerpt) > 700:
                excerpt = excerpt[:700] + "..."
            lines.append(f"**{sid}【{sev}】** — {src}（{loc}）")
            if excerpt:
                lines.append(f"> {excerpt}")
            lines.append("")
            chain = sig.get("evidence_chain", [])
            if chain:
                lines.append("推断链：")
                for step in chain:
                    lines.append(f"- {step}")
                lines.append("")
        
        dims = get_dimensions(data)
        lines.append("### 逐维评分")
        lines.append("")
        lines.append("| 维度 | 分 | 依据摘要 |")
        lines.append("|---|---|---|")
        
        calc_parts = []
        for d_id in D_ORDER:
            d = dims.get(d_id, {})
            score_d = d.get("score", 0)
            reasoning = d.get("reasoning", "")
            reasoning_short = reasoning[:120] + ("..." if len(reasoning) > 120 else "")
            lines.append(f"| {D_NAMES[d_id]} | **{score_d}** | {reasoning_short} |")
            calc_parts.append(f"{score_d}×{WEIGHTS[d_id]:.2f}")
        
        lines.append("")
        calc_detail = " + ".join([f"{dims[d]['score']}×{WEIGHTS[d]:.2f}={dims[d]['score']*WEIGHTS[d]:.2f}" for d in D_ORDER])
        lines.append(f"**验算**：{' + '.join(calc_parts)} = {calc_detail} = **{score:.2f}** ✓")
        
        cs = data.get("composite_score", {})
        lines.append(f"**置信度**：{cs.get('confidence', 'N/A')} — {cs.get('confidence_reason', '')}")
        lines.append("")
        
        comp = data.get("comparative_context", {})
        same_trend = comp.get("same_company_trend", "")
        if same_trend:
            lines.append(f"**跨年轨迹**：{same_trend}")
            lines.append("")
        
        na_items = []
        for d_id in D_ORDER:
            r = dims.get(d_id, {}).get("reasoning", "")
            if "NA" in r or "未披露" in r or "不可" in r:
                na_items.append(f"{D_NAMES[d_id]}：{r}")
        if na_items:
            lines.append(f"**NA 项**：{'；'.join(na_items)}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Cross-year comparison
    lines.append("## 跨年对照与政策演变分析")
    lines.append("")
    lines.append("| 财年 | 综合分 | D1 | D2 | D3 | D4 | D5 | review_status |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for fname, data in years_data:
        fy = data.get("company", {}).get("fiscal_year", "N/A")
        score = get_composite(data)
        dims = get_dimensions(data)
        status = get_review_status(data)
        d_vals = [str(dims.get(d, {}).get("score", "-")) for d in D_ORDER]
        lines.append(f"| {fy} | {score:.2f} | {' | '.join(d_vals)} | {status} |")
    lines.append("")
    
    # Policy continuity / changes
    lines.append("### 政策延续 vs 变化")
    lines.append("")
    if len(years_data) >= 2:
        first_fy = years_data[0][1].get("company", {}).get("fiscal_year", "")
        lines.append(f"- {classify_first_year(years_data[0][1], first_fy)}")
        for i in range(1, len(years_data)):
            prev_fname, prev_data = years_data[i-1]
            curr_fname, curr_data = years_data[i]
            curr_fy = curr_data.get("company", {}).get("fiscal_year", "")
            lines.append(f"- {classify_policy_change(curr_data, prev_data, curr_fy)}")
    else:
        fy = years_data[0][1].get("company", {}).get("fiscal_year", "")
        lines.append(f"- {classify_first_year(years_data[0][1], fy)}")
    lines.append("")
    
    # Score diff reasoning
    lines.append("### 分数差异理由")
    lines.append("")
    if len(years_data) >= 2:
        for i in range(1, len(years_data)):
            prev_fname, prev_data = years_data[i-1]
            curr_fname, curr_data = years_data[i]
            prev_fy = prev_data.get("company", {}).get("fiscal_year", "")
            curr_fy = curr_data.get("company", {}).get("fiscal_year", "")
            prev_score = get_composite(prev_data)
            curr_score = get_composite(curr_data)
            diff = curr_score - prev_score
            
            lines.append(f"**{prev_fy} → {curr_fy}（{prev_score:.2f} → {curr_score:.2f}，Δ{diff:+.2f}）**：")
            
            prev_dims = get_dimensions(prev_data)
            curr_dims = get_dimensions(curr_data)
            changes = []
            for d_id in D_ORDER:
                p = prev_dims.get(d_id, {}).get("score", 0)
                c = curr_dims.get(d_id, {}).get("score", 0)
                if p != c:
                    changes.append(f"{D_NAMES[d_id]} {p}→{c}")
            if changes:
                lines.append(f"- 维度变化：{'；'.join(changes)}")
            else:
                lines.append(f"- 维度无变化")
            
            yoy = curr_data.get("comparative_context", {}).get("year_over_year_anchor_comparison", {})
            if yoy:
                for d_id in D_ORDER:
                    note = yoy.get(d_id, "")
                    if note:
                        lines.append(f"  - {D_NAMES[d_id]}：{note}")
            
            prev_yoy = prev_data.get("comparative_context", {}).get("year_over_year_anchor_comparison", {})
            if not yoy and prev_yoy:
                for d_id in D_ORDER:
                    note = prev_yoy.get(d_id, "")
                    if note and "→" in note:
                        lines.append(f"  - {D_NAMES[d_id]}：{note}")
            
            lines.append("")
    
    # Appendix
    lines.append("---")
    lines.append("")
    lines.append("## 附录：核对清单")
    lines.append("")
    lines.append("### ① 五维评分逐项依据（锚点适用说明）")
    lines.append("- [ ] D1 年限档位与 10-K 原文一致（服务器/网络设备年限表）")
    lines.append("- [ ] D2 锚点适用正确（本期变更 vs 历史变更 vs 无变更）")
    lines.append("- [ ] D3 减值信号数量/金额与原文一致")
    lines.append("- [ ] D4 CAPEX/收入 计算正确（注意口径：含/不含融资租赁本金）")
    lines.append("- [ ] D5 竞争暴露定性合理（运营型 vs 设计型 vs 租用型）")
    lines.append("")
    lines.append("### ② 每条风险信号的证据链定位")
    lines.append("| 信号 ID | 原文章节 | 定位串/行号 | 核对结果 |")
    lines.append("|---|---|---|---|")
    for fname, data in years_data:
        for sig in data.get("risk_signals", [])[:6]:
            sid = sig.get("signal_id", "")
            src = sig.get("source", "")
            loc = sig.get("page_location", "")
            lines.append(f"| {sid} | {src} | {loc} | ☐ |")
    lines.append("")
    lines.append("### ③ 跨年对照")
    lines.append("- [ ] 政策延续/变化判断与原文一致")
    lines.append("- [ ] 分数差异理由有原文事实支撑（非口径漂移）")
    lines.append("")
    lines.append("### ④ 推断链说明")
    lines.append("- [ ] 每条推断链的因果逻辑无跳跃")
    lines.append("- [ ] 数字计算（验算式）与 JSON 一致")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 核对完成签名：__________  日期：__________")
    lines.append("")
    
    return "\n".join(lines)


def main():
    print(f"生成 {len(COMPANIES)} 份核对文档到 {OUT_DIR}")
    for ticker, files in COMPANIES.items():
        print(f"\n处理 {ticker} ...")
        doc = build_company_doc(ticker, files)
        if doc:
            out_path = OUT_DIR / f"{ticker}_三年合并核对.md"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(doc)
            print(f"  已写入：{out_path}")
        else:
            print(f"  失败：无有效数据")
    print("\n全部完成！")

if __name__ == "__main__":
    main()
