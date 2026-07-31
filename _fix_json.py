import json

# Fix GOOGL 2022
with open('D:/depreciation-risk-detection/data/annotated/GOOGL_2022_annotation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['financial_highlights']['depreciation_expense_millions'] = 13475
data['financial_highlights']['depreciation_expense_note'] = (
    "Depreciation of property and equipment $13,475M (pure depreciation, per GOOGL 2023 10-K cash flow statement comparative disclosure). "
    "GOOGL 2022 10-K Note 1 (HTML line 2163) reports $15.3B for depreciation AND impairment combined; "
    "the difference of ~$1,825M is impairment expense, which should not be included in this field."
)

with open('D:/depreciation-risk-detection/data/annotated/GOOGL_2022_annotation.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Fix TSLA 2024
with open('D:/depreciation-risk-detection/data/annotated/TSLA_2024_annotation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['financial_highlights']['net_income_millions'] = 7153
data['financial_highlights']['net_income_note'] = (
    "Net income $7,153M (Consolidated Statements of Comprehensive Income, raw text line 3805)."
)

with open('D:/depreciation-risk-detection/data/annotated/TSLA_2024_annotation.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done")
