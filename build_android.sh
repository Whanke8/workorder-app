#!/bin/bash
# 维修工单系统 - Android APK 编译脚本 (需在 Linux/WSL 环境运行)

echo "============================================"
echo "  维修工单系统 - Android APK 编译"
echo "============================================"

# 检查是否在 Linux 环境
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "错误: 此脚本需要在 Linux 环境运行"
    echo "请使用 WSL 或 Linux 虚拟机"
    exit 1
fi

# 安装依赖
echo "[1/4] 安装系统依赖..."
sudo apt-get update
sudo apt-get install -y build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev \
    zlib1g-dev libssl-dev openssl libgdbm-dev libgdbm-compat-dev liblzma-dev \
    libreadline-dev libncursesw5-dev libffi-dev uuid-dev libfreetype6-dev \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# 安装 buildozer
echo "[2/4] 安装 Buildozer..."
pip3 install --user buildozer
pip3 install --user cython==0.29.33

# 初始化 buildozer
echo "[3/4] 初始化编译环境..."
buildozer init

# 编译 APK
echo "[4/4] 编译 Android APK..."
buildozer android debug

echo ""
echo "============================================"
echo "  编译完成!"
echo "  APK 文件位于: bin/*.apk"
echo "============================================"
