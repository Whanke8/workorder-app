# 维修工单系统 Android APP - 编译指南

## 快速编译方案

由于 Windows 不支持直接编译 Android APK，提供以下三种编译方式：

---

## 方案一：Google Colab 云端编译（推荐，免费）

### 步骤

1. **打开 Google Colab**
   - 访问 https://colab.research.google.com/
   - 登录 Google 账号

2. **上传笔记本**
   - 点击「文件」→「上传笔记本」
   - 选择 `build_colab.ipynb`

3. **运行编译**
   - 依次运行每个单元格
   - 在第3步上传项目文件（main.py, config.py, api_client.py, buildozer.spec）
   - 等待编译完成（首次约 15-30 分钟）

4. **下载 APK**
   - 编译完成后自动下载 APK 文件

---

## 方案二：GitHub Actions 自动编译

### 步骤

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/workorder-app.git
   git push -u origin main
   ```

2. **触发编译**
   - 推送代码后自动触发 GitHub Actions
   - 或在仓库的「Actions」页面手动触发

3. **下载 APK**
   - 编译完成后在「Artifacts」中下载
   - 或在「Releases」中下载发布的 APK

---

## 方案三：本地 Linux 环境编译

### 前置要求

- Ubuntu 20.04+ 或 WSL2
- 至少 10GB 磁盘空间
- 稳定的网络连接

### 步骤

```bash
# 1. 安装系统依赖
sudo apt-get update
sudo apt-get install -y build-essential libsqlite3-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev libreadline-dev libssl-dev \
    libgdbm-dev libgdbm-compat-dev liblzma-dev libffi-dev \
    libbz2-dev uuid-dev libfreetype6-dev libsdl2-dev \
    libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev

# 2. 安装 Python 依赖
pip3 install --user buildozer cython==0.29.33 kivy requests pillow

# 3. 进入项目目录
cd workorder-app

# 4. 编译 APK（首次会自动下载 Android SDK/NDK，约需 30 分钟）
buildozer android debug

# 5. 编译完成的 APK 位于 bin/ 目录
ls bin/*.apk
```

---

## 方案四：使用 Docker 编译

```bash
# 使用预配置的 Buildozer Docker 镜像
docker pull kivy/buildozer

# 运行编译
docker run --rm -v "$PWD":/app kivy/buildozer android debug
```

---

## 项目文件清单

编译所需的最小文件集：

```
workorder-app/
├── main.py           # 主程序（必需）
├── config.py         # 配置文件（必需）
├── api_client.py     # API 客户端（必需）
├── buildozer.spec    # 打包配置（必需）
└── README.md         # 说明文档
```

---

## 常见问题

### Q: 编译失败提示 "SDK not found"
A: 首次编译会自动下载 SDK，请确保网络通畅。如下载失败，可设置代理：
```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### Q: 编译时间太长
A: 首次编译需要下载约 2GB 的 SDK/NDK，后续编译会快很多。

### Q: APK 安装后闪退
A: 检查 config.py 中的 API 地址是否正确，确保手机能访问服务器。

### Q: 如何修改 APP 图标
A: 在 buildozer.spec 中设置：
```ini
icon.filename = %(source.dir)s/assets/icon.png
```

---

## 测试 APK

编译完成后：

1. 将 APK 传输到 Android 手机
2. 允许安装未知来源应用
3. 安装并运行
4. 检查功能是否正常

---

## 发布版本

生成签名的发布版 APK：

```bash
# 创建签名密钥（首次）
keytool -genkey -v -keystore workorder.keystore -alias workorder -keyalg RSA -keysize 2048 -validity 10000

# 编译发布版
buildozer android release

# 签名
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore workorder.keystore bin/workorder-1.0.0-release-unsigned.apk workorder
```
