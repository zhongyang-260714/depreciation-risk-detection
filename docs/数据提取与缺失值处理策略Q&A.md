# 数据提取与缺失值处理策略（Q&A）

> **回答三个核心问题**：
> 1. 不同公司指标不一致，怎么统一算法？
> 2. 数据提取是否靠 Python 自动化？
> 3. 缺失值怎么处理？

---

## 一、你的理解对吗？

**基本正确，但有三个关键补充**：

| 你的理解 | 正确性 | 补充说明 |
|---------|--------|---------|
| 指标从 9 个扩充到 45 个 | ✅ 正确 | Tier 1（25个）必须，Tier 2/3 是加分项 |
| 分三级（必须/建议/可选） | ✅ 正确 | 优先级清晰，避免胡子眉毛一把抓 |
| 数据提取靠 Python 自动化 | ✅ 正确 | 队友写脚本，你负责标注 |
| 不同公司指标不一致 → 算法不统一 | ⚠️ 部分正确 | **有标准处理方案**，见下文 |

---

## 二、问题1：不同公司指标不一致，怎么统一算法？

这是数据科学中最常见的问题：**缺失值处理**。

### 2.1 为什么指标会不一致？

| 原因 | 例子 | 发生频率 |
|------|------|---------|
| **公司规模不同** | 小公司不披露员工人数 | 常见 |
| **行业差异** | 软件公司没有"在建工程" | 常见 |
| **会计政策差异** | 有的公司合并 D&A，有的分开 | 非常常见 |
| **披露粒度不同** | 有的公司给固定资产明细，有的只给合计 | 常见 |
| **并购影响** | 收购当年商誉激增，下一年正常 | 偶发 |
| **美国 vs 中国** | A 股无形资产明细披露不足 | 常见 |

### 2.2 缺失值的三种类型

```
类型A：结构性缺失（Structural Missing）
  → 这家公司本来就没有这个指标
  → 例：软件公司没有"在建工程"
  → 处理：填 0 或特殊标记

类型B：披露性缺失（Disclosure Missing）
  → 公司有这个指标，但没披露
  → 例：小公司不披露员工人数
  → 处理：用行业平均值填充

类型C：提取失败（Extraction Failure）
  → 脚本没提取到，但数据其实存在
  → 例：XBRL 标签名称不一致
  → 处理：人工补录或改进脚本
```

### 2.3 统一算法的核心策略：缺失值填充

**策略 1：填 0（适用于结构性缺失）**

```python
# 例：Meta 没有"在建工程"，填 0
if company['construction_in_progress'] is None:
    company['construction_in_progress'] = 0
```

适用场景：
- 公司没有这类资产（如软件公司没有在建工程）
- 公司没有发生这类交易（如当年没有资产减值）

**策略 2：行业平均值填充（适用于披露性缺失）**

```python
# 例：小公司不披露员工人数，用行业平均填充
industry_avg_employees = 50000  # 科技行业平均
df['employee_count'] = df['employee_count'].fillna(industry_avg_employees)
```

适用场景：
- 员工人数、有效税率、毛利率等
- 注意：不能用行业平均填**核心指标**（如折旧、收入）

**策略 3：中位数填充（Robust 方法）**

```python
# 用同行业、同规模公司的中位数填充
peer_median = df[df['sector'] == 'Technology']['capex_to_revenue'].median()
df['capex_to_revenue'] = df['capex_to_revenue'].fillna(peer_median)
```

适用场景：
- CAPEX/收入、研发强度等同行业可比指标
- 比平均值更抗极端值影响

**策略 4：回归预测填充（高级方法）**

```python
# 用其他指标预测缺失值
# 例：用 "收入" 和 "净利润" 预测 "员工人数"
from sklearn.linear_model import LinearRegression

# 已知数据训练模型
known = df[df['employee_count'].notna()]
X = known[['revenue', 'net_income']]
y = known['employee_count']
model = LinearRegression().fit(X, y)

# 预测缺失值
missing = df[df['employee_count'].isna()]
df.loc[missing.index, 'employee_count'] = model.predict(missing[['revenue', 'net_income']])
```

适用场景：
- 有多个相关指标时，用已知指标预测缺失指标
- 精度高于简单平均值

**策略 5：标记缺失 + 模型处理（最佳实践）**

```python
# 不仅填充，还要告诉模型"这个值是填充的"
df['capex_ppe'] = df['capex_ppe'].fillna(0)
df['capex_ppe_missing'] = df['capex_ppe'].isna().astype(int)  # 1=缺失, 0=正常
```

这样模型知道：
- 这个公司的 CAPEX 是 0（或填充值）
- 但这个值**不可靠**（标记为缺失）

### 2.4 具体到我们的项目

| 指标 | 缺失概率 | 处理方案 |
|------|---------|---------|
| 折旧费用 | 低 | 所有美国公司都有，缺失 = 提取失败 → 人工补录 |
| 摊销费用 | 中 | 有些公司合并 D&A → 如果缺失，设为 0 |
| 固定资产明细 | 高 | 不是所有公司都给明细 → 缺失填 0，用合计替代 |
| 在建工程 | 中 | 服务/软件公司可能没有 → 缺失填 0 |
| 员工人数 | 中 | 小公司不披露 → 行业平均填充 |
| 有效税率 | 低 | 所有公司都有，缺失 = 计算：所得税/税前利润 |
| R&D 资本化 | 高 | 大部分美国科技公司不资本化 → 缺失填 0 |
| 资产减值损失 | 高 | 不是每年都有 → 缺失填 0 |
| 服务器折旧占比 | 高 | 极少公司披露 → 用行业平均 60% 填充 |
| 使用寿命 | 低 | 所有公司都披露 → 缺失 = 提取失败 → 人工补录 |

### 2.5 最关键的原则

> **核心指标（Tier 1）不能缺失，否则这家公司不能用。**

**Tier 1 指标（25个）的缺失处理**：

```
如果 Tier 1 指标缺失：
  1. 先检查是否是提取失败（类型C）→ 改进脚本或人工补录
  2. 如果是结构性缺失（类型A）→ 用 0 填充
  3. 如果是披露性缺失（类型B）→ 用行业平均填充
  4. 如果无法填充 → 这家公司从训练集中剔除
```

**为什么可以剔除？**
- 我们计划标注 20-30 家公司
- 如果 1-2 家因为数据缺失被剔除，不影响模型训练
- 比强行填充错误数据要好得多

---

## 三、问题2：数据提取靠 Python 自动化？

**是的，完全正确。**

### 3.1 分工明确

| 角色 | 任务 | 工具 | 产出 |
|------|------|------|------|
| **队友** | 写 Python 脚本，自动从 SEC EDGAR 下载 10-K，提取所有指标 | Python + requests + BeautifulSoup/regex | JSON 数据文件 |
| **你** | 阅读 10-K 的 Risk Factors 和附注，人工判断风险等级，给出评分 | 人眼 + 专业知识 | 标注结果（JSON） |

### 3.2 为什么必须自动化？

**假设手工提取 1 家公司需要 2 小时**：

| 公司数量 | 手工时间 | 自动化时间 |
|---------|---------|-----------|
| 1 家 | 2 小时 | 脚本写好后 5 分钟 |
| 5 家 | 10 小时 | 25 分钟 |
| 10 家 | 20 小时 | 50 分钟 |
| 20 家 | 40 小时 | 1.7 小时 |

**更重要的是**：自动化保证了**格式统一**和**错误可追溯**。

### 3.3 自动化流程

```
输入：公司代码列表（如 ['META', 'GOOGL', 'MSFT', 'AMZN']）
  ↓
Step 1: 下载 10-K
  - 访问 SEC EDGAR API
  - 下载 HTML/XBRL 文件
  - 保存到 data/raw/{ticker}_{year}_10k.html
  ↓
Step 2: 解析 XBRL 标签
  - 用 BeautifulSoup 解析 HTML
  - 查找 us-gaap:XXX 标签
  - 提取数值 + 单位 + 财年
  ↓
Step 3: 解析附注文本
  - 用正则表达式匹配 "useful life"
  - 提取 "4-5 years" 等文本
  - 解析表格（PP&E Schedule）
  ↓
Step 4: 验证数据完整性
  - 检查 Tier 1 指标是否全部提取
  - 标记缺失值
  - 输出验证报告
  ↓
输出：data/extracted/{ticker}_{year}.json
```

### 3.4 人工什么时候介入？

自动化**不是万能的**，以下情况需要人工：

| 场景 | 人工任务 | 为什么机器做不到 |
|------|---------|---------------|
| XBRL 标签名称不一致 | 检查并映射正确的标签 | 不同公司用不同标签名 |
| 附注表格解析失败 | 手动复制粘贴 | 表格格式千差万别 |
| 使用寿命是文本（"4-5 years"） | 手动提取并标准化 | NLP 可能有歧义 |
| Risk Factors 文本分析 | 人工判断风险等级 | 需要专业知识和语境理解 |
| 数据异常（如负数折旧） | 人工核实 | 可能是提取错误 |
| 缺失值处理决策 | 判断是类型A/B/C | 需要业务知识 |

**理想的分工比例**：
- 队友：80% 自动化提取 + 20% 人工修复
- 你：0% 数据提取 + 100% 风险标注

---

## 四、问题3：统一算法的具体实现

### 4.1 数据结构标准化

**所有公司输出统一的 JSON 格式**，缺失值用 `null` 标记：

```json
{
  "balance_sheet": {
    "total_assets": 229623,
    "ppe_net": 96587,
    "servers_network_gross": null,  // 这家公司没披露明细
    ...
  }
}
```

### 4.2 缺失值预处理脚本

```python
# 在训练模型前，运行预处理脚本
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

def preprocess_data(df):
    """缺失值预处理"""
    
    # 1. 结构性缺失 → 填 0
    zero_fill_cols = [
        'construction_in_progress', 'impairment_loss', 
        'rd_capitalized', 'ppe_sales_proceeds'
    ]
    df[zero_fill_cols] = df[zero_fill_cols].fillna(0)
    
    # 2. 行业平均值填充
    industry_cols = ['employee_count', 'effective_tax_rate']
    for col in industry_cols:
        industry_mean = df.groupby('sector')[col].transform('mean')
        df[col] = df[col].fillna(industry_mean)
    
    # 3. 中位数填充（同行业）
    median_cols = ['capex_to_revenue', 'rd_intensity']
    for col in median_cols:
        industry_median = df.groupby('sector')[col].transform('median')
        df[col] = df[col].fillna(industry_median)
    
    # 4. 核心指标缺失 → 剔除
    core_cols = ['depreciation', 'revenue', 'net_income', 'ppe_net']
    df = df.dropna(subset=core_cols)
    
    return df
```

### 4.3 模型训练时的缺失值处理

XGBoost 和 LightGBM 本身**支持缺失值**，不需要填充：

```python
import xgboost as xgb

# XGBoost 自动处理缺失值
model = xgb.XGBClassifier(
    missing=np.nan,  # 告诉模型这是缺失值标记
    # ... 其他参数
)

# 直接传入含 NaN 的数据
model.fit(X_train, y_train)
```

**XGBoost 处理缺失值的原理**：
- 训练时，模型会学习"缺失值应该往左走还是往右走"
- 自动找到缺失值的最优分裂方向
- 不需要人工填充

**但要注意**：
- 只有 XGBoost/LightGBM 支持缺失值
- 如果后续用神经网络或线性模型，必须填充

### 4.4 我们的推荐方案

```
Phase 1（现在）：
  - 队友写脚本提取 Tier 1 指标
  - 用 Meta 2023 验证脚本正确性
  - 标记缺失值类型（A/B/C）

Phase 2（下周）：
  - 批量提取 10-20 家公司
  - 运行缺失值预处理脚本
  - 人工补录提取失败的指标
  - 剔除无法补录的公司

Phase 3（8月初）：
  - 生成最终训练数据集（JSON → CSV）
  - 训练 XGBoost 模型（利用其缺失值处理能力）
  - 交叉验证模型效果
```

---

## 五、一句话总结

| 问题 | 答案 |
|------|------|
| 指标不一致怎么办？ | **有标准处理方案**：填0、行业平均、中位数、回归预测、标记缺失 |
| 数据提取靠自动化吗？ | **是的**，队友写 Python 脚本，你只管标注 |
| 缺失值怎么处理？ | **Tier 1 核心指标不能缺**，Tier 2/3 可以用填充策略 |
| 公司数据不全就剔除？ | **可以**，20-30 家的训练集，剔除 2-3 家不影响 |
| XGBoost 支持缺失值？ | **支持**，自动学习最优处理方向 |

**你的理解完全正确，只是需要补上"缺失值处理"这一课。这恰恰是数据科学的核心能力之一。**

