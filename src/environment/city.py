"""
Main City Environment - Combines all components
This is the main environment that the AI agent interacts with
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
from enum import Enum

from .drone import Drone
from .obstacles import CityObstacles, ZoneType
from .weather import WeatherSystem
from ..utils.config import (
    GRID_SIZE, MAX_ALTITUDE, REWARD_DELIVERY_SUCCESS,
    REWARD_FAST_DELIVERY_BONUS, REWARD_BATTERY_EFFICIENT,
    REWARD_COLLISION, REWARD_BATTERY_DEPLETED, REWARD_NO_FLY_VIOLATION,
    REWARD_NO_FLY_INTERCEPTION, REWARD_STORM_CRASH, REWARD_PAYLOAD_SPOILED,
    REWARD_TIME_PENALTY, REWARD_CHARGING, MAX_STEPS_PER_EPISODE
)
from ..utils.logger import get_logger


class MissionStatus(Enum):
    """حالة المهمة"""
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED_COLLISION = "failed_collision"  # 💥 اصطدام بمبنى
    FAILED_BATTERY = "failed_battery"  # 🔋 نفاد البطارية
    FAILED_TIMEOUT = "failed_timeout"  # ⏱️ انتهاء الوقت
    FAILED_VIOLATION = "failed_violation"  # 🚫 انتهاك منطقة محظورة
    FAILED_INTERCEPTION = "failed_interception"  # 🔫 إسقاط أمني
    FAILED_STORM = "failed_storm"  # ⛈️ تحطم بسبب العاصفة
    FAILED_PAYLOAD_SPOILED = "failed_payload_spoiled"  # 🩸 فساد العينة


class CityEnvironment:
    """
    البيئة الرئيسية للمدينة
    تجمع الطائرة، العقبات، الطقس، والمنطق
    """
    
    def __init__(self, grid_size: int = GRID_SIZE, weather: str = "clear", seed: int = None):
        """
        تهيئة البيئة
        
        Args:
            grid_size: حجم الشبكة
            weather: حالة الطقس الابتدائية
            seed: seed للعشوائية
        """
        self.grid_size = grid_size
        self.seed = seed
        
        # Initialize components
        self.obstacles = CityObstacles(grid_size, seed)
        self.weather = WeatherSystem(weather)
        self.logger = get_logger()
        
        # Mission state
        self.mission_id = 0
        self.start_position = None
        self.target_position = None
        self.drone = None
        self.current_step = 0
        self.mission_status = MissionStatus.IN_PROGRESS
        
        # Statistics
        self.total_reward = 0.0
        self.violations = 0
        self.collisions = 0
        self.interceptions = 0
        self.storm_crashes = 0
        self.payload_spoilages = 0
        
        # Action space
        self.actions = [
            'MOVE_NORTH',
            'MOVE_SOUTH',
            'MOVE_EAST',
            'MOVE_WEST',
            'MOVE_UP',
            'MOVE_DOWN',
            'HOVER',
            'CHARGE'
        ]
        
        self.logger.info(f"City Environment initialized: {grid_size}x{grid_size}")
    
    def reset(self) -> Dict:
        """
        إعادة تعيين البيئة لمهمة جديدة
        
        Returns:
            الحالة الابتدائية
        """
        self.mission_id += 1
        
        # Get random start (hospital) and target (lab)
        self.start_position = self.obstacles.get_random_hospital()
        self.target_position = self.obstacles.get_random_lab()
        
        # Add altitude (start at safe altitude)
        start_alt = self.obstacles.get_min_safe_altitude(*self.start_position)
        self.start_position = (*self.start_position, start_alt)
        
        target_alt = self.obstacles.get_min_safe_altitude(*self.target_position)
        self.target_position = (*self.target_position, target_alt)
        
        # Initialize drone
        self.drone = Drone(self.start_position)
        
        # 📦 استلام الشحنة من المستشفى (نقطة البداية)
        # يتم تفعيل القفل الإلكتروني GPS-based تلقائياً
        self.drone.pickup_cargo("blood_sample", self.start_position[:2])
        
        # Reset mission state
        self.current_step = 0
        self.mission_status = MissionStatus.IN_PROGRESS
        self.total_reward = 0.0
        self.violations = 0
        self.collisions = 0
        self.interceptions = 0
        self.storm_crashes = 0
        self.payload_spoilages = 0
        
        # Log mission start
        self.logger.log_mission_start(
            self.mission_id,
            self.start_position,
            self.target_position
        )
        
        return self._get_state()
    
    def step(self, action: str) -> Tuple[Dict, float, bool, Dict]:
        """
        تنفيذ خطوة في البيئة
        
        Args:
            action: الإجراء المطلوب
        
        Returns:
            (state, reward, done, info)
        """
        self.current_step += 1
        reward = 0.0
        done = False
        info = {}
        
        # Update weather
        self.weather.update()
        
        # Update payload condition (medical cargo spoilage)
        self.drone.update_payload_condition(time_step=1.0)
        
        # Get wind effect
        wind_effect = self.weather.get_wind_effect()
        
        # ═══════════════════════════════════════════════════════════
        # PRE-FLIGHT CHECKS (قبل الحركة)
        # ═══════════════════════════════════════════════════════════
        
        # 🩸 CHECK 1: Payload Spoilage (فساد العينة الطبية)
        if self.drone.is_payload_spoiled():
            reward = REWARD_PAYLOAD_SPOILED
            done = True
            self.mission_status = MissionStatus.FAILED_PAYLOAD_SPOILED
            self.payload_spoilages += 1
            self.logger.log_safety_violation(
                "payload_spoiled",
                f"Medical sample expired after {self.drone.time_since_pickup:.0f}s"
            )
            info = {'mission_status': self.mission_status.value, 'reason': 'payload_spoiled'}
            return self._get_state(), reward, done, info
        
        # ⛈️ CHECK 2: Extreme Weather (طقس قاسٍ)
        from ..utils.config import EXTREME_WIND_SPEED
        if self.weather.wind_speed >= EXTREME_WIND_SPEED:
            self.drone.crash("storm_damage")
            reward = REWARD_STORM_CRASH
            done = True
            self.mission_status = MissionStatus.FAILED_STORM
            self.storm_crashes += 1
            self.logger.log_weather_event(
                self.weather.condition.value,
                f"Extreme wind {self.weather.wind_speed:.0f} km/h - Drone crashed"
            )
            info = {'mission_status': self.mission_status.value, 'reason': 'extreme_weather'}
            return self._get_state(), reward, done, info
        
        # Execute action
        success = self.drone.move(action, wind_effect)
        
        if not success:
            # Drone crashed or can't move
            if self.drone.is_crashed:
                if self.drone.crash_reason == "battery_depleted":
                    reward = REWARD_BATTERY_DEPLETED
                    done = True
                    self.mission_status = MissionStatus.FAILED_BATTERY
                    self.logger.log_battery_warning(self.drone.battery, "CRASHED - FREE FALL")
                else:
                    reward = REWARD_COLLISION
                    done = True
                    self.mission_status = MissionStatus.FAILED_COLLISION
        
        # Get current position
        x, y, z = self.drone.position
        
        # ═══════════════════════════════════════════════════════════
        # POST-FLIGHT CHECKS (بعد الحركة)
        # ═══════════════════════════════════════════════════════════
        
        # 💥 CHECK 3: Structural Collision (اصطدام بمبنى)
        if self.obstacles.is_collision(x, y, z):
            self.drone.crash("collision")
            reward = REWARD_COLLISION
            done = True
            self.mission_status = MissionStatus.FAILED_COLLISION
            self.collisions += 1
            building_height = self.obstacles.get_building_height(x, y)
            self.logger.log_collision(
                "building",
                f"Position: ({x}, {y}, {z}) - Building height: {building_height}"
            )
        
        # 🚫 CHECK 4: No-Fly Zone Interception (إسقاط أمني)
        if self.obstacles.is_no_fly_zone(x, y):
            self.drone.crash("no_fly_interception")
            reward = REWARD_NO_FLY_INTERCEPTION
            done = True
            self.mission_status = MissionStatus.FAILED_INTERCEPTION
            self.interceptions += 1
            self.logger.log_safety_violation(
                "no_fly_zone_interception",
                f"🔫 Security interception at ({x}, {y}) - Drone shot down!"
            )
        
        # ⛈️ CHECK 5: Storm Damage (تلف بسبب العاصفة)
        from ..utils.config import STORM_DAMAGE_THRESHOLD
        if self.weather.condition.value in ['storm', 'thunderstorm']:
            self.drone.steps_in_storm += 1
            if self.drone.steps_in_storm >= STORM_DAMAGE_THRESHOLD:
                self.drone.crash("storm_damage")
                reward = REWARD_STORM_CRASH
                done = True
                self.mission_status = MissionStatus.FAILED_STORM
                self.storm_crashes += 1
                self.logger.log_weather_event(
                    self.weather.condition.value,
                    f"⚡ Drone lost control after {self.drone.steps_in_storm} steps in storm"
                )
        else:
            # Reset storm counter if weather improves
            self.drone.steps_in_storm = 0
        
        # Check if reached target
        if self._is_at_target():
            # 🎯 وصلنا للهدف - محاولة التسليم
            
            # 🔓 تسليم الشحنة (يفتح القفل الإلكتروني تلقائياً)
            delivered = self.drone.deliver_cargo(self.target_position[:2])
            
            if delivered:
                # ✅ تسليم ناجح!
                delivery_time = self.current_step
                battery_used = 100 - self.drone.battery
                
                # Base reward
                reward = REWARD_DELIVERY_SUCCESS
                
                # Time bonus (faster is better)
                time_ratio = delivery_time / MAX_STEPS_PER_EPISODE
                time_bonus = REWARD_FAST_DELIVERY_BONUS * (1 - time_ratio)
                reward += time_bonus
                
                # Battery efficiency bonus
                battery_bonus = REWARD_BATTERY_EFFICIENT * (self.drone.battery / 100)
                reward += battery_bonus
                
                done = True
                self.mission_status = MissionStatus.SUCCESS
                
                self.logger.log_mission_complete(
                    self.mission_id,
                    True,
                    {
                        'time': delivery_time,
                        'battery': self.drone.battery,
                        'reward': reward,
                        'cargo_delivered': delivered
                    }
                )
        
        # Time penalty (encourage faster delivery)
        if not done:
            reward += REWARD_TIME_PENALTY
        
        # Charging penalty
        if action == 'CHARGE':
            reward += REWARD_CHARGING
        
        # Check timeout
        if self.current_step >= MAX_STEPS_PER_EPISODE:
            done = True
            self.mission_status = MissionStatus.FAILED_TIMEOUT
            reward = REWARD_COLLISION  # penalty for timeout
        
        # Update total reward
        self.total_reward += reward
        
        # Get new state
        state = self._get_state()
        
        # Info dictionary
        info = {
            'mission_id': self.mission_id,
            'step': self.current_step,
            'position': self.drone.position,
            'battery': self.drone.battery,
            'distance_to_target': self._distance_to_target(),
            'mission_status': self.mission_status.value,
            'violations': self.violations,
            'collisions': self.collisions,
            'interceptions': self.interceptions,
            'storm_crashes': self.storm_crashes,
            'payload_spoilages': self.payload_spoilages,
            'weather': self.weather.condition.value,
            'payload_condition': self.drone.payload_condition,
            'time_since_pickup': self.drone.time_since_pickup,
            'crash_reason': self.drone.crash_reason if self.drone.is_crashed else None
        }
        
        return state, reward, done, info
    
    def get_state(self) -> Dict:
        """نسخة آمنة للحصول على الحالة"""
        if self.drone is None:
            return {
                'position': (0, 0, 0),
                'battery': 100,
                'has_cargo': False,
                'speed': 0,
                'heading': 0,
                'target': self.target_position if self.target_position else (0, 0, 0),
                'distance_to_target': 0,
                'weather': self.weather.condition.value,
                'safe_to_fly': self.weather.is_safe_to_fly(),
                'step': self.current_step
            }
        return self._get_state()

    def _get_state(self) -> Dict:
        """
        الحصول على حالة البيئة الحالية
        
        Returns:
            قاموس يحتوي على جميع معلومات الحالة
        """
        x, y, z = self.drone.position
        tx, ty, tz = self.target_position
        
        # Calculate relative position to target
        dx = tx - x
        dy = ty - y
        dz = tz - z
        
        # Get nearby obstacles
        nearby_obstacles = self.obstacles.get_obstacles_in_radius(x, y, 3)
        
        # Check if in no-fly zone
        in_no_fly = self.obstacles.is_no_fly_zone(x, y)
        
        # Get nearest charging station
        nearest_station = self.obstacles.get_nearest_charging_station(x, y)
        if nearest_station:
            sx, sy = nearest_station
            station_dx = sx - x
            station_dy = sy - y
        else:
            station_dx, station_dy = 0, 0
        
        state = {
            # Drone state
            'position': (x, y, z),
            'battery': self.drone.battery,
            'has_cargo': self.drone.cargo is not None,
            'speed': self.drone.speed,
            'heading': self.drone.heading,
            
            # Target information
            'target': self.target_position,
            'relative_target': (dx, dy, dz),
            'distance_to_target': self._distance_to_target(),
            
            # Environment
            'nearby_obstacles': len(nearby_obstacles),
            'in_no_fly_zone': in_no_fly,
            'building_height': self.obstacles.get_building_height(x, y),
            
            # 🛡️ Predictive Safety Neighbors (Help for Logic Engine)
            'neighbor_buildings': {
                'MOVE_NORTH': self.obstacles.get_building_height(x, y-1),
                'MOVE_SOUTH': self.obstacles.get_building_height(x, y+1),
                'MOVE_EAST': self.obstacles.get_building_height(x+1, y),
                'MOVE_WEST': self.obstacles.get_building_height(x-1, y)
            },
            'neighbor_no_fly': {
                'MOVE_NORTH': self.obstacles.is_no_fly_zone(x, y-1),
                'MOVE_SOUTH': self.obstacles.is_no_fly_zone(x, y+1),
                'MOVE_EAST': self.obstacles.is_no_fly_zone(x+1, y),
                'MOVE_WEST': self.obstacles.is_no_fly_zone(x-1, y)
            },
            
            # Charging station
            'nearest_station': (station_dx, station_dy),
            
            # Weather
            'weather': self.weather.condition.value,
            'wind_speed': self.weather.wind_speed,
            'safe_to_fly': self.weather.is_safe_to_fly(),
            
            # Mission
            'step': self.current_step,
            'mission_id': self.mission_id,
            'at_pickup_location': self._is_at_pickup(),
            'at_delivery_location': self._is_at_delivery()
        }
        
        return state
    
    def _is_at_target(self) -> bool:
        """التحقق من الوصول إلى الهدف"""
        x, y, z = self.drone.position
        tx, ty, tz = self.target_position
        
        # Within 1 cell of target
        return abs(x - tx) <= 1 and abs(y - ty) <= 1 and abs(z - tz) <= 1
    
    def _is_at_pickup(self) -> bool:
        """التحقق من الوصول إلى موقع الاستلام"""
        if not hasattr(self, 'pickup_location'):
            return False
        x, y, z = self.drone.position
        px, py, pz = self.pickup_location
        return abs(x - px) <= 1 and abs(y - py) <= 1 and abs(z - pz) <= 1
    
    def _is_at_delivery(self) -> bool:
        """التحقق من الوصول إلى موقع التسليم"""
        if not hasattr(self, 'delivery_location'):
            return False
        x, y, z = self.drone.position
        dx, dy, dz = self.delivery_location
        return abs(x - dx) <= 1 and abs(y - dy) <= 1 and abs(z - dz) <= 1
    
    def _distance_to_target(self) -> float:
        """حساب المسافة إلى الهدف (Manhattan distance)"""
        x, y, z = self.drone.position
        tx, ty, tz = self.target_position
        
        return abs(x - tx) + abs(y - ty) + abs(z - tz)
    
    def get_valid_actions(self) -> List[str]:
        """
        الحصول على الإجراءات الصالحة في الحالة الحالية
        
        Returns:
            قائمة بالإجراءات الصالحة
        """
        valid = []
        x, y, z = self.drone.position
        
        for action in self.actions:
            # Check if action is valid
            if action == 'MOVE_NORTH' and y > 0:
                valid.append(action)
            elif action == 'MOVE_SOUTH' and y < self.grid_size - 1:
                valid.append(action)
            elif action == 'MOVE_EAST' and x < self.grid_size - 1:
                valid.append(action)
            elif action == 'MOVE_WEST' and x > 0:
                valid.append(action)
            elif action == 'MOVE_UP' and z < MAX_ALTITUDE - 1:
                valid.append(action)
            elif action == 'MOVE_DOWN' and z > 0:
                valid.append(action)
            elif action == 'HOVER':
                valid.append(action)
            elif action == 'CHARGE':
                # Can only charge at charging station
                zone_type = self.obstacles.get_zone_type(x, y)
                if zone_type == ZoneType.CHARGING_STATION:
                    valid.append(action)
        
        return valid if valid else ['HOVER']
    
    def render(self):
        """رسم البيئة (للتصحيح)"""
        # Simple text-based rendering
        print(f"\n=== Mission #{self.mission_id} - Step {self.current_step} ===")
        print(f"Drone: {self.drone.position} | Battery: {self.drone.battery:.1f}%")
        print(f"Target: {self.target_position} | Distance: {self._distance_to_target():.1f}")
        print(f"Weather: {self.weather} | Safe: {self.weather.is_safe_to_fly()}")
        print(f"Status: {self.mission_status.value}")
        print(f"Reward: {self.total_reward:.1f}")
    
    def get_env_info(self) -> Dict:
        """الحصول على معلومات البيئة"""
        return {
            'grid_size': self.grid_size,
            'mission_id': self.mission_id,
            'current_step': self.current_step,
            'drone': self.drone.get_telemetry() if self.drone else None,
            'obstacles': self.obstacles.get_city_info(),
            'weather': self.weather.get_weather_info(),
            'mission_status': self.mission_status.value,
            'total_reward': self.total_reward,
            'violations': self.violations,
            'collisions': self.collisions
        }
    
    def __repr__(self) -> str:
        return f"CityEnvironment(size={self.grid_size}, mission={self.mission_id})"
