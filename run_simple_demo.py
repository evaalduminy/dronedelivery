#!/usr/bin/env python3
"""
Simple Demo Runner (No GUI Dependencies)
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_simple_demo():
    """تشغيل عرض توضيحي بسيط بدون GUI"""
    print("🚁 Autonomous Medical Drone Delivery - Simple Demo")
    print("=" * 50)
    
    try:
        from src.ai.hybrid_controller import HybridController
        from src.environment.city import CityEnvironment
        
        # إنشاء البيئة والمتحكم
        env = CityEnvironment()
        controller = HybridController()
        
        print("🌍 Environment created with realistic city simulation")
        print("🧠 Hybrid AI controller initialized (Q-Learning + Logic Engine)")
        print("\n🎯 Starting autonomous missions...\n")
        
        # تشغيل عدة مهام
        total_missions = 3
        successful_missions = 0
        
        for mission in range(total_missions):
            print(f"🚀 Mission {mission + 1}/{total_missions}")
            print("-" * 30)
            
            # إعادة تعيين البيئة
            state = env.reset()
            total_reward = 0
            steps = 0
            
            # معلومات المهمة
            drone_pos = env.drone.position
            target_pos = env.target_position
            print(f"📍 Start: ({drone_pos[0]}, {drone_pos[1]}, {drone_pos[2]})")
            print(f"🎯 Target: ({target_pos[0]}, {target_pos[1]}, {target_pos[2]})")
            print(f"🔋 Battery: {state['battery']:.1f}%")
            print(f"🌤️  Weather: {state['weather']} (Safe: {state['safe_to_fly']})")
            
            # تنفيذ المهمة
            decision_log = []
            
            for step in range(200):  # حد أقصى 200 خطوة
                # اختيار إجراء (وضع demo - بدون استكشاف)
                action, decision_info = controller.choose_action(state, training=False)
                
                # تنفيذ الإجراء
                next_state, reward, done, info = env.step(action)
                
                total_reward += reward
                steps += 1
                
                # تسجيل القرار
                decision_log.append({
                    'step': step + 1,
                    'action': action,
                    'reward': reward,
                    'decision_type': decision_info['decision_type'],
                    'battery': state['battery'],
                    'position': state['position']
                })
                
                # طباعة معلومات كل 25 خطوة
                if (step + 1) % 25 == 0:
                    print(f"  Step {step + 1:3d}: {action:12s} | "
                          f"Reward: {reward:6.1f} | "
                          f"Battery: {state['battery']:5.1f}% | "
                          f"Type: {decision_info['decision_type']}")
                
                state = next_state
                
                if done:
                    break
            
            # نتيجة المهمة
            success = info.get('success', False)
            reason = info.get('reason', 'Unknown')
            
            if success:
                successful_missions += 1
                print(f"✅ SUCCESS: {reason}")
            else:
                print(f"❌ FAILED: {reason}")
            
            print(f"📊 Total Reward: {total_reward:.1f}")
            print(f"📊 Steps Taken: {steps}")
            print(f"📊 Final Battery: {next_state['battery']:.1f}%")
            
            # عرض آخر 5 قرارات
            print("🧠 Last 5 Decisions:")
            for decision in decision_log[-5:]:
                print(f"  Step {decision['step']:3d}: {decision['action']:12s} "
                      f"({decision['decision_type']}) -> Reward: {decision['reward']:6.1f}")
            
            print()
        
        # النتائج النهائية
        print("=" * 50)
        print("🎉 DEMO COMPLETED!")
        print(f"📊 Success Rate: {successful_missions}/{total_missions} "
              f"({successful_missions/total_missions*100:.1f}%)")
        
        # إحصائيات المتحكم
        stats = controller.get_statistics()
        print(f"🧠 AI Statistics:")
        print(f"   Total Decisions: {stats['hybrid_controller']['decisions_made']}")
        print(f"   Safety Overrides: {stats['hybrid_controller']['safety_overrides']}")
        print(f"   Q-Table Size: {stats['q_learning']['q_table_size']}")
        print(f"   Logic Rules: {stats['logic_engine']['total_rules']}")
        
        if successful_missions > 0:
            print("\n✨ The hybrid AI successfully demonstrated:")
            print("   🧠 Learning-based navigation (Q-Learning)")
            print("   ⚖️ Safety-critical rule enforcement")
            print("   🔄 Real-time decision making")
            print("   📊 Explainable AI decisions")
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # إعداد المجلدات
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    
    success = run_simple_demo()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Run training: python run_training.py")
        print("2. Install GUI deps: pip install pygame PyQt5")
        print("3. Run full GUI: python run_gui.py")
    else:
        sys.exit(1)