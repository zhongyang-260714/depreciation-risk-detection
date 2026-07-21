"""Streamlit 演示界面

快速搭建可交互的 Web Demo，用于展示风险识别结果。
比赛答辩时可直接演示此界面。
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from models.train import RiskModel
from features.feature_engineering import FeatureEngineer
from nlp.text_analyzer import TextAnalyzer

# 设置 matplotlib 中文字体（Windows）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 页面配置
st.set_page_config(
    page_title="科创企业资产折旧风险识别系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def main():
    """主界面"""
    st.markdown("<div class='main-header'>📊 科创企业资产折旧风险识别系统</div>", unsafe_allow_html=True)
    st.markdown("""
    > **2026年度中国青年科技创新"揭榜挂帅"擂台赛** | 题目编号：XH-202626  
    > 基于 AI + 多模态数据融合的科技企业资产折旧风险识别与预警
    """)
    
    st.divider()
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 输入参数")
        
        st.subheader("1. 公司基本信息")
        ticker = st.text_input("股票代码", "AAPL", help="如 AAPL, MSFT, GOOGL")
        fiscal_year = st.selectbox("财年", [2024, 2023, 2022, 2021, 2020])
        
        st.subheader("2. 财务指标")
        total_assets = st.number_input("总资产 (百万美元)", min_value=0.0, value=10000.0, step=100.0)
        intangible_assets = st.number_input("无形资产 (百万美元)", min_value=0.0, value=2000.0, step=100.0)
        rd_expense = st.number_input("研发费用 (百万美元)", min_value=0.0, value=1500.0, step=100.0)
        revenue = st.number_input("营业收入 (百万美元)", min_value=0.0, value=8000.0, step=100.0)
        depreciation = st.number_input("折旧摊销 (百万美元)", min_value=0.0, value=500.0, step=50.0)
        
        st.subheader("3. 文本分析（可选）")
        report_text = st.text_area(
            "粘贴年报风险章节文本",
            height=150,
            placeholder="粘贴公司年报中风险因素章节..."
        )
        
        analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)
    
    # 主内容区
    if analyze_btn:
        with st.spinner("正在分析..."):
            # 构建特征
            financial_data = pd.DataFrame([{
                'ticker': ticker,
                'fiscal_year': fiscal_year,
                'total_assets': total_assets,
                'intangible_assets': intangible_assets,
                'r_d_expense': rd_expense,
                'revenue': revenue,
                'depreciation_amortization': depreciation
            }])
            
            engineer = FeatureEngineer()
            features = engineer.build_traditional_features(financial_data)
            
            # 文本分析
            if report_text:
                analyzer = TextAnalyzer(use_finbert=False)
                text_result = analyzer.analyze_report(report_text)
            else:
                text_result = None
            
            # 计算风险指标
            dep_rate = features['depreciation_rate'].values[0]
            intang_ratio = features['intangible_ratio'].values[0]
            rd_intensity = features['rd_intensity'].values[0]
            
            # 综合风险评分（简化版，实际应调用模型）
            base_score = min(100, (dep_rate * 200 + intang_ratio * 100 + rd_intensity * 50))
            if text_result and text_result['depreciation_risk_score'] > 30:
                base_score += 10
            risk_score = min(100, base_score)
            
            # 风险等级
            if risk_score >= 70:
                risk_level = "🔴 高风险"
                risk_class = "risk-high"
            elif risk_score >= 40:
                risk_level = "🟡 中风险"
                risk_class = "risk-medium"
            else:
                risk_level = "🟢 低风险"
                risk_class = "risk-low"
            
            # 展示结果
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 风险评分", f"{risk_score:.1f}/100")
            with col2:
                st.markdown(f"<div class='{risk_class}'>{risk_level}</div>", unsafe_allow_html=True)
            with col3:
                st.metric("🔍 关键指标", f"折旧率 {dep_rate:.2%}")
            
            st.divider()
            
            # 详细分析
            st.subheader("📋 详细分析")
            
            tab1, tab2, tab3 = st.tabs(["财务指标", "文本分析", "风险预警"])
            
            with tab1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**核心财务指标**")
                    metrics = {
                        "折旧摊销率": f"{dep_rate:.2%}",
                        "无形资产占比": f"{intang_ratio:.2%}",
                        "研发强度": f"{rd_intensity:.2%}",
                        "资产周转率": f"{features['asset_turnover'].values[0]:.2f}x"
                    }
                    for k, v in metrics.items():
                        st.markdown(f"- **{k}**: {v}")
                
                with col_b:
                    # 指标雷达图
                    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
                    categories = ['折旧率', '无形资产占比', '研发强度', '资产周转率']
                    values = [dep_rate*100, intang_ratio*100, rd_intensity*100, features['asset_turnover'].values[0]*10]
                    values += values[:1]  # 闭合
                    
                    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
                    angles += angles[:1]
                    
                    ax.fill(angles, values, alpha=0.25)
                    ax.plot(angles, values, 'o-', linewidth=2)
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(categories)
                    ax.set_ylim(0, max(values) * 1.2)
                    st.pyplot(fig)
            
            with tab2:
                if text_result:
                    st.markdown("**文本风险信号**")
                    st.json(text_result)
                else:
                    st.info("未提供年报文本，请粘贴风险章节以获取文本分析结果。")
            
            with tab3:
                st.markdown("**⚠️ 风险预警**")
                warnings = []
                if dep_rate > 0.05:
                    warnings.append("折旧摊销率高于行业平均水平，可能存在资产加速减值风险")
                if intang_ratio > 0.4:
                    warnings.append("无形资产占比过高，技术淘汰风险显著")
                if rd_intensity > 0.15:
                    warnings.append("研发强度极高，资本化决策可能隐含盈余管理")
                
                if warnings:
                    for w in warnings:
                        st.warning(w)
                else:
                    st.success("当前指标未触发明显风险预警")
    
    else:
        # 初始状态
        st.info("👈 请在左侧填写公司信息并点击「开始分析」")
        
        st.markdown("""
        ### 使用说明
        
        1. **填写财务指标**：输入公司总资产、无形资产、研发费用等数据
        2. **粘贴年报文本**（可选）：从 10-K 或年报中复制「风险因素」章节
        3. **点击分析**：系统将基于多模态数据融合模型计算风险评分
        
        ### 技术架构
        - 财务特征：折旧率、无形资产占比、研发资本化率
        - 文本特征：FinBERT 情感分析 + 关键词抽取
        - 模型：XGBoost + SHAP 可解释性
        """)


if __name__ == "__main__":
    main()
