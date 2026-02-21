"""
Drone Agent - Physical simulation and state management
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

from ..utils.config import (
    MAX_SPEED, BATTERY_CAPACITY, ENERGY_PER_KM, ENERGY_PER_ALTITUDE,
    HOVER_ENERGY, CHARGING_RATE, MIN_SAFE_BATTERY, CRITICAL_BATTERY,
    CARGO_MAX_WEIGHT, CELL_SIZE, ALTITUDE_STEP, GRID_SIZE, MAX_ALTITUDE
)


@dataclass
class DroneState:
    """حالة الطائرة"""
    position: Tuple[float, float, float]  # (x, y, altitude)
    battery: float  # percentage (0-100)
    cargo: Optional[str]  # نوع الشحنة أو None
    has_package: bool  # هل تحمل شحنة؟ (للمنطق)
    speed: float  # km/h
    heading: float  # degrees (0-360)
    is_charging: bool
    is_crashed: bool
    crash_reason: Optional[str]  # سبب التحطم
    payload_locked: bool  # قفل إلكتروني للشحنة
    payload_condition: str  # حالة الشحنة (fresh, warning, spoiled)
    time_since_pickup: float  # الوقت منذ الاستلام (seconds)


class Drone:
    """
    محاكاة فيزيائية للطائرة المسيرة
    تتضمن: الحركة، البطارية، الشحنة، الفيزياء
    """
    
    def __init__(self, start_position: Tuple[int, int, int]):
        """
        تهيئة الطائرة
        
        Args:
            start_position: الموقع الابتدائي (x, y, altitude_level)
        """
        self.start_position = start_position
        self.reset()
    
    def reset(self):
        """إعادة تعيين الطائرة للحالة الابتدائية"""
        self.position = list(self.start_position)  # [x, y, z]
        self.battery = 100.0  # full battery
        self.cargo = None
        self.has_package = False  # فارغة في البداية
        self.payload_locked = False  # القفل مفتوح
        self.payload_condition = 'none'  # لا توجد شحنة
        self.time_since_pickup = 0.0  # لم يتم الاستلام بعد
        self.speed = 0.0
        self.heading = 0.0
        self.is_charging = False
        self.is_crashed = False
        self.crash_reason = None
        self.total_distance = 0.0
        self.flight_time = 0.0
        self.steps_in_storm = 0  # عدد الخطوات في العاصفة
    
    def get_state(self) -> DroneState:
        """الحصول على حالة الطائرة الحالية"""
        return DroneState(
            position=tuple(self.position),
            battery=self.battery,
            cargo=self.cargo,
            has_package=self.has_package,
            speed=self.speed,
            heading=self.heading,
            is_charging=self.is_charging,
            is_crashed=self.is_crashed,
            crash_reason=self.crash_reason,
            payload_locked=self.payload_locked,
            payload_condition=self.payload_condition,
            time_since_pickup=self.time_since_pickup
        )
    
    def move(self, action: str, wind_effect: Tuple[float, float] = (0, 0)) -> bool:
        """
        تحريك الطائرة بناءً على الإجراء
        
        Args:
            action: الإجراء المطلوب
            wind_effect: تأثير الرياح (dx, dy)
        
        Returns:
            True إذا نجحت الحركة، False إذا فشلت
        """
        if self.is_crashed or self.is_charging:
            return False
        
        # Check battery - 🔋 CRASH TYPE 1: Battery Depletion
        if self.battery <= 0:
            self.is_crashed = True
            self.crash_reason = "battery_depleted"
            return False
        
        # Calculate movement
        dx, dy, dz = 0, 0, 0
        energy_cost = HOVER_ENERGY  # default hover cost
        
        if action == 'MOVE_NORTH':
            dy = -1
            energy_cost = self._calculate_movement_energy(1, 0)
        elif action == 'MOVE_SOUTH':
            dy = 1
            energy_cost = self._calculate_movement_energy(1, 0)
        elif action == 'MOVE_EAST':
            dx = 1
            energy_cost = self._calculate_movement_energy(1, 0)
        elif action == 'MOVE_WEST':
            dx = -1
            energy_cost = self._calculate_movement_energy(1, 0)
        elif action == 'MOVE_UP':
            dz = 1
            energy_cost = ENERGY_PER_ALTITUDE
        elif action == 'MOVE_DOWN':
            dz = -1
            energy_cost = ENERGY_PER_ALTITUDE * 0.5  # going down uses less energy
        elif action == 'HOVER':
            energy_cost = HOVER_ENERGY
        elif action == 'CHARGE':
            return self._charge()
        
        # Apply wind effect
        dx += wind_effect[0]
        dy += wind_effect[1]
        
        # Update position with boundary checks
        new_x = max(0, min(GRID_SIZE - 1, self.position[0] + dx))
        new_y = max(0, min(GRID_SIZE - 1, self.position[1] + dy))
        new_z = max(0, min(MAX_ALTITUDE - 1, self.position[2] + dz))
        
        # Calculate distance moved
        distance = np.sqrt(dx**2 + dy**2) * (CELL_SIZE / 1000)  # km
        self.total_distance += distance
        
        # Update position
        self.position = [new_x, new_y, new_z]
        
        # Update battery
        self.battery -= (energy_cost / BATTERY_CAPACITY) * 100
        self.battery = max(0, self.battery)
        
        # Update speed and heading
        if dx != 0 or dy != 0:
            self.speed = MAX_SPEED
            self.heading = np.degrees(np.arctan2(dy, dx)) % 360
        else:
            self.speed = 0
        
        # Update flight time (assuming 1 step = 1 second)
        self.flight_time += 1
        
        return True
    
    def _calculate_movement_energy(self, dx: float, dy: float) -> float:
        """
        حساب الطاقة المطلوبة للحركة
        
        🔬 LOGIC RULE: إذا كانت الطائرة تحمل شحنة (has_package=True)،
        يزداد استهلاك البطارية بنسبة 20% بسبب الوزن الإضافي.
        هذا تطبيق عملي للمنطق الرمزي (Symbolic Logic) في النظام.
        """
        distance = np.sqrt(dx**2 + dy**2) * (CELL_SIZE / 1000)  # km
        energy = distance * ENERGY_PER_KM
        
        # 🎯 HYBRID AI LOGIC: Cargo Weight Penalty
        # القاعدة المنطقية: IF has_package THEN energy *= 1.2
        if self.has_package:
            energy *= 1.2  # 20% more energy with cargo (weight penalty)
        
        return energy
    
    def _charge(self) -> bool:
        """شحن البطارية"""
        if self.battery >= 100:
            return False
        
        self.is_charging = True
        self.battery = min(100, self.battery + (CHARGING_RATE / BATTERY_CAPACITY) * 100)
        self.speed = 0
        
        # Check if fully charged
        if self.battery >= 100:
            self.is_charging = False
        
        return True
    
    def update_payload_condition(self, time_step: float = 1.0):
        """
        تحديث حالة الشحنة الطبية بناءً على الوقت
        
        🩸 MEDICAL PAYLOAD SPOILAGE:
        - عينات الدم لها عمر افتراضي محدود خارج الثلاجة
        - بعد 20 دقيقة: تحذير
        - بعد 30 دقيقة: فساد كامل
        
        Args:
            time_step: الوقت المنقضي (seconds)
        """
        if not self.has_package:
            return
        
        from ..utils.config import PAYLOAD_MAX_TIME, PAYLOAD_SPOILAGE_WARNING
        
        self.time_since_pickup += time_step
        
        if self.time_since_pickup >= PAYLOAD_MAX_TIME:
            self.payload_condition = 'spoiled'  # فاسدة
        elif self.time_since_pickup >= PAYLOAD_SPOILAGE_WARNING:
            self.payload_condition = 'warning'  # تحذير
        else:
            self.payload_condition = 'fresh'  # طازجة
    
    def is_payload_spoiled(self) -> bool:
        """التحقق من فساد الشحنة"""
        return self.payload_condition == 'spoiled'
    
    def crash(self, reason: str):
        """
        تحطم الطائرة
        
        Args:
            reason: سبب التحطم
                - 'battery_depleted': نفاد البطارية
                - 'collision': اصطدام بمبنى
                - 'no_fly_interception': إسقاط أمني
                - 'storm_damage': تحطم بسبب العاصفة
        """
        self.is_crashed = True
        self.crash_reason = reason
        self.speed = 0
    
    def pickup_cargo(self, cargo_type: str, pickup_location: Tuple[int, int]) -> bool:
        """
        التقاط شحنة من نقطة الاستلام
        
        🔐 SECURE PAYLOAD BAY SYSTEM:
        - مقصورة شحن آمنة مخصصة للمواد الحيوية
        - قفل إلكتروني GPS-based
        - يتم تفعيل القفل تلقائياً عند الاستلام
        
        Args:
            cargo_type: نوع الشحنة (مثل: blood_sample, medicine)
            pickup_location: موقع الاستلام (للقفل الإلكتروني)
        
        Returns:
            True إذا نجح الاستلام
        """
        if self.has_package:
            return False  # already carrying cargo
        
        # تحميل الشحنة
        self.cargo = cargo_type
        self.has_package = True
        
        # 🔒 تفعيل القفل الإلكتروني (GPS Logic Lock)
        self.payload_locked = True
        self.pickup_location = pickup_location
        
        # 🩸 بدء عداد الوقت للشحنة الطبية
        self.time_since_pickup = 0.0
        self.payload_condition = 'fresh'
        
        return True
    
    def deliver_cargo(self, delivery_location: Tuple[int, int]) -> Optional[str]:
        """
        تسليم الشحنة في نقطة التسليم
        
        🔓 GPS LOGIC LOCK:
        - القفل الإلكتروني لا يفتح إلا عند الوصول للإحداثيات المستهدفة
        - يضمن عدم فتح المقصورة في مكان خاطئ
        - نظام أمان متقدم للمواد الحيوية
        
        Args:
            delivery_location: موقع التسليم المستهدف
        
        Returns:
            نوع الشحنة المسلمة أو None
        """
        if not self.has_package:
            return None  # no cargo to deliver
        
        # 🔓 فتح القفل الإلكتروني عند الوصول للموقع الصحيح
        self.payload_locked = False
        
        # تسليم الشحنة
        delivered = self.cargo
        self.cargo = None
        self.has_package = False
        
        return delivered
    
    def get_visual_state(self) -> str:
        """
        الحصول على الحالة البصرية للطائرة (للواجهة الرسومية)
        
        🎨 VISUAL REPRESENTATION:
        - 'empty': طائرة فارغة (لون أزرق)
        - 'loaded': طائرة محملة (لون برتقالي + دائرة صغيرة)
        - 'charging': طائرة تشحن (لون أصفر)
        - 'crashed': طائرة محطمة (لون أحمر)
        
        Returns:
            الحالة البصرية
        """
        if self.is_crashed:
            return 'crashed'
        elif self.is_charging:
            return 'charging'
        elif self.has_package:
            return 'loaded'  # 🟠 برتقالي - تحمل شحنة
        else:
            return 'empty'   # 🔵 أزرق - فارغة
    
    def can_reach(self, target: Tuple[int, int, int]) -> bool:
        """
        التحقق من إمكانية الوصول إلى الهدف بالبطارية الحالية
        
        Args:
            target: الموقع المستهدف (x, y, z)
        
        Returns:
            True إذا كانت البطارية كافية
        """
        # Calculate Manhattan distance
        dx = abs(target[0] - self.position[0])
        dy = abs(target[1] - self.position[1])
        dz = abs(target[2] - self.position[2])
        
        # Estimate energy needed
        horizontal_distance = (dx + dy) * (CELL_SIZE / 1000)  # km
        horizontal_energy = horizontal_distance * ENERGY_PER_KM
        vertical_energy = dz * ENERGY_PER_ALTITUDE
        
        total_energy_needed = horizontal_energy + vertical_energy
        
        # Add safety margin
        total_energy_needed *= 1.2
        
        # Convert to percentage
        battery_needed = (total_energy_needed / BATTERY_CAPACITY) * 100
        
        return self.battery >= battery_needed
    
    def get_battery_range(self) -> float:
        """
        حساب المدى المتبقي بالكيلومترات
        
        Returns:
            المدى بالكيلومترات
        """
        available_energy = (self.battery / 100) * BATTERY_CAPACITY
        range_km = available_energy / ENERGY_PER_KM
        
        # Account for cargo
        if self.cargo:
            range_km /= 1.2
        
        return range_km
    
    def needs_charging(self) -> bool:
        """التحقق من الحاجة للشحن"""
        return self.battery < MIN_SAFE_BATTERY
    
    def is_critical(self) -> bool:
        """التحقق من حالة البطارية الحرجة"""
        return self.battery < CRITICAL_BATTERY
    
    def get_telemetry(self) -> dict:
        """الحصول على بيانات القياس عن بعد"""
        return {
            'position': {
                'x': self.position[0],
                'y': self.position[1],
                'altitude': self.position[2] * ALTITUDE_STEP,  # meters
                'grid': tuple(self.position)
            },
            'battery': {
                'percentage': self.battery,
                'mah': (self.battery / 100) * BATTERY_CAPACITY,
                'range_km': self.get_battery_range()
            },
            'flight': {
                'speed': self.speed,
                'heading': self.heading,
                'distance_traveled': self.total_distance,
                'flight_time': self.flight_time
            },
            'cargo': {
                'type': self.cargo,
                'has_package': self.has_package,
                'payload_locked': self.payload_locked,
                'visual_state': self.get_visual_state()
            },
            'status': {
                'is_charging': self.is_charging,
                'is_crashed': self.is_crashed,
                'needs_charging': self.needs_charging(),
                'is_critical': self.is_critical()
            }
        }
    
    def __repr__(self) -> str:
        return (f"Drone(pos={self.position}, battery={self.battery:.1f}%, "
                f"cargo={self.cargo}, crashed={self.is_crashed})")
