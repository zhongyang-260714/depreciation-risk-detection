@echo off
chcp 65001 >nul
echo ==========================================
echo  清除缓存工具
echo ==========================================
echo.

:: 切换到项目目录
cd /d D:\depreciation-risk-detection
echo [OK] 工作目录: D:\depreciation-risk-detection

:: 激活虚拟环境
call venv\Scripts\activate
echo [OK] 虚拟环境已激活

:: 运行清除缓存脚本
echo.
echo [执行] 正在清除缓存...
python clear_cache.py
echo.

echo ==========================================
echo  缓存清除完成
echo ==========================================
pause
