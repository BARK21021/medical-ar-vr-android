#!/bin/bash
echo "========================================"
echo "  医学AR+VR学术教程系统 - Android版"
echo "========================================"
echo ""

cd "$(dirname "$0")"

if ! command -v buildozer &> /dev/null
then
    echo "正在安装Buildozer..."
    pip install buildozer
fi

echo "正在构建APK..."
buildozer android debug

echo "构建完成！APK文件位于bin目录下"
