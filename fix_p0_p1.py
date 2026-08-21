import re

with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# P0: 科技指纹词升级逻辑
# ============================================================

# 在 _detect_asset_type 函数末尾添加科技推断逻辑
old_detect_end = '''    if not scores:
        return "unknown"
    return max(scores, key=scores.get)'''

new_detect_end = '''    # P0: 科技行业指纹词升级逻辑（通用化，不硬编码公司名单）
    best_type = max(scores, key=scores.get) if scores else "unknown"
    if best_type in ("general_equipment", "unknown") and has_depreciation_context:
        tech_indicators = [
            "server", "datacenter", "data center", "cloud", "network",
            "computing", "hardware", "technology infrastructure",
            "digital infrastructure", "gpu", "processor", "semiconductor",
            "artificial intelligence", "machine learning", "ai accelerator",
            "networking", "information technology", "it equipment",
            "technology assets", "digital assets",
        ]
        if any(ind in text_lower for ind in tech_indicators):
            # 科技行业折旧上下文，将通用设备升级为服务器/数据中心设备
            return "server"

    if not scores:
        return "unknown"
    return best_type'''

if old_detect_end in content:
    content = content.replace(old_detect_end, new_detect_end, 1)
    print("P0: Added tech inference upgrade logic")
else:
    print("P0: Pattern not found")

# ============================================================
# P1: 多资产类型年限关联过滤
# ============================================================

# 在 _extract_life_years_from_context 中，提取 years 后添加过滤逻辑
old_years_filter = '''    if not years:
        return None

    # v5优化：取最大值而非中位数，风险由最长年限决定
    max_life = max(years)'''

new_years_filter = '''    if not years:
        return None

    # P1: 根据资产类型过滤不合理的年限（解决多资产类型段落中
    # buildings 的 30 年混入 manufacturing_equipment 的问题）
    if asset_type in ("server", "datacenter_equipment", "gpu_cluster"):
        years = [y for y in years if y <= 10]  # 服务器类设备通常 <= 10 年
    elif asset_type in ("manufacturing_equipment", "general_equipment"):
        years = [y for y in years if y <= 15]  # 生产设备通常 <= 15 年（排除 buildings 的 20-30 年）
    elif asset_type in ("software", "patent", "intangible"):
        years = [y for y in years if y <= 10]  # 软件/无形资产通常 <= 10 年
    elif asset_type in ("building", "land"):
        years = [y for y in years if y >= 10]  # 建筑物通常 >= 10 年

    if not years:
        return None

    # v5优化：取最大值而非中位数，风险由最长年限决定
    max_life = max(years)'''

if old_years_filter in content:
    content = content.replace(old_years_filter, new_years_filter, 1)
    print("P1: Added asset-type-based year filtering")
else:
    print("P1: Pattern not found")

with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nAll P0/P1 fixes applied.")
