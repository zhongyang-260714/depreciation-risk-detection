# Streamlit 前端优化方向清单（供队友参考）

> 生成时间：2026-07-20  
> 项目：科创企业资产折旧风险识别算法  
> 当前文件：`src/dashboard/app.py`（211 行，简化 Demo 框架）  
> 优化目标：从"手工输入 Demo"升级为"可直接用于答辩的专业级风险识别仪表盘"

---

## 方向一：接入真实标注数据（最高优先级）

**当前问题**：`app.py` 用的是用户手输的模拟数据，没有读取已标注的 5 家公司 JSON。

**具体任务**：
- [ ] 读取 `data/annotated/` 目录下的 `*_annotation.json`（Meta/NVIDIA/AMD/Google/Microsoft）
- [ ] 首页展示"五家公司风险对比总览"（类似 leaderboard）
- [ ] 点击某家公司进入详情页，展示其 5 个维度评分雷达图
- [ ] 增加筛选器：按风险等级（HIGH/ELEVATED/MODERATE）筛选

**预期效果**：打开页面直接看到 5 家公司风险排名，点击看详情。

**技术提示**：
```python
import json, glob
files = glob.glob("data/annotated/*_annotation.json")
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
```

---

## 方向二：风险维度可视化升级

**当前问题**：只有一个简陋的 matplotlib 雷达图，中文有字体问题，且不可交互。

**具体任务**：
- [ ] 用 **Plotly** 替代 matplotlib（交互式，鼠标悬停查看数值）
- [ ] 为每家公司绘制"五维风险雷达图"（D1-D5）
- [ ] 增加"横向对比"：选中 2-3 家公司，同一张图对比雷达图
- [ ] 增加"时间趋势"：如果有多财年数据，展示同一公司历年评分变化折线图

**推荐库**：`plotly`（已安装）、`altair`

**参考代码片段**：
```python
import plotly.graph_objects as go

categories = ['D1 年限错配', 'D2 政策保守性', 'D3 减值触发', 'D4 CAPEX 强度', 'D5 竞争替代']
values = [5, 5, 4, 3, 4]  # 从 JSON 读取
values += values[:1]  # 闭合

categories += categories[:1]
fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself'))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
st.plotly_chart(fig)
```

---

## 方向三：10-K 文件上传 + 自动分析（杀手级答辩功能）

**当前问题**：只能手动粘贴文本，无法直接上传文件。

**具体任务**：
- [ ] 增加文件上传组件：`st.file_uploader("上传 10-K HTML/PDF", type=["html", "pdf"])`
- [ ] 上传后自动提取文本（HTML 用 `BeautifulSoup`，PDF 用 `PyPDF2`）
- [ ] 调用 `src/nlp/text_analyzer.py` 进行 FinBERT 情感分析（或先用关键词匹配）
- [ ] 自动高亮文本中的风险关键词（年限延长、减值、CAPEX、impairment 等）
- [ ] 输出自动风险评分 + 关键证据摘要

**比赛演示价值**：答辩时现场上传一家未标注公司年报，10 秒内出风险评分 —— 非常震撼。

**注意**：不要自动上传文件到互联网，仅本地分析。

---

## 方向四：评分解释面板（可解释性 AI）

**具体任务**：
- [ ] 增加"为什么是这个分数？"展开面板（`st.expander`）
- [ ] 展示每个维度的具体证据（引用 10-K 原文片段，从 JSON 的 `evidence.text` 读取）
- [ ] 用颜色标注风险等级：🔴 严重 / 🟡 中等 / 🟢 正常
- [ ] 增加"同类公司对比"：该公司评分在 5 家样本中处于什么百分位

**示例展示**：
> **D1 折旧年限 vs 技术寿命：5/5 🔴**  
> 证据：*"服务器年限从 4 年延长至 6 年"*（Note 1, 第 2886 行）  
> 推断：H100→B200 仅需 1-2 年，会计寿命错配 3-6 倍

---

## 方向五：仪表盘总览（Dashboard 模式）

**具体任务**：
- [ ] 顶部 KPI 卡片区：
  - 5 家公司平均风险分
  - 高风险公司数量（≥4.0）
  - 总训练样本数
- [ ] 中部热力图：公司 × 维度 的评分矩阵（`st.dataframe` 或 Plotly heatmap）
  - 一眼看出哪家公司在哪方面最危险
- [ ] 底部最新动态：最近添加的标注、最近分析的 10-K 文件

**参考样式**：类似金融数据终端（Bloomberg / Wind）的卡片式布局。

---

## 方向六：移动端适配 + 答辩模式

**具体任务**：
- [ ] 当前 `layout="wide"` 在投影屏幕上字太小，答辩时看不清
- [ ] 增加"答辩模式"切换按钮（字体放大、图表简化、只展示核心结论）
- [ ] 增加导出功能：一键生成 PNG 截图（`st.download_button`）或 PDF 报告
- [ ] 适配 16:9 投影屏幕比例（1920×1080）

---

## 推荐执行顺序

| 阶段 | 任务 | 预计耗时 | 产出 | 优先级 |
|------|------|----------|------|--------|
| **第 1 天** | 方向一：接入 5 家真实数据 | 4-6h | 可运行的对比 Demo | 🔴 P0 |
| **第 2-3 天** | 方向二：Plotly 可视化升级 | 6-8h | 交互式雷达图 + 对比 | 🔴 P0 |
| **第 4-5 天** | 方向三：10-K 上传分析 | 8-10h | 杀手级演示功能 | 🟡 P1 |
| **第 6-7 天** | 方向四 + 五：解释面板 + 仪表盘 | 6-8h | 完整答辩界面 | 🟡 P1 |
| **有余力** | 方向六：答辩模式 + 导出 | 4-6h | 最终交付物 | 🟢 P2 |

---

## 技术依赖检查

**已安装（requirements.txt 中）**：
- `streamlit`
- `pandas`
- `numpy`
- `matplotlib`
- `plotly`（已加入 requirements）
- `beautifulsoup4`（用于 HTML 解析）

**可能需要安装**：
- `PyPDF2`（PDF 解析）
- `kaleido`（Plotly 导出 PNG）

```bash
pip install PyPDF2 kaleido
```

---

## 数据来源说明

**5 家已完成标注的公司（JSON 路径）**：

| 文件 | 综合评分 | 风险等级 |
|------|----------|----------|
| `data/annotated/META_2023_annotation.json` | 4.0 | HIGH |
| `data/annotated/GOOGL_2023_annotation.json` | 4.25 | HIGH |
| `data/annotated/MSFT_FY2024_annotation.json` | 4.20 | HIGH |
| `data/annotated/NVIDIA_FY2024_annotation.json` | 3.10 | ELEVATED |
| `data/annotated/AMD_FY2023_annotation.json` | 2.40 | MODERATE |

JSON 结构：每个文件包含 `metadata`、`company`、`financial_highlights`、`risk_signals`、`dimension_scores`、`composite_score`、`key_metrics` 等字段，可直接读取展示。

---

## 当前 `app.py` 运行方式

```bash
cd /d/depreciation-risk-detection
streamlit run src/dashboard/app.py
```

浏览器自动打开 `http://localhost:8501`

---

> 负责人（zhongyang-260714）已完成 5 家核心公司标注，评分依据见 `docs/评分依据与推断核对.md`。前端开发可立即开始。
