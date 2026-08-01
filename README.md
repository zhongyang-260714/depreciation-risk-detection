# 科创企业资产折旧风险识别系统

> 第十九届"挑战杯"2026 年度中国青年科技创新"揭榜挂帅"擂台赛 · 中国青基会平安励志计划
> 题目编号：XH-202626 ｜ 题目名称：科创企业特有风险的识别与管理
> 发榜单位：中国青少年发展基金会（中国平安励志计划）

---

## 一、项目简介

**AI 风口之上，财报之下，隐藏着数百亿美元的折旧错配。**

AI 算力资产的技术迭代周期仅 1–2 年，美国科技巨头却普遍按 4–8 年计提折旧——**技术寿命与会计寿命的结构性错配，使折旧费用被系统性低估、利润被系统性高估**。Burry 估计，2026–2028 年全行业低估折旧约 **1,760 亿美元**。

本项目以 SEC 法定披露的 10-K 年报为数据源，构建**证据链标注体系**与**五维度折旧风险评分模型（5D-DRS）**：以"原文—行号—会计含义—推断链"四列结构固化风险信号，经五维度加权评分，并将方法论工程化为**可运行的智能识别系统**（本仓库）。

### 三重错配
- **时间错配**：技术迭代周期（1–2 年）<< 会计折旧周期（4–8 年）
- **规则错配**：工业时代准则（GAAP）→ 数字时代现实（AI 资产快速淘汰）
- **激励错配**：AI 军备竞赛 × 业绩美化动机 × 审计师技术盲区

---

## 二、核心方法与实证要点

- **样本**：10 家美国科技公司 × 3 财年 = **30 份面板标注**，全部经"AI 草拟 + 人工逐条复核"闭环，状态均为 `confirmed`；
- **发现 ①**：5 家公司在 AI 投资爆发后约 12 个月内**同步延长折旧年限**，Oracle 与 Meta 为"连续延长者"；
- **发现 ②**：变更年五维评分均值 **4.25**，显著高于非变更年的 **3.43**；
- **发现 ③**：风险 = 假设激进度 × 资产敞口；错配沿"折旧—存货—商誉—租赁"四通道分化；
- **模型化验证（PoC）**：30 行 × 55 特征面板上的 XGBoost 可行性验证，LOGO（留一公司法）MAE **0.418**，较朴素基线 0.784 改善 **46.6%**；SHAP 重要性首位为资本开支强度（capex_to_revenue，平均 |SHAP| 0.403），模型独立复现了人工评分逻辑。

---

## 三、智能识别系统（Streamlit，六个页面）

| 页面 | 功能 |
|------|------|
| P1 · 总览热力图 | 30 份标注的公司 × 财年风险全景、最新财年排行、标注明细 |
| P2 · 公司画像 | 单公司五维评分、验算式（Σ 权重×得分 现场重算）、证据链原文 |
| P3 · 跨年轨迹 | 同一公司多年评分轨迹，标注折旧年限政策变更事件点 |
| P4 · 权重敏感性 | 拖动权重滑块实时重算综合分，识别评分"杠杆点" |
| P5 · 方法论 | 三重错配、5D-DRS 评分体系、数据来源与标注流程 |
| P6 · 实时评分演示 | XGBoost 模型**实时推理**：输入指标 → 综合评分 + 风险等级 + SHAP 单项贡献解释；支持样本公司预填与自定义指标两种模式，缺失指标自动处理 |
| **P7 · 智能标注** | **DeepSeek AI 驱动**：输入公司代码 + 财年 → 自动下载 10-K → 关键词定位 → AI 草拟证据链与五维评分 → 程序逐字验真 → 综合算分；AI 草稿与人工 confirmed 标注并排对照，人工确认后入库 |

同源 FastAPI 接口：`POST /predict` / `POST /batch_predict`，与 P6 调用同一评分器实例。
P7 的 AI 标注引擎独立运行，支持本地 10-K HTML 上传模式。

同源 FastAPI 接口：`POST /predict` / `POST /batch_predict`，与 P6 调用同一评分器实例。

---

## 四、快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动智能识别系统（浏览器访问 http://localhost:8501）
streamlit run src/dashboard/app.py
#    支持 URL 直达页面：?page=p1 ... ?page=p7

# 3.（可选）启动实时评分 API
uvicorn src.api.main:app --port 8000
streamlit run src/dashboard/app.py
#    支持 URL 直达页面：?page=p1 ... ?page=p6

# 3.（可选）启动实时评分 API
uvicorn src.api.main:app --port 8000
#    POST /predict        单条评分
#    POST /batch_predict  批量评分

# 4. 验证（无需浏览器）
python smoke_test_app.py        # 看板数据链路：30 份 confirmed + 六页可导入 + 评分链路
python smoke_test_scorer.py     # 评分链路：样本回代 + 缺失值路由 + API 双接口
python tests/verify_all_pages.py  # AppTest 真实执行六页渲染 + P6 完整推理

# 5.（可选）重新训练演示模型
python train_scorer.py          # 30×85 面板 → 55 特征 → 序列化至 models/
```

---

## 五、目录结构

```
depreciation-risk-detection/
├── src/
│   ├── dashboard/          # Streamlit 看板
│   │   ├── app.py          #   入口（七页导航）
│   │   ├── data_loader.py  #   数据加载（动态读取，禁止硬编码）
│   │   ├── ui_common.py    #   公共 UI 组件
│   │   └── views/          #   p1_overview … p7_ai_annotation
│   ├── ai_annotation/      # DeepSeek 智能标注引擎（P7 后台）
│   │   ├── deepseek_client.py   #   DeepSeek API 封装
│   │   ├── text_locator.py      #   关键词矩阵定位 + XBRL 噪声排除
│   │   ├── verifier.py          #   程序逐字验真（防 AI 编造）
│   │   ├── scorer_calculator.py #   五维加权算分
│   │   ├── edgar_fetcher.py     #   SEC EDGAR 10-K 下载
│   │   └── prompts.py           #   Prompt 模板集中管理
│   ├── scoring/            # 评分引擎（predictor.py：评分 + SHAP 单项贡献）
│   └── api/                # FastAPI 实时评分接口（main.py）
│   ├── dashboard/          # Streamlit 看板
│   │   ├── app.py          #   入口（六页导航）
│   │   ├── data_loader.py  #   数据加载（动态读取，禁止硬编码）
│   │   ├── ui_common.py    #   公共 UI 组件
│   │   └── views/          #   p1_overview … p6_live_scoring
│   ├── scoring/            # 评分引擎（predictor.py：评分 + SHAP 单项贡献）
│   └── api/                # FastAPI 实时评分接口（main.py）
├── models/                 # depreciation_scorer_v03.joblib + meta.json（PoC 演示模型）
├── data/
│   ├── annotated/          # 30 份证据链标注 JSON（10 家 × 3 财年，全部 confirmed）
│   └── processed/          # 训练面板（v0.6：30 行 × 85 列）
├── tests/                  # AppTest 页面级验证
├── docs/                   # 战略与评估文档
├── smoke_test_app.py       # 看板冒烟测试
├── smoke_test_scorer.py    # 评分链路冒烟测试
└── train_scorer.py         # 演示模型训练与序列化脚本
```

---

## 六、数据说明

- **标注数据**：`data/annotated/*.json` —— 每份含四列证据链（原文片段、行号、会计含义、推断链）、五维度评分、综合分与 `review_status`；文件名以 `_` 开头或含 backup/draft/old/tmp 的为过程文件，系统自动跳过；
- **数据来源**：美国 SEC EDGAR 披露的 10-K 年度报告；
- **协作协议**：AI 完成初筛与草拟，项目负责人逐条回原文复核（逐字一致性、正文位置、推断逻辑、锚点符合度四项检查），复核通过后状态方由 `draft_pending_review` 转为 `confirmed`。

---

## 七、免责声明

实时评分引擎（P6 与 API）为 **30 样本可行性验证（PoC）演示模型**，全部输出均不构成预测能力声明或投资建议。模型对全新样本的复现能力以 LOGO（留一公司法）交叉验证为准。

---

## 八、License

MIT License
