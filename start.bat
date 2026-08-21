@echo off
chcp 65001 >nul
echo ==========================================
echo  科创企业资产折旧风险识别系统 - 启动器
echo ==========================================
echo.

:: DeepSeek API Key 从系统环境变量读取（安全规范：密钥不得硬编码入库）
if defined DEEPSEEK_API_KEY (echo [OK] DeepSeek API Key loaded) else (echo [WARN] DEEPSEEK_API_KEY not set - P7 AI annotation unavailable)

:: 切换到项目目录
cd /d D:\depreciation-risk-detection
echo [OK] Working dir: D:\depreciation-risk-detection

:: 激活虚拟环境
call venv\Scripts\activate
echo [OK] Virtual env activated

:: 启动 Streamlit
echo.
echo [Launch] Starting Streamlit...
echo [Hint] Browser will open http://localhost:8501
echo.
streamlit run src\dashboard\app.py

pause
