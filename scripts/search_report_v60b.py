import re, zipfile

TXT = r"D:\depreciation-risk-detection\tmp\report_v60_text.txt"
with open(TXT, encoding='utf-8') as f:
    text = f.read()
lines = text.split('\n')

def find(patterns, label, ctx=0):
    print("\n==== %s ====" % label)
    hits=0
    for i, ln in enumerate(lines):
        for p in patterns:
            if re.search(p, ln):
                lo=max(0,i-ctx); hi=min(len(lines),i+ctx+1)
                for j in range(lo,hi):
                    tag=">>" if j==i else "  "
                    print("%s L%04d: %s"%(tag,j+1,lines[j][:150]))
                hits+=1
                break
    if hits==0: print("(无命中)")

find([r'页码为预估值', r'请更新域', r'更新目录', r'字段', r'预估值'], "目录页码提示残留")
find([r'v4\.0|v4\.1|V4\.0|V4\.1', r'4\.0\b'], "旧版本号残留")
find([r'扩样', r'扩展样本', r'新增.*观测', r'20\s*个观测', r'50\s*个'], "扩样/扩展样本口径")
find([r'图\s*[0-9]', r'见[图图表]', r'图表', r'雷达图', r'热力图', r'折线图', r'柱状图', r'散点'], "图表引用")
find([r'A股|科创版|六家|6家.*样本|中国验证', r'训练集|验证集'], "中国A股验证口径")
find([r'数据来源|样本选择|筛选', r'SEC|EDGAR|10-K'], "数据来源")

# check docx media
DOCX = r"D:\科创企业资产折旧算法\XH-202626_科创企业特有风险的识别与管理_v6.0_final.docx"
z = zipfile.ZipFile(DOCX)
media = [n for n in z.namelist() if n.startswith('word/media/')]
print("\n==== docx 内嵌媒体文件 ====")
print("media count:", len(media))
for m in media[:30]:
    print("  ", m, z.getinfo(m).file_size)
