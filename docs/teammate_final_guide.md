# 队友操作指南（最终版）

> 目标：把 GitHub 仓库下载到本地，并用 VSCode 跑通 Streamlit 界面。
> 前提：Git 已装好，VSCode 已装好，Streamlit 已装好。

---

## 第 1 步：确认电脑有没有 D 盘

打开"此电脑"，看看有没有 **D 盘**。

- **如果有 D 盘** → 继续按下面步骤（推荐，和负责人路径统一）
- **如果没有 D 盘** → 把下面所有 `D:` 改成 `C:` 即可

---

## 第 2 步：打开 VSCode 终端

1. 打开 VSCode
2. 顶部菜单 → `Terminal` → `New Terminal`
3. 底部弹出终端面板

---

## 第 3 步：克隆仓库（下载代码）

在 VSCode 终端里**逐行输入**，每行输完按回车：

```bash
cd /d D:/
git clone https://github.com/zhongyang-260714/depreciation-risk-detection.git
```

**成功标志**：终端显示类似 `Receiving objects: 100% ... done`，D 盘出现 `depreciation-risk-detection` 文件夹。

**如果报错 `git 不是内部命令`** → 关闭 VSCode 重新打开（Git 刚装好，VSCode 没刷新环境变量）。

---

## 第 4 步：用 VSCode 打开项目

VSCode → 顶部菜单 `File` → `Open Folder` → 找到 `D:/depreciation-risk-detection` → 点击 `Select Folder`。

此时左侧文件栏应该显示：
```
depreciation-risk-detection
├── config/
├── data/
├── docs/
├── notebooks/
├── src/
│   ├── api/
│   ├── dashboard/
│   │   └── app.py
│   ├── features/
│   ├── models/
│   └── nlp/
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 第 5 步：进入项目目录

在 VSCode 终端里输入：

```bash
cd /d D:/depreciation-risk-detection
```

**确认终端路径变成了**：
```
PS D:\depreciation-risk-detection>
```

---

## 第 6 步：运行 Streamlit

在终端里输入：

```bash
streamlit run src/dashboard/app.py
```

**成功标志**：
1. 终端显示：
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   ```
2. 浏览器自动弹出，显示 **"科创企业资产折旧风险识别系统"**

---

## 如果报错

| 报错 | 原因 | 解决 |
|------|------|------|
| `streamlit 不是内部命令` | 之前装的 Streamlit 不在当前 Python 环境 | `pip install streamlit` 再试 |
| `ModuleNotFoundError: No module named 'pandas'` | 缺少依赖 | `pip install pandas numpy matplotlib plotly pyyaml` |
| `FileNotFoundError: [Errno 2] No such file or directory: 'src/dashboard/app.py'` | 终端不在项目根目录 | 重新执行 `cd /d D:/depreciation-risk-detection` |
| `Permission denied` | 权限不足 | 以管理员身份运行 VSCode |

---

## 验证成功后的操作

浏览器打开后：
1. 左侧输入股票代码（如 `META`）
2. 修改几个财务数字
3. 点击左下角 **「开始分析」**
4. 右侧显示风险评分、雷达图、预警信息

**截图发给负责人确认。**

---

## 之后改代码怎么上传？

改完 `app.py` 后，在 VSCode 终端里：

```bash
git add .
git commit -m "描述你改了什么"
git push origin main
```

**第一次 push 时 VSCode 会弹窗让你登录 GitHub**，按提示授权即可。

---

> 负责人路径：`D:\depreciation-risk-detection`  
> 队友路径：`D:\depreciation-risk-detection`（统一）  
> 有任何报错截图发到群里。
