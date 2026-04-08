# 维修工单系统 - APK 编译说明

## 当前状态

Windows 环境无法直接编译 APK。群辉 NAS 的 Docker 需要管理员权限才能运行。

---

## 最快方案：手动编译

### 步骤 1：登录群辉 DSM

1. 打开浏览器，访问 `http://172.16.21.199:5000`
2. 使用你的账号登录

### 步骤 2：启动 Docker

1. 打开「套件中心」
2. 找到「Container Manager」
3. 点击「启动」

### 步骤 3：通过 SSH 编译

启动 Docker 后，告诉我，我会帮你执行编译命令。

---

## 替代方案

### 方案 A：使用 GitHub Actions

1. 创建 GitHub 账号（如果没有）
2. 创建新仓库
3. 上传项目文件
4. GitHub 自动编译 APK
5. 下载 APK

### 方案 B：使用 Google Colab

1. 打开 https://colab.research.google.com/
2. 运行以下代码：

```python
!apt-get update && apt-get install -y build-essential libffi-dev libssl-dev
!pip install buildozer cython==0.29.33

# 上传项目文件
from google.colab import files
uploaded = files.upload()  # 上传 main.py, config.py, api_client.py, widgets.py, buildozer.spec

# 编译
!mkdir -p workorder-app && mv *.py *.spec workorder-app/
%cd workorder-app
!buildozer android debug

# 下载
import glob
for apk in glob.glob('bin/*.apk'):
    files.download(apk)
```

---

## 如果你愿意等待

我可以：
1. 帮你在 GitHub 上创建仓库并触发编译
2. 或者指导你完成 Colab 编译流程

请告诉我你的选择。
