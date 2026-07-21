"""科创企业资产折旧风险识别系统 · Streamlit 演示界面

比赛答辩用 Web Demo：
- 「单公司分析」：手工输入财务指标（+可选年报文本），计算折旧风险评分
- 「案例库」：展示团队已完成的 5 家美国科技公司 10-K 人工标注结果
  （读取 data/annotated/*.json，无需联网、无需模型，开箱即演）

运行方式（在仓库根目录）：
    streamlit run src/dashboard/app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 让 src/ 下的 features、nlp 包可以被导入（app.py 位于 src/dashboard/ 下）
SRC_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# matplotlib 中文字体（Windows 优先黑体/雅黑）
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# ----------------------------------------------------------------------------
# 1. 页面配置（必须是第一个 st.* 调用）
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="科创企业资产折旧风险识别系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# 2. 全局样式：低饱和、暖色调、大留白、清晰层级
# ----------------------------------------------------------------------------
PRIMARY = "#17705C"      # 主色：低饱和深青
BG_WARM = "#FAF8F5"      # 暖白背景
INK = "#2B2B28"          # 正文墨色
MUTED = "#8A877F"        # 次要文字
RISK_COLORS = {"high": "#B3402F", "medium": "#C07A1B", "low": "#2E7D5B"}

st.markdown(
    f"""
<style>
    /* 页面背景与顶部留白 */
    .stApp {{ background-color: {BG_WARM}; }}
    .block-container {{ padding-top: 2.2rem; max-width: 1180px; }}

    /* 顶部 Hero 区 */
    .hero {{
        background: #FFFFFF;
        border: 1px solid #E8E4DD;
        border-left: 6px solid {PRIMARY};
        border-radius: 12px;
        padding: 1.6rem 2rem 1.4rem 2rem;
        margin-bottom: 1.4rem;
    }}
    .hero h1 {{ margin: 0; font-size: 1.9rem; color: {INK}; letter-spacing: 0.5px; }}
    .hero .subtitle {{ color: {MUTED}; margin-top: 0.35rem; font-size: 0.98rem; }}
    .chips {{ margin-top: 0.8rem; }}
    .chip {{
        display: inline-block; font-size: 0.78rem; color: {PRIMARY};
        background: #EEF5F2; border: 1px solid #D5E5DF;
        border-radius: 999px; padding: 0.15rem 0.75rem; margin-right: 0.45rem;
    }}
    .chip.gray {{ color: {MUTED}; background: #F4F2EE; border-color: #E6E2DA; }}

    /* 卡片 */
    .card {{
        background: #FFFFFF; border: 1px solid #E8E4DD; border-radius: 12px;
        padding: 1.1rem 1.25rem; height: 100%;
    }}
    .card h4 {{ margin: 0 0 0.4rem 0; color: {INK}; font-size: 1.02rem; }}
    .card p {{ margin: 0; color: {MUTED}; font-size: 0.9rem; line-height: 1.55; }}

    /* 风险等级徽章 */
    .risk-badge {{
        display: inline-block; font-weight: 700; font-size: 1.05rem;
        border-radius: 8px; padding: 0.35rem 0.9rem; color: #FFFFFF;
    }}
    .risk-high   {{ background: {RISK_COLORS['high']}; }}
    .risk-medium {{ background: {RISK_COLORS['medium']}; }}
    .risk-low    {{ background: {RISK_COLORS['low']}; }}

    /* 评分大数字 */
    .big-score {{ font-size: 2.6rem; font-weight: 800; color: {INK}; line-height: 1.1; }}
    .big-score small {{ font-size: 1rem; color: {MUTED}; font-weight: 500; }}

    /* 小节标题 */
    .section-title {{
        font-size: 1.15rem; font-weight: 700; color: {INK};
        margin: 0.4rem 0 0.8rem 0; padding-left: 0.6rem;
        border-left: 4px solid {PRIMARY};
    }}

    /* 引用块 */
    .quote {{
        background: #F4F2EE; border-left: 4px solid #C9C2B4; border-radius: 6px;
        padding: 0.85rem 1.1rem; color: {INK}; font-size: 0.95rem; line-height: 1.7;
    }}

    /* 页脚 */
    .footer {{ color: {MUTED}; font-size: 0.8rem; text-align: center; margin-top: 2.5rem; }}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# 3. 案例库数据加载（兼容两种标注 JSON 格式）
# ----------------------------------------------------------------------------
ANNOTATED_DIR = REPO_ROOT / "data" / "annotated"

# 英文风险等级 -> 中文 + 颜色
LEVEL_MAP = {
    "HIGH": ("高风险", RISK_COLORS["high"]),
    "MEDIUM-HIGH": ("中高风险", RISK_COLORS["medium"]),
    "MEDIUM": ("中风险", RISK_COLORS["medium"]),
    "LOW": ("低风险", RISK_COLORS["low"]),
}


def _normalize_case(raw: dict, fallback_ticker: str) -> dict:
    """把两种标注格式统一成同一种结构，界面只认这个结构。"""
    # 格式 A：嵌套式（NVDA / AMD / META / GOOGL）
    if "composite_score" in raw:
        comp = raw["composite_score"]
        company = raw.get("company", {})
        dims = [
            {
                "name": d.get("dimension_name", d.get("dimension_id", "")),
                "score": d.get("score", 0),
                "max": d.get("score_max", 5),
                "label": d.get("score_label", ""),
                "reasoning": d.get("reasoning", ""),
            }
            for d in raw.get("dimension_scores", [])
        ]
        signals = [
            {
                "id": s.get("signal_id", ""),
                "source": s.get("source", ""),
                "excerpt": s.get("text_excerpt", ""),
                "note": s.get("note") or s.get("annotation_note") or "",
            }
            for s in raw.get("risk_signals", [])
        ]
        return {
            "ticker": company.get("ticker", fallback_ticker),
            "name": company.get("name", ""),
            "fiscal_year": company.get("fiscal_year", ""),
            "score": comp.get("weighted_score", 0),
            "level": comp.get("risk_level", ""),
            "color": comp.get("risk_level_color", RISK_COLORS["medium"]),
            "summary": raw.get("summary") or comp.get("confidence_reason", ""),
            "dimensions": dims,
            "signals": signals,
        }

    # 格式 B：平铺式（MSFT）
    level_cn, color = LEVEL_MAP.get(
        str(raw.get("risk_level", "")).upper(), ("中风险", RISK_COLORS["medium"])
    )
    dims = []
    signals = []
    for key, d in raw.get("dimensions", {}).items():
        pretty = key.split("_", 1)[-1].replace("_", " ").title()
        dims.append(
            {
                "name": pretty,
                "score": d.get("score", 0),
                "max": 5,
                "label": "",
                "reasoning": "；".join(d.get("risk_indicators", [])[:2]),
            }
        )
        for ev in d.get("evidence", []):
            signals.append(
                {
                    "id": f"{pretty} · {ev.get('significance', '')}",
                    "source": ev.get("location", ""),
                    "excerpt": ev.get("text", ""),
                    "note": ev.get("note", ""),
                }
            )
    # 优先展示 significance 高的证据
    signals.sort(key=lambda s: 0 if "critical" in s["id"].lower() else 1)
    return {
        "ticker": raw.get("ticker", fallback_ticker),
        "name": raw.get("company", ""),
        "fiscal_year": raw.get("fiscal_year", ""),
        "score": raw.get("overall_risk_score", 0),
        "level": level_cn,
        "color": color,
        "summary": raw.get("summary", ""),
        "dimensions": dims,
        "signals": signals[:8],
    }


@st.cache_data(show_spinner=False)  # 缓存：只在第一次读取 JSON，之后切页面不重读
def load_case_library() -> list:
    """读取 data/annotated/ 下全部标注 JSON，返回统一格式的案例列表。

    防护规则：
    1. 文件名含 backup / draft / old 的视为草稿备份，自动跳过
    2. 按（公司 + 财年）去重，同一家公司只保留评分最高的一份
    """
    # 文件名里的草稿/备份关键词（不区分大小写）
    SKIP_KEYWORDS = ("backup", "draft", "old")

    cases = []
    if not ANNOTATED_DIR.exists():
        return cases
    for path in sorted(ANNOTATED_DIR.glob("*.json")):
        if any(kw in path.stem.lower() for kw in SKIP_KEYWORDS):
            continue  # 跳过草稿备份
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            cases.append(_normalize_case(raw, path.stem.split("_")[0]))
        except Exception:
            continue  # 单个文件损坏不影响整体展示

    # 按（公司 + 财年）去重：分数高的优先保留
    best = {}
    for case in cases:
        key = (case["ticker"], str(case["fiscal_year"]))
        if key not in best or case["score"] > best[key]["score"]:
            best[key] = case
    cases = sorted(best.values(), key=lambda c: c["score"], reverse=True)  # 风险高的排前面
    return cases


# ----------------------------------------------------------------------------
# 4. 风险评分逻辑（演示用简化公式，团队后续可替换为训练好的模型）
# ----------------------------------------------------------------------------
def compute_risk_score(dep_rate, intang_ratio, rd_intensity, text_score=None):
    """综合风险评分（0-100）。返回总分和各因子贡献，便于向评委解释。"""
    contributions = {
        "折旧摊销率（×200）": dep_rate * 200,
        "无形资产占比（×100）": intang_ratio * 100,
        "研发强度（×50）": rd_intensity * 50,
    }
    base = sum(contributions.values())
    text_bonus = 10.0 if (text_score is not None and text_score > 30) else 0.0
    if text_bonus:
        contributions["文本风险信号（加分项）"] = text_bonus
    return min(100.0, base + text_bonus), contributions


def risk_level_of(score):
    if score >= 70:
        return "高风险", "risk-high"
    if score >= 40:
        return "中风险", "risk-medium"
    return "低风险", "risk-low"


# ----------------------------------------------------------------------------
# 5. 各页面组件
# ----------------------------------------------------------------------------
def render_hero():
    st.markdown(
        """
    <div class="hero">
        <h1>📊 科创企业资产折旧风险识别系统</h1>
        <div class="subtitle">AI-Driven Depreciation Risk Detection for Tech Companies
        —— 基于 AI + 多模态数据融合的资产折旧风险识别与预警</div>
        <div class="chips">
            <span class="chip">2026 “揭榜挂帅”擂台赛</span>
            <span class="chip">题目编号 XH-202626</span>
            <span class="chip gray">财务特征 × 文本分析 × 可解释评分</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_landing(cases):
    """未开始分析时的初始界面：讲清楚这是什么、怎么用。"""
    st.markdown("<div class='section-title'>三步完成一次风险分析</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "<div class='card'><h4>① 填写财务指标</h4>"
            "<p>在左侧输入总资产、无形资产、研发费用、营业收入、折旧摊销。"
            "这些数据来自公司 10-K 年报的资产负债表与利润表。</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            "<div class='card'><h4>② 粘贴年报文本（可选）</h4>"
            "<p>复制年报中「风险因素（Risk Factors）」章节，系统会做关键词频率"
            "与文本风险信号分析。</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            "<div class='card'><h4>③ 点击「开始分析」</h4>"
            "<p>系统输出 0-100 风险评分、风险等级、指标雷达图与分级预警，"
            "并展示评分的计算过程。</p></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    if cases:
        st.markdown(
            "<div class='section-title'>已标注案例（点击左侧「案例库」查看详情）</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(cases))
        for col, case in zip(cols, cases):
            with col:
                st.markdown(
                    f"<div class='card' style='text-align:center'>"
                    f"<h4>{case['ticker']}</h4>"
                    f"<p>FY{case['fiscal_year']}</p>"
                    f"<div class='big-score' style='font-size:1.7rem;color:{case['color']}'>"
                    f"{case['score']:.1f}<small> / 5.0</small></div>"
                    f"<p style='color:{case['color']};font-weight:600'>{case['level']}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.write("")
    with st.expander("⚙️ 技术架构说明"):
        st.markdown(
            """
- **财务特征**：折旧摊销率、无形资产占比、研发强度、资产周转率
- **文本特征**：折旧/减值关键词频率、风险信号词统计（预留 FinBERT 情感分析接口）
- **评分模型**：当前为规则评分演示版，后续接入 XGBoost + SHAP 可解释性分析
- **数据基础**：团队已完成 5 家美国科技公司 10-K 年报的人工标注（见「案例库」）
            """
        )


def render_case_library(cases):
    """案例库页面：展示人工标注的 5 家公司风险画像。"""
    if not cases:
        st.warning("未找到标注数据，请确认 data/annotated/ 目录下有 JSON 文件。")
        return

    tickers = [c["ticker"] for c in cases]
    selected = st.selectbox("选择公司", tickers, index=0)
    case = next(c for c in cases if c["ticker"] == selected)

    # 顶部：公司信息 + 总分
    left, right = st.columns([2, 1])
    with left:
        st.markdown(
            f"<div class='card'>"
            f"<h4 style='font-size:1.25rem'>{case['name']}（{case['ticker']}）</h4>"
            f"<p>财年 FY{case['fiscal_year']} · 10-K 人工标注</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"<div class='card' style='text-align:center'>"
            f"<div class='big-score' style='color:{case['color']}'>{case['score']:.1f}"
            f"<small> / 5.0</small></div>"
            f"<span class='risk-badge' style='background:{case['color']}'>{case['level']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.progress(min(case["score"] / 5.0, 1.0))

    # 维度评分
    if case["dimensions"]:
        st.markdown("<div class='section-title'>五维度评分</div>", unsafe_allow_html=True)
        for d in case["dimensions"]:
            label = f"**{d['name']}** — {d['score']}/{d['max']}"
            if d["label"]:
                label += f"（{d['label']}）"
            st.markdown(label)
            st.progress(min(d["score"] / max(d["max"], 1), 1.0))
            if d["reasoning"]:
                with st.expander("评分依据"):
                    st.markdown(d["reasoning"])

    # 综合结论
    if case["summary"]:
        st.markdown("<div class='section-title'>综合结论</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='quote'>{case['summary']}</div>", unsafe_allow_html=True)

    # 风险信号证据
    if case["signals"]:
        st.markdown(
            f"<div class='section-title'>关键风险信号（{len(case['signals'])} 条证据）</div>",
            unsafe_allow_html=True,
        )
        for s in case["signals"]:
            with st.expander(f"🔎 {s['id'] or '风险信号'}"):
                if s["source"]:
                    st.caption(f"来源：{s['source']}")
                if s["excerpt"]:
                    st.markdown(f"> {s['excerpt']}")
                if s["note"]:
                    st.info(f"标注说明：{s['note']}")


def render_analysis_results(result):
    """单公司分析的结果区。"""
    score = result["score"]
    level, level_class = risk_level_of(score)

    # 顶部三个核心结论
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='card' style='text-align:center'>"
            f"<p>综合风险评分</p><div class='big-score'>{score:.1f}"
            f"<small> / 100</small></div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='card' style='text-align:center'><p>风险等级</p><br>"
            f"<span class='risk-badge {level_class}'>{level}</span></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='card' style='text-align:center'><p>折旧摊销率</p>"
            f"<div class='big-score'>{result['dep_rate']:.2%}</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # 四项核心指标
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("折旧摊销率", f"{result['dep_rate']:.2%}", help="折旧摊销 / 总资产")
    m2.metric("无形资产占比", f"{result['intang_ratio']:.2%}", help="无形资产 / 总资产")
    m3.metric("研发强度", f"{result['rd_intensity']:.2%}", help="研发费用 / 营业收入")
    m4.metric("资产周转率", f"{result['asset_turnover']:.2f}x", help="营业收入 / 总资产")

    st.write("")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 指标可视化", "📝 文本分析", "⚠️ 风险预警", "ℹ️ 评分说明"])

    # --- Tab 1: 雷达图 + 柱状图 ---
    with tab1:
        col_radar, col_bar = st.columns(2)
        with col_radar:
            st.markdown("**指标雷达图**（各指标按上限归一化到 0-100）")
            caps = {"折旧率": 10, "无形占比": 50, "研发强度": 25, "资产周转": 200}
            raw_vals = [
                result["dep_rate"] * 100,
                result["intang_ratio"] * 100,
                result["rd_intensity"] * 100,
                result["asset_turnover"] * 100,
            ]
            categories = list(caps.keys())
            values = [min(v / caps[c] * 100, 100) for v, c in zip(raw_vals, categories)]
            values += values[:1]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(4.6, 4.6), subplot_kw=dict(polar=True))
            ax.fill(angles, values, color=PRIMARY, alpha=0.18)
            ax.plot(angles, values, "o-", linewidth=2, color=PRIMARY)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=11)
            ax.set_ylim(0, 100)
            ax.set_yticks([25, 50, 75, 100])
            ax.tick_params(colors=MUTED)
            ax.spines["polar"].set_color("#DDD8CE")
            st.pyplot(fig)
            plt.close(fig)

        with col_bar:
            st.markdown("**评分因子贡献分解**（各部分对总分的贡献）")
            contrib = result["contributions"]
            fig2, ax2 = plt.subplots(figsize=(5.2, 3.4))
            names = list(contrib.keys())
            vals = list(contrib.values())
            bars = ax2.barh(names, vals, color=PRIMARY, alpha=0.85, height=0.55)
            ax2.set_xlim(0, max(vals + [1]) * 1.25)
            ax2.bar_label(bars, fmt="%.1f", padding=4, color=INK)
            ax2.spines[["top", "right"]].set_visible(False)
            ax2.spines[["left", "bottom"]].set_color("#DDD8CE")
            ax2.tick_params(colors=MUTED)
            st.pyplot(fig2)
            plt.close(fig2)
            st.caption("哪个柱子长，说明总分主要由哪个因素推高——答辩时可以指着这张图讲。")

    # --- Tab 2: 文本分析 ---
    with tab2:
        text_result = result["text_result"]
        if text_result:
            t1, t2, t3 = st.columns(3)
            t1.metric("折旧/减值关键词命中", f"{text_result['depreciation_keyword_count']} 次")
            t2.metric("风险信号词命中", f"{text_result['risk_signal_count']} 次")
            t3.metric("文本风险得分", f"{text_result['depreciation_risk_score']:.1f} / 100")
            st.write("")
            st.markdown("**情感倾向（FinBERT 未启用时为关键词近似）**")
            sent = {
                "消极": text_result.get("sentiment_negative", 0),
                "中性": text_result.get("sentiment_neutral", 0),
                "积极": text_result.get("sentiment_positive", 0),
            }
            for k, v in sent.items():
                st.markdown(f"{k}")
                st.progress(min(max(v, 0.0), 1.0))
            with st.expander("查看关键词命中明细"):
                st.json(text_result["keyword_details"])
        else:
            st.info("本次未提供年报文本。在左侧粘贴「风险因素」章节后重新分析，即可看到关键词命中与文本风险得分。")

    # --- Tab 3: 风险预警 ---
    with tab3:
        warnings = []
        if result["dep_rate"] > 0.05:
            warnings.append("折旧摊销率高于 5%，资产加速减值风险需关注")
        if result["intang_ratio"] > 0.4:
            warnings.append("无形资产占比超过 40%，技术淘汰可能引发大额减值")
        if result["rd_intensity"] > 0.15:
            warnings.append("研发强度超过 15%，需关注研发资本化政策是否隐含盈余管理")
        if result["asset_turnover"] < 0.3:
            warnings.append("资产周转率低于 0.3x，资产利用效率偏低，重资产风险累积")
        if result["text_result"] and result["text_result"]["depreciation_risk_score"] > 30:
            warnings.append("年报文本中折旧/减值信号密集，管理层已在风险章节频繁提示")

        if warnings:
            for w in warnings:
                st.warning(w)
        else:
            st.success("当前指标未触发明显风险预警 ✅")

    # --- Tab 4: 评分说明 ---
    with tab4:
        st.markdown(
            """
**评分公式（演示版规则模型）**

```
风险评分 = 折旧摊销率×200 + 无形资产占比×100 + 研发强度×50 [+ 文本信号加10分]
```

- 三个系数是团队根据已标注案例的经验设定的权重，体现「折旧错配」在总分中的主导地位
- 评分上限 100 分；≥70 为高风险，40-70 为中风险，<40 为低风险
- 后续迭代方向：用已标注数据训练 XGBoost 模型替代人工系数，并用 SHAP 输出因子贡献
            """
        )


# ----------------------------------------------------------------------------
# 6. 主流程
# ----------------------------------------------------------------------------
def main():
    render_hero()

    with st.sidebar:
        st.markdown("### 🧭 功能导航")
        mode = st.radio(
            "选择功能",
            ["🔍 单公司分析", "📚 案例库（已标注 5 家）"],
            label_visibility="collapsed",
        )
        st.divider()

        inputs = {}
        if mode.startswith("🔍"):
            st.markdown("### 1️⃣ 公司信息")
            inputs["ticker"] = st.text_input("股票代码", "AAPL", help="如 AAPL、MSFT、NVDA")
            inputs["fiscal_year"] = st.selectbox("财年", [2025, 2024, 2023, 2022, 2021], index=1)

            st.markdown("### 2️⃣ 财务指标（百万美元）")
            inputs["total_assets"] = st.number_input(
                "总资产", min_value=0.0, value=10000.0, step=100.0,
                help="10-K 资产负债表：Total Assets",
            )
            inputs["intangible_assets"] = st.number_input(
                "无形资产", min_value=0.0, value=2000.0, step=100.0,
                help="10-K 资产负债表：Intangible Assets（可含商誉）",
            )
            inputs["rd_expense"] = st.number_input(
                "研发费用", min_value=0.0, value=1500.0, step=100.0,
                help="10-K 利润表：Research and Development",
            )
            inputs["revenue"] = st.number_input(
                "营业收入", min_value=0.0, value=8000.0, step=100.0,
                help="10-K 利润表：Total Revenue / Net Sales",
            )
            inputs["depreciation"] = st.number_input(
                "折旧摊销", min_value=0.0, value=500.0, step=50.0,
                help="10-K 现金流量表：Depreciation and Amortization",
            )

            st.markdown("### 3️⃣ 文本分析（可选）")
            inputs["report_text"] = st.text_area(
                "粘贴年报「风险因素」章节",
                height=140,
                placeholder="从 10-K 中复制 ITEM 1A. RISK FACTORS 的内容……",
            )

            st.write("")
            analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)

    cases = load_case_library()

    # ---------- 案例库模式 ----------
    if mode.startswith("📚"):
        render_case_library(cases)

    # ---------- 单公司分析模式 ----------
    else:
        if not analyze_btn:
            render_landing(cases)
        else:
            with st.spinner("正在计算风险评分……"):
                # 特征计算（失败时退回手工计算，保证演示不中断）
                try:
                    from features.feature_engineering import FeatureEngineer

                    df = pd.DataFrame(
                        [{
                            "ticker": inputs["ticker"],
                            "fiscal_year": inputs["fiscal_year"],
                            "total_assets": inputs["total_assets"],
                            "intangible_assets": inputs["intangible_assets"],
                            "r_d_expense": inputs["rd_expense"],
                            "revenue": inputs["revenue"],
                            "depreciation_amortization": inputs["depreciation"],
                        }]
                    )
                    feats = FeatureEngineer().build_traditional_features(df)
                    dep_rate = float(feats["depreciation_rate"].iloc[0])
                    intang_ratio = float(feats["intangible_ratio"].iloc[0])
                    rd_intensity = float(feats["rd_intensity"].iloc[0])
                    asset_turnover = float(feats["asset_turnover"].iloc[0])
                except Exception:
                    ta = max(inputs["total_assets"], 1e-9)
                    rev = max(inputs["revenue"], 1e-9)
                    dep_rate = inputs["depreciation"] / ta
                    intang_ratio = inputs["intangible_assets"] / ta
                    rd_intensity = inputs["rd_expense"] / rev
                    asset_turnover = rev / ta

                # 文本分析（可选，失败不影响主流程）
                text_result = None
                if inputs["report_text"].strip():
                    try:
                        from nlp.text_analyzer import TextAnalyzer

                        analyzer = TextAnalyzer(use_finbert=False)
                        text_result = analyzer.analyze_report(inputs["report_text"])
                    except Exception as e:
                        st.warning(f"文本分析模块出错，已跳过：{e}")

                score, contributions = compute_risk_score(
                    dep_rate, intang_ratio, rd_intensity,
                    text_result["depreciation_risk_score"] if text_result else None,
                )

            render_analysis_results(
                {
                    "score": score,
                    "contributions": contributions,
                    "dep_rate": dep_rate,
                    "intang_ratio": intang_ratio,
                    "rd_intensity": rd_intensity,
                    "asset_turnover": asset_turnover,
                    "text_result": text_result,
                }
            )

    st.markdown(
        "<div class='footer'>2026 中国青年科技创新「揭榜挂帅」擂台赛 · XH-202626 · "
        "科创企业特有风险的识别与管理</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
