@echo off
chcp 65001 >nul
echo ========================================
echo   医学AR+VR学术教程系统
echo ========================================
echo.

cd /d "%~dp0"

echo 正在启动应用程序...
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用程序启动失败！
    echo 请检查 Python 环境是否正常
)

pause
