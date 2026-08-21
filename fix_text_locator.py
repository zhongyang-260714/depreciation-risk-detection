#!/usr/bin/env python3
"""修复text_locator.py中的损坏代码"""

with open('D:/depreciation-risk-detection/src/ai_annotation/text_locator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到_extract_structured_sections函数开始位置
func_start = content.find('def _extract_structured_sections(html_text: str) -> List[Dict]:')
if func_start < 0:
    print("Function not found")
    exit(1)

# 找到下一个函数定义（locate_candidates）
next_func_pos = content.find('\ndef locate_candidates(', func_start + 1)
if next_func_pos < 0:
    print("Next function not found")
    exit(1)

# 构建新的函数（注意：使用原始字符串避免转义问题）
new_func = r'''def _extract_structured_sections(html_text: str) -> List[Dict]:
    """强制提取关键章节的结构化内容。
    
    提取以下高价值章节：
    1. Note 1 - 会计政策（特别是折旧政策部分）
    2. Note 4/6/11 - PP&E明细
    3. Item 1A - 风险因素（技术过时、竞争相关）
    4. Item 7 MD&A - 关键会计估计、CAPEX讨论
    5. Note 9/13 - 租赁承诺
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_text, "html.parser")
    
    # 移除 XBRL 和脚本标签
    for tag in soup.find_all(["ix:header", "ix:hidden", "ix:nonnumeric", "ix:numeric",
                              "ix:nonfraction", "script", "style", "head", "noscript", "meta", "link"]):
        tag.decompose()
    for tag in soup.find_all(True):
        if tag.name and (tag.name.startswith("ix-") or tag.name.startswith("ix:")):
            tag.decompose()
    
    structured = []
    full_text = soup.get_text(separator="\n", strip=True)
    lines = full_text.split("\n")
    
    # 关键章节标记模式（v2.4修复：更宽松匹配，跳过引用）
    section_markers = [
        # Note 1 - 会计政策（支持多种格式：点号、连字符、特殊字符、任意间隔）
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*(?:SUMMARY\s+OF\s*)?SIGNIFICANT\s+ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*ORGANIZATION\s+AND\s*(?:SUMMARY\s+OF\s*)?SIGNIFICANT\s+ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        (re.compile(r"NOTE\s+1\s*.{0,3}\s*ACCOUNTING\s+POLICIES", re.I), "Note 1 - Accounting Policies", 10000),
        # PP&E Note（支持Note 4/6/11）
        (re.compile(r"NOTE\s+[46]\s*.{0,3}\s*PROPERTY.*?EQUIPMENT", re.I), "PP&E Note", 8000),
        (re.compile(r"NOTE\s+11\s*.{0,3}\s*BALANCE\s+SHEET\s+COMPONENTS", re.I), "Balance Sheet Components", 6000),
        # Item 1A / Item 7
        (re.compile(r"ITEM\s+1A\s*.{0,3}\s*RISK\s*FACTORS", re.I), "Item 1A - Risk Factors", 12000),
        (re.compile(r"ITEM\s+7\s*.{0,3}\s*MANAGEMENT.*?DISCUSSION", re.I), "Item 7 - MD&A", 12000),
        # 其他关键Note
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*LEASES", re.I), "Leases Note", 6000),
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*COMMITMENTS", re.I), "Commitments Note", 5000),
        (re.compile(r"NOTE\s+\d+\s*.{0,3}\s*INTANGIBLE\s+ASSETS", re.I), "Intangible Assets Note", 5000),
    ]
    
    for pattern, section_name, max_chars in section_markers:
        # v2.4修复：查找所有匹配，跳过引用
        all_matches = list(pattern.finditer(full_text))
        for match in all_matches:
            start = match.start()
            # 检查前面100字符是否是引用
            before_text = full_text[max(0, start-100):start]
            is_reference = any(ref_word in before_text.lower() for ref_word in 
                              ["refer to", "see", "reference", "for further information", 
                               "for more information", "as discussed in", "described in"])
            
            if is_reference:
                continue  # 跳过引用，找下一个匹配
            
            # 找到实际的章节内容
            end = start + max_chars
            # 尝试找到下一个主要章节作为结束点
            for other_pattern, _, _ in section_markers:
                if other_pattern != pattern:
                    next_matches = list(other_pattern.finditer(full_text, start + 200))
                    for next_match in next_matches:
                        next_start = next_match.start()
                        next_before = full_text[max(0, next_start-100):next_start]
                        if not any(ref_word in next_before.lower() for ref_word in 
                                  ["refer to", "see", "reference", "for further information"]):
                            if next_start < end:
                                end = min(end, next_start)
                            break
            
            section_text = full_text[start:end].strip()
            if len(section_text) > 300:  # 至少300字符才是有效章节
                structured.append({
                    "text": section_text,
                    "tag": "structured_section",
                    "section_name": section_name,
                    "approx_line": full_text[:start].count("\n") + 1,
                })
            break  # 找到第一个非引用匹配就停止
    
    return structured


'''

new_content = content[:func_start] + new_func + content[next_func_pos:]

with open('D:/depreciation-risk-detection/src/ai_annotation/text_locator.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed text_locator.py")
