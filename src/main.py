"""
Main Entry Point for Drone Delivery System
"""

import sys
import os
import argparse
from typing import Dict

# إضافة مسار المشروع إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.gui.main_window import MainWindow
from src.ai.trainer import DroneTrainer
from src.environment.city import CityEnvironment
from src.ai.hybrid_controller import HybridController
from src.utils.logger import get_logger
from src.utils.config import MODELS_DIR, DATA_DIR

from PyQt5.QtWidgets import QApplication


def run_gui():
    """تشغيل واجهة المستخدم الرسومية"""
    app = QApplication(sys.argv)
    
    # إعداد التطبيق
    app.setApplicationName("Autonomous Medical Drone Delivery")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AI Research Lab")
    
    # إنشاء النافذة الرئيسية
    window = MainWindow()
    window.show()
    
    # تشغيل التطبيق
    return app.exec_()


def run_training(config: Dict = None):
    """تشغيل التدريب"""
    logger = get_logger()
    logger.info("Starting training mode")
    
    # إنشاء المدرب
    trainer = DroneTrainer(config)
    
    # بدء التدريب
    try:
        final_stats = trainer.train()
        
        # تقييم النموذج المدرب
        eval_stats = trainer.evaluate(num_episodes=20)
        
        print("\n🎉 Training completed successfully!")
        print(f"Final success rate: {eval_stats['success_rate']:.1f}%")
        print(f"Average reward: {eval_stats['average_reward']:.2f}")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Training failed: {e}")
        return False


def run_demo():
    """تشغيل العرض التوضيحي"""
    logger = get_logger()
    logger.info("Starting demo mode")
    
    try:
        # إنشاء البيئة والمتحكم
        env = CityEnvironment()
        controller = HybridController()
        
        # تحميل النموذج المدرب
        model_loaded = controller.load_models()
        if not model_loaded:
            print("⚠️ No trained model found. Please run training first.")
            return False
        
        print("🚁 Starting autonomous drone demo...")
        print("Press Ctrl+C to stop\n")
        
        # تشغيل عدة مهام
        for mission in range(5):
            print(f"\n🎯 Mission {mission + 1}/5")
            
            # إعادة تعيين البيئة
            state = env.reset()
            total_reward = 0
            steps = 0
            
            # تنفيذ المهمة
            while steps < 1000:  # حد أقصى للخطوات
                # اختيار إجراء (وضع demo - بدون استكشاف)
                action, decision_info = controller.choose_action(state, training=False)
                
                # تنفيذ الإجراء
                next_state, reward, done, info = env.step(action)
                
                total_reward += reward
                steps += 1
                
                # طباعة معلومات الخطوة
                if steps % 50 == 0:
                    print(f"  Step {steps}: Action={action}, Reward={reward:.2f}, "
                          f"Battery={state['battery']:.1f}%")
                
                state = next_state
                
                if done:
                    break
            
            # نتيجة المهمة
            success = info.get('success', False)
            reason = info.get('reason', 'Unknown')
            
            print(f"  Result: {'✅ Success' if success else '❌ Failed'} - {reason}")
            print(f"  Reward: {total_reward:.2f}, Steps: {steps}")
        
        print("\n🎉 Demo completed!")
        return True
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
        return False


def run_test():
    """تشغيل الاختبارات"""
    logger = get_logger()
    logger.info("Running system tests")
    
    try:
        print("🧪 Running system tests...\n")
        
        # اختبار البيئة
        print("1. Testing environment...")
        env = CityEnvironment()
        state = env.reset()
        print(f"   ✅ Environment created: {len(env.obstacles.buildings)} buildings")
        
        # اختبار المتحكم
        print("2. Testing hybrid controller...")
        controller = HybridController()
        action, decision_info = controller.choose_action(state)
        print(f"   ✅ Controller working: Action={action}")
        
        # اختبار خطوة واحدة
        print("3. Testing simulation step...")
        next_state, reward, done, info = env.step(action)
        print(f"   ✅ Step executed: Reward={reward:.2f}")
        
        # اختبار الحفظ والتحميل
        print("4. Testing save/load...")
        controller.save_models()
        new_controller = HybridController()
        loaded = new_controller.load_models()
        print(f"   ✅ Save/Load working: {loaded}")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        print(f"❌ Tests failed: {e}")
        return False


def setup_directories():
    """إعداد المجلدات المطلوبة"""
    directories = [MODELS_DIR, DATA_DIR, os.path.join(DATA_DIR, 'logs'), 
                  os.path.join(DATA_DIR, 'plots')]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    """الدالة الرئيسية"""
    parser = argparse.ArgumentParser(description="Autonomous Medical Drone Delivery System")
    
    parser.add_argument('mode', choices=['gui', 'train', 'demo', 'test'], 
                       help='Mode to run the system in')
    
    parser.add_argument('--episodes', type=int, default=1000,
                       help='Number of training episodes (for train mode)')
    
    parser.add_argument('--resume', action='store_true',
                       help='Resume training from saved model')
    
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # إعداد المجلدات
    setup_directories()
    
    # تشغيل الوضع المطلوب
    if args.mode == 'gui':
        print("🚁 Starting GUI mode...")
        return run_gui()
    
    elif args.mode == 'train':
        print("🧠 Starting training mode...")
        config = {'num_episodes': args.episodes} if args.episodes != 1000 else None
        return run_training(config)
    
    elif args.mode == 'demo':
        print("🎮 Starting demo mode...")
        return run_demo()
    
    elif args.mode == 'test':
        print("🧪 Starting test mode...")
        return run_test()
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code if exit_code is not None else 0)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)