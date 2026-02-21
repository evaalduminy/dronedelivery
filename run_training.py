#!/usr/bin/env python3
"""
Quick Training Runner for Drone Delivery System
"""

import sys
import os

# إضافة مسار المشروع
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.main import run_training, setup_directories

if __name__ == "__main__":
    print("🧠 Autonomous Medical Drone Delivery - Training Mode")
    print("=" * 50)
    
    # إعداد المجلدات
    setup_directories()
    
    # إعدادات التدريب
    config = {
        'num_episodes': 500,  # عدد أقل للاختبار السريع
        'save_interval': 50,
        'plot_interval': 100
    }
    
    print(f"Training for {config['num_episodes']} episodes...")
    print("Press Ctrl+C to stop training early\n")
    
    # تشغيل التدريب
    success = run_training(config)
    
    if success:
        print("\n✅ Training completed successfully!")
        print("You can now run the demo or GUI to see the trained agent.")
    else:
        print("\n❌ Training failed or was interrupted.")
        sys.exit(1)