"""
Q-Learning Agent for Drone Navigation
Neural Layer of the Hybrid Architecture
"""

import numpy as np
import pickle
import os
from typing import Dict, Tuple, List
from collections import defaultdict

from ..utils.config import (
    LEARNING_RATE, DISCOUNT_FACTOR, EPSILON_START, EPSILON_END,
    EPSILON_DECAY, NUM_EPISODES, MODELS_DIR
)
from ..utils.logger import get_logger


class QLearningAgent:
    """
    وكيل Q-Learning للتعلم المعزز
    
    الطبقة العصبية (Neural Layer):
    - يتعلم من التجربة والخطأ
    - يحسن الكفاءة مع الوقت
    - يبني Q-table لتقييم الإجراءات
    """
    
    def __init__(self, actions: List[str], learning_rate: float = LEARNING_RATE,
                 discount_factor: float = DISCOUNT_FACTOR):
        """
        تهيئة الوكيل
        
        Args:
            actions: قائمة الإجراءات الممكنة
            learning_rate: معدل التعلم (alpha)
            discount_factor: معامل الخصم (gamma)
        """
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Q-table: Q(state, action) = expected reward
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Exploration parameters
        self.epsilon = EPSILON_START
        self.epsilon_min = EPSILON_END
        self.epsilon_decay = EPSILON_DECAY
        
        # Statistics
        self.total_updates = 0
        self.episodes_trained = 0
        
        self.logger = get_logger()
        self.logger.info("Q-Learning Agent initialized")
    
    def get_state_key(self, state: Dict) -> Tuple:
        """
        تحويل الحالة إلى مفتاح للـ Q-table
        
        Args:
            state: حالة البيئة
        
        Returns:
            tuple يمكن استخدامه كمفتاح
        """
        # Discretize continuous values
        dx, dy, dz = state['relative_target']
        
        # Discretize distance (bins)
        distance_bin = min(int(abs(dx) + abs(dy)) // 5, 10)  # 0-10
        
        # Discretize battery (bins of 10%)
        battery_bin = int(state['battery'] // 10)  # 0-10
        
        # Has package?
        has_package = 1 if state['has_cargo'] else 0
        
        # Weather condition (simplified)
        weather_safe = 1 if state['safe_to_fly'] else 0
        
        # Direction to target (8 directions)
        if abs(dx) > abs(dy):
            direction = 0 if dx > 0 else 4  # East or West
        else:
            direction = 2 if dy > 0 else 6  # South or North
        
        # Nearby obstacles
        obstacles_nearby = min(state['nearby_obstacles'], 5)
        
        # In no-fly zone?
        in_no_fly = 1 if state['in_no_fly_zone'] else 0
        
        state_key = (
            distance_bin,
            battery_bin,
            has_package,
            weather_safe,
            direction,
            obstacles_nearby,
            in_no_fly
        )
        
        return state_key
    
    def choose_action(self, state: Dict, valid_actions: List[str] = None) -> str:
        """
        اختيار إجراء بناءً على سياسة epsilon-greedy
        
        Args:
            state: الحالة الحالية
            valid_actions: الإجراءات الصالحة (أو None لجميع الإجراءات)
        
        Returns:
            الإجراء المختار
        """
        if valid_actions is None:
            valid_actions = self.actions
        
        # Epsilon-greedy policy
        if np.random.random() < self.epsilon:
            # Exploration: random action
            action = np.random.choice(valid_actions)
        else:
            # Exploitation: best action from Q-table
            action = self._get_best_action(state, valid_actions)
        
        return action
    
    def _get_best_action(self, state: Dict, valid_actions: List[str]) -> str:
        """
        الحصول على أفضل إجراء من Q-table
        
        Args:
            state: الحالة الحالية
            valid_actions: الإجراءات الصالحة
        
        Returns:
            أفضل إجراء
        """
        state_key = self.get_state_key(state)
        
        # Get Q-values for all valid actions
        q_values = {action: self.q_table[state_key][action] 
                   for action in valid_actions}
        
        # Return action with highest Q-value
        if q_values:
            best_action = max(q_values, key=q_values.get)
        else:
            best_action = np.random.choice(valid_actions)
        
        return best_action
    
    def update(self, state: Dict, action: str, reward: float, 
               next_state: Dict, done: bool):
        """
        تحديث Q-table بناءً على التجربة
        
        Q-Learning Update Rule:
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: الحالة الحالية
            action: الإجراء المنفذ
            reward: المكافأة المستلمة
            next_state: الحالة التالية
            done: هل انتهت الحلقة؟
        """
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Maximum Q-value for next state
        if done:
            max_next_q = 0  # no future reward if episode ended
        else:
            next_q_values = self.q_table[next_state_key]
            max_next_q = max(next_q_values.values()) if next_q_values else 0
        
        # Q-Learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        # Update Q-table
        self.q_table[state_key][action] = new_q
        
        self.total_updates += 1
    
    def decay_epsilon(self):
        """تقليل epsilon (تقليل الاستكشاف مع الوقت)"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def get_q_value(self, state: Dict, action: str) -> float:
        """
        الحصول على Q-value لحالة وإجراء معين
        
        Args:
            state: الحالة
            action: الإجراء
        
        Returns:
            Q-value
        """
        state_key = self.get_state_key(state)
        return self.q_table[state_key][action]
    
    def get_best_action_greedy(self, state: Dict, valid_actions: List[str] = None) -> str:
        """
        الحصول على أفضل إجراء (بدون استكشاف)
        للاستخدام في وضع Demo
        
        Args:
            state: الحالة
            valid_actions: الإجراءات الصالحة
        
        Returns:
            أفضل إجراء
        """
        if valid_actions is None:
            valid_actions = self.actions
        
        return self._get_best_action(state, valid_actions)
    
    def save(self, filepath: str = None):
        """
        حفظ Q-table
        
        Args:
            filepath: مسار الملف (أو None للمسار الافتراضي)
        """
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, 'q_table.pkl')
        
        data = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'episodes_trained': self.episodes_trained,
            'total_updates': self.total_updates
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        
        self.logger.info(f"Q-table saved to {filepath}")
    
    def load(self, filepath: str = None):
        """
        تحميل Q-table
        
        Args:
            filepath: مسار الملف
        """
        if filepath is None:
            filepath = os.path.join(MODELS_DIR, 'q_table.pkl')
        
        if not os.path.exists(filepath):
            self.logger.warning(f"Q-table file not found: {filepath}")
            return False
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        self.q_table = defaultdict(lambda: defaultdict(float), data['q_table'])
        self.epsilon = data.get('epsilon', self.epsilon_min)
        self.episodes_trained = data.get('episodes_trained', 0)
        self.total_updates = data.get('total_updates', 0)
        
        self.logger.info(f"Q-table loaded from {filepath}")
        return True
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات الوكيل"""
        return {
            'q_table_size': len(self.q_table),
            'total_updates': self.total_updates,
            'episodes_trained': self.episodes_trained,
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor
        }
    
    def reset_for_episode(self):
        """إعادة تعيين للحلقة الجديدة"""
        self.episodes_trained += 1
    
    def __repr__(self) -> str:
        return (f"QLearningAgent(states={len(self.q_table)}, "
                f"epsilon={self.epsilon:.3f}, episodes={self.episodes_trained})")