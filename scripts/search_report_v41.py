import re
P = r"D:\depreciation-risk-detection\tmp\report_v41.txt"
lines = open(P, encoding='utf-8').read().split('\n')

def grep(patterns, label, ctx=0):
    print("\n########## %s ##########" % label)
    pats = [re.compile(p) for p in patterns]
    for i, ln in enumerate(lines):
        if any(p.search(ln) for p in pats):
            pre = lines[max(0,i-ctx)] if ctx else ''
            print("[L%03d] %s" % (i+1, ln[:200]))

# Cover / title
grep([r'折旧错配', r'赛题编号', r'揭榜挂帅', r'挑战杯'], '封面/标题信息', ctx=0)
# Team
grep([r'团队', r'姓名', r'专业', r'成员', r'分工', r'组长', r'指导'], '团队/分工信息')
# GitHub
grep([r'[Gg]it[Hh]ub', r'开源', r'代码'], 'GitHub/开源声明')
# Oracle
grep([r'[Oo]racle', r'折旧年限', r'延长至', r'行号'], 'Oracle/折旧年限/行号')
# Internal residue
grep([r'待填', r'待确认', r'修改要求', r'提交前', r'待办', r'【', r'内部', r'作者'], '内部指令/占位残留')
# pandas
grep([r'pandas', r'Python', r'版本'], '环境/版本')
# Key data
grep([r'NVIDIA', r'5D-DRS', r'5D', r'权重', r'面板', r'样本', r'评分模型', r'维度'], '核心方法/数据')
# Conclusions
grep([r'结论', r'贡献', r'局限', r'展望', r'启示'], '结论/贡献/局限')
# Appendix
grep([r'附录', r'附录E', r'附录A', r'附录B', r'附录F'], '附录')
