"""
Control Panel for Drone Delivery System
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QGroupBox,
    QSlider, QSpinBox, QCheckBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

from ..utils.logger import get_logger


class ControlPanel(QWidget):
    """
    لوحة التحكم الرئيسية
    
    تحتوي على:
    - أزرار التحكم في المحاكاة
    - عرض المقاييس والإحصائيات
    - سجل القرارات
    - معلومات الطائرة
    """
    
    # إشارات مخصصة
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    speed_changed = pyqtSignal(float)
    
    def __init__(self):
        """تهيئة لوحة التحكم"""
        super().__init__()
        
        self.logger = get_logger()
        self.controller = None
        
        # إحصائيات
        self.episode_count = 0
        self.total_reward = 0
        self.success_count = 0
        
        # إعداد واجهة المستخدم
        self.setup_ui()
        
        # مؤقت التحديث
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(100)  # تحديث كل 100ms
        
        self.logger.info("Control panel initialized")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # إنشاء التبويبات
        self.tabs = QTabWidget()
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        layout.addWidget(self.tabs)
        
        # تبويب التحكم
        self.create_control_tab()
        
        # تبويب المقاييس
        self.create_metrics_tab()
        
        # تبويب القرارات
        self.create_decisions_tab()
        
        # تبويب الإحصائيات
        self.create_statistics_tab()
        
        # تطبيق الستايل
        self.apply_style()
    
    def create_control_tab(self):
        """إنشاء تبويب التحكم"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # مجموعة أزرار المحاكاة
        sim_group = QGroupBox("التحكم في المحاكاة")
        sim_layout = QVBoxLayout(sim_group)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ بدء")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setToolTip("بدء المحاكاة أو استئنافها")
        self.start_btn.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ إيقاف")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setToolTip("إيقاف المحاكاة مؤقتاً")
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        button_layout.addWidget(self.stop_btn)
        
        self.reset_btn = QPushButton("🔄 إعادة")
        self.reset_btn.setToolTip("إعادة تعيين البيئة والبدء من جديد")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        button_layout.addWidget(self.reset_btn)
        
        sim_layout.addLayout(button_layout)
        
        # سرعة المحاكاة
        speed_layout = QHBoxLayout()
        speed_label_obj = QLabel("السرعة:")
        speed_label_obj.setToolTip("تغيير سرعة المحاكاة")
        speed_layout.addWidget(speed_label_obj)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.setToolTip("اسحب لتغيير السرعة (1x - 10x)")
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("5x")
        speed_layout.addWidget(self.speed_label)
        
        sim_layout.addLayout(speed_layout)
        
        layout.addWidget(sim_group)
        
        # مجموعة معلومات الطائرة
        drone_group = QGroupBox("حالة الطائرة المسيرة")
        drone_layout = QGridLayout(drone_group)
        
        # البطارية
        battery_label_obj = QLabel("البطارية:")
        battery_label_obj.setToolTip("مستوى شحن بطارية الطائرة")
        drone_layout.addWidget(battery_label_obj, 0, 0)
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(100)
        drone_layout.addWidget(self.battery_bar, 0, 1)
        self.battery_label = QLabel("100%")
        drone_layout.addWidget(self.battery_label, 0, 2)
        
        # الموقع
        pos_label_obj = QLabel("الموقع:")
        pos_label_obj.setToolTip("إحداثيات الطائرة الحالية (X, Y, Altitude)")
        drone_layout.addWidget(pos_label_obj, 1, 0)
        self.position_label = QLabel("(0, 0, 0)")
        drone_layout.addWidget(self.position_label, 1, 1, 1, 2)
        
        # الشحنة
        cargo_label_obj = QLabel("الشحنة:")
        cargo_label_obj.setToolTip("هل تحمل الطائرة شحنة حالياً؟")
        drone_layout.addWidget(cargo_label_obj, 2, 0)
        self.cargo_label = QLabel("لا يوجد")
        drone_layout.addWidget(self.cargo_label, 2, 1, 1, 2)
        
        # حالة الطيران
        flight_status_label_obj = QLabel("حالة الطيران:")
        flight_status_label_obj.setToolTip("مدى أمان الطيران في الظروف الحالية")
        drone_layout.addWidget(flight_status_label_obj, 3, 0)
        self.flight_status_label = QLabel("آمن")
        drone_layout.addWidget(self.flight_status_label, 3, 1, 1, 2)
        
        layout.addWidget(drone_group)
        
        # مجموعة حالة الطقس والبيئة
        weather_group = QGroupBox("🌤️ حالة الطقس والبيئة")
        weather_layout = QGridLayout(weather_group)
        
        # حالة الطقس
        weather_layout.addWidget(QLabel("الطقس:"), 0, 0)
        self.weather_condition_label = QLabel("صافٍ ☀️")
        weather_layout.addWidget(self.weather_condition_label, 0, 1)
        
        # سرعة الرياح
        weather_layout.addWidget(QLabel("الرياح:"), 1, 0)
        self.wind_speed_label = QLabel("0 كم/س")
        weather_layout.addWidget(self.wind_speed_label, 1, 1)
        
        # الرؤية
        weather_layout.addWidget(QLabel("الرؤية:"), 2, 0)
        self.visibility_bar = QProgressBar()
        self.visibility_bar.setRange(0, 100)
        self.visibility_bar.setValue(100)
        self.visibility_bar.setTextVisible(True)
        weather_layout.addWidget(self.visibility_bar, 2, 1)
        
        layout.addWidget(weather_group)
        
        # مجموعة المهمة
        mission_group = QGroupBox("حالة المهمة")
        mission_layout = QGridLayout(mission_group)
        
        # تقدم المهمة
        progress_label_obj = QLabel("التقدم:")
        progress_label_obj.setToolTip("مدى اكتمال المهمة الحالية")
        mission_layout.addWidget(progress_label_obj, 0, 0)
        self.mission_bar = QProgressBar()
        self.mission_bar.setRange(0, 100)
        mission_layout.addWidget(self.mission_bar, 0, 1)
        
        # الهدف الحالي
        target_label_obj = QLabel("الهدف الحالي:")
        target_label_obj.setToolTip("موقع الاستلام أو التسليم المستهدف")
        mission_layout.addWidget(target_label_obj, 1, 0)
        self.target_label = QLabel("موقع الاستلام")
        mission_layout.addWidget(self.target_label, 1, 1)
        
        # المسافة للهدف
        distance_label_obj = QLabel("المسافة:")
        distance_label_obj.setToolTip("المسافة المتبقية للوصول للهدف")
        mission_layout.addWidget(distance_label_obj, 2, 0)
        self.distance_label = QLabel("0 م")
        mission_layout.addWidget(self.distance_label, 2, 1)
        
        layout.addWidget(mission_group)
        
        # إضافة مساحة فارغة
        layout.addStretch()
        
        # تعليمات سريعة للمستخدم
        help_group = QGroupBox("💡 تعليمات سريعة")
        help_layout = QVBoxLayout(help_group)
        help_text = QLabel(
            "1. استخدم زر 'بدء' لتشغيل المحاكاة.\n"
            "2. انقر في أي مكان على الخريطة لتغيير الهدف يدوياً.\n"
            "3. الخط المنقط الأزرق يوضح المسار المخطط للهدف.\n"
            "4. الدرون ستتعلم تدريجياً كيف تتفادى العوائق."
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #2980b9; font-weight: bold;")
        help_layout.addWidget(help_text)
        layout.addWidget(help_group)
        
        self.tabs.addTab(control_widget, "🎮 التحكم")
    
    def create_metrics_tab(self):
        """إنشاء تبويب المقاييس"""
        metrics_widget = QWidget()
        layout = QVBoxLayout(metrics_widget)
        
        # مجموعة الأداء
        performance_group = QGroupBox("مقاييس الأداء")
        perf_layout = QGridLayout(performance_group)
        
        # المكافأة الحالية
        perf_layout.addWidget(QLabel("المكافأة الحالية:"), 0, 0)
        self.reward_label = QLabel("0")
        perf_layout.addWidget(self.reward_label, 0, 1)
        
        # إجمالي المكافآت
        perf_layout.addWidget(QLabel("إجمالي المكافآت:"), 1, 0)
        self.total_reward_label = QLabel("0")
        perf_layout.addWidget(self.total_reward_label, 1, 1)
        
        # عدد الخطوات
        perf_layout.addWidget(QLabel("الخطوات:"), 2, 0)
        self.steps_label = QLabel("0")
        perf_layout.addWidget(self.steps_label, 2, 1)
        
        # معدل النجاح
        perf_layout.addWidget(QLabel("معدل النجاح:"), 3, 0)
        self.success_rate_label = QLabel("0%")
        perf_layout.addWidget(self.success_rate_label, 3, 1)
        
        layout.addWidget(performance_group)
        
        # مجموعة Q-Learning
        q_group = QGroupBox("إحصائيات التعلم (Q-Learning)")
        q_layout = QGridLayout(q_group)
        
        # Epsilon
        q_layout.addWidget(QLabel("معامل الاستكشاف (ε):"), 0, 0)
        self.epsilon_label = QLabel("0.1")
        q_layout.addWidget(self.epsilon_label, 0, 1)
        
        # حجم Q-table
        q_layout.addWidget(QLabel("حجم جدول Q:"), 1, 0)
        self.qtable_size_label = QLabel("0")
        q_layout.addWidget(self.qtable_size_label, 1, 1)
        
        # عدد التحديثات
        q_layout.addWidget(QLabel("التحديثات:"), 2, 0)
        self.updates_label = QLabel("0")
        q_layout.addWidget(self.updates_label, 2, 1)
        
        layout.addWidget(q_group)
        
        # مجموعة الأمان
        safety_group = QGroupBox("إحصائيات الأمان")
        safety_layout = QGridLayout(safety_group)
        
        # تدخلات الأمان
        safety_layout.addWidget(QLabel("تدخلات الأمان:"), 0, 0)
        self.safety_overrides_label = QLabel("0")
        safety_layout.addWidget(self.safety_overrides_label, 0, 1)
        
        # معدل تدخل الأمان
        safety_layout.addWidget(QLabel("معدل التدخل:"), 1, 0)
        self.override_rate_label = QLabel("0%")
        safety_layout.addWidget(self.override_rate_label, 1, 1)
        
        # القواعد النشطة
        safety_layout.addWidget(QLabel("القواعد المنفذة:"), 2, 0)
        self.active_rules_label = QLabel("0")
        safety_layout.addWidget(self.active_rules_label, 2, 1)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        
        self.tabs.addTab(metrics_widget, "📊 المقاييس")
    
    def create_decisions_tab(self):
        """إنشاء تبويب القرارات"""
        decisions_widget = QWidget()
        layout = QVBoxLayout(decisions_widget)
        
        # معلومات القرار الحالي
        current_group = QGroupBox("القرار الحالي")
        current_layout = QGridLayout(current_group)
        
        # الإجراء المختار
        current_layout.addWidget(QLabel("الإجراء:"), 0, 0)
        self.current_action_label = QLabel("لا يوجد")
        current_layout.addWidget(self.current_action_label, 0, 1)
        
        # نوع القرار
        current_layout.addWidget(QLabel("نوع القرار:"), 1, 0)
        self.decision_type_label = QLabel("لا يوجد")
        current_layout.addWidget(self.decision_type_label, 1, 1)
        
        # القاعدة المطبقة
        current_layout.addWidget(QLabel("القاعدة المطبقة:"), 2, 0)
        self.applied_rule_label = QLabel("لا يوجد")
        current_layout.addWidget(self.applied_rule_label, 2, 1)
        
        layout.addWidget(current_group)
        
        # سجل القرارات
        log_group = QGroupBox("سجل القرارات")
        log_layout = QVBoxLayout(log_group)
        
        self.decision_log = QTextEdit()
        self.decision_log.setMaximumHeight(200)
        self.decision_log.setReadOnly(True)
        self.decision_log.setToolTip("سجل الإجراءات والقرارات المتخذة")
        log_layout.addWidget(self.decision_log)
        
        # أزرار التحكم في السجل
        log_buttons = QHBoxLayout()
        
        clear_log_btn = QPushButton("مسح السجل")
        clear_log_btn.clicked.connect(self.clear_decision_log)
        log_buttons.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("حفظ السجل")
        save_log_btn.clicked.connect(self.save_decision_log)
        log_buttons.addWidget(save_log_btn)
        
        log_layout.addLayout(log_buttons)
        
        layout.addWidget(log_group)
        
        # Q-Values للإجراءات
        qvalues_group = QGroupBox("قيم الجودة (Q-Values)")
        qvalues_layout = QVBoxLayout(qvalues_group)
        
        self.qvalues_table = QTableWidget()
        self.qvalues_table.setColumnCount(2)
        self.qvalues_table.setHorizontalHeaderLabels(["الإجراء", "القيمة"])
        self.qvalues_table.setToolTip("المكافأة المتوقعة لكل إجراء")
        qvalues_layout.addWidget(self.qvalues_table)
        
        layout.addWidget(qvalues_group)
        
        self.tabs.addTab(decisions_widget, "🧠 القرارات")
    
    def create_statistics_tab(self):
        """إنشاء تبويب الإحصائيات"""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        # إحصائيات الحلقات
        episodes_group = QGroupBox("إحصائيات الجولات")
        episodes_layout = QGridLayout(episodes_group)
        
        # عدد الحلقات
        episodes_layout.addWidget(QLabel("عدد الجولات:"), 0, 0)
        self.episodes_label = QLabel("0")
        episodes_layout.addWidget(self.episodes_label, 0, 1)
        
        # الحلقات الناجحة
        episodes_layout.addWidget(QLabel("الجولات الناجحة:"), 1, 0)
        self.successful_episodes_label = QLabel("0")
        episodes_layout.addWidget(self.successful_episodes_label, 1, 1)
        
        # متوسط المكافأة
        episodes_layout.addWidget(QLabel("متوسط المكافأة:"), 2, 0)
        self.avg_reward_label = QLabel("0")
        episodes_layout.addWidget(self.avg_reward_label, 2, 1)
        
        # متوسط الخطوات
        episodes_layout.addWidget(QLabel("متوسط الخطوات:"), 3, 0)
        self.avg_steps_label = QLabel("0")
        episodes_layout.addWidget(self.avg_steps_label, 3, 1)
        
        # نسبة النجاح (مرئية)
        episodes_layout.addWidget(QLabel("معدل النجاح الإجمالي:"), 4, 0)
        self.success_rate_bar = QProgressBar()
        self.success_rate_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        self.success_rate_bar.setValue(0)
        episodes_layout.addWidget(self.success_rate_bar, 4, 1)
        
        layout.addWidget(episodes_group)
        
        # إحصائيات الأداء
        performance_group = QGroupBox("سجل الأداء")
        performance_layout = QVBoxLayout(performance_group)
        
        # جدول الأداء
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(4)
        self.performance_table.setHorizontalHeaderLabels(["الجولة", "المكافأة", "الخطوات", "النتيجة"])
        performance_layout.addWidget(self.performance_table)
        
        layout.addWidget(performance_group)
        
        # أزرار الإحصائيات
        stats_buttons = QHBoxLayout()
        
        reset_stats_btn = QPushButton("إعادة تعيين الإحصائيات")
        reset_stats_btn.clicked.connect(self.reset_statistics)
        stats_buttons.addWidget(reset_stats_btn)
        
        export_stats_btn = QPushButton("تصدير الإحصائيات")
        export_stats_btn.clicked.connect(self.export_statistics)
        stats_buttons.addWidget(export_stats_btn)
        
        layout.addLayout(stats_buttons)
        
        self.tabs.addTab(stats_widget, "📈 الإحصائيات")
    
    def apply_style(self):
        """تطبيق الستايل العصري (Glass Aesthetics)"""
        style = """
            QTabWidget::pane {
                border: 1px solid rgba(0, 0, 0, 30);
                background: rgba(245, 245, 250, 240);
                border-radius: 12px;
            }
            QTabBar::tab {
                background: rgba(220, 220, 230, 200);
                border: 1px solid rgba(0, 0, 0, 20);
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                color: #555;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: #0078d7;
                color: white;
            }
            QPushButton#start_btn {
                background: #28a745;
                font-weight: bold;
            }
            QPushButton#stop_btn {
                background: #dc3545;
                font-weight: bold;
            }
            QGroupBox {
                background: rgba(255, 255, 255, 200);
                border: 1px solid rgba(0, 0, 0, 40);
                border-radius: 10px;
                margin-top: 15px;
                font-weight: bold;
                padding-top: 10px;
            }
        """
        self.setStyleSheet(style)

    def _on_start_clicked(self):
        """عند الضغط على بدء"""
        self.logger.info("GUI: Start button clicked")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.start_requested.emit()

    def _on_stop_clicked(self):
        """عند الضغط على إيقاف"""
        self.logger.info("GUI: Stop button clicked")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stop_requested.emit()

    def _on_reset_clicked(self):
        """عند الضغط على إعادة تعيين"""
        self.logger.info("GUI: Reset button clicked")
        self.reset_requested.emit()
    
    def set_controller(self, controller):
        """تعيين المتحكم"""
        self.controller = controller
    
    def set_training_mode(self, enabled: bool):
        """تعيين وضع التدريب"""
        mode_text = "Training Mode" if enabled else "Demo Mode"
        # يمكن إضافة مؤشر بصري هنا
    
    def get_simulation_speed(self) -> float:
        """الحصول على سرعة المحاكاة"""
        return self.speed_slider.value()
    
    def on_speed_changed(self, value):
        """تغيير سرعة المحاكاة"""
        self.speed_label.setText(f"{value}x")
        self.speed_changed.emit(float(value))
    
    def update_metrics(self, state: dict, action: str, reward: float, decision_info: dict):
        """تحديث المقاييس"""
        
        # تحديث معلومات الطائرة
        self.battery_bar.setValue(int(state.get('battery', 0)))
        self.battery_label.setText(f"{state.get('battery', 0):.1f}%")
        
        pos = state.get('position', [0, 0, 0])
        self.position_label.setText(f"({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
        
        has_cargo = state.get('has_cargo', False)
        self.cargo_label.setText("نعم 📦" if has_cargo else "لا")
        self.flight_status_label.setText("آمن ✅" if state.get('safe_to_fly', True) else "غير آمن ⚠️")
        
        # تحديث حالة المهمة
        target = state.get('target', None)
        start = state.get('start', None)
        
        if target and len(target) >= 2:
            # حساب المسافة للهدف
            import numpy as np
            distance = np.linalg.norm(np.array(pos[:2]) - np.array(target[:2]))
            self.distance_label.setText(f"{distance:.1f} م")
            
            # تحديد الهدف الحالي
            if has_cargo:
                self.target_label.setText("🚁 التوجه لنقطة التسليم")
            else:
                self.target_label.setText("📍 التوجه لنقطة الاستلام")
            
            # حساب نسبة التقدم
            if start and len(start) >= 2:
                total_distance = np.linalg.norm(np.array(start[:2]) - np.array(target[:2]))
                if total_distance > 0:
                    progress = max(0, min(100, (1 - distance / total_distance) * 100))
                    self.mission_bar.setValue(int(progress))
                else:
                    self.mission_bar.setValue(100)
            else:
                # استخدام المسافة فقط كمؤشر
                # كلما اقتربنا، زاد التقدم (نفترض مسافة قصوى 70 وحدة)
                max_dist = 70.0
                progress = max(0, min(100, (1 - distance / max_dist) * 100))
                self.mission_bar.setValue(int(progress))
        else:
            self.distance_label.setText("--")
            self.target_label.setText("لا يوجد هدف")
            self.mission_bar.setValue(0)
        
        # تحديث معلومات القرار
        self.current_action_label.setText(action)
        self.decision_type_label.setText(decision_info.get('decision_type', 'غير معروف'))
        self.applied_rule_label.setText(decision_info.get('top_rule', 'لا يوجد'))
        
        # 🛡️ تحديث إحصائيات الأمان (القواعد المنفذة والتدخلات)
        triggered_count = decision_info.get('triggered_rules', 0)
        self.active_rules_label.setText(str(triggered_count))
        
        # إذا كان هناك تدخل أمان، نقوم بتحديث العداد فوراً
        if decision_info.get('safety_override', False):
            # العداد الإجمالي سيتم تحديثه في update_displays من قبل المتحكم
            pass
        
        # تحديث المكافأة
        self.reward_label.setText(f"{reward:.2f}")
        self.total_reward += reward
        self.total_reward_label.setText(f"{self.total_reward:.2f}")
        
        # تحديث عدد الخطوات
        step_count = state.get('step', 0)
        self.steps_label.setText(str(step_count))
        
        # إضافة إلى سجل القرارات (فقط كل 5 خطوات لتجنب الازدحام)
        if step_count % 5 == 0:
            log_entry = f"[{step_count}] {action} | R: {reward:.1f} | {decision_info.get('decision_type', '?')}"
            self.decision_log.append(log_entry)
        
        # تحديث Q-Values
        self.update_qvalues_table(decision_info.get('q_values', {}))
    
    def update_qvalues_table(self, q_values: dict):
        """تحديث جدول Q-Values"""
        self.qvalues_table.setRowCount(len(q_values))
        
        for i, (action, value) in enumerate(q_values.items()):
            self.qvalues_table.setItem(i, 0, QTableWidgetItem(action))
            self.qvalues_table.setItem(i, 1, QTableWidgetItem(f"{value:.3f}"))
    
    def update_displays(self):
        """تحديث العروض الدورية"""
        if self.controller:
            stats = self.controller.get_statistics()
            
            # تحديث إحصائيات Q-Learning
            q_stats = stats.get('q_learning', {})
            self.epsilon_label.setText(f"{q_stats.get('epsilon', 0):.3f}")
            self.qtable_size_label.setText(str(q_stats.get('q_table_size', 0)))
            self.updates_label.setText(str(q_stats.get('total_updates', 0)))
            
            # تحديث إحصائيات الأمان
            hybrid_stats = stats.get('hybrid_controller', {})
            self.safety_overrides_label.setText(str(hybrid_stats.get('safety_overrides', 0)))
            
            override_rate = hybrid_stats.get('safety_override_rate', 0) * 100
            self.override_rate_label.setText(f"{override_rate:.1f}%")
            
            # تحديث معلومات الطقس (إذا كانت متوفرة في الحالة)
            if hasattr(self.controller, 'env') and self.controller.env:
                weather_info = self.controller.env.weather.get_weather_info()
                icon = self.controller.env.weather.get_weather_icon()
                self.weather_condition_label.setText(f"{weather_info['condition']} {icon}")
                self.wind_speed_label.setText(f"{weather_info['wind_speed']:.1f} كم/س")
                self.visibility_bar.setValue(int(weather_info['visibility']))
            
            # تحديث نسبة النجاح العامة
            if self.episode_count > 0:
                success_rate = (self.success_count / self.episode_count) * 100
                self.success_rate_bar.setValue(int(success_rate))
                self.success_rate_bar.setFormat(f"{success_rate:.1f}%")
                
                # تغيير لون الشريط بناءً على النسبة
                if success_rate < 30:
                    color = "#F44336" # Red
                elif success_rate < 70:
                    color = "#FF9800" # Orange
                else:
                    color = "#4CAF50" # Green
                
                self.success_rate_bar.setStyleSheet(f"""
                    QProgressBar::chunk {{ background-color: {color}; }}
                    QProgressBar {{ text-align: center; border-radius: 5px; border: 1px solid rgba(0,0,0,0.1); }}
                """)
    
    def show_episode_result(self, success: bool, reason: str):
        """عرض نتيجة الحلقة"""
        self.episode_count += 1
        if success:
            self.success_count += 1
        
        # تحديث الإحصائيات
        self.episodes_label.setText(str(self.episode_count))
        self.successful_episodes_label.setText(str(self.success_count))
        
        success_rate = (self.success_count / self.episode_count) * 100 if self.episode_count > 0 else 0
        self.success_rate_label.setText(f"{success_rate:.1f}%")
        
        # إضافة إلى جدول الأداء
        row = self.performance_table.rowCount()
        self.performance_table.insertRow(row)
        
        self.performance_table.setItem(row, 0, QTableWidgetItem(str(self.episode_count)))
        self.performance_table.setItem(row, 1, QTableWidgetItem(f"{self.total_reward:.2f}"))
        self.performance_table.setItem(row, 2, QTableWidgetItem("N/A"))  # سيتم تحديثه لاحقاً
        self.performance_table.setItem(row, 3, QTableWidgetItem("✅" if success else "❌"))
    
    def show_drone_details(self, drone_info: dict):
        """عرض تفاصيل الطائرة"""
        # يمكن إضافة نافذة منبثقة أو تبويب إضافي
        pass
    
    def reset_metrics(self):
        """إعادة تعيين المقاييس"""
        self.total_reward = 0
        self.total_reward_label.setText("0")
        self.reward_label.setText("0")
        self.steps_label.setText("0")
        self.decision_log.clear()
    
    def reset_statistics(self):
        """إعادة تعيين الإحصائيات"""
        self.episode_count = 0
        self.success_count = 0
        self.total_reward = 0
        
        self.episodes_label.setText("0")
        self.successful_episodes_label.setText("0")
        self.success_rate_label.setText("0%")
        self.avg_reward_label.setText("0")
        self.avg_steps_label.setText("0")
        
        self.performance_table.setRowCount(0)
    
    def clear_decision_log(self):
        """مسح سجل القرارات"""
        self.decision_log.clear()
    
    def save_decision_log(self):
        """حفظ سجل القرارات"""
        # يمكن إضافة حفظ إلى ملف
        pass
    
    def export_statistics(self):
        """تصدير الإحصائيات"""
        # يمكن إضافة تصدير إلى CSV أو JSON
        pass