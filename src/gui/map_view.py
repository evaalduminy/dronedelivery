"""
3D Map View for Drone Visualization
"""

import numpy as np
import math
import random
import time
from typing import Dict, List, Tuple, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint, QRect, QPointF
from PyQt5.QtGui import QImage, QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient, QPolygon, QConicalGradient, QFont


from ..utils.logger import get_logger


class MapView(QWidget):
    """
    عرض الخريطة ثلاثية الأبعاد
    
    يعرض:
    - المدينة والمباني
    - الطائرة المسيرة
    - المسار والأهداف
    - العقبات والمناطق المحظورة
    """
    
    # إشارات مخصصة
    drone_clicked = pyqtSignal(object)  # موقع الطائرة عند النقر
    target_selected = pyqtSignal(tuple) # موقع الهدف الجديد
    
    def __init__(self):
        """تهيئة عرض الخريطة"""
        super().__init__()
        
        self.logger = get_logger()
        
        # البيئة
        self.env = None
        
        # إعدادات العرض
        self.camera_pos = [150, 150, 100]  # موقع الكاميرا
        self.camera_target = [100, 100, 0]  # هدف الكاميرا
        self.zoom = 1.0
        self.rotation_x = -30  # زاوية الدوران حول X
        self.rotation_z = 45   # زاوية الدوران حول Z
        
        # إعدادات الألوان
        self.colors = {
            'sky': (135, 206, 235),
            'ground': (34, 139, 34),
            'building': (128, 128, 128),
            'hospital': (255, 0, 0),
            'lab': (0, 0, 255),
            'drone': (255, 255, 0),
            'path': (255, 165, 0),
            'no_fly': (255, 0, 0, 100),
            'target': (0, 255, 0)
        }
        
        # حالة الرسم
        self.show_path = True
        self.show_no_fly_zones = True
        self.show_grid = True
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
        # مؤقت التحديث
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(50)  # 20 FPS
        
        self.logger.info("Map view initialized")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # منطقة الرسم
        self.canvas = MapCanvas()
        self.canvas.setMinimumSize(800, 600)
        layout.addWidget(self.canvas)
        
        # أدوات التحكم
        controls_layout = QHBoxLayout()
        
        # أزرار العرض
        self.path_btn = QPushButton("إظهار المسار")
        self.path_btn.setToolTip("إظهار أو إخفاء مسار الطائرة")
        self.path_btn.setCheckable(True)
        self.path_btn.setChecked(True)
        self.path_btn.clicked.connect(self.toggle_path)
        controls_layout.addWidget(self.path_btn)
        
        self.no_fly_btn = QPushButton("المناطق المحظورة")
        self.no_fly_btn.setToolTip("إظهار أو إخفاء مناطق حظر الطيران")
        self.no_fly_btn.setCheckable(True)
        self.no_fly_btn.setChecked(True)
        self.no_fly_btn.clicked.connect(self.toggle_no_fly_zones)
        controls_layout.addWidget(self.no_fly_btn)
        
        self.grid_btn = QPushButton("إظهار الشبكة")
        self.grid_btn.setToolTip("إظهار أو إخفاء الشبكة الأرضية")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        self.grid_btn.clicked.connect(self.toggle_grid)
        controls_layout.addWidget(self.grid_btn)
        
        # التكبير
        controls_layout.addWidget(QLabel("التكبير:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setToolTip("تعديل مستوى تكبير الخريطة")
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        controls_layout.addWidget(self.zoom_slider)
        
        # إعادة التعيين
        reset_btn = QPushButton("إعادة العرض")
        reset_btn.setToolTip("إعادة إعدادات الكاميرا والزوم للوضع الافتراضي")
        reset_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(reset_btn)
        
        layout.addLayout(controls_layout)
        
        # ربط الأحداث
        self.canvas.mouse_clicked.connect(self.on_canvas_clicked)
    
    def set_environment(self, env):
        """تعيين البيئة للعرض"""
        self.env = env
        self.canvas.set_environment(env)
        self.update_display()
    
    def update_display(self):
        """تحديث العرض"""
        if self.env:
            self.canvas.update_view(
                camera_pos=self.camera_pos,
                camera_target=self.camera_target,
                zoom=self.zoom,
                rotation_x=self.rotation_x,
                rotation_z=self.rotation_z,
                show_path=self.show_path,
                show_no_fly_zones=self.show_no_fly_zones,
                show_grid=self.show_grid
            )
    
    def toggle_path(self, checked):
        """تبديل عرض المسار"""
        self.show_path = checked
        self.update_display()
    
    def toggle_no_fly_zones(self, checked):
        """تبديل عرض المناطق المحظورة"""
        self.show_no_fly_zones = checked
        self.update_display()
    
    def toggle_grid(self, checked):
        """تبديل عرض الشبكة"""
        self.show_grid = checked
        self.update_display()
    
    def change_zoom(self, value):
        """تغيير التكبير"""
        self.zoom = value / 100.0
        self.update_display()
    
    def reset_view(self):
        """إعادة تعيين العرض"""
        self.camera_pos = [150, 150, 100]
        self.camera_target = [100, 100, 0]
        self.zoom = 1.0
        self.rotation_x = -30
        self.rotation_z = 45
        self.zoom_slider.setValue(100)
        self.update_display()
    
    def on_canvas_clicked(self, position):
        """التعامل مع النقر على الكانفاس"""
        if self.env:
            # تحويل موقع النقر إلى إحداثيات العالم
            world_pos = self.canvas.screen_to_world(position)
            
            # التحقق من أن النقر ضمن الحدود (0-50) مع هامش صغير
            GRID_SIZE = 50
            if 0 <= world_pos[0] <= GRID_SIZE and 0 <= world_pos[1] <= GRID_SIZE:
                # تقييد القيم ضمن الحدود الفعلية
                target_x = max(0, min(GRID_SIZE, world_pos[0]))
                target_y = max(0, min(GRID_SIZE, world_pos[1]))
                
                self.logger.info(f"GUI: Map Clicked -> Target Emitted: ({target_x:.1f}, {target_y:.1f})")
                self.target_selected.emit((target_x, target_y))
            else:
                self.logger.warning(f"GUI: Click out of bounds: {world_pos[:2]}")


class MapCanvas(QWidget):
    """
    كانفاس الرسم للخريطة
    """
    
    # إشارات مخصصة
    mouse_clicked = pyqtSignal(object)
    
    def __init__(self):
        """تهيئة الكانفاس"""
        super().__init__()
        
        self.env = None
        
        # إعدادات العرض
        self.width = 800
        self.height = 600
        
        # 🎬 التنعيم البصري (Visual Smoothing)
        self.render_pos = [25, 25, 5] # الموقع الذي يتم رسمه فعلياً
        self.smoothness = 0.15 # معامل التنعيم (Lerp factor)
        self.path_history = [] # سجل المواقع لرسم المسار
        self.max_path_points = 200 # أقصى عدد من النقاط في المسار
        
    def set_environment(self, env):
        """تعيين البيئة"""
        self.env = env
        self.path_history = [] # مسح التتبع القديم
        if env and env.drone:
            self.render_pos = list(env.drone.position)
        self.update()
    
    def update_view(self, **kwargs):
        """تحديث العرض"""
        # تخزين الإعدادات الحالية
        self.show_path = kwargs.get('show_path', True)
        self.show_no_fly_zones = kwargs.get('show_no_fly_zones', True)
        self.show_grid = kwargs.get('show_grid', True)
        self.zoom = kwargs.get('zoom', 1.0)
        self.update()
    
    def paintEvent(self, event):
        """رسم احترافي عالي الجودة"""
        if not self.env:
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.black)
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, "بانتظار تهيئة البيئة...")
            painter.end()
            return
            
        try:
            # 🚀 تحديث الموقع المنعم (Lerp)
            if self.env.drone:
                target_pos = self.env.drone.position
                for i in range(3):
                    # تحريك الموقع المنعم ببطء نحو موقع الدرون الحقيقي
                    self.render_pos[i] += (target_pos[i] - self.render_pos[i]) * self.smoothness
                    
                # إضافة الموقع الحالي للسجل (لحذف النقاط القديمة جداً)
                if not self.path_history or np.linalg.norm(np.array(self.render_pos) - np.array(self.path_history[-1])) > 0.2:
                    self.path_history.append(list(self.render_pos))
                    if len(self.path_history) > self.max_path_points:
                        self.path_history.pop(0)

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 1. رسم السماء (تدرج ليلي عميق)
            sky_gradient = QLinearGradient(0, 0, 0, self.height)
            sky_gradient.setColorAt(0, QColor(10, 10, 35))
            sky_gradient.setColorAt(0.6, QColor(25, 25, 70))
            sky_gradient.setColorAt(1, QColor(40, 60, 110))
            painter.fillRect(self.rect(), sky_gradient)
            
            # إضافة نجوم (Atmospheric Stars)
            random.seed(42) # للثبات
            painter.setPen(QColor(255, 255, 255, 150))
            for _ in range(50):
                px = random.randint(0, self.width)
                py = random.randint(0, int(self.height * 0.6))
                size = random.randint(1, 2)
                painter.drawEllipse(px, py, size, size)
            
            # 2. رسم الأرض (Stylized City Floor)
            ground_y = int(self.height * 0.7)
            ground_rect = QRect(0, ground_y, self.width, self.height - ground_y)
            
            # تدرج للأرض مع تأثير "أرضية المدينة"
            ground_grad = QLinearGradient(0, ground_rect.top(), 0, ground_rect.bottom())
            ground_grad.setColorAt(0, QColor(20, 40, 20)) # أخضر داكن جداً
            ground_grad.setColorAt(1, QColor(5, 15, 5))
            painter.fillRect(ground_rect, ground_grad)

            # 2.5 رسم الشبكة الأرضية (Cyber Grid)
            if hasattr(self, 'show_grid') and self.show_grid:
                self.draw_grid(painter)
            
            # 3. رسم الكيانات (المباني، الأهداف، الطائرة)
            if hasattr(self.env, 'obstacles') and self.env.obstacles:
                # ترتيب رسم المباني لجعل البعيد خلف القريب
                buildings = sorted(self.env.obstacles.buildings, key=lambda b: b.position[1], reverse=True)
                
                for building in buildings:
                    self.draw_building_3d(painter, building)
                    
                # رسم المناطق المحظورة (توهج أحمر)
                if getattr(self, 'show_no_fly_zones', True):
                    for zone in self.env.obstacles.no_fly_zones:
                        self.draw_no_fly_zone(painter, zone)
                
                # إظهار مسار الدرون السابق
                if getattr(self, 'show_path', True):
                    self.draw_path(painter)
                
            # 4. رسم الأهداف (توهج نابض)
            if hasattr(self.env, 'start_position') and self.env.start_position:
                self.draw_target(painter, self.env.start_position, QColor(46, 204, 113), "نقطة الاستلام")
                
            if hasattr(self.env, 'target_position') and self.env.target_position:
                self.draw_target(painter, self.env.target_position, QColor(155, 89, 182), "نقطة التسليم")
                
            # 5. رسم الطائرة (موديل مفصل مع مراوح)
            if hasattr(self.env, 'drone') and self.env.drone:
                self.draw_drone_high_res(painter, self.env.drone)
                
                # 6. رسم خط إرشاد للهدف (Target Guide Line)
                if hasattr(self.env, 'target_position') and self.env.target_position:
                    self.draw_target_guide(painter)
            
            # 7. رسم واجهة المعلومات العلوية (HUD)
            self.draw_hud(painter)
            
            painter.end()
        except Exception as e:
            from ..utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Error in MapCanvas.paintEvent: {e}")
            if painter.isActive():
                painter.end()

    def draw_path(self, painter):
        """رسم مسار الطائرة السابق بخط متدرج متوهج"""
        if len(self.path_history) < 2:
            return
            
        painter.save()
        
        # إعداد القلم لرسم المسار
        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        
        # رسم المسار كخطوط متصلة
        for i in range(len(self.path_history) - 1):
            p1 = self.world_to_screen(self.path_history[i])
            p2 = self.world_to_screen(self.path_history[i+1])
            
            # تدرج لوني للمسار (يتلاشى في البداية ويزداد سطوعاً عند الدرون)
            alpha = int(255 * (i / len(self.path_history)))
            color = QColor(255, 165, 0, alpha) # برتقالي متلاشي
            pen.setColor(color)
            painter.setPen(pen)
            
            painter.drawLine(p1[0], p1[1], p2[0], p2[1])
            
        painter.restore()

    def draw_grid(self, painter):
        """رسم شبكة إحداثيات أرضية بتأثير تقني"""
        grid_pen = QPen(QColor(0, 255, 255, 30), 1)
        painter.setPen(grid_pen)
        
        # رسم الخطوط الرئيسية
        for i in range(0, 51, 5):
            # خطوط موازية لـ X
            p1 = self.world_to_screen((0, i, 0))
            p2 = self.world_to_screen((50, i, 0))
            painter.drawLine(p1[0], p1[1], p2[0], p2[1])
            
            # خطوط موازية لـ Y
            p1 = self.world_to_screen((i, 0, 0))
            p2 = self.world_to_screen((i, 50, 0))
            painter.drawLine(p1[0], p1[1], p2[0], p2[1])

    def draw_building_3d(self, painter, building):
        """رسم مبنى بواقعية محسنة"""
        bx, by = building.position
        base_pos = self.world_to_screen((bx, by, 0))
        
        # تحجيم متناسب مع الزووم
        zom = getattr(self, 'zoom', 1.0)
        height_px = int(building.height * 20 * zom)
        width_px = int(35 * zom)
        
        # تحديد لون المبنى
        try:
            type_name = str(building.zone_type).lower()
        except:
            type_name = "building"

        if 'hospital' in type_name:
            main_color = QColor(192, 57, 43) # أحمر طبي (Deep Red)
        elif 'lab' in type_name:
            main_color = QColor(41, 128, 185) # أزرق تقني (Belize Hole)
        else:
            main_color = QColor(52, 73, 94) # رمادي مدني (Wet Asphalt)
            
        # 1. الوجه الأمامي (Main Facade)
        front_rect = QRect(base_pos[0] - width_px//2, base_pos[1] - height_px, width_px, height_px)
        
        # تدرج للإضاءة من الأعلى
        facade_grad = QLinearGradient(front_rect.topLeft(), front_rect.bottomLeft())
        facade_grad.setColorAt(0, main_color.lighter(120))
        facade_grad.setColorAt(1, main_color.darker(120))
        
        painter.setBrush(facade_grad)
        painter.setPen(QPen(main_color.darker(150), 1))
        painter.drawRect(front_rect)
        
        # 2. الوجه الجانبي (Side Shadow)
        side_depth = int(12 * zom)
        side_poly = QPolygon([
            QPoint(front_rect.right(), front_rect.top()),
            QPoint(front_rect.right() + side_depth, front_rect.top() - int(side_depth * 0.7)),
            QPoint(front_rect.right() + side_depth, front_rect.bottom() - int(side_depth * 0.7)),
            QPoint(front_rect.right(), front_rect.bottom())
        ])
        painter.setBrush(main_color.darker(150))
        painter.drawPolygon(side_poly)
        
        # 3. الوجه العلوي (Roof Detail)
        top_poly = QPolygon([
            QPoint(front_rect.left(), front_rect.top()),
            QPoint(front_rect.left() + side_depth, front_rect.top() - int(side_depth * 0.7)),
            QPoint(front_rect.right() + side_depth, front_rect.top() - int(side_depth * 0.7)),
            QPoint(front_rect.right(), front_rect.top())
        ])
        painter.setBrush(main_color.lighter(150))
        painter.drawPolygon(top_poly)
        
        # 4. إضافة نوافذ مضيئة (Windows)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 190, 180)) # لون الضوء الدافئ
        for i in range(1, 5):
            for j in range(1, 4):
                # احتمال عشوائي لفتح النور
                if hash(f"{bx}{by}{i}{j}") % 5 > 1:
                    win_x = front_rect.left() + j * (width_px // 4)
                    win_y = front_rect.top() + i * (height_px // 6)
                    painter.drawRect(win_x, win_y, int(4*zom), int(4*zom))

    def draw_no_fly_zone(self, painter, zone):
        """رسم منطقة محظورة بتأثير "قبة أمنية" """
        zx, zy = zone.center
        center = self.world_to_screen((zx, zy, 0))
        zom = getattr(self, 'zoom', 1.0)
        radius = int(zone.radius * 12 * zom)
        
        # تدرج شعاعي يعطي إيحاء بالقبة
        grad = QRadialGradient(QPoint(center[0], center[1]), radius)
        grad.setColorAt(0, QColor(255, 0, 0, 40))
        grad.setColorAt(0.8, QColor(255, 0, 0, 20))
        grad.setColorAt(1, Qt.transparent)
        
        painter.setBrush(grad)
        painter.setPen(QPen(QColor(255, 0, 0, 100), 1, Qt.DashLine))
        painter.drawEllipse(center[0] - radius, center[1] - radius, radius * 2, radius * 2)

    def draw_target(self, painter, world_pos, color, label):
        """رسم هدف بتأثير Holo-display"""
        if len(world_pos) == 2:
            world_pos = (*world_pos, 0)
        pos = self.world_to_screen(world_pos)
        zom = getattr(self, 'zoom', 1.0)
        
        # تأثير التوهج الشعاعي
        t = time.time()
        pulse = math.sin(t * 4.0) * 5
        glow_radius = (20 + pulse) * zom
        
        grad = QRadialGradient(QPoint(pos[0], pos[1]), glow_radius)
        grad.setColorAt(0, color)
        grad.setColorAt(1, Qt.transparent)
        
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos[0] - int(glow_radius), pos[1] - int(glow_radius), int(glow_radius*2), int(glow_radius*2))
        
        # رسم الحلقات الخارجية (Cyber UI style)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(color, 2))
        painter.drawEllipse(pos[0] - int(10*zom), pos[1] - int(10*zom), int(20*zom), int(20*zom))
        
        # كتابة اسم الموقع
        painter.setPen(Qt.white)
        font = painter.font()
        font.setPointSize(max(8, int(10 * zom)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pos[0] + 15, pos[1] + 5, label)

    def draw_drone_high_res(self, painter, drone):
        """رسم الدرون بتفاصيل ميكانيكية"""
        # استخدام render_pos بدلاً من drone.position للحصول على حركة سلسة
        pos = self.world_to_screen(self.render_pos)
        zom = getattr(self, 'zoom', 1.0)
        drone_scale = 1.8 * zom
        
        # 1. ظل ناعم
        painter.setBrush(QColor(0, 0, 0, 80))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pos[0] - int(12*drone_scale), pos[1] + int(25*drone_scale), int(24*drone_scale), int(12*drone_scale))
        
        painter.save()
        painter.translate(pos[0], pos[1])
        painter.scale(drone_scale, drone_scale)
        
        # الدوران بناءً على الاتجاه (Heading)
        heading = getattr(drone, 'heading', 0)
        painter.rotate(heading) # دوران الموديل بالكامل
        
        # الأذرع الميكانيكية (Carbon Fiber look)
        painter.setPen(QPen(QColor(40, 40, 40), 4))
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            painter.drawLine(0, 0, int(16 * math.cos(rad)), int(16 * math.sin(rad)))
            
        # المراوح الدوارة
        t = time.time()
        prop_rot = (t * 2000) % 360 # سرعة دوران عالية
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            px, py = int(16 * math.cos(rad)), int(16 * math.sin(rad))
            
            # محركات المراوح
            painter.setBrush(QColor(80, 80, 80))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(px - 4, py - 4, 8, 8)
            
            # تأثير الشفرات السريعة
            painter.setPen(QPen(QColor(220, 220, 220, 120), 1))
            p_rad = math.radians(prop_rot)
            painter.drawLine(px, py, px + int(10 * math.cos(p_rad)), py + int(10 * math.sin(p_rad)))
            painter.drawLine(px, py, px - int(10 * math.cos(p_rad)), py - int(10 * math.sin(p_rad)))
        
        # جسم الدرون (الكبسولة الرئيسية)
        body_grad = QConicalGradient(0, 0, 0)
        body_grad.setColorAt(0, QColor(240, 240, 240))
        body_grad.setColorAt(0.5, QColor(180, 180, 180))
        body_grad.setColorAt(1, QColor(240, 240, 240))
        
        painter.setBrush(body_grad)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(-9, -9, 18, 18)
        
        # ضوء الحالة (LED)
        led_color = Qt.red if getattr(drone, 'has_package', False) else Qt.cyan
        painter.setBrush(led_color)
        painter.drawEllipse(-3, -3, 6, 6)
        
        painter.restore()
        
        # سهم اتجاه الحركة (بخط متوهج)
        rad = math.radians(heading)
        end_x = pos[0] + int(45 * drone_scale * math.cos(rad))
        end_y = pos[1] + int(45 * drone_scale * math.sin(rad))
        painter.setPen(QPen(led_color, 2, Qt.DashLine))
        painter.drawLine(pos[0], pos[1], end_x, end_y)

    def draw_target_guide(self, painter):
        """رسم خط إرشادي من الدرون إلى الهدف"""
        # استخدام الموقع المنعم لجعل الخط متناسقاً مع حركة الدرون
        drone_pos = self.render_pos
        target_pos = self.env.target_position
        
        p1 = self.world_to_screen(drone_pos)
        p2 = self.world_to_screen(target_pos)
        
        # خط منقط متوهج
        pen = QPen(QColor(0, 255, 255, 100), 1, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(p1[0], p1[1], p2[0], p2[1])

    def draw_hud(self, painter):
        """رسم لوحة معلومات شفافة مع توجيهات للمستخدم"""
        painter.save()
        
        # صندوق المعلومات
        hud_rect = QRect(20, 20, 260, 110)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor(0, 255, 255, 120), 1))
        painter.drawRoundedRect(hud_rect, 8, 8)
        
        # إعداد الخط
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        if self.env and self.env.drone:
            # 1. حالة المحاكاة (مهم جداً)
            is_running = getattr(self.window(), 'is_simulation_running', False)
            if not is_running:
                painter.setPen(QColor(255, 100, 100)) # أحمر تحذيري
                painter.drawText(35, 45, "⚠️ المحاكاة متوقفة - اضغط 'بدء'")
            else:
                painter.setPen(QColor(100, 255, 100)) # أخضر
                painter.drawText(35, 45, "✅ المحاكاة تعمل بنجاح")

            # 2. حالة الدرون
            painter.setPen(Qt.white)
            status_text = "الدرون: في وضع الاستعداد"
            if self.env.drone.has_package:
                 status_text = "الدرون: يحمل شحنة طبية 📦"
            painter.drawText(35, 70, status_text)
            
            # 3. توجيه النقر
            painter.setPen(QColor(255, 255, 100))
            font.setPointSize(8)
            font.setBold(False)
            painter.setFont(font)
            painter.drawText(35, 95, "💡 انقر على الخريطة لتغيير الهدف")
            
        painter.restore()

    def resizeEvent(self, event):
        """التعامل مع تغيير الحجم"""
        self.width = event.size().width()
        self.height = event.size().height()
        self.update()

    def world_to_screen(self, world_pos):
        """تحويل إحداثيات العالم إلى إحداثيات الشاشة بأسلوب المنظور"""
        # استخدام نظام إحداثيات مركز في أسفل الشاشة لإعطاء طابع العمق
        offset_x = self.width // 2
        offset_y = int(self.height * 0.7)
        
        # GRID_SIZE is 50, so we want to center (25, 25)
        # Scale world units to pixels
        base_scale = min(self.width, self.height) / 70.0
        # Ensure self.zoom is defined
        zom = getattr(self, 'zoom', 1.0)
        scale = base_scale * zom 
        
        # Perspective effect: Y coordinate increases as we go "into" the screen
        # X: (world_x - 25) * scale
        # Y: (world_y - 25) * scale * 0.7 (foreshortening)
        
        # Handle 2D or 3D positions
        if len(world_pos) == 2:
            world_x, world_y = world_pos
            world_z = 0
        else:
            world_x, world_y, world_z = world_pos
        
        # Perspective distortion
        dist_from_bottom = (world_y / 50.0)
        perspective_factor = 1.0 - (dist_from_bottom * 0.4)
        
        screen_x = offset_x + int((world_x - 25) * scale * perspective_factor)
        screen_y = offset_y - int((world_y - 25) * scale * 0.6)
        
        # Altitude effect
        screen_y -= int(world_z * scale * 0.8)
        
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos):
        """تحويل إحداثيات الشاشة إلى إحداثيات العالم بدقة عالية"""
        offset_x = self.width // 2
        offset_y = int(self.height * 0.7)
        
        base_scale = min(self.width, self.height) / 70.0
        scale = base_scale * getattr(self, 'zoom', 1.0)
        
        # 1. حساب Y أولاً (لأنه يؤثر على المنظور)
        # العلاقة: screen_y = offset_y - (world_y - 25) * scale * 0.6
        world_y = 25 - (screen_pos[1] - offset_y) / (scale * 0.6)
        
        # 2. حساب عامل المنظور بناءً على Y المحسوب
        dist_from_bottom = (world_y / 50.0)
        perspective_factor = 1.0 - (max(0.0, min(1.0, dist_from_bottom)) * 0.4)
        
        # 3. حساب X مع مراعاة المنظور
        # العلاقة: screen_x = offset_x + (world_x - 25) * scale * perspective_factor
        world_x = 25 + (screen_pos[0] - offset_x) / (scale * perspective_factor)
        
        return (world_x, world_y, 0)
    
    def mousePressEvent(self, event):
        """التعامل مع النقر بالماوس"""
        if event.button() == Qt.LeftButton:
            pos = (event.x(), event.y())
            self.mouse_clicked.emit(pos)
            self.update()
