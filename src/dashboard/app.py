"""科创企业资产折旧风险识别系统 · T7 交互看板

七个页面：
- P1 总览热力图      —— 30 份标注的公司 × 财年风险全景
- P2 公司画像        —— 单公司五维评分 + 验算式 + 证据链原文
- P3 跨年轨迹        —— 同一公司多年评分轨迹，标注政策变更事件点
- P4 权重敏感性      —— 拖动权重滑块，实时重算综合分
- P5 方法论          —— 评分体系、数据来源、草稿状态说明
- P6 实时评分演示    —— XGBoost 模型实时推理
- P7 智能标注        —— DeepSeek AI 驱动，自动证据链标注

数据全部动态读取：data/annotated/*.json（30 份）+ data/processed/training_v05_panel_30.csv
运行：streamlit run src/dashboard/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="科创企业资产折旧风险识别系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 让 ui_common / data_loader / pages 可以被导入（app.py 所在目录加入 sys.path）
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ui_common as ui
from data_loader import load_all

PAGES = {
    "P1 · 总览热力图": "views.p1_overview",
    "P2 · 公司画像": "views.p2_company",
    "P3 · 跨年轨迹": "views.p3_trajectory",
    "P4 · 权重敏感性": "views.p4_sensitivity",
    "P5 · 方法论": "views.p5_methodology",
    "P6 · 实时评分演示": "views.p6_live_scoring",
    "P7 · 智能标注": "views.p7_ai_annotation",
}

# 支持 URL 直达某页，如 ?page=p2（答辩演示/截图用）
_SHORT_CODES = {f"p{i+1}": name for i, name in enumerate(PAGES)}


def main():
    ui.inject_css()

    data = load_all()
    n_draft = sum(1 for c in data["cases"] if c["is_draft"])
    n_confirmed = len(data["cases"]) - n_draft

    with st.sidebar:
        st.markdown("### 🧭 页面导航")
        qp = str(st.query_params.get("page", "")).lower()
        default_index = list(_SHORT_CODES).index(qp) if qp in _SHORT_CODES else 0
        choice = st.radio(
            "选择页面", list(PAGES.keys()), index=default_index,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption(f"📁 已加载标注 {len(data['cases'])} 份")
        st.caption(f"✅ 已确认 {n_confirmed} 份 · 📝 草稿待审 {n_draft} 份")
        st.caption("分数动态读取，草稿后续微调会自动生效")

    ui.hero(
        "📊 科创企业资产折旧风险识别系统",
        "AI-Driven Depreciation Risk Detection —— AI 泡沫 × 资产折旧错配的系统性风险识别",
        [
            ("2026 "揭榜挂帅"擂台赛", ""),
            ("XH-202626", ""),
            (f"标注 {len(data['cases'])} 份", "gray"),
            (f"草稿待审 {n_draft} 份", "amber" if n_draft else "gray"),
        ],
    )

    import importlib

    module = importlib.import_module(PAGES[choice])
    module.render(data)

    ui.footer()


if __name__ == "__main__":
    main()
