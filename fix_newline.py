import re

with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 _extract_life_years_from_context 函数并在 text.lower() 前添加换行符处理
old = '''def _extract_life_years_from_context(text: str) -> Optional[Tuple[float, str, str, float]]:
    text_lower = text.lower()'''

new = '''def _extract_life_years_from_context(text: str) -> Optional[Tuple[float, str, str, float]]:
    text = text.replace('\\n', ' ').replace('\\r', ' ')
    text_lower = text.lower()'''

if old in content:
    content = content.replace(old, new, 1)
    with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("修复成功：已添加换行符处理")
else:
    print("未找到目标代码，可能已经修复或文件结构变化")
    # 打印函数定义附近的内容用于调试
    idx = content.find('def _extract_life_years_from_context')
    if idx >= 0:
        print("找到函数位置，附近内容：")
        print(repr(content[idx:idx+120]))
