#!/usr/bin/env python3
"""重写scorer_calculator.py，删除损坏的重复代码"""
import re

with open('D:/depreciation-risk-detection/src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第一个函数的结束位置（return (max_life, asset_type, confidence, baseline)）
# 然后删除从 line 323 开始的第二个损坏函数
lines = content.split('\n')

# 找到第一个正确函数的结束行号
first_func_end = -1
for i, line in enumerate(lines):
    if 'return (max_life, asset_type, confidence, baseline)' in line:
        first_func_end = i
        break

if first_func_end > 0:
    # 找到第二个损坏函数的起始位置（line 323: text_lower = text.lower()）
    # 我们需要保留到第一个函数结束，然后跳到_def _extract_life_years(
    second_func_start = -1
    for i in range(first_func_end + 1, len(lines)):
        if 'def _extract_life_years(' in lines[i]:
            second_func_start = i
            break
    
    if second_func_start > 0:
        # 保留lines[0:first_func_end+1]和lines[second_func_start:]
        new_lines = lines[:first_func_end + 1] + [''] + lines[second_func_start:]
        new_content = '\n'.join(new_lines)
        
        with open('D:/depreciation-risk-detection/src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Fixed! Removed corrupted duplicate function.")
    else:
        print("Could not find second function start")
else:
    print("Could not find first function end")
