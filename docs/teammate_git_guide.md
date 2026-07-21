# 队友科普：Git Bash 是什么？项目里需要用到吗？

> 写给队友（计算机科学方向，负责前端/后端开发）
> 核心结论：**你可以不用记 Git 命令，但你需要知道怎么把代码传到 GitHub。**

---

## 一、Git Bash 是什么？

简单说：**Git Bash 是一个命令行工具，让你能在 Windows 上运行 Linux 风格的命令。**

类比理解：
| 你熟悉的工具 | 类比 | Git Bash 的作用 |
|-------------|------|----------------|
| 微信文件传输助手 | 发文件给别人 | Git Bash 是"发代码给 GitHub"的命令行版本 |
| VSCode 保存文件 | `Ctrl + S` | Git Bash 是"保存代码到云端仓库"的快捷键 |
| 百度网盘同步盘 | 自动同步文件 | Git Bash 让你手动控制"哪些代码要同步、什么时候同步" |

**Git Bash 本身不写代码、不运行代码**，它只是：
- 把本地代码**上传**到 GitHub
- 把 GitHub 上的新代码**下载**到本地
- 记录代码**修改历史**（谁改了什么、什么时候改的）

---

## 二、为什么项目要用 GitHub + Git Bash？

因为你们两个人要写同一个项目：

### 不用 GitHub 的问题
- 你改了一个文件，队友也在改同一个文件 → 互相覆盖，代码丢了
- 你写了一个功能，后来发现有 bug → 回不到之前能用的版本
- 比赛前一周改崩了 → 没有备份，完蛋

### 用 GitHub 的好处
- ✅ 每人改自己的部分，自动合并
- ✅ 改错了随时回退到上一个能用的版本
- ✅ 比赛提交时，评委可以直接访问你们的代码仓库
- ✅ 所有修改都有记录，谁改了什么一清二楚

---

## 三、队友（前端/后端开发）需要用到的 Git 命令

**其实只需要记住 4 个：**

```bash
# 1. 下载项目（第一次用）
git clone https://github.com/zhongyang-260714/depreciation-risk-detection.git

# 2. 查看自己改了哪些文件
git status

# 3. 把改好的代码传上去（每次写完功能后）
git add .
git commit -m "描述你改了什么"
git push origin main

# 4. 把队友的新代码拉下来（每天早上开工前）
git pull origin main
```

**就这四步。记不住也没关系，下面有更简单的方法。**

---

## 四、如果你不想用命令行，有更简单的办法

### 方案 A：VSCode 内置 Git（推荐）

VSCode 左边有一个"源代码管理"图标（分支符号），点击后：
- 能看到你改了哪些文件
- 输入描述 → 点击 ✅ 提交
- 点击 ↑ 推送（上传）/ ↓ 拉取（下载）

**完全不用记命令，点鼠标就行。**

### 方案 B：GitHub Desktop（最简单）

官网下载：https://desktop.github.com/

界面像网盘一样直观：
- 左边看改了哪些文件
- 中间写描述
- 点击"Commit" → "Push"

**适合完全不想碰命令行的队友。**

---

## 五、Git Bash 到底重不重要？

| 场景 | 是否需要 Git Bash | 替代方案 |
|------|------------------|----------|
| 写前端代码（Streamlit/HTML/CSS） | ❌ 不需要 | VSCode 直接写 |
| 运行 Python 程序 | ❌ 不需要 | VSCode 终端 / CMD |
| 把代码传到 GitHub | ✅ 可以用 | VSCode Git 插件 / GitHub Desktop |
| 解决代码冲突 | ✅ 需要命令行 | 让负责人帮忙处理 |

**结论：队友作为前端开发，Git Bash 不是必须的。** 用 VSCode 的 Git 插件或者 GitHub Desktop 完全够用。

---

## 六、队友现在该做什么？

**第 1 步：把代码拿到本地**

选一个你喜欢的方式：
- **方式 A（命令行）**：打开 Git Bash，输入 `git clone https://github.com/zhongyang-260714/depreciation-risk-detection.git`
- **方式 B（GitHub Desktop）**：打开软件 → File → Clone Repository → 粘贴上面的链接
- **方式 C（直接下载）**：打开 GitHub 网页 → 点击绿色 Code 按钮 → Download ZIP → 解压

**第 2 步：安装依赖**

打开终端（VSCode 里按 `Ctrl + ~`），输入：
```bash
pip install streamlit pandas numpy matplotlib plotly
```

**第 3 步：运行项目**
```bash
streamlit run src/dashboard/app.py
```

**第 4 步：开始写代码**

改 `src/dashboard/app.py`，改完后用 VSCode Git 插件或者 GitHub Desktop 上传。

---

## 七、遇到冲突怎么办？

如果你上传时提示 "merge conflict"（合并冲突），**不要自己硬解决**，直接告诉负责人：

> "我 push 的时候报冲突了，帮我看一下。"

负责人用 Git Bash 几行命令就能搞定，你自己折腾可能越搞越乱。

---

> **一句话总结：Git Bash 是"快递小哥"，负责把代码送到 GitHub。你可以不用亲自当快递小哥（用 VSCode/GitHub Desktop 代替），但你要知道"快递"这件事必须做。**
