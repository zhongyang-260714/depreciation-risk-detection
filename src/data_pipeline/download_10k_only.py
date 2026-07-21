"""
极简 10-K 下载脚本
只下载 10-K 原文，不提取任何数据
作者：AI Assistant
"""

from sec_edgar_downloader import Downloader
import time
from pathlib import Path

# 配置
DOWNLOAD_DIR = Path("D:/depreciation-risk-detection/data/raw")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 5 家公司
COMPANIES = [
    {"ticker": "META", "name": "Meta Platforms"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "AMD", "name": "AMD"},
    {"ticker": "GOOGL", "name": "Alphabet"},
    {"ticker": "MSFT", "name": "Microsoft"},
]

# 创建下载器（SEC 要求提供邮箱）
dl = Downloader(
    company_name="depreciation-risk-detection",
    email_address="zhongyang_260714@example.com",  # 可以填你的邮箱
    download_folder=str(DOWNLOAD_DIR)
)

print("=" * 60)
print("📥 10-K 自动下载脚本")
print("=" * 60)

for company in COMPANIES:
    ticker = company["ticker"]
    name = company["name"]
    
    try:
        print(f"\n⏳ 正在下载 {ticker} ({name}) 的最新 10-K...")
        
        # amount=1 表示只下载最近一份
        dl.get("10-K", ticker, amount=1)
        
        print(f"✅ {ticker} 下载完成！")
        
    except Exception as e:
        print(f"❌ {ticker} 下载失败: {str(e)}")
        print(f"   原因可能是：网络超时 / SEC 访问限制 / 找不到文件")
    
    # SEC 限制频率，间隔 3 秒
    time.sleep(3)

print("\n" + "=" * 60)
print("📂 下载文件位置：")
print(f"   {DOWNLOAD_DIR}")
print("   └── sec-edgar-filings/")
print("       ├── META/10-K/...")
print("       ├── NVDA/10-K/...")
print("       ├── AMD/10-K/...")
print("       ├── GOOGL/10-K/...")
print("       └── MSFT/10-K/...")
print("=" * 60)
print("\n💡 如果全部失败，请告诉我，我帮你找手动下载链接。")
