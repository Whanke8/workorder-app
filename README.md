# 维修工单系统 - Android APP

## 版本 1.1.0

完整的维修工单管理移动应用，支持照片上传和电子签名。

---

## 功能特性

### ✅ 已实现功能

| 功能 | 说明 |
|------|------|
| 首页仪表盘 | 统计概览、单位列表快速入口 |
| 工单列表 | 支持状态筛选 |
| 工单详情 | 完整信息展示 |
| 创建工单 | 支持所有字段输入 |
| **📷 照片上传** | 拍照/相册选择，最多5张，支持预览和删除 |
| **✍️ 电子签名** | 手写签名板，支持清除重签 |
| 更新状态 | 一键更新工单状态 |
| 管理后台 | 密码登录，财务统计 |

### 🔄 待开发功能

- 批量结款
- 数据导出
- 推送通知
- 离线模式

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.12 |
| UI 框架 | Kivy 2.3 |
| 图片处理 | Pillow |
| 网络请求 | requests |
| Android 打包 | Buildozer |

---

## 项目结构

```
workorder-app/
├── main.py           # 主程序入口
├── config.py         # 配置文件
├── api_client.py     # API 客户端
├── widgets.py        # 自定义组件（照片选择器、签名板）
├── version.json      # 版本信息
├── buildozer.spec    # Android 打包配置
└── README.md         # 说明文档
```

---

## 快速开始

### 运行桌面版

```bash
pip install kivy requests pillow
cd workorder-app
python main.py
```

### 编译 Android APK

**方式一：Google Colab（推荐）**

1. 打开 https://colab.research.google.com/
2. 上传 `build_colab.ipynb`
3. 运行并上传项目文件
4. 等待编译，下载 APK

**方式二：GitHub Actions**

推送代码到 GitHub，Actions 自动编译。

---

## 照片上传功能

### 使用方式

1. 在新建工单页面，点击「拍照」或「相册」按钮
2. 选择或拍摄照片（最多5张）
3. 点击照片上的「X」可删除
4. 提交工单时自动上传照片

### 技术实现

- 使用 `plyer` 调用系统相机和相册
- 照片预览使用 Kivy Image 组件
- 上传使用 multipart/form-data 格式

---

## 电子签名功能

### 使用方式

1. 进入工单详情页面
2. 点击「点击签名」按钮
3. 在签名区域手写签名
4. 点击「清除」可重新签名
5. 点击「确认签名」保存

### 技术实现

- 使用 Kivy Canvas 绘制签名路径
- 支持触摸事件捕获
- 签名导出为 PNG 格式
- 通过 Base64 编码上传到服务器

---

## 配置说明

### 修改服务器地址

编辑 `config.py`:

```python
API_BASE_URL = "http://your-server:8088"
API_LOCAL_URL = "http://192.168.x.x:8088"
```

### 修改管理员密码

```python
ADMIN_PASSWORD = "lianhua2024"
```

### 修改照片数量限制

编辑 `widgets.py`:

```python
class PhotoPicker(BoxLayout):
    max_photos = 5  # 修改这里
```

---

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/units` | GET/POST | 单位列表/创建 |
| `/api/workorders` | GET/POST | 工单列表/创建 |
| `/api/workorders/<id>` | GET/PUT | 工单详情/更新 |
| `/api/workorders/<id>/photos` | POST | 上传照片 |
| `/api/workorders/<id>/signature` | POST | 保存签名 |
| `/api/files/<filename>` | GET | 获取文件 |
| `/api/stats` | GET | 统计数据 |

---

## 更新日志

### v1.1.0 (2026-04-07)
- ✨ 新增照片上传功能（拍照/相册）
- ✨ 新增电子签名功能
- 🎨 优化工单详情页面布局
- 📷 显示照片和签名缩略图

### v1.0.0 (2026-04-07)
- 🎉 初始版本发布
- ✅ 基础工单管理功能

---

## 许可证

MIT License
