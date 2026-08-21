"""Prompt 模板集中管理 v3-enhanced

增强版：增加详细评分锚点和跨年对比指导，帮助AI更准确地评分。
"""

COMPANY_PROFILES = {
    "META": {"d1_guardrail": "Server depreciation life PRIMARY focus. 2022:4y→2023:5y→2024:5.5y (SECOND extension)", "typical": "4.00-4.60", "d2_note": "Repeated extensions (2022+2024) = highest conservatism risk"},
    "MSFT": {"d1_guardrail": "Server depreciation life PRIMARY focus. 2022:4y→6y (one-time, still in force)", "typical": "4.20-4.40", "d2_note": "FY2025 removed change narrative - opacity risk"},
    "GOOGL": {"d1_guardrail": "Server depreciation life PRIMARY focus. 2022:4y→6y (one-time)", "typical": "4.20-4.25", "d2_note": "Similar to MSFT but quantified $3.9B impact"},
    "ORCL": {"d1_guardrail": "Server depreciation PRIMARY. 2023 Q1:4→5y, 2025 Q1:5→6y (SECOND extension)", "typical": "3.60-4.45", "d2_note": "Two extensions in 3 years, timing with 3x capex surge"},
    "INTC": {"d1_guardrail": "Wafer fab baseline 3.5y (NOT 1.5y server baseline).", "typical": "3.90-4.55", "d2_note": "IDM manufacturing, not cloud"},
    "MU": {"d1_guardrail": "Memory fab baseline ~3.5y. Production equipment 7y fixed.", "typical": "4.00-4.20", "d2_note": "No life changes but inventory/goodwill volatility high"},
    "NVDA": {"d1_guardrail": "FIXED ASSET minimal. Watch INVENTORY. D4 MUST be 1-2.", "typical": "2.85-3.45", "d2_note": "Fabless, but FY2023 extended server 3→4-5y, test 5→7y"},
    "AMD": {"d1_guardrail": "Amortization of intangibles does NOT count toward D1. D1=PP&E only.", "typical": "2.40-2.60", "d2_note": "Fabless, asset-light"},
    "CRM": {"d1_guardrail": "Very low fixed asset base.", "typical": "2.10", "d2_note": "SaaS model"},
    "TSLA": {"d1_guardrail": "Auto equipment ~5-7y baseline AND AI hardware ~1.5-2y.", "typical": "3.20-3.75", "d2_note": "Dual asset structure"},
}

D1_RUBRIC = """D1 Scoring by Asset Type (ONLY PP&E counts):

[A] Servers/Network/Datacenter: baseline 1.5y
  5: >=6y | 4: 4-6y | 3: 3-4y | 2: 2-3y | 1: <=2y
[B] Wafer Fab/Manufacturing: baseline 3.5y
  5: >=10y | 4: 7-10y | 3: 5-7y | 2: 3.5-5y | 1: <=3.5y
[C] General Equipment/Software: baseline 2-4y
  5: >=7y | 4: 5-7y | 3: 3-5y | 2: 2-3y | 1: <=2y

RULES: Use NEW extended life. For RANGE, use UPPER BOUND.
"""

D2_RUBRIC = """D2 Accounting Policy Conservatism (w=0.20):

Scoring:
  5: Extended life THIS YEAR + prospectively applied
  4: Historical extension, no change THIS YEAR
  3: No extension ever / neutral policy
  2: Retrospective adjustment used
  1: Shortened useful life

BONUS: Extended TWICE in 3 years → D2=5 regardless of current year.
"""

D3_RUBRIC = """D3 Impairment Risk Triggers (w=0.20):

Scoring:
  5: PP&E impairment >=$100M THIS YEAR
  4: Historical impairment + multiple direct signals / >$1B inventory write-down
  3: Indirect signals only / zero impairment 3+ years
  2: Sparse signals
  1: No signals

NOTE: For fabless (NVDA, AMD), inventory provisions ARE primary obsolescence channel.
"""

D4_RUBRIC = """D4 CAPEX Intensity (w=0.20):

Calculate: CAPEX / Total Revenue * 100%

Scoring:
  5: >=25% | 4: 15-25% | 3: 8-15% | 2: 3-8% | 1: <3%

NOTE: Fabless companies naturally LOW. Include finance leases.
"""

D5_RUBRIC = """D5 Technology Substitution/Competition (w=0.15):

Scoring:
  5: Operates GPU/AI infra + annual tech cycle
  4: Cloud/AI infra OR manufacturing node pressure
  3: Fabless but high tech iteration
  2: Sells chips only
  1: Software/services minimal hardware

KEY SIGNALS: "rapidly evolving technology", "excess and obsolescence risk"
"""

SCORING_RUBRIC = f"""{D1_RUBRIC}

{D2_RUBRIC}

{D3_RUBRIC}

{D4_RUBRIC}

{D5_RUBRIC}
"""

CRITICAL_RULES = """RULES:
1. NO invented text. Every excerpt must be verbatim from the input.
2. NO hallucinated numbers. Mark missing as "not_disclosed".
3. Skip paragraphs with no real risk signal.
4. Evidence chain: FACT->CONTRADICTION->PROFIT_IMPACT.
5. Conservative scoring. When ambiguous, use LOWER score.
6. D1: select correct asset-type. Buildings/land/intangibles/amortization EXCLUDED.
7. Insufficient evidence: score=null, insufficient_evidence=true.
8. Output valid JSON ONLY. No markdown.
9. FINANCIAL DATA: Extract specific numbers (revenue, capex, depreciation, impairment) with dollar amounts.
10. YEAR-OVER-YEAR: If data shows trends (e.g., depreciation $5.3B→$7.3B→$11.3B), note the acceleration.
11. CROSS-CHECK: D1 and D2 should be consistent. If D1=5 (very long life), D2 should be >=4.
"""

OUTPUT_SCHEMA = """OUTPUT JSON:
{
  "accounting_policy": {"depreciation_method":null,"server_useful_life_years":null,"change_in_estimate_method":null,"policy_risk_note":null},
  "risk_signals": [{"signal_id":"TICKER-FY-SIG-001","source":"","keyword_matched":"","text_excerpt":"VERBATIM","page_location":"","risk_type":"","severity":"high","evidence_chain":["","",""],"accounting_meaning":""}],
  "dimension_scores": [{"dimension_id":"D1","dimension_name":"Depreciation Life vs Technology Useful Life","weight":0.25,"score":1,"score_max":5,"score_label":"High Risk","reasoning":"","supporting_signals":[""],"insufficient_evidence":false}],
  "summary": ""
}"""

ANNOTATION_PROMPT = """You are a forensic accounting analyst. Analyze candidate paragraphs from a 10-K filing and produce structured risk annotations.

Company: {ticker} | FY: {fiscal_year} | Industry: {industry}

Profile: {company_profile}

{scoring_rubric}

{critical_rules}

{output_schema}

Candidates to analyze:
{candidates_text}

Generate JSON now."""


def _format_company_profile(ticker: str) -> str:
    p = COMPANY_PROFILES.get(ticker.upper())
    if not p:
        return "General tech company."
    return f"D1: {p['d1_guardrail']} | D2: {p['d2_note']} | Typical: {p['typical']}"


def build_annotation_prompt(candidates: list[dict], company: dict) -> str:
    """构建增强版标注 Prompt。"""
    blocks = []
    for i, c in enumerate(candidates, 1):
        excerpt = c.get('text_excerpt', '')
        # 截断过长文本，保留前1000字符（增加以包含更多表格数据）
        if len(excerpt) > 1000:
            excerpt = excerpt[:1000] + "...[truncated]"
        blocks.append(
            f"[{i}] {c.get('keyword_matched','')} | {c.get('source_section','')} | tier={c.get('keyword_tier','')}:\n{excerpt}\n"
        )
    return ANNOTATION_PROMPT.format(
        ticker=company.get("ticker", "UNKNOWN"),
        fiscal_year=company.get("fiscal_year", "UNKNOWN"),
        industry=company.get("industry", "Technology"),
        company_profile=_format_company_profile(company.get("ticker", "")),
        scoring_rubric=SCORING_RUBRIC,
        critical_rules=CRITICAL_RULES,
        output_schema=OUTPUT_SCHEMA,
        candidates_text="\n".join(blocks),
    )
