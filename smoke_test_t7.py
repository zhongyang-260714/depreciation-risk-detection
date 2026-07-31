"""T7 看板集成测试：真实执行 app.py 并逐页切换，验证五个页面全部无异常渲染。"""
from streamlit.testing.v1 import AppTest

APP = "src/dashboard/app.py"
PAGES = ["P1 · 总览热力图", "P2 · 公司画像", "P3 · 跨年轨迹", "P4 · 权重敏感性", "P5 · 方法论"]

at = AppTest.from_file(APP, default_timeout=120)
at.run()
assert not at.exception, f"外壳启动报错: {at.exception}"
print("✅ 外壳启动 OK")

for page in PAGES:
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, f"{page} 报错: {at.exception}"
    n_err = len(at.error)
    assert n_err == 0, f"{page} 页面出现 st.error: {[e.value for e in at.error]}"
    print(f"✅ {page} OK (markdown={len(at.markdown)}, plotly图表={len(at.get('plotly_chart')) if hasattr(at, 'get') else 'n/a'})")

# P2 交互：切换公司 selectbox 验证联动（用真实 ticker 原始值，AppTest 的 options 是格式化后的）
import sys
sys.path.insert(0, "src/dashboard")
from data_loader import load_cases

at.sidebar.radio[0].set_value("P2 · 公司画像").run()
tickers = sorted({c["ticker"] for c in load_cases()})
if len(at.selectbox) >= 2:
    for t in tickers[:3]:
        at.selectbox[0].set_value(t).run()
        assert not at.exception, f"P2 切换公司 {t} 报错: {at.exception}"
    print(f"✅ P2 公司联动 OK（共 {len(tickers)} 家公司）")

# P4 交互：切换公司 + 拖滑块
at.sidebar.radio[0].set_value("P4 · 权重敏感性").run()
if len(at.selectbox) >= 1:
    at.selectbox[0].set_value(tickers[0]).run()
    assert not at.exception, f"P4 切换公司报错: {at.exception}"
    if len(at.slider) >= 5:
        at.slider[0].set_value(0.5).run()
        assert not at.exception, f"P4 拖滑块报错: {at.exception}"
    print("✅ P4 滑块交互 OK")

print("\n🎉 T7 看板五个页面全部集成测试通过")
