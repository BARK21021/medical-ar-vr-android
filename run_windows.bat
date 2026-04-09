@echo off
chcp 65001 >nul
echo ========================================
echo   医学AR+VR学术教程系统 - Windows版
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo 正在安装依赖...
pip install -r requirements_windows.txt -q

echo 正在启动应用程序...
python main.py

pause
