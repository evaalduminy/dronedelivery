"""
Main Window for Drone Delivery GUI
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QStatusBar, QAction, QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from .map_view import MapView
from .control_panel import ControlPanel
from ..ai.hybrid_controller import HybridController
from ..environment.city import CityEnvironment
from ..utils.logger import get_logger
from ..utils.config import ACTIONS, GRID_SIZE, MAX_ALTITUDE


class MainWindow(QMainWindow):
    """
    النافذة الرئيسية للتطبيق
    
    تحتوي على:
    - عرض الخريطة ثلاثية الأبعاد
    - لوحة التحكم
    - قوائم وأشرطة الأدوات
    """
    
    # إشارات مخصصة
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    
    def __init__(self):
        """تهيئة النافذة الرئيسية"""
        super().__init__()
        
        self.logger = get_logger()
        
        # المكونات الأساسية
        self.env = None
        self.controller = None
        self.simulation_timer = QTimer()
        self.is_simulation_running = False
        
        # إعداد النافذة
        self.setup_ui()
        self.setup_connections()
        
        # تحميل الإعدادات
        self.load_settings()
        
        self.logger.info("Main window initialized")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        
        # إعدادات النافذة الأساسية
        self.setWindowTitle("🚁 نظام توصيل الطائرات المسيرة ذاتي القيادة")
        self.setGeometry(100, 100, 1400, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # إعداد الخط
        font = QFont("Arial", 10)
        self.setFont(font)
        
        # إنشاء القوائم
        self.create_menus()
        
        # إنشاء شريط الحالة
        self.create_status_bar()
        
        # إنشاء الواجهة المركزية
        self.create_central_widget()
        
        # تطبيق الستايل
        self.apply_style()
    
    def create_menus(self):
        """إنشاء القوائم"""
        menubar = self.menuBar()
        
        # قائمة الملف
        file_menu = menubar.addMenu('&ملف')
        
        # تحميل نموذج
        load_action = QAction('&تحميل النموذج', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setStatusTip('تحميل نموذج ذكاء اصطناعي مدرب مسبقاً')
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)
        
        # حفظ نموذج
        save_action = QAction('&حفظ النموذج', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('حفظ النموذج الحالي')
        save_action.triggered.connect(self.save_model)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # خروج
        exit_action = QAction('&خروج', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('إغلاق التطبيق')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # قائمة المحاكاة
        sim_menu = menubar.addMenu('&محاكاة')
        
        # بدء المحاكاة
        self.start_action = QAction('&بدء المحاكاة', self)
        self.start_action.setShortcut('F5')
        self.start_action.setStatusTip('بدء مهمة توصيل جديدة')
        self.start_action.triggered.connect(self.start_simulation)
        sim_menu.addAction(self.start_action)
        
        # إيقاف المحاكاة
        self.stop_action = QAction('&إيقاف المحاكاة', self)
        self.stop_action.setShortcut('F6')
        self.stop_action.setStatusTip('إيقاف المحاكاة الحالية مؤقتاً')
        self.stop_action.setEnabled(False)
        sim_menu.addAction(self.stop_action)
        
        # إعادة تعيين
        reset_action = QAction('&إعادة تعيين البيئة', self)
        reset_action.setShortcut('F7')
        reset_action.setStatusTip('إعادة تعيين المدينة وموقع الطائرة')
        reset_action.triggered.connect(self.reset_environment)
        sim_menu.addAction(reset_action)
        
        sim_menu.addSeparator()
        
        # وضع التدريب
        self.training_action = QAction('&وضع التدريب', self)
        self.training_action.setCheckable(True)
        self.training_action.setStatusTip('تمكين تحديث النموذج أثناء الطيران')
        self.training_action.triggered.connect(self.toggle_training_mode)
        sim_menu.addAction(self.training_action)
        
        # قائمة المساعدة
        help_menu = menubar.addMenu('&مساعدة')
        
        # حول
        about_action = QAction('&حول التطبيق', self)
        about_action.setStatusTip('معلومات حول النظام وتقنياته')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("جاهز - قم بتحميل نموذج للبدء")
    
    def create_central_widget(self):
        """إنشاء الواجهة المركزية"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # التخطيط الرئيسي
        main_layout = QHBoxLayout(central_widget)
        
        # إنشاء المقسم
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # عرض الخريطة (الجانب الأيسر)
        self.map_view = MapView()
        splitter.addWidget(self.map_view)
        
        # لوحة التحكم (الجانب الأيمن)
        self.control_panel = ControlPanel()
        self.control_panel.setMinimumWidth(450) # Ensure it's wide enough for tabs
        splitter.addWidget(self.control_panel)
        
        # تعيين النسب
        splitter.setSizes([900, 500])  # Adjust sizes
    
    def setup_connections(self):
        """إعداد الاتصالات بين المكونات"""
        
        # اتصالات المحاكاة
        self.simulation_timer.timeout.connect(self.simulation_step)
        
        # اتصالات لوحة التحكم
        self.control_panel.start_requested.connect(self.start_simulation)
        self.control_panel.stop_requested.connect(self.stop_simulation)
        self.control_panel.reset_requested.connect(self.reset_environment)
        self.control_panel.speed_changed.connect(self.change_simulation_speed)
        
        # اتصالات عرض الخريطة
        self.map_view.drone_clicked.connect(self.on_drone_clicked)
        self.map_view.target_selected.connect(self.set_manual_target)
    
    def apply_style(self):
        """تطبيق الستايل على النافذة"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            border: none;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #34495e;
        }
        
        QStatusBar {
            background-color: #34495e;
            color: white;
            border: none;
        }
        
        QSplitter::handle {
            background-color: #bdc3c7;
            width: 2px;
        }
        
        QSplitter::handle:hover {
            background-color: #3498db;
        }
        """
        
        self.setStyleSheet(style)
    
    def initialize_simulation(self):
        """تهيئة المحاكاة"""
        try:
            # إنشاء البيئة والمتحكم
            self.env = CityEnvironment()
            self.controller = HybridController()
            
            # محاولة تحميل نموذج محفوظ
            model_loaded = self.controller.load_models()
            
            if model_loaded:
                self.status_bar.showMessage("تم تحميل النموذج بنجاح")
                self.logger.info("Pre-trained model loaded")
            else:
                self.status_bar.showMessage("لم يتم العثور على نموذج - استخدام سياسة عشوائية")
                self.logger.warning("No pre-trained model found")
            
            # تحديث واجهة المستخدم
            self.map_view.set_environment(self.env)
            self.control_panel.set_controller(self.controller)
            self.control_panel.start_btn.setEnabled(True)
            self.control_panel.stop_btn.setEnabled(False)
            self.control_panel.reset_btn.setEnabled(True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize simulation: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize simulation:\n{str(e)}")
            return False
    
    def start_simulation(self):
        """بدء المحاكاة"""
        if not self.env or not self.controller:
            if not self.initialize_simulation():
                return
        
        if not self.is_simulation_running:
            # إعادة تعيين البيئة
            state = self.env.reset()
            
            # بدء المؤقت
            speed = self.control_panel.get_simulation_speed()
            self.simulation_timer.start(int(1000 / speed))  # FPS to milliseconds
            
            self.is_simulation_running = True
            
            # تحديث واجهة المستخدم
            self.start_action.setEnabled(False)
            self.stop_action.setEnabled(True)
            self.control_panel.start_btn.setEnabled(False)
            self.control_panel.stop_btn.setEnabled(True)
            self.status_bar.showMessage("المحاكاة تعمل...")
            
            # إشارة بدء المحاكاة
            self.simulation_started.emit()
            
            self.logger.info("Simulation started")
    
    def stop_simulation(self):
        """إيقاف المحاكاة"""
        if self.is_simulation_running:
            self.simulation_timer.stop()
            self.is_simulation_running = False
            
            # تحديث واجهة المستخدم
            self.start_action.setEnabled(True)
            self.stop_action.setEnabled(False)
            self.control_panel.start_btn.setEnabled(True)
            self.control_panel.stop_btn.setEnabled(False)
            self.status_bar.showMessage("تم إيقاف المحاكاة")
            
            # إشارة إيقاف المحاكاة
            self.simulation_stopped.emit()
            
            self.logger.info("Simulation stopped")
    
    def simulation_step(self):
        """خطوة واحدة من المحاكاة"""
        if not self.env or not self.controller:
            return
        
        try:
            # الحصول على الحالة الحالية
            state = self.env.get_state()
            
            # اختيار إجراء
            training_mode = self.training_action.isChecked()
            action, decision_info = self.controller.choose_action(state, training=training_mode)
            
            # تنفيذ الإجراء
            next_state, reward, done, info = self.env.step(action)
            
            # تسجيل الحركة للتحقق
            if state['step'] % 20 == 0:
                 self.logger.info(f"Step {state['step']}: Action={action} at {state['position']} -> {info.get('reason', '')}")
            
            # تحديث Q-Learning في وضع التدريب
            if training_mode:
                self.controller.update(state, action, reward, next_state, done)
            
            # تحديث واجهة المستخدم
            self.map_view.update_display()
            self.control_panel.update_metrics(state, action, reward, decision_info)
            self.control_panel.update_displays()
            
            # التحقق من انتهاء الحلقة
            if done:
                self.handle_episode_end(info)
        
        except Exception as e:
            self.logger.error(f"Simulation step error: {e}")
            self.stop_simulation()
    
    def handle_episode_end(self, info: dict):
        """التعامل مع انتهاء الحلقة"""
        success = info.get('success', False)
        reason = info.get('reason', 'غير معروف')
        
        message = f"انتهت الجولة: {reason}"
        if success:
            message = f"✅ تم اكتمال المهمة بنجاح! {reason}"
        else:
            message = f"❌ فشلت المهمة: {reason}"
        
        self.status_bar.showMessage(message)
        self.control_panel.show_episode_result(success, reason)
        
        # إعادة تعيين البيئة للحلقة التالية
        if self.is_simulation_running:
            self.env.reset()
    
    def reset_environment(self):
        """إعادة تعيين البيئة بالكامل مع بناء مدينة جديدة"""
        if not self.env or not self.controller:
            if not self.initialize_simulation():
                return
                
        if self.is_simulation_running:
            self.stop_simulation()
            
        # إنشاء بيئة جديدة تماماً لتطبيق تغييرات تقسيم المدينة
        self.env = CityEnvironment()
        self.env.reset()
        self.controller.reset_statistics()
        
        # إبلاغ المكونات بالبيئة الجديدة
        self.map_view.set_environment(self.env)
        # استرجاع الحالة الابتدائية للتحديث
        initial_state = self.env.get_state()
        self.control_panel.update_metrics(initial_state, "RESET", 0, {"reason": "City Regeneration"})
        self.update_displays()
        
        self.logger.info("Environment reset and city regenerated")
        self.statusBar().showMessage("تمت إعادة تعيين البيئة وبناء خريطة جديدة")
    
    def change_simulation_speed(self, speed: float):
        """تغيير سرعة المحاكاة"""
        if self.is_simulation_running:
            self.simulation_timer.setInterval(int(1000 / speed))
    
    def toggle_training_mode(self, enabled: bool):
        """تبديل وضع التدريب"""
        mode = "تدريبي" if enabled else "استعراضي"
        self.status_bar.showMessage(f"تم تغيير الوضع إلى: {mode}")
        self.control_panel.set_training_mode(enabled)
    
    def load_model(self):
        """تحميل نموذج"""
        if self.controller:
            success = self.controller.load_models()
            if success:
                QMessageBox.information(self, "نجاح", "تم تحميل النموذج بنجاح!")
                self.status_bar.showMessage("تم تحميل النموذج")
            else:
                QMessageBox.warning(self, "تحذير", "لم يتم العثور على نموذج محفوظ!")
    
    def save_model(self):
        """حفظ النموذج"""
        if self.controller:
            self.controller.save_models()
            QMessageBox.information(self, "نجاح", "تم حفظ النموذج بنجاح!")
            self.status_bar.showMessage("تم حفظ النموذج")
    
    def on_drone_clicked(self, position):
        """التعامل مع النقر على الطائرة"""
        if self.env:
            drone_info = self.env.get_drone_info()
            self.control_panel.show_drone_details(drone_info)
    
    def show_about(self):
        """عرض معلومات حول التطبيق"""
        about_text = """
        <div dir='rtl'>
        <h2>🚁 نظام توصيل الطائرات المسيرة الطبي ذاتي القيادة</h2>
        <p><b>الإصدار:</b> 1.0</p>
        <p><b>المعمارية:</b> ذكاء اصطناعي هجين (عصبي-رمزي)</p>
        
        <h3>المميزات:</h3>
        <ul>
        <li>🧠 استخدام Q-Learning لتحسين كفاءة المسارات</li>
        <li>⚖️ محرك منطقي لضمان قواعد الأمان والقيود</li>
        <li>🌍 بيئة مدينة ثلاثية الأبعاد واقعية</li>
        <li>🛡️ ملاحة ذاتية حرجة لسلامة الطيران</li>
        <li>📊 مراقبة الأداء والنتائج في الوقت الفعلي</li>
        </ul>
        
        <h3>المكونات:</h3>
        <ul>
        <li><b>الطبقة العصبية:</b> تتعلم المسارات المثلى عبر الخبرة</li>
        <li><b>الطبقة الرمزية:</b> تفرض قواعد وقيود الأمان بدقة</li>
        <li><b>المتحكم الهجين:</b> يجمع بين كفاءة التعلم ودقة المنطق</li>
        </ul>
        
        <p><i>تم تطوير هذا النظام لمحاكاة توصيل الإمدادات الطبية في المناطق الحضرية.</i></p>
        </div>
        """
        
        QMessageBox.about(self, "حول التطبيق", about_text)
    
    def load_settings(self):
        """تحميل الإعدادات"""
        # يمكن إضافة تحميل الإعدادات من ملف هنا
        pass
    
    def save_settings(self):
        """حفظ الإعدادات"""
        # يمكن إضافة حفظ الإعدادات هنا
        pass
    
    def set_manual_target(self, position):
        """تعيين هدف يدوي من خلال النقر على الخريطة"""
        if self.env:
            # الحفاظ على الارتفاع الحالي أو استخدام ارتفاع آمن
            current_z = self.env.drone.position[2]
            safe_z = self.env.obstacles.get_min_safe_altitude(*position)
            z = max(current_z, safe_z)
            
            self.env.target_position = (*position, z)
            self.logger.info(f"Target manually set to: {self.env.target_position}")
            
            # تحديث الواجهة فوراً
            self.map_view.update_display()
            self.control_panel.update_metrics(
                self.env.get_state(), 
                "MANUAL_TARGET", 
                0, 
                {"reason": "User manual override"}
            )

    def closeEvent(self, event):
        """التعامل مع إغلاق النافذة"""
        if self.is_simulation_running:
            self.stop_simulation()
        
        self.save_settings()
        event.accept()


def main():
    """دالة رئيسية لتشغيل التطبيق"""
    app = QApplication(sys.argv)
    
    # إعداد التطبيق
    app.setApplicationName("Drone Delivery System")
    app.setApplicationVersion("1.0")
    
    # إنشاء النافذة الرئيسية
    window = MainWindow()
    window.show()
    
    # تشغيل التطبيق
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()