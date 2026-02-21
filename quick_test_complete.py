#!/usr/bin/env python3
"""
Quick Test for Complete Drone Delivery System
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """اختبار استيراد جميع المكونات"""
    print("🔍 Testing imports...")
    
    try:
        # اختبار البيئة
        from src.environment.city import CityEnvironment
        from src.environment.drone import Drone
        from src.environment.obstacles import ObstacleManager
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
        
        # اختبار واجهة المستخدم (اختياري)
        try:
            from src.gui.main_window import MainWindow
            from src.gui.map_view import MapView
            from src.gui.control_panel import ControlPanel
            print("   ✅ GUI modules imported")
        except ImportError as e:
            print(f"   ⚠️ GUI modules not available: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_basic_functionality():
    """اختبار الوظائف الأساسية"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # إنشاء البيئة
        from src.environment.city import CityEnvironment
        env = CityEnvironment()
        print("   ✅ Environment created")
        
        # إعادة تعيين البيئة
        state = env.reset()
        print(f"   ✅ Environment reset: {len(state)} state variables")
        
        # إنشاء المتحكم الهجين
        from src.ai.hybrid_controller import HybridController
        controller = HybridController()
        print("   ✅ Hybrid controller created")
        
        # اختبار اتخاذ القرار
        action, decision_info = controller.choose_action(state)
        print(f"   ✅ Decision made: {action} ({decision_info['decision_type']})")
        
        # اختبار خطوة المحاكاة
        next_state, reward, done, info = env.step(action)
        print(f"   ✅ Simulation step: reward={reward:.2f}, done={done}")
        
        # اختبار تحديث Q-Learning
        controller.update(state, action, reward, next_state, done)
        print("   ✅ Q-Learning update completed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False


def test_ai_components():
    """اختبار مكونات الذكاء الاصطناعي"""
    print("\n🧠 Testing AI components...")
    
    try:
        from src.ai.q_learning import QLearningAgent
        from src.ai.logic_engine import LogicEngine
        from src.utils.config import ACTIONS
        
        # اختبار Q-Learning
        q_agent = QLearningAgent(ACTIONS)
        print("   ✅ Q-Learning agent created")
        
        # اختبار Logic Engine
        logic_engine = LogicEngine()
        rules_count = len(logic_engine.rules)
        print(f"   ✅ Logic engine created with {rules_count} rules")
        
        # اختبار تقييم القواعد
        dummy_state = {
            'battery': 50,
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
        
        triggered_rules = logic_engine.get_triggered_rules(dummy_state)
        print(f"   ✅ Rules evaluation: {len(triggered_rules)} rules triggered")
        
        # اختبار الإجراءات الآمنة
        safe_actions = logic_engine.get_valid_actions(dummy_state, ACTIONS)
        print(f"   ✅ Safety check: {len(safe_actions)}/{len(ACTIONS)} actions safe")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AI components test failed: {e}")
        return False


def test_training_setup():
    """اختبار إعداد التدريب"""
    print("\n🏋️ Testing training setup...")
    
    try:
        from src.ai.trainer import DroneTrainer
        
        # إنشاء المدرب
        trainer = DroneTrainer({'num_episodes': 5})  # عدد قليل للاختبار
        print("   ✅ Trainer created")
        
        # اختبار حفظ وتحميل النماذج
        trainer.controller.save_models()
        print("   ✅ Model saving works")
        
        loaded = trainer.controller.load_models()
        print(f"   ✅ Model loading works: {loaded}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Training setup test failed: {e}")
        return False


def test_mini_training():
    """اختبار تدريب مصغر"""
    print("\n🚀 Running mini training session...")
    
    try:
        from src.ai.trainer import DroneTrainer
        
        # تدريب قصير جداً
        config = {
            'num_episodes': 3,
            'save_interval': 999,  # لا نريد حفظ
            'plot_interval': 999   # لا نريد رسوم بيانية
        }
        
        trainer = DroneTrainer(config)
        
        # تشغيل حلقات قليلة
        total_reward = 0
        for episode in range(3):
            episode_stats = trainer.controller.train_episode(trainer.env, max_steps=50)
            total_reward += episode_stats['total_reward']
            print(f"   Episode {episode + 1}: reward={episode_stats['total_reward']:.2f}, "
                  f"steps={episode_stats['steps']}, success={episode_stats['success']}")
        
        print(f"   ✅ Mini training completed: avg reward={total_reward/3:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Mini training failed: {e}")
        return False


def main():
    """الدالة الرئيسية للاختبار"""
    print("🚁 Autonomous Medical Drone Delivery - Complete System Test")
    print("=" * 60)
    
    # إعداد المجلدات
    from src.main import setup_directories
    setup_directories()
    
    # تشغيل الاختبارات
    tests = [
        ("Import Test", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("AI Components", test_ai_components),
        ("Training Setup", test_training_setup),
        ("Mini Training", test_mini_training)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    # النتيجة النهائية
    print("\n" + "="*60)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python run_training.py' to train the agent")
        print("2. Run 'python run_demo.py' to see the trained agent")
        print("3. Run 'python run_gui.py' for the graphical interface")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())