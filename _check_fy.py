import json, glob
for f in sorted(glob.glob(r'D:\depreciation-risk-detection\data\annotated\GOOGL*.json')):
    d = json.load(open(f, encoding='utf-8'))
    print(f.split('\\')[-1], '-> ticker:', d['company']['ticker'], 'fy:', d['company']['fiscal_year'])
