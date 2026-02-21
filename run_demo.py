#!/usr/bin/env python3
"""
Quick Demo Runner for Drone Delivery System
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import run_demo, setup_directories

if __name__ == "__main__":
    print("🚁 Autonomous Medical Drone Delivery - Quick Demo")
    print("=" * 50)
    
    # إعداد المجلدات
    setup_directories()
    
    # تشغيل العرض التوضيحي
    success = run_demo()
    
    if success:
        print("\n✅ Demo completed successfully!")
    else:
        print("\n❌ Demo failed. Please check the logs.")
        sys.exit(1)