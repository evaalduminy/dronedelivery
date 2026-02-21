#!/usr/bin/env python3
"""
Debug Test to Find the Indexing Issue
"""

import sys
import os
import traceback

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def debug_environment():
    """اختبار مفصل للبيئة"""
    print("🔍 Debug Environment Test...")
    
    try:
        from src.environment.city import CityEnvironment
        
        # إنشاء البيئة
        print("Creating environment...")
        env = CityEnvironment()
        print("✅ Environment created")
        
        # إعادة تعيين
        print("Resetting environment...")
        state = env.reset()
        print("✅ Environment reset")
        
        # طباعة معلومات الحالة
        print(f"State keys: {list(state.keys())}")
        print(f"Drone position: {env.drone.position}")
        print(f"Target position: {env.target_position}")
        
        # اختبار خطوة واحدة
        print("Testing step...")
        action = "move_forward"
        
        try:
            next_state, reward, done, info = env.step(action)
            print("✅ Step completed successfully")
        except Exception as e:
            print(f"❌ Step failed: {e}")
            print("Traceback:")
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_environment()