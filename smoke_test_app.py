"""冒烟测试：用 Streamlit 官方 AppTest 在无浏览器环境下真实执行 app.py 的三种状态。"""
from streamlit.testing.v1 import AppTest

APP = "src/dashboard/app.py"

# 1. 初始界面（单公司分析 · 未点击按钮）
at = AppTest.from_file(APP, default_timeout=60)
at.run()
assert not at.exception, f"初始界面报错: {at.exception}"
print("✅ 初始界面 OK | 标题块:", len(at.markdown), "| 按钮:", len(at.button))

# 2. 案例库模式
at2 = AppTest.from_file(APP, default_timeout=60)
at2.run()
at2.sidebar.radio[0].set_value("📚 案例库（已标注 5 家）").run()
assert not at2.exception, f"案例库报错: {at2.exception}"
opts = list(at2.selectbox[0].options)
print("✅ 案例库 OK | 可选公司:", opts)
assert len(opts) == 5, "应当加载 5 家标注公司"
# 切换每一家公司都跑一遍
for t in opts:
    at2.selectbox[0].set_value(t).run()
    assert not at2.exception, f"案例 {t} 报错: {at2.exception}"
print("✅ 5 家公司页面全部可渲染")

# 3. 点击「开始分析」跑完整分析流程
at3 = AppTest.from_file(APP, default_timeout=60)
at3.run()
at3.sidebar.text_input[0].set_value("NVDA")
at3.sidebar.text_area[0].set_value(
    "ITEM 1A. RISK FACTORS. Our business faces risks related to depreciation, "
    "impairment and amortization of long-lived assets. Rapid technology change "
    "may cause our equipment to become obsolete, leading to impairment charges. "
    "Uncertain market conditions add pressure and risk of decline."
)
at3.sidebar.button[0].click().run()
assert not at3.exception, f"分析流程报错: {at3.exception}"
print("✅ 分析流程 OK | 指标卡片:", len(at3.metric), "| Tab:", len(at3.tabs))
assert len(at3.metric) >= 4, "结果区应至少显示 4 个指标"

print("\n🎉 全部冒烟测试通过")
