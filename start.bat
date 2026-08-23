@echo off
chcp 65001 >nul
title 科创企业资产折旧风险识别系统
echo ==========================================
echo  科创企业资产折旧风险识别系统 - 启动器
echo ==========================================
echo.

:: 切换到本脚本所在目录（任意安装路径均可运行）
cd /d "%~dp0"
echo [OK] 工作目录: %CD%

:: 优先使用项目自带虚拟环境；没有则使用系统 Python
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    echo [OK] 已激活项目虚拟环境 venv
) else (
    echo [提示] 未发现 venv，使用系统 Python
)

:: 检查核心依赖是否就绪
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo.
    echo [警告] 未检测到 streamlit，请先安装依赖：
    echo        pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: DeepSeek API Key（可选，仅 P7 AI 标注需要；密钥不入库）
if defined DEEPSEEK_API_KEY (
    echo [OK] DeepSeek API Key 已加载
) else (
    echo [提示] 未设置 DEEPSEEK_API_KEY，P7 AI 标注不可用，P1-P6 不受影响
)

echo.
echo [启动] 正在启动系统，浏览器将打开 http://localhost:8501
echo.
streamlit run src\dashboard\app.py

pause
