"""
Logging system for the Autonomous Drone Delivery System
Handles event logging, metrics tracking, and debugging
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any
import json

from .config import LOG_FILE_PATH, LOG_LEVEL, LOGS_DIR


class DroneLogger:
    """
    مسجل الأحداث للنظام
    يسجل جميع الأحداث المهمة والقرارات والمقاييس
    """
    
    def __init__(self, name: str = "DroneDelivery"):
        """تهيئة المسجل"""
        self.name = name
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # إنشاء ملف log خاص بهذه الجلسة
        self.log_file = os.path.join(LOGS_DIR, f"session_{self.session_id}.log")
        
        # إعداد Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Decision log (for GUI display)
        self.decision_log: List[Dict[str, Any]] = []
        self.max_decision_log_size = 100
        
        self.logger.info(f"Logger initialized - Session ID: {self.session_id}")
    
    def log_mission_start(self, mission_id: int, start_pos: tuple, end_pos: tuple):
        """تسجيل بداية مهمة"""
        msg = f"Mission #{mission_id} started: {start_pos} → {end_pos}"
        self.logger.info(msg)
        self._add_to_decision_log("🎯", "Mission Started", msg)
    
    def log_mission_complete(self, mission_id: int, success: bool, stats: Dict):
        """تسجيل انتهاء مهمة"""
        status = "SUCCESS" if success else "FAILED"
        msg = f"Mission #{mission_id} {status} - Time: {stats.get('time', 0):.1f}s, Battery: {stats.get('battery', 0):.1f}%"
        
        if success:
            self.logger.info(msg)
            self._add_to_decision_log("✅", "Mission Complete", msg)
        else:
            self.logger.warning(msg)
            self._add_to_decision_log("❌", "Mission Failed", msg)
    
    def log_ai_decision(self, neural_action: str, logic_override: bool, final_action: str, reason: str = ""):
        """تسجيل قرار الذكاء الاصطناعي"""
        if logic_override:
            msg = f"Logic Override: {neural_action} → {final_action} ({reason})"
            self.logger.warning(msg)
            self._add_to_decision_log("⚠️", "Logic Override", msg)
        else:
            msg = f"Action: {final_action}"
            self.logger.debug(msg)
            self._add_to_decision_log("🧠", "AI Decision", msg)
    
    def log_safety_violation(self, violation_type: str, details: str):
        """تسجيل انتهاك قواعد السلامة"""
        msg = f"SAFETY VIOLATION: {violation_type} - {details}"
        self.logger.error(msg)
        self._add_to_decision_log("🚫", "Safety Violation", msg)
    
    def log_battery_warning(self, battery_level: float, action: str):
        """تسجيل تحذير البطارية"""
        msg = f"Battery Warning: {battery_level:.1f}% - Action: {action}"
        self.logger.warning(msg)
        self._add_to_decision_log("🔋", "Battery Warning", msg)
    
    def log_weather_event(self, weather: str, impact: str):
        """تسجيل حدث طقس"""
        msg = f"Weather: {weather} - Impact: {impact}"
        self.logger.info(msg)
        self._add_to_decision_log("💨", "Weather Event", msg)
    
    def log_collision(self, obstacle_type: str, position: tuple):
        """تسجيل تصادم"""
        msg = f"COLLISION with {obstacle_type} at {position}"
        self.logger.error(msg)
        self._add_to_decision_log("💥", "Collision", msg)
    
    def log_reroute(self, reason: str, old_path_length: int, new_path_length: int):
        """تسجيل إعادة توجيه المسار"""
        msg = f"Rerouting: {reason} - Path length: {old_path_length} → {new_path_length}"
        self.logger.info(msg)
        self._add_to_decision_log("🔄", "Rerouting", msg)
    
    def log_training_episode(self, episode: int, stats: Dict):
        """تسجيل نتائج حلقة تدريب"""
        msg = (f"Episode {episode}: "
               f"Success={stats.get('success', False)}, "
               f"Reward={stats.get('total_reward', 0):.1f}, "
               f"Steps={stats.get('steps', 0)}, "
               f"Epsilon={stats.get('epsilon', 0):.3f}")
        self.logger.info(msg)
    
    def log_training_milestone(self, episode: int, success_rate: float, avg_reward: float):
        """تسجيل إنجاز في التدريب"""
        msg = f"Training Milestone - Episode {episode}: Success Rate={success_rate:.1%}, Avg Reward={avg_reward:.1f}"
        self.logger.info(msg)
        self._add_to_decision_log("📊", "Training Milestone", msg)
    
    def _add_to_decision_log(self, icon: str, category: str, message: str):
        """إضافة قرار إلى سجل القرارات (للعرض في الواجهة)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            'timestamp': timestamp,
            'icon': icon,
            'category': category,
            'message': message
        }
        
        self.decision_log.append(entry)
        
        # الحفاظ على حجم السجل
        if len(self.decision_log) > self.max_decision_log_size:
            self.decision_log.pop(0)
    
    def get_recent_decisions(self, count: int = 10) -> List[Dict]:
        """الحصول على آخر N قرار"""
        return self.decision_log[-count:]
    
    def clear_decision_log(self):
        """مسح سجل القرارات"""
        self.decision_log.clear()
    
    def save_session_summary(self, summary: Dict):
        """حفظ ملخص الجلسة"""
        summary_file = os.path.join(LOGS_DIR, f"summary_{self.session_id}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Session summary saved to {summary_file}")
    
    def debug(self, message: str):
        """رسالة debug"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """رسالة info"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """رسالة warning"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """رسالة error"""
        self.logger.error(message)


# Global logger instance
_global_logger = None

def get_logger() -> DroneLogger:
    """الحصول على المسجل العام"""
    global _global_logger
    if _global_logger is None:
        _global_logger = DroneLogger()
    return _global_logger
