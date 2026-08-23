# 科创企业资产折旧风险识别系统

> 第十九届"挑战杯"2026 年度中国青年科技创新"揭榜挂帅"擂台赛 · 中国平安励志计划
> 题目编号：XH-202626 ｜ 题目名称：科创企业特有风险的识别与管理

---

## 一、项目简介

**AI 风口之上，财报之下，隐藏着行业级的折旧错配。**

AI 算力资产的技术迭代周期仅 **1–2 年**，美国科技巨头却普遍按 **4–8 年**计提折旧。技术寿命与会计寿命的结构性错配，使折旧费用被系统性低估、当期利润被系统性前置——Burry 估计 2026–2028 年全行业低估折旧约 **1760 亿美元**。实证发现：6 家公司在 AI 投资爆发后约 12 个月内同步延长折旧年限，这是行业级计量现象，而非个别公司的会计瑕疵。

本项目构建 **"证据链标注 + 5D-DRS 五维评分 + 智能识别系统"** 的完整方案，将折旧错配从"不可识别的会计偏差"转化为"可量化、可预警、可缓释的风险指标"，为科技金融"投、融、贷、保"全流程提供风险度量基础设施。

### 核心发现

- **估计变更共振**：6 家公司在 ChatGPT 发布后同一窗口同步延长年限（Oracle 与 Meta 为"连续延长者"）
- **变更年评分 4.25 vs 非变更年 3.43**（差值 0.82 分，描述性报告）
- **风险 = 假设激进度 × 资产敞口**：重资产的制造型与运营型霸榜高风险区，排序由模型内生生成
- **四通道分化**：错配沿"折旧—存货—商誉—租赁"通道兑现，存在可干预的时间差

---

## 二、双市场覆盖

| 市场 | 样本 | 数据源 | 状态 |
|------|------|--------|------|
| 美股 | 10 家科技公司 × 3 财年 = 30 份 10-K | SEC EDGAR | 全部完成证据链标注（confirmed） |
| A股 | 10 家上市公司 × 3 年 = 30 份年报 PDF | 巨潮资讯网 | 全部完成 AI 标注 + 人工复核（confirmed），验证 5D-DRS 不因国别预设方向 |

A股样本：中科曙光、数据港、寒武纪、浪潮信息、科大讯飞、奥飞数据、光环新网、海光信息、工业富联、润泽科技。

---

## 三、智能识别系统（Streamlit，P1–P7）

| 页面 | 功能 |
|------|------|
| P1 · 总览热力图 | 双市场 20 家 × 3 财年五维综合评分全景，颜色越深风险越高 |
| P2 · 公司画像 | 五维雷达图 + 风险信号列表，每条信号可展开英文原文、行号、推断链 |
| P3 · 跨年轨迹 | 同一公司多年评分轨迹，标注折旧年限政策变更事件点 |
| P4 · 权重敏感性 | 拖动权重滑块实时重算综合分，识别评分"杠杆点" |
| P5 · 方法论 | 三重错配、5D-DRS 评分体系、数据来源与标注流程 |
| P6 · 实时评分演示 | XGBoost 模型实时推理：输入指标 → 评分 + 风险等级 + SHAP 单项贡献解释 |
| P7 · 智能标注 | DeepSeek AI 驱动六步流水线：获取原文 → 五级关键词检索定位 → AI 草拟 → 程序逐字验真 → 规则引擎修正 → 输出评分与证据链；支持美股 Ticker 自动下载与 A股 PDF 上传两种模式 |

同源 FastAPI 接口：`POST /predict` / `POST /batch_predict`，与 P6 调用同一评分器实例。

### AI 应用架构：五环复合流水线

**生成 → 验真 → 修正 → 验证 → 归因**：大语言模型草拟证据链与评分建议（生成），程序逐字比对原文（验真），规则引擎硬规则修正（修正），XGBoost 在 30 样本面板上验证人工评分逻辑的可计算性（验证），SHAP 归因解释模型结构（归因）。规则引擎兜底防 AI 幻觉，是设计而非妥协。

### 五级关键词检索体系

核心层（人工六词矩阵）→ 语义扩展层 → 正则模式层 → MUST_INCLUDE 强制注入层（折旧/减值指纹）→ 结构化章节提取层。按信号强度排序截取候选段落，兼顾召回率与 Token 成本。

### 机器学习验证（诚实声明）

30 样本面板、55 特征上，LOGO（留一公司）交叉验证 **MAE = 0.418**（朴素基线 0.784，相对改善 **46.6%**）。结论定位为"人工评分逻辑可计算性"的**存在性证明 / 方向验证**，不构成预测能力声明；LOO 结果因面板泄漏仅作连续可比参考。

---

## 四、快速开始

> 🎯 **评委请直接阅读 [评委快速上手指南.md](评委快速上手指南.md)**：三步跑通系统 + 各页面看点 + 常见问题。

```bash
# 环境：Python 3.10+，安装依赖（精简运行版，约 2–3 分钟）
pip install -r requirements.txt
# 完整研究环境（FinBERT 实验等）：pip install -r requirements-full.txt

# 如需 P7 AI 标注功能，先设置环境变量（密钥不得硬编码）
# Windows: set DEEPSEEK_API_KEY=your_key

# 一键启动（脚本自动定位目录，任意安装路径可用）
start.bat
# 等价于：streamlit run src/dashboard/app.py

# 财报防误删备份（增量同步 + 完整性校验）
python scripts/backup_filings.py            # 实际备份
python scripts/backup_filings.py --dry-run  # 预览
python scripts/backup_filings.py --verify   # 校验
```

冒烟测试：`python smoke_test_app.py`（系统启动）/ `python smoke_test_scorer.py`（评分链路）。

---

## 五、目录结构

```
depreciation-risk-detection/
├── src/
│   ├── dashboard/             # Streamlit 看板
│   │   ├── app.py             #   入口（P1–P7 静态导入导航）
│   │   ├── data_loader.py     #   数据加载（动态读取，禁止硬编码）
│   │   ├── ui_common.py       #   公共 UI 组件
│   │   └── views/             #   p1_overview … p7_ai_annotation
│   ├── ai_annotation/         # 智能标注引擎（P7 后台）
│   │   ├── deepseek_client.py    #   DeepSeek API 封装
│   │   ├── text_locator.py       #   美股五级关键词检索 + XBRL 噪声排除
│   │   ├── cn_text_locator.py    #   A股五级关键词检索（中文指纹体系）
│   │   ├── cn_report_fetcher.py  #   A股年报获取（巨潮资讯）
│   │   ├── verifier.py           #   程序逐字验真（防 AI 编造）
│   │   ├── scorer_calculator.py  #   五维加权算分 + 规则引擎修正
│   │   ├── edgar_fetcher.py      #   SEC EDGAR 10-K 下载（data.sec.gov JSON API）
│   │   └── prompts.py / cn_prompts.py  # Prompt 模板集中管理
│   ├── scoring/               # 评分引擎（predictor.py：评分 + SHAP 解释）
│   └── api/                   # FastAPI 实时评分接口（main.py）
├── models/                    # depreciation_scorer_v03.joblib + meta.json（演示模型）
├── data/
│   ├── annotated/             # 30 份美股证据链标注 JSON（全部 confirmed）
│   ├── annotated_cn/          # A股十公司标注库（30 份，全部 confirmed）
│   └── processed/             # 训练面板（30 行 × 85 列）
├── scripts/
│   ├── backup_filings.py      #   财报防误删备份（增量同步+删除隔离）
│   └── ...                    #   审计、验证、文档生成脚本
├── tests/                     # 页面级验证
├── docs/                      # 优化备案（v6.2→v6.5-Final）与协作文档
├── report/                    # 竞赛交付物：报告 v6.5 + 支撑材料 + 答辩 PPT
├── xgboost_poc_v3.py          # 机器学习可计算性验证复现脚本
├── train_scorer.py            # 演示模型训练与序列化
└── smoke_test_app.py / smoke_test_scorer.py
```

> 注：原始财报文件（`data/raw/us_财报/`、`data/raw/cn_财报/`，共 239M）与 API 密钥不入库；财报下载方式见 `FILING_DOWNLOAD_GUIDE.md`。

---

## 六、数据说明

- **标注数据**：`data/annotated/*.json` 与 `data/annotated_cn/` —— 每份含四列证据链（原文片段、行号、会计含义、推断链）、五维度评分、综合分与 `review_status`；文件名以 `_` 开头或含 backup/draft/old/tmp 的为过程文件，系统自动跳过；
- **协作协议**：AI 完成初筛与草拟，项目负责人逐条回原文复核（逐字一致性、正文位置、推断逻辑、锚点符合度四项检查），复核通过后状态方由 `draft_pending_review` 转为 `confirmed`；
- **优化备案**：系统迭代全过程记录见 `docs/optimization_log_v62.md` → `v63_cn` → `v64_cn` → `v65_final.md`。

---

## 七、免责声明

实时评分引擎（P6 与 API）为 **30 样本可行性概念验证演示模型**，全部输出均不构成预测能力声明或投资建议。模型对全新样本的复现能力以 LOGO（留一公司法）交叉验证为准。

## 八、License

MIT License
