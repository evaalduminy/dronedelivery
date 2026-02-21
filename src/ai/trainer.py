"""
Training Module for Hybrid Drone Controller
"""

import os
import time
import json
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

from .hybrid_controller import HybridController
from ..environment.city import CityEnvironment
from ..utils.config import (
    NUM_EPISODES, MODELS_DIR, DATA_DIR, 
    SAVE_INTERVAL, PLOT_INTERVAL
)
from ..utils.logger import get_logger
from ..utils.metrics import MetricsTracker


class DroneTrainer:
    """
    مدرب الطائرة المسيرة
    
    يدير عملية التدريب الكاملة:
    - تدريب المتحكم الهجين
    - تتبع الأداء
    - حفظ النماذج
    - إنشاء الرسوم البيانية
    """
    
    def __init__(self, config: Dict = None):
        """
        تهيئة المدرب
        
        Args:
            config: إعدادات التدريب (أو None للإعدادات الافتراضية)
        """
        self.config = config or {}
        
        # المكونات الأساسية
        self.env = CityEnvironment()
        self.controller = HybridController()
        self.metrics = MetricsTracker()
        
        # إعدادات التدريب
        self.num_episodes = self.config.get('num_episodes', NUM_EPISODES)
        self.save_interval = self.config.get('save_interval', SAVE_INTERVAL)
        self.plot_interval = self.config.get('plot_interval', PLOT_INTERVAL)
        
        # إحصائيات التدريب
        self.episode_rewards = []
        self.episode_steps = []
        self.success_rates = []
        self.safety_override_rates = []
        
        self.logger = get_logger()
        self.logger.info("Drone Trainer initialized")
    
    def train(self, resume: bool = False) -> Dict:
        """
        بدء عملية التدريب
        
        Args:
            resume: هل نستكمل التدريب من نموذج محفوظ؟
        
        Returns:
            إحصائيات التدريب النهائية
        """
        self.logger.info(f"Starting training for {self.num_episodes} episodes")
        
        # تحميل نموذج سابق إذا طُلب
        if resume:
            self.controller.load_models()
        
        # إعداد التتبع
        start_time = time.time()
        recent_rewards = []  # آخر 100 حلقة
        recent_successes = []  # آخر 100 حلقة
        
        try:
            for episode in range(self.num_episodes):
                episode_start = time.time()
                
                # تدريب حلقة واحدة
                episode_stats = self.controller.train_episode(self.env)
                
                # تسجيل الإحصائيات
                self.episode_rewards.append(episode_stats['total_reward'])
                self.episode_steps.append(episode_stats['steps'])
                
                recent_rewards.append(episode_stats['total_reward'])
                recent_successes.append(1 if episode_stats['success'] else 0)
                
                # الاحتفاظ بآخر 100 حلقة فقط
                if len(recent_rewards) > 100:
                    recent_rewards.pop(0)
                    recent_successes.pop(0)
                
                # حساب المعدلات
                avg_reward = np.mean(recent_rewards)
                success_rate = np.mean(recent_successes) * 100
                
                self.success_rates.append(success_rate)
                
                # إحصائيات المتحكم
                controller_stats = self.controller.get_statistics()
                safety_rate = controller_stats['hybrid_controller']['safety_override_rate'] * 100
                self.safety_override_rates.append(safety_rate)
                
                # طباعة التقدم
                if episode % 10 == 0 or episode == self.num_episodes - 1:
                    episode_time = time.time() - episode_start
                    self._print_progress(episode, episode_stats, avg_reward, 
                                       success_rate, safety_rate, episode_time)
                
                # حفظ النماذج
                if episode % self.save_interval == 0 and episode > 0:
                    self._save_checkpoint(episode)
                
                # إنشاء الرسوم البيانية
                if episode % self.plot_interval == 0 and episode > 0:
                    self._plot_training_progress(episode)
                
                # تسجيل المقاييس
                self.metrics.log_episode(
                    episode=episode,
                    reward=episode_stats['total_reward'],
                    steps=episode_stats['steps'],
                    success=episode_stats['success'],
                    safety_overrides=episode_stats['safety_overrides']
                )
        
        except KeyboardInterrupt:
            self.logger.info("Training interrupted by user")
        
        # إنهاء التدريب
        total_time = time.time() - start_time
        final_stats = self._finalize_training(total_time)
        
        return final_stats
    
    def _print_progress(self, episode: int, episode_stats: Dict, 
                       avg_reward: float, success_rate: float, 
                       safety_rate: float, episode_time: float):
        """طباعة تقدم التدريب"""
        print(f"\n📊 Episode {episode + 1}/{self.num_episodes}")
        print(f"   Reward: {episode_stats['total_reward']:.1f} | "
              f"Steps: {episode_stats['steps']} | "
              f"Success: {'✅' if episode_stats['success'] else '❌'}")
        print(f"   Avg Reward (100): {avg_reward:.1f} | "
              f"Success Rate: {success_rate:.1f}% | "
              f"Safety Rate: {safety_rate:.1f}%")
        print(f"   Epsilon: {self.controller.q_agent.epsilon:.3f} | "
              f"Time: {episode_time:.2f}s")
    
    def _save_checkpoint(self, episode: int):
        """حفظ نقطة تفتيش"""
        checkpoint_dir = os.path.join(MODELS_DIR, f"checkpoint_{episode}")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # حفظ النماذج
        q_table_path = os.path.join(checkpoint_dir, "q_table.pkl")
        self.controller.save_models(q_table_path)
        
        # حفظ إحصائيات التدريب
        stats_path = os.path.join(checkpoint_dir, "training_stats.json")
        stats = {
            'episode': episode,
            'episode_rewards': self.episode_rewards,
            'episode_steps': self.episode_steps,
            'success_rates': self.success_rates,
            'safety_override_rates': self.safety_override_rates
        }
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Checkpoint saved at episode {episode}")
    
    def _plot_training_progress(self, episode: int):
        """إنشاء رسوم بيانية للتقدم"""
        if len(self.episode_rewards) < 10:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Training Progress - Episode {episode + 1}', fontsize=16)
        
        # 1. المكافآت
        axes[0, 0].plot(self.episode_rewards, alpha=0.6, color='blue')
        if len(self.episode_rewards) >= 10:
            # متوسط متحرك
            window = min(50, len(self.episode_rewards) // 4)
            moving_avg = np.convolve(self.episode_rewards, 
                                   np.ones(window)/window, mode='valid')
            axes[0, 0].plot(range(window-1, len(self.episode_rewards)), 
                           moving_avg, color='red', linewidth=2)
        
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Total Reward')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. عدد الخطوات
        axes[0, 1].plot(self.episode_steps, alpha=0.6, color='green')
        axes[0, 1].set_title('Episode Steps')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Steps')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. معدل النجاح
        if len(self.success_rates) > 0:
            axes[1, 0].plot(self.success_rates, color='orange', linewidth=2)
            axes[1, 0].set_title('Success Rate (%)')
            axes[1, 0].set_xlabel('Episode')
            axes[1, 0].set_ylabel('Success Rate')
            axes[1, 0].set_ylim(0, 100)
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. معدل تدخل الأمان
        if len(self.safety_override_rates) > 0:
            axes[1, 1].plot(self.safety_override_rates, color='red', linewidth=2)
            axes[1, 1].set_title('Safety Override Rate (%)')
            axes[1, 1].set_xlabel('Episode')
            axes[1, 1].set_ylabel('Override Rate')
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # حفظ الرسم البياني
        plots_dir = os.path.join(DATA_DIR, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        plot_path = os.path.join(plots_dir, f'training_progress_{episode}.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Training plot saved: {plot_path}")
    
    def _finalize_training(self, total_time: float) -> Dict:
        """إنهاء التدريب وإنشاء التقرير النهائي"""
        
        # حفظ النماذج النهائية
        self.controller.save_models()
        
        # إنشاء الرسم البياني النهائي
        self._plot_training_progress(len(self.episode_rewards) - 1)
        
        # حساب الإحصائيات النهائية
        final_stats = {
            'training_completed': True,
            'total_episodes': len(self.episode_rewards),
            'total_time_minutes': total_time / 60,
            'average_reward': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0,
            'final_success_rate': self.success_rates[-1] if self.success_rates else 0,
            'final_safety_rate': self.safety_override_rates[-1] if self.safety_override_rates else 0,
            'controller_stats': self.controller.get_statistics()
        }
        
        # حفظ التقرير النهائي
        report_path = os.path.join(DATA_DIR, 'final_training_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_stats, f, indent=2, ensure_ascii=False)
        
        # طباعة التقرير النهائي
        self._print_final_report(final_stats)
        
        self.logger.info("Training completed successfully!")
        return final_stats
    
    def _print_final_report(self, stats: Dict):
        """طباعة التقرير النهائي"""
        print("\n" + "="*60)
        print("🎯 TRAINING COMPLETED!")
        print("="*60)
        print(f"📊 Total Episodes: {stats['total_episodes']}")
        print(f"⏱️  Total Time: {stats['total_time_minutes']:.1f} minutes")
        print(f"🏆 Final Success Rate: {stats['final_success_rate']:.1f}%")
        print(f"🛡️  Safety Override Rate: {stats['final_safety_rate']:.1f}%")
        print(f"💰 Average Reward (last 100): {stats['average_reward']:.1f}")
        
        controller_stats = stats['controller_stats']
        print(f"\n🧠 Q-Learning Stats:")
        print(f"   Q-Table Size: {controller_stats['q_learning']['q_table_size']}")
        print(f"   Total Updates: {controller_stats['q_learning']['total_updates']}")
        print(f"   Final Epsilon: {controller_stats['q_learning']['epsilon']:.3f}")
        
        print(f"\n⚖️  Logic Engine Stats:")
        print(f"   Total Rules: {controller_stats['logic_engine']['total_rules']}")
        print(f"   Safety Rules: {controller_stats['logic_engine']['rule_types']['safety']}")
        
        print(f"\n🔄 Hybrid Controller Stats:")
        print(f"   Total Decisions: {controller_stats['hybrid_controller']['decisions_made']}")
        print(f"   Safety Overrides: {controller_stats['hybrid_controller']['safety_overrides']}")
        print("="*60)
    
    def evaluate(self, num_episodes: int = 10) -> Dict:
        """
        تقييم النموذج المدرب
        
        Args:
            num_episodes: عدد حلقات التقييم
        
        Returns:
            نتائج التقييم
        """
        self.logger.info(f"Evaluating model for {num_episodes} episodes")
        
        # تحميل أفضل نموذج
        self.controller.load_models()
        
        results = []
        
        for episode in range(num_episodes):
            state = self.env.reset()
            total_reward = 0
            steps = 0
            
            while steps < 1000:  # حد أقصى للخطوات
                # استخدام الوضع الجشع (بدون استكشاف)
                action, decision_info = self.controller.choose_action(state, training=False)
                
                next_state, reward, done, info = self.env.step(action)
                
                total_reward += reward
                steps += 1
                state = next_state
                
                if done:
                    break
            
            results.append({
                'episode': episode,
                'reward': total_reward,
                'steps': steps,
                'success': info.get('success', False)
            })
        
        # حساب الإحصائيات
        eval_stats = {
            'num_episodes': num_episodes,
            'average_reward': np.mean([r['reward'] for r in results]),
            'success_rate': np.mean([r['success'] for r in results]) * 100,
            'average_steps': np.mean([r['steps'] for r in results]),
            'results': results
        }
        
        self.logger.info(f"Evaluation completed: {eval_stats['success_rate']:.1f}% success rate")
        return eval_stats


def main():
    """دالة رئيسية للتدريب"""
    trainer = DroneTrainer()
    
    # بدء التدريب
    final_stats = trainer.train()
    
    # تقييم النموذج
    eval_stats = trainer.evaluate()
    
    print(f"\n🎉 Training and evaluation completed!")
    print(f"Final success rate: {eval_stats['success_rate']:.1f}%")


if __name__ == "__main__":
    main()