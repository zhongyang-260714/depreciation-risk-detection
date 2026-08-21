from pathlib import Path

cache = Path(r'D:\depreciation-risk-detection\data\raw')
ticker = 'GOOGL'
fiscal_year = 2023

possible_names = [
    f"{ticker.upper()}_{fiscal_year}_10k.html",
    f"{ticker.lower()}_fy{fiscal_year}_10k.html",
    f"{ticker.lower()}_{fiscal_year}_10k.html",
    f"{ticker.upper()}_FY{fiscal_year}_10k.html",
]

for name in possible_names:
    cache_file = cache / name
    print(f"{name}: {cache_file.exists()}")
