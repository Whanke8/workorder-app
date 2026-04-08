# 维修工单系统 Android APP - 配置文件
# API 配置
API_BASE_URL = "http://www.xmlinyan.com:8088"
API_LOCAL_URL = "http://172.16.21.199:8088"

# 管理员密码
ADMIN_PASSWORD = "lianhua2024"

# APP 信息
APP_NAME = "维修工单系统"
APP_VERSION = "1.0.0"
APP_PACKAGE = "com.workorder.repair"

# 颜色主题
COLORS = {
    "primary": "#1e3a8a",
    "primary_light": "#2563eb",
    "accent": "#10b981",
    "background": "#f5f7fa",
    "card_bg": "#ffffff",
    "text_primary": "#1e293b",
    "text_secondary": "#64748b",
    "error": "#dc2626",
    "success": "#16a34a",
    "warning": "#f59e0b",
    # 状态颜色
    "status_pending": "#f59e0b",
    "status_processing": "#3b82f6",
    "status_awaiting": "#8b5cf6",
    "status_completed": "#10b981",
}

# 状态映射
STATUS_MAP = {
    "pending": "待处理",
    "processing": "处理中",
    "awaiting": "待签字",
    "completed": "已完成"
}

STATUS_REVERSE_MAP = {
    "待处理": "pending",
    "处理中": "processing",
    "待签字": "awaiting",
    "已完成": "completed"
}

# 支付状态
PAYMENT_STATUS_MAP = {
    "paid": "已结款",
    "unpaid": "未结款"
}

# 支付方式
PAYMENT_METHODS = ["cash", "wechat", "alipay", "bank"]
PAYMENT_METHOD_NAMES = {
    "cash": "现金",
    "wechat": "微信",
    "alipay": "支付宝",
    "bank": "银行转账"
}
