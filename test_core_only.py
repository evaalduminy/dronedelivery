#!/usr/bin/env python3
"""
Core System Test (No GUI Dependencies)
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_core_imports():
    """اختبار استيراد المكونات الأساسية"""
    print("🔍 Testing core imports...")
    
    try:
        # اختبار البيئة
        from src.environment.city import CityEnvironment
        from src.environment.drone import Drone
        from src.environment.obstacles import CityObstacles
        from src.environment.weather import WeatherSystem
        print("   ✅ Environment modules imported")
        
        # اختبار الذكاء الاصطناعي
        from src.ai.q_learning import QLearningAgent
        from src.ai.logic_engine import LogicEngine
        from src.ai.hybrid_controller import HybridController
        from src.ai.trainer import DroneTrainer
        print("   ✅ AI modules imported")
        
        # اختبار الأدوات
        from src.utils.config import ACTIONS
        from src.utils.logger import get_logger
        from src.utils.metrics import MetricsTracker
        print("   ✅ Utility modules imported")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_environment():
    """اختبار البيئة"""
    print("\n🌍 Testing environment...")
    
    try:
        from src.environment.city import CityEnvironment
        
        # إنشاء البيئة
        env = CityEnvironment()
        print(f"   ✅ Environment created with {len(env.obstacles.buildings)} buildings")
        
        # إعادة تعيين
        state = env.reset()
        print(f"   ✅ Environment reset: {len(state)} state variables")
        
        # اختبار خطوة
        action = "move_forward"
        next_state, reward, done, info = env.step(action)
        print(f"   ✅ Step executed: reward={reward:.2f}, done={done}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Environment test failed: {e}")
        return False


def test_ai_system():
    """اختبار نظام الذكاء الاصطناعي"""
    print("\n🧠 Testing AI system...")
    
    try:
        from src.ai.hybrid_controller import HybridController
        from src.environment.city import CityEnvironment
        
        # إنشاء البيئة والمتحكم
        env = CityEnvironment()
        controller = HybridController()
        
        # إعادة تعيين البيئة
        state = env.reset()
        
        # اختبار اتخاذ القرار
        action, decision_info = controller.choose_action(state)
        print(f"   ✅ Decision made: {action} ({decision_info['decision_type']})")
        
        # اختبار تنفيذ الإجراء
        next_state, reward, done, info = env.step(action)
        print(f"   ✅ Action executed: reward={reward:.2f}")
        
        # اختبار تحديث Q-Learning
        controller.update(state, action, reward, next_state, done)
        print("   ✅ Q-Learning update completed")
        
        # اختبار الإحصائيات
        stats = controller.get_statistics()
        print(f"   ✅ Statistics: {stats['hybrid_controller']['decisions_made']} decisions made")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AI system test failed: {e}")
        return False


def test_logic_engine():
    """اختبار محرك المنطق"""
    print("\n⚖️ Testing logic engine...")
    
    try:
        from src.ai.logic_engine import LogicEngine
        from src.utils.config import ACTIONS
        
        # إنشاء محرك المنطق
        logic_engine = LogicEngine()
        rules_count = len(logic_engine.rules)
        print(f"   ✅ Logic engine created with {rules_count} rules")
        
        # حالة اختبار
        test_state = {
            'battery': 15,  # بطارية منخفضة
            'position': [50, 50, 20],
            'has_cargo': False,
            'safe_to_fly': True,
            'in_no_fly_zone': False,
            'nearby_obstacles': 0,
            'at_pickup_location': False,
            'at_delivery_location': False,
            'weather': {'wind_speed': 10},
            'relative_target': [10, 10, 0]
        }
        
        # اختبار تقييم القواعد
        triggered_rules = logic_engine.get_triggered_rules(test_state)
        print(f"   ✅ Rules evaluation: {len(triggered_rules)} rules triggered")
        
        # اختبار الإجراءات الآمنة
        safe_actions = logic_engine.get_valid_actions(test_state, ACTIONS)
        print(f"   ✅ Safety check: {len(safe_actions)}/{len(ACTIONS)} actions safe")
        
        # اختبار التوصية
        recommended_action, top_rule = logic_engine.get_recommended_action(test_state)
        print(f"   ✅ Recommendation: {recommended_action} (rule: {top_rule.name if top_rule else 'None'})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Logic engine test failed: {e}")
        return False


def test_q_learning():
    """اختبار Q-Learning"""
    print("\n🎯 Testing Q-Learning...")
    
    try:
        from src.ai.q_learning import QLearningAgent
        from src.utils.config import ACTIONS
        
        # إنشاء الوكيل
        agent = QLearningAgent(ACTIONS)
        print("   ✅ Q-Learning agent created")
        
        # حالة اختبار
        test_state = {
            'battery': 80,
            'position': [50, 50, 20],
            'has_cargo': False,
            'safe_to_fly': True,
            'in_no_fly_zone': False,
            'nearby_obstacles': 0,
            'at_pickup_location': False,
            'at_delivery_location': False,
            'weather': {'wind_speed': 10},
            'relative_target': [10, 10, 0]
        }
        
        # اختبار اختيار الإجراء
        action = agent.choose_action(test_state)
        print(f"   ✅ Action chosen: {action}")
        
        # اختبار التحديث
        agent.update(test_state, action, 1.0, test_state, False)
        print("   ✅ Q-table updated")
        
        # اختبار الإحصائيات
        stats = agent.get_statistics()
        print(f"   ✅ Statistics: {stats['total_updates']} updates, epsilon={stats['epsilon']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Q-Learning test failed: {e}")
        return False


def test_mini_episode():
    """اختبار حلقة مصغرة"""
    print("\n🚀 Testing mini episode...")
    
    try:
        from src.ai.hybrid_controller import HybridController
        from src.environment.city import CityEnvironment
        
        # إنشاء المكونات
        env = CityEnvironment()
        controller = HybridController()
        
        # تشغيل حلقة قصيرة
        state = env.reset()
        total_reward = 0
        steps = 0
        
        for step in range(20):  # 20 خطوة فقط
            # اختيار إجراء
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
        
        print(f"   ✅ Mini episode completed: {steps} steps, reward={total_reward:.2f}")
        
        # إحصائيات المتحكم
        stats = controller.get_statistics()
        print(f"   ✅ Controller stats: {stats['hybrid_controller']['decisions_made']} decisions")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Mini episode test failed: {e}")
        return False


def main():
    """الدالة الرئيسية للاختبار"""
    print("🚁 Drone Delivery System - Core Components Test")
    print("=" * 55)
    
    # إعداد المجلدات
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    
    # تشغيل الاختبارات
    tests = [
        ("Core Imports", test_core_imports),
        ("Environment", test_environment),
        ("AI System", test_ai_system),
        ("Logic Engine", test_logic_engine),
        ("Q-Learning", test_q_learning),
        ("Mini Episode", test_mini_episode)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    # النتيجة النهائية
    print("\n" + "="*55)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CORE TESTS PASSED! System is working correctly.")
        print("\nNext steps:")
        print("1. Install GUI dependencies: pip install pygame PyQt5")
        print("2. Run full system test: python quick_test_complete.py")
        print("3. Start training: python run_training.py")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())