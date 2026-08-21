# Streamlit 智能识别系统 P7 中国A股优化路径备案（v6.3-CN）

> 备案时间：2026-08-19
> 备案人：AI 助手（协助用户完成）
> 系统版本：v6.3-CN（A股适配版）
> 适用范围：中国A股年报（巨潮资讯网）
> 前置依赖：美国部分优化 v6.2 已完成（optimization_log_v62.md）

---

## 一、优化背景

美国10家科技公司（SEC EDGAR 10-K）的P7优化已于v6.2阶段完成，核心解决了：
- Token超限导致的DeepSeek偶发返回空值
- 资产类型误判（MSFT/NVDA的computer equipment未识别为server）
- 多资产类型段落中buildings年限混入manufacturing equipment
- NVDA fallback搜索误匹配到Note 1 Organization段落

**本轮任务**：将v6.2美国优化的成功经验同步到中国A股pipeline，同时优化P7页面美观度，并为6家A股样本公司生成财报下载与标注指南。

---

## 二、中国A股六家公司现状

| 公司 | 股票代码 | 行业 | 已标注财年 | 数据来源 |
|------|----------|------|-----------|---------|
| **中科曙光** | 603019.SH | 高性能计算/服务器 | FY2024 | 新浪财经摘要+公开信息 |
| **数据港** | 603881.SH | IDC/数据中心 | FY2024 | 新浪财经摘要+公开信息 |
| **寒武纪** | 688256.SH | AI芯片 | FY2024 | 新浪财经摘要+公开信息 |
| **浪潮信息** | 000977.SZ | 服务器/云计算 | FY2024 | 新浪财经摘要+公开信息 |
| **科大讯飞** | 002230.SZ | AI/语音技术 | FY2024 | 新浪财经摘要+公开信息 |
| **奥飞数据** | 300738.SZ | IDC/云计算 | FY2024 | 新浪财经摘要+公开信息 |

**现状问题**：
1. 六家公司标注均基于"新浪财经年报全文摘要+公开信息交叉验证"，置信度约0.70
2. 尚未通过P7 AI pipeline（DeepSeek + 规则引擎）进行自动化验证
3. A股pipeline缺少美国v6.2已实施的优化（缓存持久化、候选数压缩、验真加固）
4. 巨潮资讯网自动下载PDF功能不稳定，需人工获取PDF

---

## 三、同步美国v6.2优化到A股

### 3.1 B1：Candidates 数量压缩 50→30

**修改文件**：`src/ai_annotation/cn_text_locator.py` line 90

```python
# 修改前
def locate_cn_candidates(text: str, max_candidates: int = 50) -> List[Dict]:

# 修改后
def locate_cn_candidates(text: str, max_candidates: int = 30) -> List[Dict]:
```

**同步位置**：`src/dashboard/views/p7_ai_annotation.py` 的 `_run_cn_pipeline` 中调用处同步修改。

**原理**：与美股一致，中文关键词定位器已按 tier（strongest > strong > medium）排序，取前30个保留最强信号，剔除弱信号noise，减少约20K tokens输入。

### 3.2 D2：缓存持久化（A股pipeline新增）

**修改文件**：`src/dashboard/views/p7_ai_annotation.py`

**美股pipeline原有缓存逻辑**（v6.2已实施）：
- 缓存位置：`data/cache/ai_annotations/{TICKER}_{FY}_ai_raw.json`
- 缓存内容：DeepSeek原始输出 + 验真结果
- 命中缓存时：跳过步骤3（DeepSeek调用）和步骤4（验真）

**A股pipeline新增**（v6.3-CN同步）：
- 在 `_run_cn_pipeline` 的步骤②和③之间插入②.⑤缓存检查
- 与美股共用同一套 `_load_ai_cache` / `_save_ai_cache` 函数
- 仅"自动下载PDF"模式启用缓存，"上传PDF"模式不缓存（避免不同文件混淆）

**预期效果**：A股测试迭代速度从3-5分钟/次提升至10-30秒/次（缓存命中时）。

### 3.3 A2：验真加固（A股版四层排除）

**美股v6.2验真排除模式**（四层）：
1. Note 1 Organization 开头段落
2. Forward-Looking Statements 前瞻性声明
3. Risk Factors 中泛泛提及 useful life
4. MD&A 中讨论竞争/市场时顺带提到 useful life

**A股v6.3-CN验真排除模式**（三层，适配中文年报结构）：

| 排除模式 | 触发条件 | 保留条件 |
|---------|---------|---------|
| 公司概况误匹配 | 段落含"公司概况"/"公司简介"/"公司基本情况" | 同时含"折旧"/"摊销"/"减值"/"固定资产"/"使用寿命" |
| 风险提示泛谈 | 段落含"前瞻性"/"风险提示"/"免责声明" | 同时含"折旧"/"摊销"/"减值"/"固定资产" |
| 管理层讨论顺带 | 段落含"管理层讨论"/"经营情况讨论" | 同时含"折旧年限"/"使用寿命"/"预计使用年限"/"折旧方法"/"固定资产" |

**修改文件**：`src/dashboard/views/p7_ai_annotation.py` 的 `_run_cn_pipeline` 步骤④

**验真精度提升**：
- 修改前：仅检查 excerpt[:20] 是否在 full_text 中（简单子串匹配）
- 修改后：子串匹配 + 三层噪声排除，减少误报率

---

## 四、页面美观度优化

### 4.1 A股公司快速选择卡片

**位置**：P7页面输入区上方

**设计**：6列等宽卡片，每卡片包含：
- 公司名称（大字）
- 股票代码（小字）
- 点击后自动提示用户切换到"上传PDF"模式

**代码实现**：在 `render()` 函数开头插入：
```python
st.markdown("#### 🇨🇳 A股样本公司快速选择")
cn_companies = [
    {"code": "603019.SH", "name": "中科曙光", "industry": "高性能计算/服务器"},
    {"code": "603881.SH", "name": "数据港", "industry": "IDC/数据中心"},
    {"code": "688256.SH", "name": "寒武纪", "industry": "AI芯片"},
    {"code": "000977.SZ", "name": "浪潮信息", "industry": "服务器/云计算"},
    {"code": "002230.SZ", "name": "科大讯飞", "industry": "AI/语音技术"},
    {"code": "300738.SZ", "name": "奥飞数据", "industry": "IDC/云计算"},
]
cols = st.columns(6)
selected_cn = None
for i, comp in enumerate(cn_companies):
    with cols[i]:
        if st.button(f"{comp['name']}\n{comp['code']}", key=f"cn_quick_{comp['code']}", use_container_width=True):
            selected_cn = comp
```

### 4.2 技术说明更新

更新P7底部"技术说明（答辩备查）"，反映v6.3-CN优化内容：
- 关键词矩阵：A股候选数30（同步压缩）
- 验真逻辑：A股=子串包含检查+三层排除（公司概况/风险提示/管理层讨论）
- 缓存持久化：美股/A股均支持

---

## 五、修改文件清单

| 文件路径 | 修改内容 | 版本标记 |
|---------|---------|---------|
| `src/ai_annotation/cn_text_locator.py` | max_candidates 50→30 | v6.3-CN |
| `src/dashboard/views/p7_ai_annotation.py` | A股缓存持久化、验真加固（三层排除）、快速选择卡片、技术说明更新 | v3.1 |

---

## 六、后续建议

### 6.1 财报下载任务（需人工完成）

| 公司 | 代码 | 需下载文件 | 下载途径 |
|------|------|-----------|---------|
| 中科曙光 | 603019.SH | 2024年年度报告PDF | 巨潮资讯网 / 上交所官网 |
| 数据港 | 603881.SH | 2024年年度报告PDF | 巨潮资讯网 / 上交所官网 |
| 寒武纪 | 688256.SH | 2024年年度报告PDF | 巨潮资讯网 / 上交所官网 |
| 浪潮信息 | 000977.SZ | 2024年年度报告PDF | 巨潮资讯网 / 深交所官网 |
| 科大讯飞 | 002230.SZ | 2024年年度报告PDF | 巨潮资讯网 / 深交所官网 |
| 奥飞数据 | 300738.SZ | 2024年年度报告PDF | 巨潮资讯网 / 深交所官网 |

**下载步骤**：
1. 访问巨潮资讯网：http://www.cninfo.com.cn
2. 搜索股票代码 → 进入公司页面 → 定期报告
3. 找到"2024年年度报告"（发布时间通常在次年3-4月）
4. 下载PDF并保存到 `data/raw/cn/` 目录

### 6.2 AI pipeline验证任务

下载PDF后，在P7界面使用"A股年报（上传PDF）"模式，逐一验证六家公司的AI评分与现有人工标注的差异：
- 重点关注 D1（年限错配）和 D3（减值触发）
- 记录AI与人工评分的偏差，作为报告6.3的素材

### 6.3 报告素材

本备案可直接用于报告：
- **6.3节"系统迭代优化"**：描述从v6.2（美股）到v6.3-CN（A股）的优化路径
- **技术附录**：展示中美双市场pipeline的架构一致性
