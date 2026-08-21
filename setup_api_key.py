"""配置DeepSeek API Key

使用方法：
1. 在下方填入你的DeepSeek API Key
2. 运行此脚本：python setup_api_key.py
3. 脚本会创建 .env 文件，供系统读取
"""

import os
from pathlib import Path

REPO_ROOT = Path("D:/depreciation-risk-detection")

def setup_api_key():
    print("=" * 60)
    print("DeepSeek API Key 配置")
    print("=" * 60)
    print()
    print("请从 DeepSeek 开放平台获取 API Key:")
    print("https://platform.deepseek.com/api_keys")
    print()
    
    # 检查是否已有环境变量
    existing = os.environ.get("DEEPSEEK_API_KEY")
    if existing:
        print(f"检测到环境变量已设置: {existing[:8]}...")
        use_existing = input("是否使用环境变量中的API Key? (y/n): ").strip().lower()
        if use_existing == 'y':
            api_key = existing
        else:
            api_key = input("请输入新的 DeepSeek API Key: ").strip()
    else:
        print("未检测到环境变量中的API Key。")
        print()
        api_key = input("请输入 DeepSeek API Key (sk-...): ").strip()
    
    if not api_key:
        print("错误：API Key不能为空")
        return False
    
    if not api_key.startswith("sk-"):
        print("警告：API Key应以 'sk-' 开头，请确认输入正确")
        confirm = input("是否继续? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # 创建 .env 文件
    env_path = REPO_ROOT / ".env"
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"DEEPSEEK_API_KEY={api_key}\n")
    
    print()
    print("✅ API Key 已保存至:", env_path)
    print("✅ 系统将通过 python-dotenv 自动读取")
    print()
    print("测试连接中...")
    
    # 测试连接
    try:
        import requests
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "Say OK"}], "max_tokens": 10},
            timeout=15,
        )
        if resp.status_code == 200:
            print("✅ API 连接测试成功！")
            return True
        else:
            print(f"❌ API 连接失败: HTTP {resp.status_code}")
            print(f"响应: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 连接测试出错: {e}")
        return False

if __name__ == "__main__":
    setup_api_key()
