import re
P = r"D:\depreciation-risk-detection\tmp\report_v41.txt"
lines = open(P, encoding='utf-8').read().split('\n')

def show(start, end, label):
    print("\n===== %s (L%d-L%d) =====" % (label, start, end))
    for i in range(start-1, min(end, len(lines))):
        print("[L%03d] %s" % (i+1, lines[i][:200]))

# 附录E team table
show(585, 600, "附录E 团队分工")
# NVIDIA data
print("\n===== NVIDIA mentions =====")
for i,ln in enumerate(lines):
    if re.search(r'NVIDIA|英伟达', ln):
        print("[L%03d] %s" % (i+1, ln[:200]))
# internal residue specific
print("\n===== 内部指令/笔误 专项 =====")
for i,ln in enumerate(lines):
    if re.search(r'修改要求|提交前|必填|待填|待完善|待验|待确认|pandas|3\.0\.3|3\.0\.2|Python 3|版本说明|changelog', ln):
        print("[L%03d] %s" % (i+1, ln[:200]))
# cover version area
show(1, 12, "封面/版本区")
