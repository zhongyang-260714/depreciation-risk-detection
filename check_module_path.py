import sys
sys.path.insert(0, 'D:/depreciation-risk-detection')

from src.ai_annotation import scorer_calculator
print(f"scorer_calculator 模块路径: {scorer_calculator.__file__}")

# 检查 _extract_life_years_from_context 的源代码行数
import inspect
lines, _ = inspect.getsourcelines(scorer_calculator._extract_life_years_from_context)
print(f"_extract_life_years_from_context 函数行数: {len(lines)}")
print(f"第一行: {lines[0].strip()}")
print(f"第二行: {lines[1].strip() if len(lines) > 1 else 'N/A'}")
