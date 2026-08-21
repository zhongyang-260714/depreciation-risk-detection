with open('src/ai_annotation/scorer_calculator.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = "d1_result = _extract_life_years(candidates, full_text=full_html); print(f[DEBUG] D1 extraction result: {d1_result})"
new = "d1_result = _extract_life_years(candidates, full_text=full_html); print(f'[DEBUG] D1 extraction result: {d1_result}')"

if old in content:
    content = content.replace(old, new, 1)
    with open('src/ai_annotation/scorer_calculator.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed syntax error")
else:
    print("Pattern not found, checking actual content...")
    idx = content.find("d1_result = _extract_life_years")
    if idx >= 0:
        print(repr(content[idx:idx+120]))
