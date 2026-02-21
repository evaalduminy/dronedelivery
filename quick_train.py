#!/usr/bin/env python3
"""
Quick Training Session (No GUI Dependencies)
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def quick_training():
    """تدريب سريع للنظام"""
    print("🧠 Quick Training Session")
    print("=" * 30)
    
    try:
        from src.ai.hybrid_controller import HybridController
        from src.environment.city import CityEnvironment
        
        # إنشاء البيئة والمتحكم
        env = CityEnvironment()
        controller = HybridController()
        
        print("🌍 Environment and AI controller ready")
        print("🚀 Starting quick training (50 episodes)...\n")
        
        # إحصائيات التدريب
        episode_rewards = []
        success_count = 0
        
        for episode in range(50):
            # إعادة تعيين البيئة
            state = env.reset()
            total_reward = 0
            steps = 0
            
            # تشغيل الحلقة
            for step in range(100):  # حد أقصى 100 خطوة لكل حلقة
                # اختيار إجراء (وضع تدريب)
                action, decision_info = controller.choose_action(state, training=True)
                
                # تنفيذ الإجراء
                next_state, reward, done, info = env.step(action)
                
                # تحديث Q-Learning
                controller.update(state, action, reward, next_state, done)
                
                total_reward += reward
                steps += 1
                state = next_state
                
                if done:
                    break
            
            # تسجيل النتائج
            episode_rewards.append(total_reward)
            success = info.get('success', False)
            if success:
                success_count += 1
            
            # تقليل epsilon
            controller.q_agent.decay_epsilon()
            controller.q_agent.reset_for_episode()
            
            # طباعة التقدم كل 10 حلقات
            if (episode + 1) % 10 == 0:
                avg_reward = sum(episode_rewards[-10:]) / 10
                success_rate = success_count / (episode + 1) * 100
                epsilon = controller.q_agent.epsilon
                
                print(f"Episode {episode + 1:2d}: "
                      f"Avg Reward: {avg_reward:6.1f} | "
                      f"Success: {success_rate:4.1f}% | "
                      f"Epsilon: {epsilon:.3f}")
        
        # النتائج النهائية
        print("\n" + "=" * 50)
        print("🎉 TRAINING COMPLETED!")
        
        final_avg = sum(episode_rewards[-10:]) / 10
        final_success_rate = success_count / 50 * 100
        
        print(f"📊 Final Results:")
        print(f"   Average Reward (last 10): {final_avg:.1f}")
        print(f"   Success Rate: {success_count}/50 ({final_success_rate:.1f}%)")
        
        # إحصائيات المتحكم
        stats = controller.get_statistics()
        print(f"   Q-Table Size: {stats['q_learning']['q_table_size']}")
        print(f"   Total Updates: {stats['q_learning']['total_updates']}")
        print(f"   Final Epsilon: {stats['q_learning']['epsilon']:.3f}")
        
        # حفظ النموذج
        controller.save_models()
        print("💾 Model saved successfully!")
        
        if final_success_rate > 20:
            print("\n✅ Training successful! The agent learned to navigate.")
            print("🎯 You can now run the demo to see the trained agent.")
        else:
            print("\n⚠️ Training needs more episodes for better performance.")
            print("🔄 Consider running more training episodes.")
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Training interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # إعداد المجلدات
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    
    success = quick_training()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Run demo: python run_simple_demo.py")
        print("2. More training: python run_training.py")
        print("3. GUI interface: python run_gui.py (after installing PyQt5)")
    else:
        sys.exit(1)