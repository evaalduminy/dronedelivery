"""
Weather system for the drone delivery environment
"""

import numpy as np
from typing import Tuple
from enum import Enum

from ..utils.config import MAX_WIND_SPEED, FORBIDDEN_WEATHER


class WeatherCondition(Enum):
    """حالات الطقس"""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    WINDY = "windy"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    THUNDERSTORM = "thunderstorm"


class WeatherSystem:
    """
    نظام الطقس الديناميكي
    يؤثر على حركة الطائرة واستهلاك الطاقة
    """
    
    def __init__(self, initial_condition: str = "clear"):
        """
        تهيئة نظام الطقس
        
        Args:
            initial_condition: حالة الطقس الابتدائية
        """
        self.condition = WeatherCondition(initial_condition)
        self.wind_speed = 0.0  # km/h
        self.wind_direction = 0.0  # degrees
        self.visibility = 100.0  # percentage
        self.temperature = 25.0  # celsius
        
        self._update_weather_effects()
    
    def _update_weather_effects(self):
        """تحديث تأثيرات الطقس بناءً على الحالة"""
        if self.condition == WeatherCondition.CLEAR:
            self.wind_speed = np.random.uniform(5, 15)
            self.visibility = 100.0
        
        elif self.condition == WeatherCondition.CLOUDY:
            self.wind_speed = np.random.uniform(10, 20)
            self.visibility = 80.0
        
        elif self.condition == WeatherCondition.WINDY:
            self.wind_speed = np.random.uniform(25, 40)
            self.visibility = 70.0
        
        elif self.condition == WeatherCondition.LIGHT_RAIN:
            self.wind_speed = np.random.uniform(15, 25)
            self.visibility = 60.0
        
        elif self.condition == WeatherCondition.HEAVY_RAIN:
            self.wind_speed = np.random.uniform(30, 45)
            self.visibility = 40.0
        
        elif self.condition == WeatherCondition.STORM:
            self.wind_speed = np.random.uniform(45, 60)
            self.visibility = 20.0
        
        elif self.condition == WeatherCondition.THUNDERSTORM:
            self.wind_speed = np.random.uniform(50, 70)
            self.visibility = 10.0
        
        # Random wind direction
        self.wind_direction = np.random.uniform(0, 360)
    
    def update(self, time_step: int = 1):
        """
        تحديث حالة الطقس (يمكن أن تتغير مع الوقت)
        
        Args:
            time_step: الخطوة الزمنية
        """
        # Small chance of weather change (تقليل الفرصة لجعل الطقس أكثر استقراراً)
        if np.random.random() < 0.003:  # 0.3% chance per step (كانت 1%)
            self._change_weather()
        
        # Wind fluctuation
        self.wind_speed += np.random.uniform(-2, 2)
        self.wind_speed = np.clip(self.wind_speed, 0, 80)
        
        # Wind direction change
        self.wind_direction += np.random.uniform(-10, 10)
        self.wind_direction = self.wind_direction % 360
    
    def _change_weather(self):
        """تغيير حالة الطقس"""
        # Transition probabilities (محسّنة لتقليل الطقس السيء)
        transitions = {
            WeatherCondition.CLEAR: [
                (WeatherCondition.CLEAR, 0.85),    # زيادة احتمال البقاء صافياً
                (WeatherCondition.CLOUDY, 0.12),
                (WeatherCondition.WINDY, 0.03)
            ],
            WeatherCondition.CLOUDY: [
                (WeatherCondition.CLEAR, 0.5),
                (WeatherCondition.CLOUDY, 0.35),
                (WeatherCondition.LIGHT_RAIN, 0.1),
                (WeatherCondition.WINDY, 0.05)
            ],
            WeatherCondition.WINDY: [
                (WeatherCondition.CLEAR, 0.4),
                (WeatherCondition.CLOUDY, 0.4),
                (WeatherCondition.WINDY, 0.15),
                (WeatherCondition.STORM, 0.05)      # تقليل احتمال العواصف
            ],
            WeatherCondition.LIGHT_RAIN: [
                (WeatherCondition.CLOUDY, 0.6),     # زيادة احتمال التحسن
                (WeatherCondition.LIGHT_RAIN, 0.3),
                (WeatherCondition.HEAVY_RAIN, 0.1)  # تقليل احتمال التدهور
            ],
            WeatherCondition.HEAVY_RAIN: [
                (WeatherCondition.LIGHT_RAIN, 0.6), # زيادة احتمال التحسن
                (WeatherCondition.HEAVY_RAIN, 0.3),
                (WeatherCondition.STORM, 0.1)       # تقليل احتمال العواصف
            ],
            WeatherCondition.STORM: [
                (WeatherCondition.HEAVY_RAIN, 0.6), # تحسن سريع من العاصفة
                (WeatherCondition.STORM, 0.3),
                (WeatherCondition.THUNDERSTORM, 0.1)
            ],
            WeatherCondition.THUNDERSTORM: [
                (WeatherCondition.STORM, 0.7),      # تحسن سريع
                (WeatherCondition.THUNDERSTORM, 0.2),
                (WeatherCondition.HEAVY_RAIN, 0.1)
            ]
        }
        
        # Get possible transitions
        possible = transitions.get(self.condition, [(WeatherCondition.CLEAR, 1.0)])
        
        # Choose new condition
        conditions, probs = zip(*possible)
        self.condition = np.random.choice(conditions, p=probs)
        
        # Update effects
        self._update_weather_effects()
    
    def get_wind_effect(self) -> Tuple[float, float]:
        """
        حساب تأثير الرياح على الحركة
        
        Returns:
            (dx, dy) التأثير على الحركة
        """
        # Convert wind to movement effect
        wind_strength = self.wind_speed / MAX_WIND_SPEED
        
        # Calculate wind vector
        rad = np.radians(self.wind_direction)
        dx = wind_strength * np.cos(rad) * 0.5  # reduced effect
        dy = wind_strength * np.sin(rad) * 0.5
        
        return (dx, dy)
    
    def is_safe_to_fly(self) -> bool:
        """
        التحقق من أمان الطيران
        
        Returns:
            True إذا كان الطيران آمناً
        """
        # Check forbidden weather
        if self.condition.value in FORBIDDEN_WEATHER:
            return False
        
        # Check wind speed
        if self.wind_speed > MAX_WIND_SPEED:
            return False
        
        return True
    
    def get_energy_multiplier(self) -> float:
        """
        حساب معامل استهلاك الطاقة بناءً على الطقس
        
        Returns:
            معامل الضرب (1.0 = عادي، > 1.0 = استهلاك أكثر)
        """
        multipliers = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.CLOUDY: 1.1,
            WeatherCondition.WINDY: 1.3,
            WeatherCondition.LIGHT_RAIN: 1.2,
            WeatherCondition.HEAVY_RAIN: 1.5,
            WeatherCondition.STORM: 2.0,
            WeatherCondition.THUNDERSTORM: 2.5
        }
        
        return multipliers.get(self.condition, 1.0)
    
    def get_visibility_factor(self) -> float:
        """
        الحصول على عامل الرؤية (0-1)
        
        Returns:
            عامل الرؤية
        """
        return self.visibility / 100.0
    
    def set_condition(self, condition: str):
        """
        تعيين حالة الطقس يدوياً
        
        Args:
            condition: حالة الطقس الجديدة
        """
        self.condition = WeatherCondition(condition)
        self._update_weather_effects()
    
    def get_weather_info(self) -> dict:
        """الحصول على معلومات الطقس"""
        return {
            'condition': self.condition.value,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'visibility': self.visibility,
            'temperature': self.temperature,
            'safe_to_fly': self.is_safe_to_fly(),
            'energy_multiplier': self.get_energy_multiplier()
        }
    
    def get_weather_icon(self) -> str:
        """الحصول على أيقونة الطقس"""
        icons = {
            WeatherCondition.CLEAR: "☀️",
            WeatherCondition.CLOUDY: "☁️",
            WeatherCondition.WINDY: "💨",
            WeatherCondition.LIGHT_RAIN: "🌧️",
            WeatherCondition.HEAVY_RAIN: "🌧️🌧️",
            WeatherCondition.STORM: "⛈️",
            WeatherCondition.THUNDERSTORM: "⚡"
        }
        return icons.get(self.condition, "❓")
    
    def __repr__(self) -> str:
        return (f"Weather({self.condition.value}, wind={self.wind_speed:.1f}km/h, "
                f"visibility={self.visibility:.0f}%)")
