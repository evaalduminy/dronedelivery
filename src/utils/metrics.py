"""
Performance metrics tracking and analysis
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import deque
import csv
import os

from .config import METRICS_FILE_PATH


class MetricsTracker:
    """
    متتبع المقاييس والأداء
    يحسب ويخزن جميع مقاييس الأداء
    """
    
    def __init__(self):
        """تهيئة المتتبع"""
        # Episode metrics
        self.episode_rewards: List[float] = []
        self.episode_steps: List[int] = []
        self.episode_success: List[bool] = []
        self.episode_times: List[float] = []
        self.episode_battery_used: List[float] = []
        
        # Moving averages (last 100 episodes)
        self.recent_rewards = deque(maxlen=100)
        self.recent_success = deque(maxlen=100)
        self.recent_times = deque(maxlen=100)
        
        # Cumulative stats
        self.total_missions = 0
        self.successful_missions = 0
        self.failed_missions = 0
        self.total_violations = 0
        self.total_collisions = 0
        
        # Best performance
        self.best_reward = float('-inf')
        self.best_time = float('inf')
        self.best_episode = 0
        
        # CSV file for detailed logging
        self.csv_file = METRICS_FILE_PATH
        self._init_csv()
    
    def _init_csv(self):
        """تهيئة ملف CSV"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Episode', 'Success', 'Reward', 'Steps', 'Time', 
                    'Battery_Used', 'Violations', 'Collisions'
                ])
    
    def record_episode(self, episode: int, success: bool, reward: float, 
                      steps: int, time: float, battery_used: float,
                      violations: int = 0, collisions: int = 0):
        """تسجيل نتائج حلقة"""
        # Store in lists
        self.episode_rewards.append(reward)
        self.episode_steps.append(steps)
        self.episode_success.append(success)
        self.episode_times.append(time)
        self.episode_battery_used.append(battery_used)
        
        # Update moving averages
        self.recent_rewards.append(reward)
        self.recent_success.append(1 if success else 0)
        self.recent_times.append(time)
        
        # Update cumulative stats
        self.total_missions += 1
        if success:
            self.successful_missions += 1
        else:
            self.failed_missions += 1
        
        self.total_violations += violations
        self.total_collisions += collisions
        
        # Update best performance
        if reward > self.best_reward:
            self.best_reward = reward
            self.best_episode = episode
        
        if success and time < self.best_time:
            self.best_time = time
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                episode, success, reward, steps, time, 
                battery_used, violations, collisions
            ])
    
    def get_success_rate(self, recent: bool = False) -> float:
        """حساب معدل النجاح"""
        if recent and len(self.recent_success) > 0:
            return np.mean(self.recent_success)
        elif self.total_missions > 0:
            return self.successful_missions / self.total_missions
        return 0.0
    
    def get_average_reward(self, recent: bool = False) -> float:
        """حساب متوسط المكافأة"""
        if recent and len(self.recent_rewards) > 0:
            return np.mean(self.recent_rewards)
        elif len(self.episode_rewards) > 0:
            return np.mean(self.episode_rewards)
        return 0.0
    
    def get_average_time(self, recent: bool = False) -> float:
        """حساب متوسط الوقت"""
        if recent and len(self.recent_times) > 0:
            return np.mean(self.recent_times)
        elif len(self.episode_times) > 0:
            return np.mean(self.episode_times)
        return 0.0
    
    def get_average_battery_used(self) -> float:
        """حساب متوسط استهلاك البطارية"""
        if len(self.episode_battery_used) > 0:
            return np.mean(self.episode_battery_used)
        return 0.0
    
    def get_statistics(self) -> Dict:
        """الحصول على جميع الإحصائيات"""
        return {
            'total_missions': self.total_missions,
            'successful_missions': self.successful_missions,
            'failed_missions': self.failed_missions,
            'success_rate': self.get_success_rate(),
            'recent_success_rate': self.get_success_rate(recent=True),
            'average_reward': self.get_average_reward(),
            'recent_average_reward': self.get_average_reward(recent=True),
            'average_time': self.get_average_time(),
            'recent_average_time': self.get_average_time(recent=True),
            'average_battery_used': self.get_average_battery_used(),
            'best_reward': self.best_reward,
            'best_time': self.best_time,
            'best_episode': self.best_episode,
            'total_violations': self.total_violations,
            'total_collisions': self.total_collisions
        }
    
    def get_learning_curve(self, window_size: int = 100) -> Tuple[List, List]:
        """الحصول على منحنى التعلم (للرسم)"""
        if len(self.episode_rewards) < window_size:
            return list(range(len(self.episode_rewards))), self.episode_rewards
        
        # Moving average
        episodes = []
        smoothed_rewards = []
        
        for i in range(window_size, len(self.episode_rewards) + 1):
            episodes.append(i)
            smoothed_rewards.append(np.mean(self.episode_rewards[i-window_size:i]))
        
        return episodes, smoothed_rewards
    
    def get_success_rate_curve(self, window_size: int = 100) -> Tuple[List, List]:
        """الحصول على منحنى معدل النجاح"""
        if len(self.episode_success) < window_size:
            return list(range(len(self.episode_success))), [
                np.mean(self.episode_success[:i+1]) for i in range(len(self.episode_success))
            ]
        
        episodes = []
        success_rates = []
        
        for i in range(window_size, len(self.episode_success) + 1):
            episodes.append(i)
            success_rates.append(np.mean(self.episode_success[i-window_size:i]))
        
        return episodes, success_rates
    
    def calculate_score(self) -> float:
        """
        حساب النقاط الإجمالية
        Score = (success_rate * 0.3 + time_efficiency * 0.2 + 
                 battery_efficiency * 0.2 + safety * 0.3) * 100
        """
        if self.total_missions == 0:
            return 0.0
        
        # Success rate (0-1)
        success_rate = self.get_success_rate()
        
        # Time efficiency (0-1) - lower is better
        avg_time = self.get_average_time()
        time_efficiency = max(0, 1 - (avg_time / 1800))  # 30 min = 1800s
        
        # Battery efficiency (0-1) - lower usage is better
        avg_battery = self.get_average_battery_used()
        battery_efficiency = max(0, 1 - (avg_battery / 100))
        
        # Safety score (0-1)
        violation_rate = self.total_violations / self.total_missions
        collision_rate = self.total_collisions / self.total_missions
        safety_score = max(0, 1 - (violation_rate + collision_rate))
        
        # Weighted score
        score = (
            success_rate * 0.3 +
            time_efficiency * 0.2 +
            battery_efficiency * 0.2 +
            safety_score * 0.3
        ) * 100
        
        return score
    
    def print_summary(self):
        """طباعة ملخص الإحصائيات"""
        stats = self.get_statistics()
        score = self.calculate_score()
        
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Total Missions: {stats['total_missions']}")
        print(f"Successful: {stats['successful_missions']} ({stats['success_rate']:.1%})")
        print(f"Failed: {stats['failed_missions']}")
        print(f"Recent Success Rate: {stats['recent_success_rate']:.1%}")
        print("-"*60)
        print(f"Average Reward: {stats['average_reward']:.1f}")
        print(f"Recent Avg Reward: {stats['recent_average_reward']:.1f}")
        print(f"Best Reward: {stats['best_reward']:.1f} (Episode {stats['best_episode']})")
        print("-"*60)
        print(f"Average Time: {stats['average_time']:.1f}s")
        print(f"Best Time: {stats['best_time']:.1f}s")
        print(f"Average Battery Used: {stats['average_battery_used']:.1f}%")
        print("-"*60)
        print(f"Total Violations: {stats['total_violations']}")
        print(f"Total Collisions: {stats['total_collisions']}")
        print("-"*60)
        print(f"OVERALL SCORE: {score:.1f}/100")
        print("="*60 + "\n")
    
    def reset(self):
        """إعادة تعيين جميع المقاييس"""
        self.episode_rewards.clear()
        self.episode_steps.clear()
        self.episode_success.clear()
        self.episode_times.clear()
        self.episode_battery_used.clear()
        self.recent_rewards.clear()
        self.recent_success.clear()
        self.recent_times.clear()
        
        self.total_missions = 0
        self.successful_missions = 0
        self.failed_missions = 0
        self.total_violations = 0
        self.total_collisions = 0
        
        self.best_reward = float('-inf')
        self.best_time = float('inf')
        self.best_episode = 0
