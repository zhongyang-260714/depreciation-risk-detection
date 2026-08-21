import re

TXT = r"D:\depreciation-risk-detection\tmp\report_v60_text.txt"
with open(TXT, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

def find(patterns, label, ctx=0):
    print("\n==== %s ====" % label)
    for i, ln in enumerate(lines):
        for p in patterns:
            if re.search(p, ln):
                lo = max(0, i-ctx); hi = min(len(lines), i+ctx+1)
                for j in range(lo, hi):
                    tag = ">>" if j==i else "  "
                    print("%s L%04d: %s" % (tag, j+1, lines[j][:160]))
                break

# 1. pandas version typo
find([r'pandas\s*3\.0\.3', r'pandas\s*[0-9]+\.[0-9]+\.[0-9]+'], "pandas 版本")
# 2. internal command / placeholder residue
find([r'待确认', r'待完善', r'待验', r'待补充', r'作者给作者', r'TODO', r'待办', r'占位', r'XXX', r'待填'], "内部指令/占位残留")
# 3. Oracle 5->8 rumor (must NOT appear)
find([r'5\s*[年年到到]\s*8\s*年', r'Oracle.*把.*延长.*到?\s*8\s*年', r'从\s*5\s*年.*到\s*8\s*年'], "Oracle 5->8 谣言残留")
# 4. NVIDIA numbers
find([r'NVIDIA.{0,30}1\.?33', r'英伟达.{0,30}1\.?33', r'[1-9]\.?[0-9]*\s*亿?美元', r'经营.*1[01]3', r'净.*1[01]3'], "NVDA 数据")
find([r'133', r'113'], "133/113 数字")
# 5. Oracle 5->6 correct
find([r'Oracle.{0,40}5.{0,5}6', r'经营费用.{0,20}7\.?33', r'7\.33'], "Oracle 5->6 / 7.33亿")
# 6. GitHub
find([r'[Gg]ithub', r'开源', r'[Pp]ublic', r'仓库'], "GitHub/开源声明")
# 7. team section E
find([r'团队分工', r'康中阳', r'程亚楠', r'金融数学', r'计算机科学与'], "团队分工(附录E)")
# 8. AI草拟 人工复核
find([r'AI\s*草拟', r'人工复核', r'双签'], "双签制")
# 9. Burry 1760
find([r'1760', r'26\.9', r'20\.8'], "Burry 1760/26.9/20.8")
# 10. 5D weights
find([r'0\.25|0\.20|0\.15', r'权重'], "5D 权重")
