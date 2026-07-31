import io

p = r"D:/depreciation-risk-detection/README.md"
with io.open(p, encoding="utf-8") as f:
    lines = f.readlines()

removed = []
out = []
for line in lines:
    s = line.rstrip("\n")
    if "孤立森林 / AutoEncoder" in s:
        removed.append(s.strip()); continue
    if "BERT/FinBERT" in s:
        removed.append(s.strip()); continue
    if "专利数据（USPTO / Google Patents / PatentsView）" in s:
        removed.append(s.strip()); continue
    out.append(line)

text = "".join(out)

repls = [
    # 删除“全球首个”过度承诺
    ("全球首个 AI 驱动的", "AI 驱动的"),
    # 删除“多模态数据融合”过度承诺
    ("通过多模态数据融合与可解释 AI", "通过可解释 AI"),
    # 校准与报告样本冲突的“五大/Amazon”
    ("全球五大科技巨头（Meta、Google、Amazon、Microsoft、Tesla）",
     "美国超大规模科技巨头（如 Meta、Google、Microsoft 等）"),
    # 删除“小型全球性金融危机”夸大表述
    ("可能触发**小型全球性金融危机**", "可能对全球资本市场造成显著冲击"),
    # 删除“已集成 CSMAR/巨潮资讯”数据源承诺
    ("• 财务报表（SEC EDGAR 10-K / CSMAR / 巨潮资讯）",
     "• 财务报表（SEC EDGAR 10-K）"),
    # LLM 用法对齐报告 3.6（辅助标注+人工复核）
    ("LLM 风险报告自动生成", "LLM 辅助标注 + 人工复核"),
    # 验证层公司对齐 ⑤ 实际验证对象
    ("（寒武纪、商汤等）", "（数据港、寒武纪、科大讯飞等）"),
]

for a, b in repls:
    if a not in text:
        print("WARN not found:", a)
    text = text.replace(a, b)

with io.open(p, "w", encoding="utf-8") as f:
    f.write(text)

print("REMOVED LINES:")
for r in removed:
    print("  -", r)
print("DONE")
