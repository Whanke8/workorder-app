"""
维修工单系统 - API 客户端
支持照片上传和签名
"""
import requests
import json
import io
from config import API_BASE_URL, API_LOCAL_URL, ADMIN_PASSWORD

class APIClient:
    def __init__(self, use_local=True):
        self.base_url = API_LOCAL_URL if use_local else API_BASE_URL
        self.session = requests.Session()
        self.admin_logged_in = False
        self.timeout = 15
        
    def set_server(self, use_local=True):
        """切换服务器地址"""
        self.base_url = API_LOCAL_URL if use_local else API_BASE_URL
        
    def _get(self, endpoint, params=None):
        """GET 请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            resp = self.session.get(url, params=params, timeout=self.timeout)
            return resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def _post(self, endpoint, data=None, files=None, json_data=None):
        """POST 请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            if files:
                resp = self.session.post(url, data=data, files=files, timeout=self.timeout)
            elif json_data:
                resp = self.session.post(url, json=json_data, timeout=self.timeout)
            else:
                resp = self.session.post(url, data=data, timeout=self.timeout)
            return resp.json() if resp.status_code == 200 else {"error": resp.status_code, "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def _put(self, endpoint, data=None):
        """PUT 请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            resp = self.session.put(url, json=data, timeout=self.timeout)
            return resp.json() if resp.status_code == 200 else {"error": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    # ==================== 单位相关 ====================
    def get_units(self):
        """获取单位列表"""
        return self._get("/api/units")
    
    def create_unit(self, name, address="", contact=""):
        """创建单位"""
        return self._post("/api/units", json_data={"name": name, "address": address})
    
    # ==================== 工单相关 ====================
    def get_workorders(self, unit_id=None, status=None):
        """获取工单列表"""
        params = {}
        if unit_id:
            params["unit_id"] = unit_id
        if status:
            params["status"] = status
        return self._get("/api/workorders", params)
    
    def get_workorder(self, workorder_id):
        """获取工单详情"""
        return self._get(f"/api/workorders/{workorder_id}")
    
    def create_workorder(self, unit_id, title, content="", location="", 
                         reporter="", contact="", labor_cost=0, material_cost=0):
        """创建工单（不含照片）"""
        data = {
            "unit_id": unit_id,
            "title": title,
            "content": content,
            "location": location,
            "reporter": reporter,
            "contact": contact,
            "labor_cost": labor_cost,
            "material_cost": material_cost
        }
        return self._post("/api/workorders", data=data)
    
    def create_workorder_with_photos(self, unit_id, title, content="", location="", 
                                     reporter="", contact="", labor_cost=0, material_cost=0,
                                     photos_data=None):
        """创建工单（含照片数据）"""
        data = {
            "unit_id": unit_id,
            "title": title,
            "content": content,
            "location": location,
            "reporter": reporter,
            "contact": contact,
            "labor_cost": str(labor_cost),
            "material_cost": str(material_cost)
        }
        
        files = None
        if photos_data:
            files = []
            for filename, file_data in photos_data:
                files.append(('photos', (filename, io.BytesIO(file_data), 'image/png')))
        
        return self._post("/api/workorders", data=data, files=files)
    
    def update_workorder(self, workorder_id, **kwargs):
        """更新工单"""
        return self._put(f"/api/workorders/{workorder_id}", data=kwargs)
    
    def update_status(self, workorder_id, status):
        """更新工单状态"""
        return self._put(f"/api/workorders/{workorder_id}", data={"status": status})
    
    def update_payment_status(self, workorder_id, payment_status, payment_method=None):
        """更新付款状态"""
        data = {"payment_status": payment_status}
        if payment_method:
            data["payment_method"] = payment_method
        return self._put(f"/api/workorders/{workorder_id}", data=data)
    
    def save_signature(self, workorder_id, signature_data):
        """保存签名
        
        Args:
            workorder_id: 工单ID
            signature_data: Base64编码的签名图片数据 (格式: data:image/png;base64,xxxxx)
        """
        return self._post(f"/api/workorders/{workorder_id}/signature", 
                         json_data={"signature_data": signature_data})
    
    def upload_photos(self, workorder_id, photo_paths):
        """上传照片（从文件路径）
        
        Args:
            workorder_id: 工单ID
            photo_paths: 照片文件路径列表
        """
        files = []
        for photo_path in photo_paths:
            try:
                files.append(("photos", open(photo_path, "rb")))
            except:
                pass
        result = self._post(f"/api/workorders/{workorder_id}/photos", files=files)
        for f in files:
            f[1].close()
        return result
    
    def upload_photos_from_data(self, workorder_id, photos_data):
        """上传照片（从内存数据）
        
        Args:
            workorder_id: 工单ID
            photos_data: [(filename, bytes_data), ...] 格式的照片数据列表
        """
        files = []
        for filename, file_data in photos_data:
            if file_data:
                files.append(('photos', (filename, io.BytesIO(file_data), 'image/png')))
        
        if not files:
            return {"message": "no photos"}
        
        return self._post(f"/api/workorders/{workorder_id}/photos", files=files)
    
    # ==================== 统计相关 ====================
    def get_stats(self):
        """获取统计数据"""
        return self._get("/api/stats")
    
    # ==================== 管理员相关 ====================
    def admin_login(self, password):
        """管理员登录"""
        result = self._post("/api/admin/login", json_data={"password": password})
        if result.get("success"):
            self.admin_logged_in = True
        return result
    
    def admin_logout(self):
        """管理员登出"""
        self.admin_logged_in = False
        return self._post("/api/admin/logout")
    
    def get_payments(self, unit_id=None):
        """获取付款记录"""
        params = {}
        if unit_id:
            params["unit_id"] = unit_id
        return self._get("/api/payments", params)
    
    def batch_payment(self, unit_id=None, date_from=None, date_to=None, 
                      payment_method="cash"):
        """批量结款"""
        data = {
            "payment_method": payment_method
        }
        if unit_id:
            data["unit_id"] = unit_id
        if date_from:
            data["date_from"] = date_from
        if date_to:
            data["date_to"] = date_to
        return self._post("/api/workorders/batch-payment", json_data=data)
    
    def batch_preview(self, unit_id=None, date_from=None, date_to=None):
        """批量结款预览"""
        data = {}
        if unit_id:
            data["unit_id"] = unit_id
        if date_from:
            data["date_from"] = date_from
        if date_to:
            data["date_to"] = date_to
        return self._post("/api/workorders/batch-preview", json_data=data)
    
    # ==================== 文件相关 ====================
    def get_file_url(self, filename):
        """获取文件URL"""
        return f"{self.base_url}/api/files/{filename}"
    
    def get_signature_url(self, workorder):
        """获取签名图片URL"""
        sig_data = workorder.get('signature_data')
        if sig_data:
            return self.get_file_url(sig_data)
        return None
    
    def get_photo_urls(self, workorder):
        """获取照片URL列表"""
        photos = workorder.get('photos', [])
        return [self.get_file_url(p) for p in photos]
    
    def get_export_url(self, unit_id=None, date_from=None, date_to=None):
        """获取导出URL"""
        params = []
        if unit_id:
            params.append(f"unit_id={unit_id}")
        if date_from:
            params.append(f"date_from={date_from}")
        if date_to:
            params.append(f"date_to={date_to}")
        query = "&".join(params)
        return f"{self.base_url}/api/export?{query}" if query else f"{self.base_url}/api/export"


# 全局 API 客户端实例
api = APIClient()
