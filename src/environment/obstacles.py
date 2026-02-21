"""
Obstacles and special zones in the city environment
"""

import numpy as np
from typing import List, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..utils.config import (
    GRID_SIZE, MIN_BUILDING_HEIGHT, MAX_BUILDING_HEIGHT,
    BUILDING_DENSITY, NUM_HOSPITALS, NUM_LABS, NUM_CHARGING_STATIONS,
    NUM_NO_FLY_ZONES
)


class ZoneType(Enum):
    """أنواع المناطق"""
    EMPTY = 0
    BUILDING = 1
    HOSPITAL = 2
    LAB = 3
    CHARGING_STATION = 4
    NO_FLY_ZONE = 5
    GOVERNMENT = 6
    AIRPORT = 7


@dataclass
class Building:
    """مبنى في المدينة"""
    position: Tuple[int, int]
    height: int  # altitude levels
    zone_type: ZoneType


@dataclass
class NoFlyZone:
    """منطقة حظر طيران"""
    center: Tuple[int, int]
    radius: int
    reason: str  # "government", "airport", "military", etc.


class CityObstacles:
    """
    إدارة العقبات والمناطق الخاصة في المدينة
    """
    
    def __init__(self, grid_size: int = GRID_SIZE, seed: int = None):
        """
        تهيئة العقبات
        
        Args:
            grid_size: حجم الشبكة
            seed: seed للعشوائية (للتكرار)
        """
        self.grid_size = grid_size
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize data structures
        self.buildings: List[Building] = []
        self.hospitals: List[Tuple[int, int]] = []
        self.labs: List[Tuple[int, int]] = []
        self.charging_stations: List[Tuple[int, int]] = []
        self.no_fly_zones: List[NoFlyZone] = []
        
        # Grid representation (height at each cell)
        self.height_map = np.zeros((grid_size, grid_size), dtype=int)
        
        # Zone type map
        self.zone_map = np.full((grid_size, grid_size), ZoneType.EMPTY, dtype=object)
        
        # Generate city
        self._generate_city()
    
    def _generate_city(self):
        """توليد المدينة بشكل عشوائي"""
        # 1. Generate buildings
        self._generate_buildings()
        
        # 2. Place hospitals
        self._place_special_zones(NUM_HOSPITALS, ZoneType.HOSPITAL, self.hospitals)
        
        # 3. Place labs
        self._place_special_zones(NUM_LABS, ZoneType.LAB, self.labs)
        
        # 4. Place charging stations
        self._place_special_zones(NUM_CHARGING_STATIONS, ZoneType.CHARGING_STATION, 
                                 self.charging_stations)
        
        # 5. Create no-fly zones
        self._create_no_fly_zones()
    
    def _generate_buildings(self):
        """توليد المباني بنمط المربعات (Grid Blocks) لضمان شوارع واسعة جداً"""
        # حجم المربع السكني (مثلاً 3x3) والفراغ بين المربعات (شوارع بعرض 3 خلايا)
        block_size = 4
        street_width = 3
        
        for x in range(2, self.grid_size - 2, block_size + street_width):
            for y in range(2, self.grid_size - 2, block_size + street_width):
                # احتمال وضع مجموعة مباني في هذا المربع
                if np.random.random() < 0.7:
                    # داخل كل مربع (Block)، نضع منازل متفرقة بجانب بعضها
                    for bx in range(x, min(x + block_size, self.grid_size - 2)):
                        for by in range(y, min(y + block_size, self.grid_size - 2)):
                            # احتمال وضع مبنى في هذه الخلية داخل المربع
                            if np.random.random() < BUILDING_DENSITY * 4:
                                height = np.random.randint(MIN_BUILDING_HEIGHT, MAX_BUILDING_HEIGHT + 1)
                                
                                building = Building(
                                    position=(bx, by),
                                    height=height,
                                    zone_type=ZoneType.BUILDING
                                )
                                self.buildings.append(building)
                                self.height_map[int(by), int(bx)] = height
                                self.zone_map[int(by), int(bx)] = ZoneType.BUILDING
    
    def _place_special_zones(self, count: int, zone_type: ZoneType, storage_list: List):
        """وضع مناطق خاصة (مستشفيات، مختبرات، إلخ)"""
        placed = 0
        attempts = 0
        max_attempts = count * 10
        
        while placed < count and attempts < max_attempts:
            x = np.random.randint(0, self.grid_size)
            y = np.random.randint(0, self.grid_size)
            
            # Check if empty
            if self.zone_map[int(y), int(x)] == ZoneType.EMPTY:
                # Place zone
                self.zone_map[int(y), int(x)] = zone_type
                storage_list.append((x, y))
                
                # Create a small building for it
                height = np.random.randint(2, 5)
                building = Building(
                    position=(x, y),
                    height=height,
                    zone_type=zone_type
                )
                self.buildings.append(building)
                self.height_map[int(y), int(x)] = height
                
                placed += 1
            
            attempts += 1
    
    def _create_no_fly_zones(self):
        """إنشاء مناطق حظر الطيران"""
        reasons = ["government", "airport", "military", "restricted"]
        
        for i in range(NUM_NO_FLY_ZONES):
            # Random center
            x = np.random.randint(5, self.grid_size - 5)
            y = np.random.randint(5, self.grid_size - 5)
            
            # Random radius
            radius = np.random.randint(2, 5)
            
            # Random reason
            reason = reasons[i % len(reasons)]
            
            no_fly_zone = NoFlyZone(
                center=(x, y),
                radius=radius,
                reason=reason
            )
            
            self.no_fly_zones.append(no_fly_zone)
    
    def is_no_fly_zone(self, x: int, y: int) -> bool:
        """
        التحقق من كون الموقع في منطقة حظر طيران
        
        Args:
            x, y: الإحداثيات
        
        Returns:
            True إذا كان في منطقة محظورة
        """
        for zone in self.no_fly_zones:
            cx, cy = zone.center
            distance = np.sqrt((x - cx)**2 + (y - cy)**2)
            if distance <= zone.radius:
                return True
        return False
    
    def get_building_height(self, x: int, y: int) -> int:
        """
        الحصول على ارتفاع المبنى في موقع معين
        
        Args:
            x, y: الإحداثيات
        
        Returns:
            الارتفاع (altitude levels)
        """
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.height_map[int(y), int(x)]
        return 0
    
    def get_zone_type(self, x: int, y: int) -> ZoneType:
        """الحصول على نوع المنطقة"""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.zone_map[int(y), int(x)]
        return ZoneType.EMPTY
    
    def is_collision(self, x: int, y: int, altitude: int) -> bool:
        """
        التحقق من التصادم مع مبنى
        
        Args:
            x, y: الإحداثيات الأفقية
            altitude: الارتفاع الحالي
        
        Returns:
            True إذا كان هناك تصادم
        """
        building_height = self.get_building_height(x, y)
        return altitude <= building_height
    
    def get_min_safe_altitude(self, x: int, y: int) -> int:
        """
        الحصول على الحد الأدنى للارتفاع الآمن
        
        Args:
            x, y: الإحداثيات
        
        Returns:
            الحد الأدنى للارتفاع الآمن (altitude level)
        """
        building_height = self.get_building_height(x, y)
        # Add 1 level clearance
        return building_height + 1
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """التحقق من صحة الموقع (داخل الحدود)"""
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size
    
    def get_nearest_charging_station(self, x: int, y: int) -> Tuple[int, int]:
        """
        الحصول على أقرب محطة شحن
        
        Args:
            x, y: الموقع الحالي
        
        Returns:
            إحداثيات أقرب محطة شحن
        """
        if not self.charging_stations:
            return None
        
        min_distance = float('inf')
        nearest = self.charging_stations[0]
        
        for station in self.charging_stations:
            sx, sy = station
            distance = abs(x - sx) + abs(y - sy)  # Manhattan distance
            if distance < min_distance:
                min_distance = distance
                nearest = station
        
        return nearest
    
    def get_random_hospital(self) -> Tuple[int, int]:
        """الحصول على مستشفى عشوائي"""
        if not self.hospitals:
            return (0, 0)
        return self.hospitals[np.random.randint(0, len(self.hospitals))]
    
    def get_random_lab(self) -> Tuple[int, int]:
        """الحصول على مختبر عشوائي"""
        if not self.labs:
            return (self.grid_size - 1, self.grid_size - 1)
        return self.labs[np.random.randint(0, len(self.labs))]
    
    def get_obstacles_in_radius(self, x: int, y: int, radius: int) -> List[Tuple[int, int, int]]:
        """
        الحصول على العقبات في نطاق معين
        
        Args:
            x, y: المركز
            radius: نصف القطر
        
        Returns:
            قائمة بالعقبات [(x, y, height), ...]
        """
        obstacles = []
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if self.is_valid_position(nx, ny):
                    height = self.get_building_height(nx, ny)
                    if height > 0:
                        obstacles.append((nx, ny, height))
        
        return obstacles
    
    def get_city_info(self) -> dict:
        """الحصول على معلومات المدينة"""
        return {
            'grid_size': self.grid_size,
            'num_buildings': len(self.buildings),
            'num_hospitals': len(self.hospitals),
            'num_labs': len(self.labs),
            'num_charging_stations': len(self.charging_stations),
            'num_no_fly_zones': len(self.no_fly_zones),
            'hospitals': self.hospitals,
            'labs': self.labs,
            'charging_stations': self.charging_stations,
            'no_fly_zones': [(z.center, z.radius, z.reason) for z in self.no_fly_zones]
        }
    
    def __repr__(self) -> str:
        return (f"CityObstacles(size={self.grid_size}, buildings={len(self.buildings)}, "
                f"hospitals={len(self.hospitals)}, labs={len(self.labs)})")
