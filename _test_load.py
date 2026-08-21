from pathlib import Path
import sys
sys.path.insert(0, r'D:\depreciation-risk-detection')
sys.path.insert(0, r'D:\depreciation-risk-detection\src')
sys.path.insert(0, r'D:\depreciation-risk-detection\src\ai_annotation')

from edgar_fetcher import load_10k_html

try:
    text = load_10k_html('GOOGL', 2023, cache_dir=Path(r'D:\depreciation-risk-detection\data\raw'))
    print(f'成功！文本长度: {len(text)}')
except Exception as e:
    print(f'失败: {e}')
