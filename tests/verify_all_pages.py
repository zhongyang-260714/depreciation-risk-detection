# -*- coding: utf-8 -*-
"""临时验证脚本：用 AppTest 逐页真实执行 app.py（无浏览器）"""
from streamlit.testing.v1 import AppTest

APP = "src/dashboard/app.py"
PAGES = ["P1 · 总览热力图", "P2 · 公司画像", "P3 · 跨年轨迹",
         "P4 · 权重敏感性", "P5 · 方法论", "P6 · 实时评分演示"]

for page in PAGES:
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception, f"初始加载报错: {at.exception}"
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, f"{page} 渲染报错: {at.exception}"
    print(f"OK  {page} 渲染成功")

# P6 额外验证：点击「运行实时评分」走完整推理链路
at = AppTest.from_file(APP, default_timeout=120)
at.run()
at.sidebar.radio[0].set_value("P6 · 实时评分演示").run()
assert not at.exception
btn = [b for b in at.button if "运行实时评分" in b.label]
assert btn, "P6 未找到运行按钮"
btn[0].click().run()
assert not at.exception, f"P6 推理报错: {at.exception}"
assert len(at.metric) >= 1, "P6 推理后未显示评分指标"
print(f"OK  P6 完整推理链路成功（模型评分 {at.metric[0].value}）")
print("ALL PAGES PASSED")
