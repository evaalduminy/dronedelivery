#!/usr/bin/env python3
"""
Test Script for AI Components
اختبار مكونات الذكاء الاصطناعي
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد مباشر لتجنب مشاكل الاستيراد
from src.ai.q_learning import QLearningAgent
from src.ai.logic_engine import LogicEngine
from src.ai.hybrid_controller import HybridController
from src.environment.city import CityEnvironment
from src.utils.config import ACTIONS


def test_q_learning():
    """اختبار Q-Learning Agent"""
    print("🧠 Testing Q-Learning Agent...")
    
    agent = QLearningAgent(ACTIONS)
    
    # إنشاء حالة تجريبية
    test_state = {
        'position': [50, 50, 30],
        'relative_target': [10, -5, 0],
        'battery': 75,
        'has_cargo': False,
        'safe_to_fly': True,
        'nearby_obstacles': 0,
        'in_no_fly_zone': False,
        'weather': {'wind_speed': 5}
    }
    
    # اختبار اختيار الإجراء
    action = agent.choose_action(test_state)
    print(f"   ✓ Action chosen: {action}")
    
    # اختبار التحديث
    next_state = test_state.copy()
    next_state['position'] = [55, 50, 30]
    agent.update(test_state, action, 10.0, next_state, False)
    print(f"   ✓ Q-table updated")
    
    # اختبار الإحصائيات
    stats = agent.get_statistics()
    print(f"   ✓ Statistics: {stats}")
    
    print("   ✅ Q-Learning Agent test passed!\n")


def test_logic_engine():
    """اختبار Logic Engine"""
    print("⚖️  Testing Logic Engine...")
    
    engine = LogicEngine()
    
    # حالة آمنة
    safe_state = {
        'position': [50, 50, 30],
        'battery': 80,
        'has_cargo': False,
        'safe_to_fly': True,
        'nearby_obstacles': 0,
        'in_no_fly_zone': False,
        'at_pickup_location': False,
        'at_delivery_location': False,
        'weather': {'wind_speed': 5}
    }
    
    triggered_rules = engine.get_triggered_rules(safe_state)
    print(f"   ✓ Triggered rules (safe): {len(triggered_rules)}")
    
    # حالة خطيرة
    dangerous_state = safe_state.copy()
    dangerous_state['battery'] = 15  # بطارية منخفضة
    dangerous_state['safe_to_fly'] = False  # طقس سيء
    
    triggered_rules = engine.get_triggered_rules(dangerous_state)
    print(f"   ✓ Triggered rules (dangerous): {len(triggered_rules)}")
    
    # اختبار الإجراءات الآمنة
    safe_actions = engine.get_valid_actions(dangerous_state, ACTIONS)
    print(f"   ✓ Safe actions in danger: {safe_actions}")
    
    # اختبار التوصية
    action, rule = engine.get_recommended_action(dangerous_state)
    print(f"   ✓ Recommended action: {action} (rule: {rule.name if rule else None})")
    
    print("   ✅ Logic Engine test passed!\n")


def test_hybrid_controller():
    """اختبار Hybrid Controller"""
    print("🔄 Testing Hybrid Controller...")
    
    controller = HybridController()
    
    # حالة تجريبية
    test_state = {
        'position': [50, 50, 30],
        'relative_target': [10, -5, 0],
        'battery': 60,
        'has_cargo': False,
        'safe_to_fly': True,
        'nearby_obstacles': 1,
        'in_no_fly_zone': False,
        'at_pickup_location': False,
        'at_delivery_location': False,
        'weather': {'wind_speed': 10}
    }
    
    # اختبار اتخاذ القرار
    action, decision_info = controller.choose_action(test_state, training=True)
    print(f"   ✓ Action chosen: {action}")
    print(f"   ✓ Decision type: {decision_info['decision_type']}")
    print(f"   ✓ Safety override: {decision_info['safety_override']}")
    
    # اختبار التحليل
    analysis = controller.get_state_analysis(test_state)
    print(f"   ✓ Logic rules triggered: {len(analysis['logic_analysis']['triggered_rules'])}")
    print(f"   ✓ Safe actions: {len(analysis['logic_analysis']['safe_actions'])}")
    
    # اختبار التحديث
    next_state = test_state.copy()
    next_state['position'] = [55, 45, 30]
    controller.update(test_state, action, 5.0, next_state, False)
    print(f"   ✓ Controller updated")
    
    # اختبار الإحصائيات
    stats = controller.get_statistics()
    print(f"   ✓ Decisions made: {stats['hybrid_controller']['decisions_made']}")
    
    print("   ✅ Hybrid Controller test passed!\n")


def test_integration():
    """اختبار التكامل مع البيئة"""
    print("🌍 Testing Integration with Environment...")
    
    env = CityEnvironment()
    controller = HybridController()
    
    # إعادة تعيين البيئة
    state = env.reset()
    print(f"   ✓ Environment reset")
    print(f"   ✓ Initial state keys: {list(state.keys())}")
    
    # تشغيل بضع خطوات
    total_reward = 0
    for step in range(5):
        action, decision_info = controller.choose_action(state, training=True)
        next_state, reward, done, info = env.step(action)
        
        controller.update(state, action, reward, next_state, done)
        
        total_reward += reward
        state = next_state
        
        print(f"   Step {step + 1}: {action} -> reward: {reward:.1f}")
        
        if done:
            break
    
    print(f"   ✓ Total reward: {total_reward:.1f}")
    print("   ✅ Integration test passed!\n")


def main():
    """تشغيل جميع الاختبارات"""
    print("🧪 Testing AI Components for Drone Delivery")
    print("=" * 50)
    
    try:
        test_q_learning()
        test_logic_engine()
        test_hybrid_controller()
        test_integration()
        
        print("🎉 All AI tests passed successfully!")
        print("\n📋 Next Steps:")
        print("   1. Run training: python -m src.ai.trainer")
        print("   2. Create GUI components")
        print("   3. Build main application")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)