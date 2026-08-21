# clear_cache.py - 清除 Streamlit + Python 缓存
# 用法: 在终端执行 python clear_cache.py

import os, shutil

print("[1/3] 停止 Streamlit...")
os.system("taskkill /F /IM streamlit.exe 2>nul")

print("[2/3] 清除 Python 缓存...")
for root, dirs, files in os.walk('.'):
    for d in dirs:
        if d == '__pycache__':
            try: shutil.rmtree(os.path.join(root, d))
            except: pass
    for f in files:
        if f.endswith('.pyc'):
            try: os.remove(os.path.join(root, f))
            except: pass
print("  完成")

print("[3/3] 验证规则引擎...")
with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    code = f.read()
    if 'if 1.5 <= max_y <= 30:' in code:
        print("  规则引擎 v3 已就绪")
    else:
        print("  警告: 代码可能未更新")

print("\n现在启动 Streamlit:")
print("  streamlit run src/dashboard/app.py")
