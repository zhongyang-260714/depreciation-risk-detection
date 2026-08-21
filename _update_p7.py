#!/usr/bin/env python3
"""Script to update P7 page from 6 to 10 companies."""

import re
from pathlib import Path

FILE = Path("src/dashboard/views/p7_ai_annotation.py")
text = FILE.read_text(encoding="utf-8")

# 1. Update header version
old_header = '"""P7 · 智能标注（DeepSeek AI 驱动）v3.2'
new_header = '"""P7 · 智能标注（DeepSeek AI 驱动）v3.3'
text = text.replace(old_header, new_header)

# 2. Add v3.3 changelog after v3.2 line
old_changelog = 'v3.2 优化（A股财年定义与下载指南完善）：'
new_changelog = '''v3.3 优化（A股样本扩展 6→10 家）：
- A股样本公司从6家扩展至10家（新增：光环新网、海光信息、工业富联、润泽科技）
- 更新必要说明区域：10家公司下载清单、财年覆盖说明
- 同步P7页面文案：六家→十家

v3.2 优化（A股财年定义与下载指南完善）：'''
text = text.replace(old_changelog, new_changelog)

# 3. Update "新增六家公司" -> "新增十家公司"
text = text.replace('新增六家公司下载清单表格', '新增十家公司下载清单表格')

# 4. Update A股 company list
old_companies = '- **中国 A 股六家公司**：中科曙光（603019.SH）、数据港（603881.SH）、寒武纪（688256.SH）、浪潮信息（000977.SZ）、科大讯飞（002230.SZ）、奥飞数据（300738.SZ）'
new_companies = '- **中国 A 股十家公司**：中科曙光（603019.SH）、数据港（603881.SH）、寒武纪（688256.SH）、浪潮信息（000977.SZ）、科大讯飞（002230.SZ）、奥飞数据（300738.SZ）、光环新网（300383.SZ）、海光信息（688041.SH）、工业富联（601138.SH）、润泽科技（300442.SZ）'
text = text.replace(old_companies, new_companies)

# 5. Update PDF count
old_count = '工作量较大（6 家 × 3 年 = 18 份 PDF）'
new_count = '工作量较大（10 家 × 3 年 = 30 份 PDF）'
text = text.replace(old_count, new_count)

# 6. Update download list table title
old_title = '**六家公司所需下载清单：**'
new_title = '**十家公司所需下载清单：**'
text = text.replace(old_title, new_title)

# 7. Update download list DataFrame
old_df = '''        download_df = pd.DataFrame([
            {"公司": "中科曙光", "代码": "603019.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "数据港", "代码": "603881.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "寒武纪", "代码": "688256.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "浪潮信息", "代码": "000977.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "科大讯飞", "代码": "002230.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "奥飞数据", "代码": "300738.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
        ])'''
new_df = '''        download_df = pd.DataFrame([
            {"公司": "中科曙光", "代码": "603019.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "数据港", "代码": "603881.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "寒武纪", "代码": "688256.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "浪潮信息", "代码": "000977.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "科大讯飞", "代码": "002230.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "奥飞数据", "代码": "300738.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "✅（已有标注）"},
            {"公司": "光环新网", "代码": "300383.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "海光信息", "代码": "688041.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "工业富联", "代码": "601138.SH", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
            {"公司": "润泽科技", "代码": "300442.SZ", "2022年报": "✅", "2023年报": "✅", "2024年报": "🆕（待AI标注）"},
        ])'''
text = text.replace(old_df, new_df)

# 8. Update caption at bottom of expander
old_caption = '📌 注：六家公司的 FY2024 已有初步人工标注，下载后可通过 P7 进行 AI 验证与对照。FY2022 和 FY2023 用于 P3「跨年轨迹」展示（可选）。'
new_caption = '📌 注：前六家公司的 FY2024 已有初步人工标注，新增四家（光环新网、海光信息、工业富联、润泽科技）待 AI 标注。下载后可通过 P7 进行 AI 验证与对照。FY2022 和 FY2023 用于 P3「跨年轨迹」展示（可选）。'
text = text.replace(old_caption, new_caption)

# Write back
FILE.write_text(text, encoding="utf-8")
print("✅ P7 page updated successfully.")

# Verify changes
verify = FILE.read_text(encoding="utf-8")
assert "v3.3" in verify
assert "十家公司" in verify
assert "光环新网" in verify
assert "海光信息" in verify
assert "工业富联" in verify
assert "润泽科技" in verify
print("✅ All verifications passed.")
