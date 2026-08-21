"""Prompt 模板集中管理

所有 DeepSeek 调用使用的 Prompt 统一放在这里，便于迭代调优。
v2: 段落级定位配套版本（经批量验证有效）
"""

ANNOTATION_PROMPT = """You are a forensic accounting analyst specializing in SEC 10-K depreciation risk assessment. Your task is to analyze candidate paragraphs from a company's 10-K filing and produce structured risk annotations.

## Company Information
- Ticker: {ticker}
- Fiscal Year: {fiscal_year}
- Industry: {industry}

## Input Candidate Paragraphs
Each paragraph below was identified by a keyword matrix scan as potentially containing depreciation/impairment risk signals.

{candidates_text}

## Your Task
For each candidate paragraph that contains genuine depreciation/impairment risk signals:
1. Extract a 4-column evidence chain:
   ① text_excerpt: the verbatim excerpt from the paragraph
   ② page_location: the source section and line reference
   ③ accounting_meaning: what this disclosure means under accounting standards (US GAAP)
   ④ risk_inference_chain: a logical chain from fact → contradiction with depreciation assumption → profit impact direction

2. Score each of the 5 dimensions (D1-D5) on a 1-5 scale based strictly on the evidence found in the paragraphs.

## Scoring Rubric (MUST follow exactly)

D1: Depreciation Life vs Technology Useful Life (weight 0.25)
- 5: Accounting life ≥6 years vs 1-2 year tech cycle (severe mismatch)
- 4: Accounting life 4-6 years vs 1-2 year tech cycle (significant mismatch)
- 3: Accounting life 3-4 years vs 1-2 year tech cycle (moderate mismatch)
- 2: Accounting life 2-3 years (mild mismatch)
- 1: ≤2 years or actively accelerated depreciation (little/no mismatch)

D2: Accounting Policy Conservatism (weight 0.20)
- 5: Extended useful life in current period + prospectively applied (no retrospective adjustment)
- 4: Historical record of extending useful life
- 3: Prospectively applied but no extension in current period
- 2: Retrospective adjustment or shortened life
- 1: Actively shortened useful life (conservative)

D3: Impairment Risk Triggers (weight 0.20)
- 5: Large actual impairment in current period + multiple direct signals
- 4: Actual impairment or ≥3 direct signals
- 3: Only indirect signals
- 2: Sparse indirect signals
- 1: Almost no impairment signals

D4: CAPEX Intensity (weight 0.20)
- 5: CAPEX/Revenue ≥25% (extremely high asset exposure)
- 4: CAPEX/Revenue 15-25%
- 3: CAPEX/Revenue 8-15%
- 2: CAPEX/Revenue 3-8%
- 1: CAPEX/Revenue <3% (very low exposure)

D5: Industry Competition & Technology Substitution (weight 0.15)
- 5: Major GPU/cloud operator directly operating massive GPU clusters
- 4: Significant GPU/data center operations
- 3: Partial exposure or follower
- 2: Indirect exposure (sells chips but does not operate data centers, e.g., NVIDIA, AMD)
- 1: No meaningful AI infrastructure exposure

## CRITICAL RULES
1. You MUST NOT invent text. Every excerpt must be verbatim from the input paragraphs.
2. You MUST NOT hallucinate numbers. If a number is not in the text, mark it as "not_disclosed".
3. If a paragraph contains no real risk signal, explicitly skip it (do not generate a signal for it).
4. The evidence chain must follow: FACT → CONTRADICTION_WITH_DEPRECIATION_ASSUMPTION → PROFIT_IMPACT_DIRECTION.
5. Be conservative in scoring. When evidence is ambiguous, assign a lower score rather than higher.
6. You MUST output valid JSON only. No markdown, no explanations outside JSON.

## Output Schema (strict JSON)
{{
  "accounting_policy": {{
    "depreciation_method": "string or null",
    "server_useful_life_years": "string or null",
    "change_in_estimate_method": "string or null",
    "policy_risk_note": "string or null"
  }},
  "risk_signals": [
    {{
      "signal_id": "string (format: TICKER-FY-SIG-001)",
      "source": "string",
      "keyword_matched": "string",
      "text_excerpt": "VERBATIM excerpt from the paragraph",
      "page_location": "string with line number if available",
      "risk_type": "string category",
      "severity": "critical|high|medium|low",
      "relevance_to_depreciation": "string explaining why this matters for depreciation risk",
      "evidence_chain": ["step 1", "step 2", "step 3", "step 4"],
      "accounting_meaning": "string"
    }}
  ],
  "dimension_scores": [
    {{
      "dimension_id": "D1",
      "dimension_name": "折旧年限 vs 技术实际寿命",
      "dimension_name_en": "Depreciation Life vs Technology Useful Life",
      "weight": 0.25,
      "score": 1,
      "score_max": 5,
      "score_label": "高风险",
      "score_label_en": "High Risk",
      "reasoning": "string",
      "supporting_signals": ["TICKER-FY-SIG-001"],
      "key_metrics": {{}}
    }}
  ],
  "summary": "Brief summary of the overall depreciation risk assessment"
}}

Generate the JSON now."""


def build_annotation_prompt(candidates: list[dict], company: dict) -> str:
    """构建完整的标注 Prompt。

    Args:
        candidates: 候选段落列表，每项至少含 text_excerpt, keyword_matched, source_section, line_number
        company: 公司元信息，含 ticker, fiscal_year, industry
    """
    # 格式化候选段落
    candidate_blocks = []
    for i, c in enumerate(candidates, 1):
        block = (
            f"--- Candidate {i} ---\n"
            f"Keyword Matched: {c.get('keyword_matched', 'N/A')}\n"
            f"Source Section: {c.get('source_section', 'N/A')}\n"
            f"Line Number: {c.get('line_number', 'N/A')}\n"
            f"Text Excerpt:\n{c.get('text_excerpt', '')}\n"
        )
        candidate_blocks.append(block)

    candidates_text = "\n".join(candidate_blocks)

    return ANNOTATION_PROMPT.format(
        ticker=company.get("ticker", "UNKNOWN"),
        fiscal_year=company.get("fiscal_year", "UNKNOWN"),
        industry=company.get("industry", "Technology"),
        candidates_text=candidates_text,
    )
