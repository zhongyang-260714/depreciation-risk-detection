"""中文DeepSeek提示词 v4 — A股年报折旧风险标注（精简版）

v4改进：
- 移除锚点示例，减少Token消耗
- 精简自检要求，保留核心护栏
- D1护栏保留但压缩表述
- 评分标准和输出格式不变
"""

from .prompts import COMPANY_PROFILES


# ============================================================
# D1 资产类型护栏（中文精简版）
# ============================================================

D1_ASSET_TYPE_RUBRIC_CN = """
## D1 评分标准（按资产类型分表）

D1衡量**会计折旧年限**与**技术实际寿命**的错配程度。
**只评估固定资产折旧（房屋、机器设备、服务器）。无形资产摊销、商誉减值不计入D1。**

### 子表A：服务器/网络设备
- 技术基准：1.5年
- 5分：≥6年 | 4分：4-6年 | 3分：3-4年 | 2分：2-3年 | 1分：≤2年

### 子表B：晶圆厂/半导体制造设备
- 技术基准：3.5年
- 5分：≥10年 | 4分：7-10年 | 3分：5-7年 | 2分：3.5-5年 | 1分：≤3.5年

### 子表C：房屋建筑物/土地使用权
- **不计入D1**

### 子表D：无形资产/商誉/软件/专利权
- **不计入D1**。遇到"摊销"、"无形资产"、"商誉" → 明确声明不计入D1
"""


# ============================================================
# 系统提示词（精简版）
# ============================================================

CN_SYSTEM_PROMPT_V4 = """你是一名资深财务分析专家，专门分析中国A股上市公司的年报，识别折旧、摊销、减值、研发资本化等会计估计风险。

## 中国会计准则背景
- 固定资产折旧年限变更采用"未来适用法"，不追溯调整
- 研发支出可资本化也可费用化，资本化率过高是风险信号
- 无形资产摊销不计入D1评分
- 资产减值采用"可收回金额"vs"账面价值"孰低原则

## 五维度评分模型（5D-DRS）

| 维度 | 权重 | 1分(低) | 3分(中) | 5分(高) |
|------|------|---------|---------|---------|
| D1 固定资产折旧年限 vs 技术寿命 | 0.25 | ≤2年/加速折旧 | 3-4年 | ≥5年 |
| D2 会计政策保守性 | 0.20 | 主动缩短年限 | 无变更 | 本期延长+未来适用 |
| D3 减值/跌价触发 | 0.20 | 基本无减值 | 少量间接信号 | 大额减值+多处信号 |
| D4 资本开支/研发强度 | 0.20 | <3% | 8-15% | ≥25% |
| D5 技术替代/行业竞争 | 0.15 | 基本无暴露 | 部分暴露 | 极端技术替代压力 |

## D1 关键护栏
1. **只评估固定资产折旧**：房屋、机器设备、服务器
2. **无形资产摊销不计入D1**：遇到"摊销"、"无形资产"、"商誉" → 声明不计入D1
3. **房屋建筑物不计入D1**
4. **按资产类型选子表**：服务器基准1.5年，晶圆厂设备基准3.5年

## 评分原则
1. **保守评分**：证据不足时给低分，不要猜
2. **证据不足可放空**：某维度无证据时，score填null，insufficient_evidence填true
3. **避免平均化偏差**：五个维度不要全部集中在2.5-3.5分
4. **只基于候选段落分析**，禁止编造原文

## 输出格式
严格输出JSON。"""


# ============================================================
# 构建中文标注Prompt（精简版）
# ============================================================

def build_cn_annotation_prompt(candidates: list[dict], company_meta: dict) -> str:
    """构建中文标注提示词 v4（精简版）。"""
    ticker = company_meta.get("ticker", "UNKNOWN")
    year = company_meta.get("fiscal_year", 2024)
    industry = company_meta.get("industry", "Technology")
    
    # 获取公司档案（如有）
    profile = COMPANY_PROFILES.get(ticker.upper())
    if profile:
        profile_text = (
            f"\n## 公司档案\n"
            f"- 资产类型：{profile['asset_type_cn']}\n"
            f"- D4典型水平：{profile['d4_baseline']}\n"
            f"- D5典型水平：{profile['d5_baseline']}\n"
            f"- 主要风险通道：{profile['risk_channel']}\n"
            f"- D1评分护栏：{profile['d1_guardrail']}\n"
        )
    else:
        profile_text = "\n## 公司档案\n无特定档案，使用一般性假设。\n"
    
    prompt = f"""请分析以下中国A股公司年报候选段落，识别折旧/摊销/减值/研发资本化风险。

公司：{ticker}
年份：{year}年报
行业：{industry}
{profile_text}

{D1_ASSET_TYPE_RUBRIC_CN}

## 候选段落（共{len(candidates)}段）

"""
    for i, c in enumerate(candidates, 1):
        prompt += f"""--- 段落 {i} [强度: {c.get('signal_strength', 'unknown')}] ---
关键词：{c.get('keyword_matched', '')}
位置：{c.get('page_location', '')}
文本：
{c.get('text_excerpt', '')}

"""
    
    prompt += """
## 任务要求
1. 识别与**固定资产折旧**相关的风险信号（严格区分折旧vs摊销）
2. 为每个信号生成"原文—会计含义—推断链"证据链
3. 对五个维度进行1-5分评分，证据不足时score填null
4. 避免五个维度得分全部集中在2.5-3.5分（平均化偏差）
5. 只基于提供的候选段落分析，禁止编造原文

## 输出JSON格式
```json
{
  "risk_signals": [
    {
      "signal_id": "SIG-001",
      "risk_type": "折旧年限延长",
      "severity": "critical/high/medium/low",
      "text_excerpt": "原文摘录（逐字）",
      "page_location": "年报附注X，第XX页",
      "accounting_meaning": "该表述在CAS下的会计含义",
      "evidence_chain": ["事实", "与准则/技术的矛盾", "对利润的影响方向"],
      "keyword_matched": "命中的关键词"
    }
  ],
  "dimension_scores": [
    {"dimension_id": "D1", "dimension_name": "年限错配", "score": 3, "weight": 0.25, "insufficient_evidence": false, "reasoning": "...", "supporting_signals": ["SIG-001"]},
    {"dimension_id": "D2", "dimension_name": "政策保守性", "score": 4, "weight": 0.20, "insufficient_evidence": false, "reasoning": "...", "supporting_signals": []},
    {"dimension_id": "D3", "dimension_name": "减值触发", "score": 2, "weight": 0.20, "insufficient_evidence": false, "reasoning": "...", "supporting_signals": []},
    {"dimension_id": "D4", "dimension_name": "资本强度", "score": null, "weight": 0.20, "insufficient_evidence": true, "reasoning": "候选段落未提供CAPEX数据", "supporting_signals": []},
    {"dimension_id": "D5", "dimension_name": "技术替代", "score": 2, "weight": 0.15, "insufficient_evidence": false, "reasoning": "...", "supporting_signals": []}
  ],
  "accounting_policy": {
    "depreciation_method": "直线法",
    "useful_life_range": "年限范围",
    "rd_capitalization_rate": "研发资本化率",
    "impairment_policy": "减值政策简述"
  },
  "summary": "总体风险判断（2-3句）"
}
```

请输出JSON分析结果。如果某段落不包含实质性风险信号，可以忽略。
"""
    return prompt


CN_SYSTEM_PROMPT = CN_SYSTEM_PROMPT_V4
