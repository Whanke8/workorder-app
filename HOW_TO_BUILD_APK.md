# 维修工单系统 Android APP - 快速编译指南

## Windows 环境无法直接编译 APK

Android APK 编译需要 Linux 环境。以下是三种编译方案：

---

## 方案一：GitHub Actions 自动编译（推荐）

### 步骤

1. **创建 GitHub 仓库**
   ```bash
   # 在 workorder-app 目录下
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/workorder-app.git
   git push -u origin main
   ```

2. **自动编译**
   - 推送后 GitHub Actions 会自动开始编译
   - 大约 15-20 分钟完成

3. **下载 APK**
   - 进入仓库的「Actions」标签
   - 点击最新的工作流
   - 在「Artifacts」中下载 APK

---

## 方案二：Google Colab 云端编译

### 步骤

1. 打开 https://colab.research.google.com/
2. 新建笔记本，粘贴以下代码：

```python
# 1. 安装依赖
!apt-get update -qq
!apt-get install -y -qq build-essential libsqlite3-dev zlib1g-dev libncurses5-dev libssl-dev libffi-dev libfreetype6-dev libsdl2-dev
!pip install -q buildozer cython==0.29.33 kivy requests pillow

# 2. 上传项目文件
from google.colab import files
print("请上传以下文件: main.py, config.py, api_client.py, widgets.py, buildozer.spec")
uploaded = files.upload()

# 3. 创建项目目录
import os
os.makedirs('workorder-app', exist_ok=True)
for f in uploaded:
    os.rename(f, f'workorder-app/{f}')

# 4. 编译 APK (首次约 20 分钟)
%cd workorder-app
!buildozer android debug

# 5. 下载 APK
from google.colab import files as dl
import glob
for apk in glob.glob('bin/*.apk'):
    dl.download(apk)
```

3. 运行并等待编译完成
4. 自动下载 APK

---

## 方案三：使用在线编译服务

### buildozer.io（如果可用）

1. 访问 https://buildozer.io
2. 上传项目文件
3. 等待编译
4. 下载 APK

---

## 当前项目文件

已打包到：`workorder-app-source.zip`

包含文件：
- main.py
- config.py
- api_client.py
- widgets.py
- buildozer.spec
- version.json
- README.md

---

## 编译完成后

1. 将 APK 传输到 Android 手机
2. 允许安装未知来源应用
3. 安装并运行
4. 测试功能

---

## 如果你想让我帮你编译

你需要提供以下之一：
1. 一台 Linux 服务器的 SSH 访问权限
2. 安装 WSL（Windows Subsystem for Linux）
3. 安装 Docker Desktop

我可以帮你远程编译。
