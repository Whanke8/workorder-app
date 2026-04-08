"""
维修工单系统 - UI 组件
照片选择器和签名组件
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.core.image import Image as CoreImage
from kivy.metrics import dp, sp
from kivy.properties import ListProperty

import io
import base64
from datetime import datetime
from functools import partial


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))


class PhotoPicker(BoxLayout):
    """照片选择器组件"""
    photos = ListProperty([])
    max_photos = 5
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.spacing = dp(10)
        self._build_ui()
    
    def _build_ui(self):
        # 按钮
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.btn_camera = Button(
            text="拍照",
            font_size=sp(14),
            background_color=hex_to_rgb("#3b82f6")+(1,),
            background_normal=''
        )
        self.btn_camera.bind(on_press=self._open_camera)
        
        self.btn_gallery = Button(
            text="相册",
            font_size=sp(14),
            background_color=hex_to_rgb("#10b981")+(1,),
            background_normal=''
        )
        self.btn_gallery.bind(on_press=self._open_gallery)
        
        self.btn_add = Button(
            text="添加测试照片",
            font_size=sp(14),
            background_color=hex_to_rgb("#f59e0b")+(1,),
            background_normal=''
        )
        self.btn_add.bind(on_press=self._add_mock_photo)
        
        btn_layout.add_widget(self.btn_camera)
        btn_layout.add_widget(self.btn_gallery)
        btn_layout.add_widget(self.btn_add)
        self.add_widget(btn_layout)
        
        # 照片预览区
        self.preview_layout = GridLayout(cols=3, size_hint_y=None, spacing=dp(5))
        self.preview_layout.bind(minimum_height=self.preview_layout.setter('height'))
        self.add_widget(self.preview_layout)
        
        # 计数
        self.count_label = Label(
            text=f"已选择 0/{self.max_photos} 张照片",
            font_size=sp(12),
            color=hex_to_rgb("#64748b")+(1,),
            size_hint_y=None,
            height=dp(25)
        )
        self.add_widget(self.count_label)
    
    def _open_camera(self, instance):
        """打开相机"""
        try:
            from plyer import camera
            camera.take_picture(self._on_photo_received, "photo_temp.jpg")
        except:
            self._add_mock_photo(None)
    
    def _open_gallery(self, instance):
        """打开相册"""
        try:
            from plyer import filechooser
            filechooser.open_file(
                title="选择照片",
                filters=["*.jpg", "*.png", "*.jpeg"],
                on_selection=self._on_gallery_selected
            )
        except:
            self._add_mock_photo(None)
    
    def _on_photo_received(self, file_path):
        """相机拍照回调"""
        if file_path:
            self._add_photo_from_path(file_path)
    
    def _on_gallery_selected(self, selection):
        """相册选择回调"""
        if selection:
            for file_path in selection:
                if len(self.photos) >= self.max_photos:
                    break
                self._add_photo_from_path(file_path)
    
    def _add_mock_photo(self, instance):
        """添加模拟照片"""
        if len(self.photos) >= self.max_photos:
            Popup(title="提示", content=Label(text=f"最多选择{self.max_photos}张照片"), 
                  size_hint=(0.7, 0.25)).open()
            return
        
        try:
            from PIL import Image as PILImage
            import random
            
            colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
            color = random.choice(colors)
            
            img = PILImage.new('RGB', (200, 200), color)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            photo_data = {
                'texture': CoreImage(buffer, ext='png').texture,
                'data': buffer.getvalue(),
                'filename': f'photo_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
            }
            
            self.photos.append(photo_data)
            self._update_preview()
        except:
            # 如果没有 PIL，创建空数据
            photo_data = {
                'texture': None,
                'data': b'',
                'filename': f'photo_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
            }
            self.photos.append(photo_data)
            self._update_preview()
    
    def _add_photo_from_path(self, file_path):
        """从文件路径添加照片"""
        import os
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            texture = CoreImage(file_path).texture
            filename = os.path.basename(file_path)
            
            photo_data = {
                'texture': texture,
                'data': data,
                'filename': filename
            }
            
            self.photos.append(photo_data)
            self._update_preview()
        except Exception as e:
            print(f"添加照片失败: {e}")
    
    def _update_preview(self):
        """更新照片预览"""
        self.preview_layout.clear_widgets()
        
        for i, photo in enumerate(self.photos):
            photo_card = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(5))
            
            if photo.get('texture'):
                img = Image(texture=photo['texture'], size_hint_x=0.75)
                img.allow_stretch = True
                img.keep_ratio = True
            else:
                img = Label(text="图片", size_hint_x=0.75, 
                           color=hex_to_rgb("#64748b")+(1,))
            
            btn_remove = Button(
                text="X",
                font_size=sp(14),
                size_hint_x=0.25,
                background_color=hex_to_rgb("#dc2626")+(1,),
                background_normal=''
            )
            btn_remove.bind(on_press=partial(self._remove_photo, i))
            
            photo_card.add_widget(img)
            photo_card.add_widget(btn_remove)
            self.preview_layout.add_widget(photo_card)
        
        self.count_label.text = f"已选择 {len(self.photos)}/{self.max_photos} 张照片"
        self.height = self.minimum_height
    
    def _remove_photo(self, index, instance):
        """删除照片"""
        if 0 <= index < len(self.photos):
            self.photos.pop(index)
            self._update_preview()
    
    def get_photos_data(self):
        """获取照片数据"""
        return [(p['filename'], p['data']) for p in self.photos if p.get('data')]
    
    def clear(self):
        """清空照片"""
        self.photos = []
        self._update_preview()


class SignatureWidget(FloatLayout):
    """电子签名组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(220)
        
        self.lines = []
        self.current_line = []
        
        self._build_ui()
    
    def _build_ui(self):
        # 白色背景
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # 边框
        with self.canvas.after:
            Color(0.8, 0.8, 0.8, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_border, size=self._update_border)
        
        # 提示文字
        self.hint = Label(
            text="请在此区域签名",
            font_size=sp(16),
            color=hex_to_rgb("#d1d5db")+(1,),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.hint)
        
        # 清除按钮
        self.btn_clear = Button(
            text="清除",
            font_size=sp(12),
            size_hint=(None, None),
            size=(dp(50), dp(28)),
            pos_hint={'right': 0.98, 'top': 0.95},
            background_color=hex_to_rgb("#64748b")+(1,),
            background_normal=''
        )
        self.btn_clear.bind(on_press=self.clear_signature)
        self.add_widget(self.btn_clear)
    
    def _update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def _update_border(self, instance, value):
        self.border.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.current_line = [touch.pos]
            self.hint.opacity = 0
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and self.current_line:
            self.current_line.append(touch.pos)
            self._draw_current_line()
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.current_line:
            if len(self.current_line) >= 2:
                self.lines.append(list(self.current_line))
            self.current_line = []
        return super().on_touch_up(touch)
    
    def _draw_current_line(self):
        """绘制当前线条"""
        if len(self.current_line) < 2:
            return
        
        with self.canvas.after:
            Color(0, 0, 0, 1)
            points = []
            for p in self.current_line:
                points.extend([p[0], p[1]])
            Line(points=points, width=dp(2))
    
    def clear_signature(self, instance=None):
        """清除签名"""
        self.canvas.after.clear()
        self.lines = []
        self.current_line = []
        
        # 重新绘制边框
        with self.canvas.after:
            Color(0.8, 0.8, 0.8, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        
        self.hint.opacity = 1
    
    def has_signature(self):
        """检查是否有签名"""
        return len(self.lines) > 0
    
    def get_signature_base64(self):
        """获取签名 Base64"""
        if not self.has_signature():
            return None
        
        try:
            from PIL import Image as PILImage, ImageDraw
            
            width, height = int(self.width), int(self.height)
            img = PILImage.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            for line in self.lines:
                if len(line) >= 2:
                    points = [(int(p[0]), height - int(p[1])) for p in line]
                    for i in range(len(points) - 1):
                        draw.line([points[i], points[i+1]], fill='black', width=3)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
        except:
            return None
