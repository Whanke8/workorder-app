"""
维修工单系统 - 主程序入口 (Kivy UI)
完整版 - 包含照片上传和电子签名功能
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window

from config import STATUS_MAP, STATUS_REVERSE_MAP, PAYMENT_STATUS_MAP, APP_NAME, ADMIN_PASSWORD
from api_client import api
from widgets import PhotoPicker, SignatureWidget, hex_to_rgb

Window.size = (400, 700)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self._build_ui()
        Clock.schedule_once(self._load_data, 0.3)
    
    def _build_ui(self):
        main = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(15))
        with header.canvas.before:
            Color(*hex_to_rgb("#1e3a8a"))
            header.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        
        title = Label(text=f"🔧 {APP_NAME}", font_size=sp(20), bold=True, color=(1,1,1,1), size_hint_x=0.5)
        btn_new = Button(text="+ 新建", font_size=sp(14), size_hint_x=0.25, background_color=hex_to_rgb("#10b981")+(1,), background_normal='')
        btn_new.bind(on_press=lambda x: setattr(self.manager, 'current', 'create'))
        btn_admin = Button(text="📊 管理", font_size=sp(14), size_hint_x=0.25, background_color=(1,1,1,0.2), background_normal='')
        btn_admin.bind(on_press=lambda x: setattr(self.manager, 'current', 'admin_login'))
        header.add_widget(title); header.add_widget(btn_new); header.add_widget(btn_admin)
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        self.stats_grid = GridLayout(cols=5, size_hint_y=None, height=dp(100), spacing=dp(8))
        self.stat_labels = {}
        for key, lbl in [("total","总工单"),("pending","待处理"),("processing","处理中"),("awaiting","待签字"),("completed","已完成")]:
            card = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(3))
            with card.canvas.before:
                Color(*hex_to_rgb("#f8fafc"))
                card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
            card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
            num = Label(text="0", font_size=sp(24), bold=True, color=hex_to_rgb("#0284c7")+(1,))
            txt = Label(text=lbl, font_size=sp(11), color=hex_to_rgb("#64748b")+(1,))
            card.add_widget(num); card.add_widget(txt)
            self.stat_labels[key] = num
            self.stats_grid.add_widget(card)
        content.add_widget(self.stats_grid)
        
        units_title = Label(text="🏢 单位列表", font_size=sp(16), bold=True, halign='left', size_hint_y=None, height=dp(40), color=hex_to_rgb("#1e293b")+(1,))
        units_title.bind(texture_size=units_title.setter('size'))
        content.add_widget(units_title)
        
        self.units_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.units_layout.bind(minimum_height=self.units_layout.setter('height'))
        self.loading = Label(text="加载中...", font_size=sp(14), size_hint_y=None, height=dp(50))
        self.units_layout.add_widget(self.loading)
        content.add_widget(self.units_layout)
        
        scroll.add_widget(content)
        main.add_widget(header); main.add_widget(scroll)
        self.add_widget(main)
    
    def _load_data(self, dt):
        stats = api.get_stats()
        if 'error' not in stats:
            status = stats.get('status', {})
            self.stat_labels['total'].text = str(stats.get('total', 0))
            for k in ['pending','processing','awaiting','completed']:
                self.stat_labels[k].text = str(status.get(k, 0))
        
        units = api.get_units()
        self.units_layout.clear_widgets()
        if 'error' in units:
            self.units_layout.add_widget(Label(text="连接失败", color=hex_to_rgb("#dc2626")+(1,), size_hint_y=None, height=dp(50)))
        else:
            for u in units:
                self.units_layout.add_widget(self._unit_card(u))
    
    def _unit_card(self, unit):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), padding=dp(12), spacing=dp(5))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        name = Label(text=unit.get('name','未知'), font_size=sp(15), bold=True, halign='left', color=hex_to_rgb("#0284c7")+(1,), size_hint_y=None, height=dp(25))
        name.bind(texture_size=name.setter('size'))
        info = Label(text=f"📍 {unit.get('address','')} | {unit.get('workorder_count',0)}个工单", font_size=sp(12), halign='left', color=hex_to_rgb("#64748b")+(1,), size_hint_y=None, height=dp(20))
        info.bind(texture_size=info.setter('size'))
        card.add_widget(name); card.add_widget(info)
        def on_touch(touch):
            if card.collide_point(*touch.pos):
                ws = self.manager.get_screen('workorders')
                ws.set_filter(unit_id=unit.get('id'))
                self.manager.current = 'workorders'
                return True
        card.on_touch_down = on_touch
        return card


class CreateScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'create'
        self.units = []
        self.selected_unit_id = None
        self._build_ui()
        Clock.schedule_once(self._load_units, 0.2)
    
    def _build_ui(self):
        main = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        with header.canvas.before:
            Color(*hex_to_rgb("#667eea"))
            header.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        btn_back = Button(text="← 返回", font_size=sp(14), size_hint_x=0.3, background_color=(1,1,1,0.2), background_normal='')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="新建维修工单", font_size=sp(16), bold=True, color=(1,1,1,1)))
        
        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        
        self.unit_spinner = Spinner(text="选择单位", values=["加载中..."], size_hint_y=None, height=dp(45))
        self.unit_spinner.bind(text=self._on_unit)
        form.add_widget(self._field("🏢 单位 *", self.unit_spinner))
        
        self.title_in = TextInput(hint_text="简单描述维修内容", multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self._field("📝 标题 *", self.title_in))
        
        self.loc_in = TextInput(hint_text="维修地点", multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self._field("📍 地点", self.loc_in))
        
        self.reporter_in = TextInput(hint_text="报修人姓名", multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self._field("👤 报修人", self.reporter_in))
        
        self.contact_in = TextInput(hint_text="手机号或短号", multiline=False, size_hint_y=None, height=dp(45))
        form.add_widget(self._field("📱 联系方式", self.contact_in))
        
        self.content_in = TextInput(hint_text="详细描述维修内容", multiline=True, size_hint_y=None, height=dp(80))
        form.add_widget(self._field("📋 详细描述", self.content_in))
        
        cost_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        self.labor_in = TextInput(hint_text="人工费", input_filter='float', multiline=False)
        self.material_in = TextInput(hint_text="物料费", input_filter='float', multiline=False)
        cost_row.add_widget(self.labor_in); cost_row.add_widget(self.material_in)
        form.add_widget(self._field("🔧 费用(元)", cost_row))
        
        form.add_widget(Label(text="📷 照片上传", font_size=sp(13), halign='left', size_hint_y=None, height=dp(22), color=hex_to_rgb("#333333")+(1,)))
        self.photo_picker = PhotoPicker()
        form.add_widget(self.photo_picker)
        
        btn_submit = Button(text="提交工单", font_size=sp(16), size_hint_y=None, height=dp(50), background_color=hex_to_rgb("#667eea")+(1,), background_normal='')
        btn_submit.bind(on_press=self._submit)
        form.add_widget(btn_submit)
        
        scroll.add_widget(form)
        main.add_widget(header); main.add_widget(scroll)
        self.add_widget(main)
    
    def _field(self, label, widget):
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(72), spacing=dp(3))
        lbl = Label(text=label, font_size=sp(13), halign='left', size_hint_y=None, height=dp(20), color=hex_to_rgb("#333333")+(1,))
        lbl.bind(texture_size=lbl.setter('size'))
        layout.add_widget(lbl); layout.add_widget(widget)
        return layout
    
    def _load_units(self, dt):
        units = api.get_units()
        if 'error' not in units:
            self.units = units
            self.unit_spinner.values = [u.get('name','未知') for u in units]
    
    def _on_unit(self, spinner, text):
        for u in self.units:
            if u.get('name') == text:
                self.selected_unit_id = u.get('id')
                break
    
    def _submit(self, instance):
        if not self.selected_unit_id:
            Popup(title="提示", content=Label(text="请选择单位"), size_hint=(0.7, 0.25)).open()
            return
        if not self.title_in.text.strip():
            Popup(title="提示", content=Label(text="请输入标题"), size_hint=(0.7, 0.25)).open()
            return
        
        result = api.create_workorder(
            unit_id=self.selected_unit_id, title=self.title_in.text.strip(),
            content=self.content_in.text.strip(), location=self.loc_in.text.strip(),
            reporter=self.reporter_in.text.strip(), contact=self.contact_in.text.strip(),
            labor_cost=float(self.labor_in.text or 0), material_cost=float(self.material_in.text or 0)
        )
        
        if 'id' in result:
            photos = self.photo_picker.get_photos_data()
            if photos:
                api.upload_photos_from_data(result['id'], photos)
            Popup(title="成功", content=Label(text=f"工单创建成功!\n工单号: {result['id']}"), size_hint=(0.8, 0.3)).open()
            self._clear()
        else:
            Popup(title="失败", content=Label(text=str(result.get('error','未知错误'))), size_hint=(0.7, 0.25)).open()
    
    def _clear(self):
        self.title_in.text = ""; self.loc_in.text = ""; self.reporter_in.text = ""
        self.contact_in.text = ""; self.content_in.text = ""
        self.labor_in.text = ""; self.material_in.text = ""
        self.unit_spinner.text = "选择单位"
        self.selected_unit_id = None
        self.photo_picker.clear()


class WorkordersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'workorders'
        self.filter_status = None
        self.filter_unit = None
        self._build_ui()
    
    def _build_ui(self):
        main = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        with header.canvas.before:
            Color(*hex_to_rgb("#1e3a8a"))
            header.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        btn_back = Button(text="← 返回", font_size=sp(14), size_hint_x=0.3, background_color=(1,1,1,0.2), background_normal='')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="工单列表", font_size=sp(16), bold=True, color=(1,1,1,1)))
        
        filter_bar = BoxLayout(size_hint_y=None, height=dp(45), padding=dp(5))
        self.status_spinner = Spinner(text="全部状态", values=["全部状态","待处理","处理中","待签字","已完成"], size_hint_x=1, font_size=sp(13))
        self.status_spinner.bind(text=self._on_filter)
        filter_bar.add_widget(self.status_spinner)
        
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8), size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.list_layout.add_widget(Label(text="加载中...", size_hint_y=None, height=dp(50)))
        scroll.add_widget(self.list_layout)
        
        main.add_widget(header); main.add_widget(filter_bar); main.add_widget(scroll)
        self.add_widget(main)
    
    def set_filter(self, status=None, unit_id=None):
        self.filter_status = STATUS_REVERSE_MAP.get(status) if status in STATUS_REVERSE_MAP else None
        self.filter_unit = unit_id
        if status: self.status_spinner.text = STATUS_MAP.get(status, status)
        self._load()
    
    def _on_filter(self, spinner, text):
        self.filter_status = None if text == "全部状态" else STATUS_REVERSE_MAP.get(text)
        self._load()
    
    def _load(self):
        workorders = api.get_workorders(unit_id=self.filter_unit, status=self.filter_status)
        self.list_layout.clear_widgets()
        if 'error' in workorders:
            self.list_layout.add_widget(Label(text="加载失败", color=hex_to_rgb("#dc2626")+(1,), size_hint_y=None, height=dp(50)))
        elif not workorders:
            self.list_layout.add_widget(Label(text="暂无工单", color=hex_to_rgb("#64748b")+(1,), size_hint_y=None, height=dp(50)))
        else:
            for wo in workorders:
                self.list_layout.add_widget(self._card(wo))
    
    def _card(self, wo):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(4))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        
        top = BoxLayout(size_hint_y=None, height=dp(22))
        title = Label(text=wo.get('title','无标题')[:20], font_size=sp(13), bold=True, halign='left', color=hex_to_rgb("#1e293b")+(1,), size_hint_x=0.65)
        st = wo.get('status','pending')
        st_colors = {'pending':'#f59e0b','processing':'#3b82f6','awaiting':'#8b5cf6','completed':'#10b981'}
        st_lbl = Label(text=STATUS_MAP.get(st,st), font_size=sp(11), color=hex_to_rgb(st_colors.get(st,'#64748b'))+(1,), size_hint_x=0.35)
        top.add_widget(title); top.add_widget(st_lbl)
        
        unit = Label(text=f"🏢 {wo.get('unit_name','')}", font_size=sp(11), halign='left', color=hex_to_rgb("#64748b")+(1,), size_hint_y=None, height=dp(18))
        
        bottom = BoxLayout(size_hint_y=None, height=dp(18))
        time_lbl = Label(text=wo.get('created_at','')[:16], font_size=sp(10), halign='left', color=hex_to_rgb("#94a3b8")+(1,), size_hint_x=0.5)
        amt = (wo.get('labor_cost') or 0) + (wo.get('material_cost') or 0)
        sign = " ✓" if wo.get('signature_data') else ""
        amt_lbl = Label(text=f"¥{amt:.0f}{sign}", font_size=sp(12), bold=True, halign='right', color=hex_to_rgb("#0284c7")+(1,), size_hint_x=0.5)
        bottom.add_widget(time_lbl); bottom.add_widget(amt_lbl)
        
        card.add_widget(top); card.add_widget(unit); card.add_widget(bottom)
        def on_touch(touch):
            if card.collide_point(*touch.pos):
                self.manager.get_screen('detail').load(wo['id'])
                self.manager.current = 'detail'
                return True
        card.on_touch_down = on_touch
        return card


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'detail'
        self.wo_id = None
        self.wo = None
        self.sig_widget = None
        self._build_ui()
    
    def _build_ui(self):
        main = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        with header.canvas.before:
            Color(*hex_to_rgb("#1e3a8a"))
            header.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        btn_back = Button(text="← 返回", font_size=sp(14), size_hint_x=0.3, background_color=(1,1,1,0.2), background_normal='')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'workorders'))
        header.add_widget(btn_back)
        header.add_widget(Label(text="工单详情", font_size=sp(16), bold=True, color=(1,1,1,1)))
        
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.content.add_widget(Label(text="加载中...", size_hint_y=None, height=dp(100)))
        scroll.add_widget(self.content)
        
        main.add_widget(header); main.add_widget(scroll)
        self.add_widget(main)
    
    def load(self, wo_id):
        self.wo_id = wo_id
        self.wo = api.get_workorder(wo_id)
        self._render()
    
    def _render(self):
        self.content.clear_widgets()
        if 'error' in self.wo:
            self.content.add_widget(Label(text="加载失败", color=hex_to_rgb("#dc2626")+(1,)))
            return
        wo = self.wo
        self.content.add_widget(self._info_card(wo))
        self.content.add_widget(self._cost_card(wo))
        if wo.get('photos'):
            self.content.add_widget(self._photos_card(wo['photos']))
        self.content.add_widget(self._sig_card(wo))
        self.content.add_widget(self._status_card(wo))
    
    def _info_card(self, wo):
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(6))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        title = Label(text=wo.get('title','无标题'), font_size=sp(17), bold=True, halign='left', size_hint_y=None, height=dp(28), color=hex_to_rgb("#1e293b")+(1,))
        title.bind(texture_size=title.setter('size'))
        card.add_widget(title)
        for lbl, key in [("单位","unit_name"),("地点","location"),("报修人","reporter"),("联系方式","contact"),("创建时间","created_at")]:
            if wo.get(key):
                row = Label(text=f"{lbl}: {wo.get(key)}", font_size=sp(12), halign='left', size_hint_y=None, height=dp(20), color=hex_to_rgb("#64748b")+(1,))
                row.bind(texture_size=row.setter('size'))
                card.add_widget(row)
        if wo.get('content'):
            c = Label(text=f"详细描述:\n{wo.get('content')}", font_size=sp(12), halign='left', color=hex_to_rgb("#333333")+(1,))
            c.bind(texture_size=c.setter('size'))
            card.add_widget(c)
        return card
    
    def _cost_card(self, wo):
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(5))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        labor = wo.get('labor_cost') or 0
        material = wo.get('material_cost') or 0
        card.add_widget(Label(text=f"费用: 人工¥{labor:.0f} + 物料¥{material:.0f} = ¥{labor+material:.0f}", font_size=sp(14), bold=True, size_hint_y=None, height=dp(25), color=hex_to_rgb("#0284c7")+(1,)))
        ps = wo.get('payment_status','unpaid')
        pt = PAYMENT_STATUS_MAP.get(ps,ps)
        pc = "#10b981" if ps == 'paid' else "#f59e0b"
        card.add_widget(Label(text=f"结款状态: {pt}", font_size=sp(12), color=hex_to_rgb(pc)+(1,), size_hint_y=None, height=dp(20)))
        return card
    
    def _photos_card(self, photos):
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(8))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        card.add_widget(Label(text=f"📷 照片 ({len(photos)}张)", font_size=sp(13), bold=True, size_hint_y=None, height=dp(25), color=hex_to_rgb("#1e293b")+(1,)))
        grid = GridLayout(cols=3, size_hint_y=None, spacing=dp(5))
        grid.bind(minimum_height=grid.setter('height'))
        for p in photos[:6]:
            img = AsyncImage(source=api.get_file_url(p), size_hint_y=None, height=dp(80), allow_stretch=True)
            grid.add_widget(img)
        card.add_widget(grid)
        return card
    
    def _sig_card(self, wo):
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(8))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        card.add_widget(Label(text="✍️ 签名", font_size=sp(13), bold=True, size_hint_y=None, height=dp(25), color=hex_to_rgb("#1e293b")+(1,)))
        
        sig = wo.get('signature_data')
        if sig:
            img = AsyncImage(source=api.get_file_url(sig), size_hint_y=None, height=dp(150), allow_stretch=True)
            card.add_widget(img)
            if wo.get('signature_time'):
                card.add_widget(Label(text=f"签名时间: {wo.get('signature_time')}", font_size=sp(11), color=hex_to_rgb("#64748b")+(1,), size_hint_y=None, height=dp(20)))
        else:
            btn = Button(text="点击签名", font_size=sp(14), size_hint_y=None, height=dp(45), background_color=hex_to_rgb("#8b5cf6")+(1,), background_normal='')
            btn.bind(on_press=self._show_sig_popup)
            card.add_widget(btn)
        return card
    
    def _show_sig_popup(self, instance):
        popup = Popup(title="电子签名", size_hint=(0.95, 0.75))
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        self.sig_widget = SignatureWidget()
        content.add_widget(self.sig_widget)
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_cancel = Button(text="取消", font_size=sp(14), background_color=hex_to_rgb("#64748b")+(1,), background_normal='')
        btn_cancel.bind(on_press=popup.dismiss)
        btn_save = Button(text="确认签名", font_size=sp(14), background_color=hex_to_rgb("#10b981")+(1,), background_normal='')
        btn_save.bind(on_press=lambda x: self._save_sig(popup))
        btns.add_widget(btn_cancel); btns.add_widget(btn_save)
        content.add_widget(btns)
        popup.content = content
        popup.open()
    
    def _save_sig(self, popup):
        if not self.sig_widget.has_signature():
            Popup(title="提示", content=Label(text="请先签名"), size_hint=(0.6, 0.2)).open()
            return
        sig_data = self.sig_widget.get_signature_base64()
        if sig_data:
            result = api.save_signature(self.wo_id, sig_data)
            if 'error' not in result:
                popup.dismiss()
                self.load(self.wo_id)
                Popup(title="成功", content=Label(text="签名已保存"), size_hint=(0.6, 0.2)).open()
            else:
                Popup(title="失败", content=Label(text=str(result.get('error'))), size_hint=(0.6, 0.25)).open()
    
    def _status_card(self, wo):
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(12), spacing=dp(8))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        card.add_widget(Label(text="更新状态", font_size=sp(13), bold=True, size_hint_y=None, height=dp(22), color=hex_to_rgb("#1e293b")+(1,)))
        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        current = wo.get('status','pending')
        for sk, sv in STATUS_MAP.items():
            btn = Button(text=sv, font_size=sp(11), background_color=hex_to_rgb("#3b82f6" if sk==current else "#e5e7eb")+(1,), color=(1,1,1,1) if sk==current else (0,0,0,1), background_normal='')
            btn.bind(on_press=lambda x, s=sk: self._update_status(s))
            btn_row.add_widget(btn)
        card.add_widget(btn_row)
        return card
    
    def _update_status(self, new_status):
        result = api.update_status(self.wo_id, new_status)
        if 'error' not in result:
            self.load(self.wo_id)
            Popup(title="成功", content=Label(text="状态已更新"), size_hint=(0.6, 0.2)).open()


class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'admin_login'
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))
        layout.add_widget(Label(text="📊 管理员登录", font_size=sp(24), bold=True, size_hint_y=None, height=dp(60)))
        self.pwd = TextInput(hint_text="请输入管理员密码", password=True, multiline=False, size_hint_y=None, height=dp(50), font_size=sp(16))
        layout.add_widget(self.pwd)
        btn_login = Button(text="登录", font_size=sp(16), size_hint_y=None, height=dp(50), background_color=hex_to_rgb("#667eea")+(1,), background_normal='')
        btn_login.bind(on_press=self._login)
        layout.add_widget(btn_login)
        btn_back = Button(text="返回首页", font_size=sp(14), size_hint_y=None, height=dp(40), background_color=hex_to_rgb("#64748b")+(1,), background_normal='')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(btn_back)
        self.add_widget(layout)
    
    def _login(self, instance):
        if self.pwd.text == ADMIN_PASSWORD:
            self.manager.current = 'admin'
        else:
            Popup(title="错误", content=Label(text="密码错误"), size_hint=(0.6, 0.25)).open()
        self.pwd.text = ""


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'admin'
        self._build_ui()
        Clock.schedule_once(self._load, 0.2)
    
    def _build_ui(self):
        main = BoxLayout(orientation='vertical')
        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        with header.canvas.before:
            Color(*hex_to_rgb("#1e3a8a"))
            header.rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        btn_back = Button(text="← 返回", font_size=sp(14), size_hint_x=0.3, background_color=(1,1,1,0.2), background_normal='')
        btn_back.bind(on_press=self._logout)
        header.add_widget(btn_back)
        header.add_widget(Label(text="📊 管理后台", font_size=sp(16), bold=True, color=(1,1,1,1)))
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        self.content.add_widget(Label(text="加载中...", size_hint_y=None, height=dp(100)))
        scroll.add_widget(self.content)
        main.add_widget(header); main.add_widget(scroll)
        self.add_widget(main)
    
    def _load(self, dt):
        stats = api.get_stats()
        self.content.clear_widgets()
        if 'error' in stats:
            self.content.add_widget(Label(text="加载失败", color=hex_to_rgb("#dc2626")+(1,)))
            return
        pay = stats.get('payment', {})
        paid = pay.get('paid', {}).get('amount', 0)
        unpaid = pay.get('unpaid', {}).get('amount', 0)
        
        card = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(8))
        with card.canvas.before:
            Color(1,1,1,1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(pos=lambda i,v: setattr(i.rect,'pos',v), size=lambda i,v: setattr(i.rect,'size',v))
        card.add_widget(Label(text="💰 财务统计", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30), color=hex_to_rgb("#1e293b")+(1,)))
        card.add_widget(Label(text=f"已结款: ¥{paid:.0f}", font_size=sp(14), color=hex_to_rgb("#10b981")+(1,), size_hint_y=None, height=dp(25)))
        card.add_widget(Label(text=f"未结款: ¥{unpaid:.0f}", font_size=sp(14), color=hex_to_rgb("#f59e0b")+(1,), size_hint_y=None, height=dp(25)))
        card.add_widget(Label(text=f"总计: ¥{paid+unpaid:.0f}", font_size=sp(14), bold=True, color=hex_to_rgb("#0284c7")+(1,), size_hint_y=None, height=dp(25)))
        self.content.add_widget(card)
        
        btn = Button(text="退出登录", font_size=sp(14), size_hint_y=None, height=dp(45), background_color=hex_to_rgb("#dc2626")+(1,), background_normal='')
        btn.bind(on_press=self._logout)
        self.content.add_widget(btn)
    
    def _logout(self, instance):
        api.admin_logout()
        self.manager.current = 'home'


class WorkorderApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(CreateScreen())
        sm.add_widget(WorkordersScreen())
        sm.add_widget(DetailScreen())
        sm.add_widget(AdminLoginScreen())
        sm.add_widget(AdminScreen())
        return sm


if __name__ == '__main__':
    WorkorderApp().run()
