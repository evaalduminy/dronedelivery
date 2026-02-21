"""
Logic Engine for Drone Safety Rules
Symbolic Layer of the Hybrid Architecture
"""

from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..utils.config import (
    MIN_BATTERY_EMERGENCY, MIN_BATTERY_RETURN, MAX_WIND_SPEED,
    SAFETY_MAX_ALTITUDE_M, SAFETY_MIN_ALTITUDE_M, EMERGENCY_LANDING_DISTANCE,
    ALTITUDE_STEP
)
from ..utils.logger import get_logger


class RuleType(Enum):
    """أنواع القواعد"""
    SAFETY = "safety"           # قواعد الأمان
    EFFICIENCY = "efficiency"   # قواعد الكفاءة
    MISSION = "mission"         # قواعد المهمة


@dataclass
class Rule:
    """
    قاعدة منطقية
    """
    name: str
    rule_type: RuleType
    condition: callable  # دالة تتحقق من الشرط
    action: str         # الإجراء المطلوب
    priority: int       # أولوية القاعدة (أعلى رقم = أولوية أعلى)
    description: str    # وصف القاعدة


class LogicEngine:
    """
    محرك المنطق للقواعد الرمزية
    
    الطبقة الرمزية (Symbolic Layer):
    - قواعد أمان صارمة لا يمكن انتهاكها
    - منطق واضح وقابل للتفسير
    - ضمان السلامة في جميع الأوقات
    """
    
    def __init__(self):
        """تهيئة محرك المنطق"""
        self.rules: List[Rule] = []
        self.logger = get_logger()
        
        # تحميل القواعد الأساسية
        self._load_safety_rules()
        self._load_efficiency_rules()
        self._load_mission_rules()
        
        self.logger.info(f"Logic Engine initialized with {len(self.rules)} rules")
    
    def _load_safety_rules(self):
        """تحميل قواعد الأمان الأساسية"""
        
        # قاعدة البطارية الحرجة
        self.add_rule(Rule(
            name="critical_battery",
            rule_type=RuleType.SAFETY,
            condition=lambda state: state['battery'] <= MIN_BATTERY_EMERGENCY,
            action="HOVER",
            priority=100,
            description="هبوط اضطراري عند انخفاض البطارية بشكل حرج"
        ))
        
        # قاعدة العودة للقاعدة
        self.add_rule(Rule(
            name="return_to_base",
            rule_type=RuleType.SAFETY,
            condition=lambda state: (
                state['battery'] <= MIN_BATTERY_RETURN and 
                not state['has_cargo']
            ),
            action="return_to_base",
            priority=90,
            description="العودة للقاعدة عند انخفاض البطارية"
        ))
        
        # قاعدة الطقس السيء
        self.add_rule(Rule(
            name="bad_weather",
            rule_type=RuleType.SAFETY,
            condition=lambda state: not state['safe_to_fly'],
            action="HOVER",
            priority=95,
            description="التوقف أو الهبوط في الطقس السيء"
        ))
        
        # قاعدة المنطقة المحظورة
        self.add_rule(Rule(
            name="no_fly_zone",
            rule_type=RuleType.SAFETY,
            condition=lambda state: state['in_no_fly_zone'],
            action="avoid_area",
            priority=85,
            description="تجنب المناطق المحظورة"
        ))
        
        # قاعدة الارتفاع الآمن
        self.add_rule(Rule(
            name="safe_altitude",
            rule_type=RuleType.SAFETY,
            condition=lambda state: (
                state['position'][2] * ALTITUDE_STEP > SAFETY_MAX_ALTITUDE_M or 
                state['position'][2] * ALTITUDE_STEP < SAFETY_MIN_ALTITUDE_M
            ),
            action="adjust_altitude",
            priority=80,
            description="الحفاظ على ارتفاع آمن"
        ))
        
        # قاعدة تجنب العقبات
        self.add_rule(Rule(
            name="avoid_obstacles",
            rule_type=RuleType.SAFETY,
            condition=lambda state: state.get('nearby_obstacles', 0) > 0 or state.get('obstacle_nearby', False),
            action="evade",
            priority=88, # زيادة الأولوية لتكون أعلى من المناطق المحظورة وأدنى من الطقس
            description="تجنب الاصطدام بالمباني والعقبات القريبة"
        ))
    
    def _load_efficiency_rules(self):
        """تحميل قواعد الكفاءة"""
        
        # قاعدة الطريق المباشر
        self.add_rule(Rule(
            name="direct_path",
            rule_type=RuleType.EFFICIENCY,
            condition=lambda state: (
                state['battery'] > 50 and 
                state['nearby_obstacles'] == 0 and
                state['safe_to_fly']
            ),
            action="move_direct",
            priority=30,
            description="التحرك مباشرة نحو الهدف عند الأمان"
        ))
        
        # قاعدة توفير الطاقة
        self.add_rule(Rule(
            name="conserve_energy",
            rule_type=RuleType.EFFICIENCY,
            condition=lambda state: state['battery'] < 40,
            action="conserve_energy",
            priority=40,
            description="توفير الطاقة عند انخفاض البطارية"
        ))
        
        # قاعدة الارتفاع الأمثل
        self.add_rule(Rule(
            name="optimal_altitude",
            rule_type=RuleType.EFFICIENCY,
            condition=lambda state: (
                state.get('wind_speed', 0) > 15 and
                state['position'][2] < 80
            ),
            action="climb_higher",
            priority=25,
            description="الارتفاع لتجنب الرياح القوية"
        ))
    
    def _load_mission_rules(self):
        """تحميل قواعد المهمة"""
        
        # قاعدة التقاط الشحنة
        self.add_rule(Rule(
            name="pickup_cargo",
            rule_type=RuleType.MISSION,
            condition=lambda state: (
                not state['has_cargo'] and
                state['at_pickup_location'] and
                state['battery'] > MIN_BATTERY_RETURN + 20
            ),
            action="pickup",
            priority=60,
            description="التقاط الشحنة من موقع الاستلام"
        ))
        
        # قاعدة تسليم الشحنة
        self.add_rule(Rule(
            name="deliver_cargo",
            rule_type=RuleType.MISSION,
            condition=lambda state: (
                state['has_cargo'] and
                state['at_delivery_location']
            ),
            action="deliver",
            priority=65,
            description="تسليم الشحنة في الموقع المحدد"
        ))
        
        # قاعدة التوجه للاستلام
        self.add_rule(Rule(
            name="go_to_pickup",
            rule_type=RuleType.MISSION,
            condition=lambda state: (
                not state['has_cargo'] and
                not state['at_pickup_location'] and
                state['battery'] > MIN_BATTERY_RETURN + 30
            ),
            action="move_to_pickup",
            priority=50,
            description="التوجه لموقع الاستلام"
        ))
        
        # قاعدة التوجه للتسليم
        self.add_rule(Rule(
            name="go_to_delivery",
            rule_type=RuleType.MISSION,
            condition=lambda state: (
                state['has_cargo'] and
                not state['at_delivery_location']
            ),
            action="move_to_delivery",
            priority=55,
            description="التوجه لموقع التسليم"
        ))
    
    def add_rule(self, rule: Rule):
        """
        إضافة قاعدة جديدة
        
        Args:
            rule: القاعدة المراد إضافتها
        """
        self.rules.append(rule)
        # ترتيب القواعد حسب الأولوية (الأعلى أولاً)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def evaluate_rules(self, state: Dict) -> List[Tuple[Rule, bool]]:
        """
        تقييم جميع القواعد على الحالة الحالية
        
        Args:
            state: حالة البيئة
        
        Returns:
            قائمة بالقواعد ونتائج تقييمها
        """
        results = []
        
        for rule in self.rules:
            try:
                is_triggered = rule.condition(state)
                results.append((rule, is_triggered))
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.name}: {e}")
                results.append((rule, False))
        
        return results
    
    def get_triggered_rules(self, state: Dict) -> List[Rule]:
        """
        الحصول على القواعد المفعلة فقط
        
        Args:
            state: حالة البيئة
        
        Returns:
            قائمة بالقواعد المفعلة مرتبة حسب الأولوية
        """
        triggered_rules = []
        
        for rule, is_triggered in self.evaluate_rules(state):
            if is_triggered:
                triggered_rules.append(rule)
        
        return triggered_rules
    
    def get_recommended_action(self, state: Dict) -> Tuple[str, Rule]:
        """
        الحصول على الإجراء الموصى به بناءً على أعلى قاعدة أولوية
        
        Args:
            state: حالة البيئة
        
        Returns:
            tuple من (الإجراء، القاعدة المطبقة)
        """
        triggered_rules = self.get_triggered_rules(state)
        
        if triggered_rules:
            # أعلى قاعدة أولوية
            top_rule = triggered_rules[0]
            return top_rule.action, top_rule
        
        # لا توجد قواعد مفعلة - إجراء افتراضي
        return "continue", None
    
    def is_action_safe(self, state: Dict, action: str) -> Tuple[bool, List[Rule]]:
        """
        التحقق من أمان إجراء معين
        
        Args:
            state: الحالة الحالية
            action: الإجراء المراد التحقق منه
        
        Returns:
            tuple من (هل الإجراء آمن؟، قائمة القواعد المنتهكة)
        """
        violated_rules = []
        
        # التحقق من قواعد الأمان فقط
        safety_rules = [r for r in self.rules if r.rule_type == RuleType.SAFETY]
        
        for rule in safety_rules:
            if rule.condition(state):
                # هذه القاعدة مفعلة - هل الإجراء يتعارض معها؟
                if self._action_violates_rule(action, rule, state):
                    violated_rules.append(rule)
        
        is_safe = len(violated_rules) == 0
        return is_safe, violated_rules
    
    def _action_violates_rule(self, action: str, rule: Rule, state: Dict) -> bool:
        """
        التحقق من انتهاك إجراء لقاعدة معينة بناءً على الحالة الحالية والتنبؤ بالموقع التالي للطائرة المجهزة ببيانات الجيران
        """
        # إذا كان الإجراء هو الانتظار أو الهبوط الاضطراري، غالباً ما يكون آمناً
        if action in ["HOVER", "CHARGE", "wait"]:
            return False

        # 1. التحقق من قاعدة المناطق المحظورة (استباقي)
        if rule.name == "no_fly_zone":
            neighbor_no_fly = state.get('neighbor_no_fly', {})
            if neighbor_no_fly.get(action, False):
                return True # الإجراء يؤدي للدخول في منطقة محظورة

        # 2. التحقق من قاعدة تجنب العقبات والمباني (استباقي)
        if rule.name == "avoid_obstacles":
            neighbor_buildings = state.get('neighbor_buildings', {})
            next_building_height = neighbor_buildings.get(action, 0)
            
            # الحصول على الارتفاع الحالي والمستهدف
            curr_pos = state.get('position', (0, 0, 0))
            curr_z = curr_pos[2]
            
            # إذا كان الإجراء حركياً أفقياً ويؤدي لاصطدام بمبنى في الارتفاع الحالي
            if action in ["MOVE_NORTH", "MOVE_SOUTH", "MOVE_EAST", "MOVE_WEST"]:
                if curr_z <= next_building_height:
                    return True # سيحدث تصادم
            
            # إذا كان الإجراء هبوطاً ويؤدي لاصطدام بالمبنى الحالي
            if action == "MOVE_DOWN":
                current_building_height = state.get('building_height', 0)
                if curr_z - 1 <= current_building_height:
                    return True # سيحدث تصادم

        # قواعد الانتهاك الثابتة (Fallbacks)
        violations = {
            "critical_battery": ["MOVE_UP", "HOVER", "MOVE_NORTH", "MOVE_SOUTH", "MOVE_EAST", "MOVE_WEST"],
            "bad_weather": ["MOVE_UP", "MOVE_NORTH", "MOVE_SOUTH", "MOVE_EAST", "MOVE_WEST"]
        }
        
        rule_violations = violations.get(rule.name, [])
        return action in rule_violations
    
    def get_valid_actions(self, state: Dict, all_actions: List[str]) -> List[str]:
        """
        الحصول على الإجراءات الصالحة (الآمنة) فقط
        
        Args:
            state: الحالة الحالية
            all_actions: جميع الإجراءات الممكنة
        
        Returns:
            قائمة بالإجراءات الآمنة
        """
        valid_actions = []
        
        for action in all_actions:
            is_safe, _ = self.is_action_safe(state, action)
            if is_safe:
                valid_actions.append(action)
        
        # ضمان وجود إجراء واحد على الأقل (الانتظار دائماً آمن)
        if not valid_actions and "wait" in all_actions:
            valid_actions.append("wait")
        
        return valid_actions
    
    def get_rule_explanation(self, rule: Rule) -> str:
        """
        الحصول على شرح مفصل للقاعدة
        
        Args:
            rule: القاعدة
        
        Returns:
            شرح مفصل
        """
        return f"""
القاعدة: {rule.name}
النوع: {rule.rule_type.value}
الأولوية: {rule.priority}
الإجراء: {rule.action}
الوصف: {rule.description}
        """.strip()
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات المحرك"""
        rule_types = {}
        for rule_type in RuleType:
            rule_types[rule_type.value] = len([r for r in self.rules if r.rule_type == rule_type])
        
        return {
            'total_rules': len(self.rules),
            'rule_types': rule_types,
            'highest_priority': max(r.priority for r in self.rules) if self.rules else 0,
            'lowest_priority': min(r.priority for r in self.rules) if self.rules else 0
        }
    
    def __repr__(self) -> str:
        return f"LogicEngine(rules={len(self.rules)})"