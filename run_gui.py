#!/usr/bin/env python3
"""
Quick GUI Runner for Drone Delivery System
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import run_gui, setup_directories

if __name__ == "__main__":
    print("Autonomous Medical Drone Delivery - GUI Mode")
    print("=" * 50)
    
    # إعداد المجلدات
    setup_directories()
    
    print("Starting graphical user interface...")
    print("Close the window to exit.\n")
    
    # تشغيل واجهة المستخدم
    exit_code = run_gui()
    
    print("GUI closed.")
    sys.exit(exit_code)