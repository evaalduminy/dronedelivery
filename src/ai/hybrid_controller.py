"""
Hybrid Neuro-Symbolic Controller
Combines Q-Learning (Neural) with Logic Engine (Symbolic)
"""

from typing import Dict, List, Tuple, Optional
import numpy as np

from .q_learning import QLearningAgent
from .logic_engine import LogicEngine, RuleType
from ..utils.config import ACTIONS
from ..utils.logger import get_logger


class HybridController:
    """
    المتحكم الهجين (Neuro-Symbolic)
    
    يجمع بين:
    - الطبقة العصبية (Q-Learning): للتعلم والكفاءة
    - الطبقة الرمزية (Logic Engine): للأمان والقواعد
    
    المبدأ:
    1. المحرك المنطقي يحدد الإجراءات الآمنة
    2. Q-Learning يختار الأفضل من الإجراءات الآمنة
    3. ضمان الأمان مع تحسين الأداء
    """
    
    def __init__(self, actions: List[str] = ACTIONS):
        """
        تهيئة المتحكم الهجين
        
        Args:
            actions: قائمة الإجراءات الممكنة
        """
        self.actions = actions
        
        # المكونات الأساسية
        self.q_agent = QLearningAgent(actions)
        self.logic_engine = LogicEngine()
        
        # إحصائيات
        self.decisions_made = 0
        self.safety_overrides = 0  # عدد مرات تدخل قواعد الأمان
        self.logic_suggestions = 0  # عدد مرات اقتراح المحرك المنطقي
        
        self.logger = get_logger()
        self.logger.info("Hybrid Controller initialized")
    
    def choose_action(self, state: Dict, training: bool = True) -> Tuple[str, Dict]:
        """
        اختيار إجراء باستخدام النهج الهجين
        
        Args:
            state: الحالة الحالية
            training: هل نحن في وضع التدريب؟
        
        Returns:
            tuple من (الإجراء المختار، معلومات القرار)
        """
        self.decisions_made += 1
        
        # 1. تحليل الحالة بالمحرك المنطقي
        triggered_rules = self.logic_engine.get_triggered_rules(state)
        recommended_action, top_rule = self.logic_engine.get_recommended_action(state)
        
        # 2. الحصول على الإجراءات الآمنة
        safe_actions = self.logic_engine.get_valid_actions(state, self.actions)
        
        # 3. معلومات القرار
        decision_info = {
            'triggered_rules': len(triggered_rules),
            'top_rule': top_rule.name if top_rule else None,
            'safe_actions_count': len(safe_actions),
            'recommended_action': recommended_action,
            'decision_type': None,
            'q_values': {},
            'safety_override': False
        }
        
        # 4. اتخاذ القرار بناءً على الأولوية
        
        # أ) قواعد الأمان الحرجة (أولوية عالية جداً)
        critical_rules = [r for r in triggered_rules 
                         if r.rule_type == RuleType.SAFETY and r.priority >= 90]
        
        if critical_rules:
            # تدخل فوري لقواعد الأمان الحرجة
            action = critical_rules[0].action
            decision_info['decision_type'] = 'safety_critical'
            decision_info['safety_override'] = True
            self.safety_overrides += 1
            
            self.logger.warning(f"Safety override: {critical_rules[0].name} -> {action}")
        
        # ب) قواعد منطقية مع خيارات Q-Learning أو التوجه للهدف
        elif safe_actions:
            # 🎯 ميزة التوجه للهدف (Goal-Oriented)
            # نطبق الهيورستيك إذا كنا في البداية (Exploration) أو إذا لم يكن لدى الوكيل خبرة كافية
            best_q_action = self.q_agent.get_best_action_greedy(state, safe_actions)
            q_val = self.q_agent.get_q_value(state, best_q_action)
            
            # إذا كان مستوى الثقة منخفضاً (Q near 0) أو كنا في وضع الاستكشاف، نستخدم التوجه للهدف
            if (training and self.q_agent.epsilon > 0.3) or (q_val < 0.1):
                best_move = self._get_goal_oriented_action(state, safe_actions)
                if best_move:
                    action = best_move
                    decision_info['decision_type'] = 'goal_oriented_heuristic'
                else:
                    action = best_q_action
                    decision_info['decision_type'] = 'hybrid_greedy'
            else:
                action = best_q_action
                decision_info['decision_type'] = 'hybrid_greedy'
                
            # حساب Q-values للإجراءات الآمنة
            for safe_action in safe_actions:
                decision_info['q_values'][safe_action] = self.q_agent.get_q_value(state, safe_action)
        
        # ج) لا توجد إجراءات آمنة - إجراء طوارئ
        else:
            action = "emergency_land"
            decision_info['decision_type'] = 'emergency'
            decision_info['safety_override'] = True
            self.safety_overrides += 1
            
            self.logger.error("No safe actions available - emergency landing")
        
        # 5. تحقق إضافي من الأمان
        is_safe, violated_rules = self.logic_engine.is_action_safe(state, action)
        if not is_safe and decision_info['decision_type'] != 'emergency':
            # إجراء غير آمن - تغيير للانتظار
            action = "wait"
            decision_info['safety_override'] = True
            decision_info['violated_rules'] = [r.name for r in violated_rules]
            self.safety_overrides += 1
            
            self.logger.warning(f"Action changed to 'wait' due to safety violations")
        
        # 6. تسجيل اقتراحات المحرك المنطقي
        if recommended_action and action == recommended_action:
            self.logic_suggestions += 1
            
        return action, decision_info

    def _get_goal_oriented_action(self, state: Dict, safe_actions: List[str]) -> Optional[str]:
        """إيجاد الإجراء الذي يقرب الدرون من الهدف من بين الإجراءات الآمنة"""
        if 'relative_target' not in state:
            return None
            
        dx, dy, dz = state['relative_target']
        
        # ترتيب الإجراءات حسب مدى تقليلها للمسافة
        best_action = None
        min_dist = float('inf')
        
        for action in safe_actions:
            adx, ady, adz = 0, 0, 0
            if action == 'MOVE_NORTH': ady = -1
            elif action == 'MOVE_SOUTH': ady = 1
            elif action == 'MOVE_EAST': adx = 1
            elif action == 'MOVE_WEST': adx = -1
            elif action == 'MOVE_UP': adz = 1
            elif action == 'MOVE_DOWN': adz = -1
            
            # حساب المسافة الجديدة المتوقعة (Manhattan distance)
            new_dist = abs(dx - adx) + abs(dy - ady) + abs(dz - adz)
            if new_dist < min_dist:
                min_dist = new_dist
                best_action = action
                
        # نختار الحركة فقط إذا كانت فعلاً تقربنا من الهدف
        current_dist = abs(dx) + abs(dy) + abs(dz)
        if min_dist < current_dist:
            return best_action
            
        return None
    
    def update(self, state: Dict, action: str, reward: float, 
               next_state: Dict, done: bool):
        """
        تحديث Q-Learning بناءً على التجربة
        
        Args:
            state: الحالة الحالية
            action: الإجراء المنفذ
            reward: المكافأة
            next_state: الحالة التالية
            done: هل انتهت الحلقة؟
        """
        # تحديث Q-Learning فقط
        self.q_agent.update(state, action, reward, next_state, done)
    
    def get_action_explanation(self, state: Dict, action: str, decision_info: Dict) -> str:
        """
        الحصول على شرح مفصل للقرار
        
        Args:
            state: الحالة
            action: الإجراء المختار
            decision_info: معلومات القرار
        
        Returns:
            شرح مفصل
        """
        explanation = f"الإجراء المختار: {action}\n"
        explanation += f"نوع القرار: {decision_info['decision_type']}\n"
        
        if decision_info['top_rule']:
            explanation += f"القاعدة الرئيسية: {decision_info['top_rule']}\n"
        
        if decision_info['safety_override']:
            explanation += "⚠️ تدخل أمان فوري\n"
        
        explanation += f"عدد الإجراءات الآمنة: {decision_info['safe_actions_count']}\n"
        explanation += f"عدد القواعد المفعلة: {decision_info['triggered_rules']}\n"
        
        if decision_info['q_values']:
            explanation += "\nQ-Values للإجراءات الآمنة:\n"
            for act, q_val in decision_info['q_values'].items():
                explanation += f"  {act}: {q_val:.3f}\n"
        
        return explanation
    
    def get_state_analysis(self, state: Dict) -> Dict:
        """
        تحليل مفصل للحالة الحالية
        
        Args:
            state: الحالة
        
        Returns:
            تحليل شامل
        """
        # تحليل المحرك المنطقي
        triggered_rules = self.logic_engine.get_triggered_rules(state)
        safe_actions = self.logic_engine.get_valid_actions(state, self.actions)
        recommended_action, top_rule = self.logic_engine.get_recommended_action(state)
        
        # تحليل Q-Learning
        q_values = {}
        for action in self.actions:
            q_values[action] = self.q_agent.get_q_value(state, action)
        
        best_q_action = max(q_values, key=q_values.get)
        
        return {
            'logic_analysis': {
                'triggered_rules': [(r.name, r.priority, r.description) for r in triggered_rules],
                'safe_actions': safe_actions,
                'recommended_action': recommended_action,
                'top_rule': top_rule.name if top_rule else None
            },
            'q_learning_analysis': {
                'q_values': q_values,
                'best_action': best_q_action,
                'epsilon': self.q_agent.epsilon,
                'q_table_size': len(self.q_agent.q_table)
            },
            'hybrid_decision': {
                'would_choose': self.choose_action(state, training=False)[0],
                'safety_constraints': len(safe_actions) < len(self.actions)
            }
        }
    
    def train_episode(self, env, max_steps: int = 1000) -> Dict:
        """
        تدريب حلقة واحدة
        
        Args:
            env: البيئة
            max_steps: أقصى عدد خطوات
        
        Returns:
            إحصائيات الحلقة
        """
        state = env.reset()
        total_reward = 0
        steps = 0
        safety_overrides = 0
        
        episode_log = []
        
        for step in range(max_steps):
            # اختيار إجراء
            action, decision_info = self.choose_action(state, training=True)
            
            # تنفيذ الإجراء
            next_state, reward, done, info = env.step(action)
            
            # تحديث Q-Learning
            self.update(state, action, reward, next_state, done)
            
            # إحصائيات
            total_reward += reward
            steps += 1
            if decision_info['safety_override']:
                safety_overrides += 1
            
            # تسجيل الخطوة
            episode_log.append({
                'step': step,
                'action': action,
                'reward': reward,
                'decision_type': decision_info['decision_type'],
                'safety_override': decision_info['safety_override']
            })
            
            state = next_state
            
            if done:
                break
        
        # تقليل epsilon
        self.q_agent.decay_epsilon()
        self.q_agent.reset_for_episode()
        
        return {
            'total_reward': total_reward,
            'steps': steps,
            'safety_overrides': safety_overrides,
            'success': info.get('success', False),
            'episode_log': episode_log
        }
    
    def save_models(self, q_table_path: str = None):
        """
        حفظ النماذج
        
        Args:
            q_table_path: مسار حفظ Q-table
        """
        self.q_agent.save(q_table_path)
        self.logger.info("Models saved successfully")
    
    def load_models(self, q_table_path: str = None):
        """
        تحميل النماذج
        
        Args:
            q_table_path: مسار Q-table
        """
        success = self.q_agent.load(q_table_path)
        if success:
            self.logger.info("Models loaded successfully")
        return success
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات شاملة"""
        q_stats = self.q_agent.get_statistics()
        logic_stats = self.logic_engine.get_statistics()
        
        return {
            'hybrid_controller': {
                'decisions_made': self.decisions_made,
                'safety_overrides': self.safety_overrides,
                'logic_suggestions': self.logic_suggestions,
                'safety_override_rate': self.safety_overrides / max(self.decisions_made, 1),
                'logic_suggestion_rate': self.logic_suggestions / max(self.decisions_made, 1)
            },
            'q_learning': q_stats,
            'logic_engine': logic_stats
        }
    
    def reset_statistics(self):
        """إعادة تعيين الإحصائيات"""
        self.decisions_made = 0
        self.safety_overrides = 0
        self.logic_suggestions = 0
    
    def __repr__(self) -> str:
        return (f"HybridController(decisions={self.decisions_made}, "
                f"safety_overrides={self.safety_overrides})")