"""T7 交互看板 · 共享 UI 组件与设计令牌

所有页面统一从这里取配色和组件，保证视觉一致。
低饱和暖色系：深青主色 + 暖白背景。
"""

import streamlit as st

# ---- 设计令牌 ----
PRIMARY = "#17705C"   # 主色：低饱和深青
BG_WARM = "#FAF8F5"   # 暖白背景
INK = "#2B2B28"       # 正文墨色
MUTED = "#8A877F"     # 次要文字
BORDER = "#E8E4DD"    # 卡片描边
CARD_BG = "#FFFFFF"

# 热力图配色（plotly colorscale，低饱和：绿 → 黄 → 红）
HEAT_COLORSCALE = [
    [0.0, "#2E7D5B"],
    [0.4, "#7A9E43"],
    [0.6, "#D9A62E"],
    [0.8, "#C07A1B"],
    [1.0, "#B3402F"],
]

PLOTLY_LAYOUT = dict(
    font=dict(family="Microsoft YaHei, SimHei, sans-serif", color=INK),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
)

# 审核状态徽章
STATUS_STYLE = {
    "confirmed": ("已确认", "#2E7D5B"),
    "draft_pending_review": ("草稿待审", "#C07A1B"),
}


def inject_css():
    st.markdown(
        f"""
<style>
    .stApp {{ background-color: {BG_WARM}; }}
    .block-container {{ padding-top: 2rem; max-width: 1240px; }}

    .hero {{
        background: {CARD_BG}; border: 1px solid {BORDER};
        border-left: 6px solid {PRIMARY}; border-radius: 12px;
        padding: 1.3rem 1.8rem 1.1rem 1.8rem; margin-bottom: 1.2rem;
    }}
    .hero h1 {{ margin: 0; font-size: 1.75rem; color: {INK}; }}
    .hero .subtitle {{ color: {MUTED}; margin-top: 0.3rem; font-size: 0.92rem; }}
    .chips {{ margin-top: 0.7rem; }}
    .chip {{
        display: inline-block; font-size: 0.76rem; color: {PRIMARY};
        background: #EEF5F2; border: 1px solid #D5E5DF;
        border-radius: 999px; padding: 0.12rem 0.7rem; margin-right: 0.4rem;
    }}
    .chip.gray {{ color: {MUTED}; background: #F4F2EE; border-color: #E6E2DA; }}
    .chip.amber {{ color: #C07A1B; background: #FBF3E4; border-color: #EBD9B4; }}

    .card {{
        background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 12px;
        padding: 1rem 1.2rem; height: 100%;
    }}
    .card h4 {{ margin: 0 0 0.35rem 0; color: {INK}; font-size: 1rem; }}
    .card p {{ margin: 0; color: {MUTED}; font-size: 0.88rem; line-height: 1.55; }}

    .risk-badge {{
        display: inline-block; font-weight: 700; font-size: 1rem;
        border-radius: 8px; padding: 0.3rem 0.85rem; color: #FFFFFF;
    }}
    .status-badge {{
        display: inline-block; font-size: 0.75rem; font-weight: 600;
        border-radius: 999px; padding: 0.12rem 0.65rem; color: #FFFFFF;
        vertical-align: middle;
    }}
    .big-score {{ font-size: 2.4rem; font-weight: 800; color: {INK}; line-height: 1.1; }}
    .big-score small {{ font-size: 0.95rem; color: {MUTED}; font-weight: 500; }}

    .section-title {{
        font-size: 1.1rem; font-weight: 700; color: {INK};
        margin: 0.5rem 0 0.75rem 0; padding-left: 0.6rem;
        border-left: 4px solid {PRIMARY};
    }}
    .quote {{
        background: #F4F2EE; border-left: 4px solid #C9C2B4; border-radius: 6px;
        padding: 0.8rem 1.05rem; color: {INK}; font-size: 0.92rem; line-height: 1.7;
    }}
    .formula {{
        background: #F0EDE7; border-radius: 8px; padding: 0.7rem 1rem;
        font-family: Consolas, monospace; font-size: 0.95rem; color: {INK};
    }}
    .footer {{ color: {MUTED}; font-size: 0.78rem; text-align: center; margin-top: 2.2rem; }}
</style>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, chips: list[tuple[str, str]] = ()):
    """页面顶部标题卡。chips: [(文字, 样式)]，样式为 '' / 'gray' / 'amber'"""
    chip_html = "".join(
        f"<span class='chip {style}'>{text}</span>" for text, style in chips
    )
    st.markdown(
        f"""<div class="hero"><h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
        <div class="chips">{chip_html}</div></div>""",
        unsafe_allow_html=True,
    )


def section(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)


def status_badge(review_status: str) -> str:
    """审核状态徽章 HTML：已确认(绿) / 草稿待审(橙) / 未知(灰)"""
    label, color = STATUS_STYLE.get(review_status, (review_status or "未知", MUTED))
    return f"<span class='status-badge' style='background:{color}'>{label}</span>"


def risk_badge(level: str, color: str) -> str:
    return f"<span class='risk-badge' style='background:{color}'>{level}</span>"


def footer():
    st.markdown(
        "<div class='footer'>2026 中国青年科技创新「揭榜挂帅」擂台赛 · XH-202626 · "
        "科创企业资产折旧风险识别系统 · 数据动态读取自 data/annotated + data/processed</div>",
        unsafe_allow_html=True,
    )
