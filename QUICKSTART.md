# 🚀 Quick Start Guide

## التثبيت السريع

### 1. المتطلبات
```bash
Python 3.10 أو أحدث
pip (مدير الحزم)
```

### 2. التثبيت
```bash
# انتقل إلى مجلد المشروع
cd drone_delivery

# ثبت المكتبات
pip install -r requirements.txt
```

### 3. اختبار البيئة
```bash
# اختبار سريع للتأكد من عمل كل شيء
python test_environment.py
```

---

## 📁 بنية المشروع

```
drone_delivery/
├── 📄 DESIGN_DOCUMENT.md    # التصميم الشامل
├── 📄 README.md             # دليل المشروع
├── 📄 PROJECT_STATUS.md     # حالة التقدم
├── 📄 QUICKSTART.md         # هذا الملف
│
├── 📁 src/                  # الكود المصدري
│   ├── environment/         # ✅ البيئة (مكتمل)
│   ├── ai/                  # 🔄 الذكاء الاصطناعي (قريباً)
│   ├── gui/                 # 🔄 الواجهة (قريباً)
│   └── utils/               # ✅ الأدوات (مكتمل)
│
└── 📁 data/                 # البيانات والنماذج
```

---

## 🎯 ما تم إنجازه حتى الآن

### ✅ البيئة الكاملة
- **المدينة**: شبكة 50x50 مع مباني بارتفاعات مختلفة
- **الطائرة**: فيزياء واقعية (بطارية، حركة، شحنة)
- **الطقس**: نظام ديناميكي (رياح، أمطار، عواصف)
- **العقبات**: مناطق حظر طيران، مستشفيات، مختبرات

### ✅ الأنظمة المساعدة
- **Logger**: تسجيل جميع الأحداث
- **Metrics**: تتبع الأداء
- **Config**: إعدادات قابلة للتخصيص

---

## 🧪 اختبار المكونات

### اختبار البيئة
```python
from environment import CityEnvironment

# إنشاء بيئة
env = CityEnvironment(grid_size=20, weather="clear")

# إعادة تعيين
state = env.reset()
print(f"Start: {state['position']}")
print(f"Target: {state['target']}")

# خطوة واحدة
state, reward, done, info = env.step('MOVE_NORTH')
print(f"Reward: {reward}, Done: {done}")
```

### اختبار الطائرة
```python
from environment import Drone

# إنشاء طائرة
drone = Drone(start_position=(10, 10, 3))

# حركة
drone.move('MOVE_NORTH')
print(f"Position: {drone.position}")
print(f"Battery: {drone.battery}%")

# معلومات القياس
telemetry = drone.get_telemetry()
print(telemetry)
```

### اختبار الطقس
```python
from environment import WeatherSystem

# إنشاء نظام طقس
weather = WeatherSystem("clear")

# تحديث
weather.update()
print(f"Condition: {weather.condition.value}")
print(f"Wind: {weather.wind_speed} km/h")
print(f"Safe to fly: {weather.is_safe_to_fly()}")
```

---

## 📊 مثال كامل

```python
import sys
import os
sys.path.insert(0, 'src')

from environment import CityEnvironment

# إنشاء البيئة
env = CityEnvironment(grid_size=20, weather="clear", seed=42)

# بدء مهمة
state = env.reset()
print(f"Mission #{env.mission_id} started!")
print(f"From: {state['position']} → To: {state['target']}")

# محاكاة 20 خطوة
for step in range(20):
    # اختيار إجراء عشوائي
    import random
    valid_actions = env.get_valid_actions()
    action = random.choice(valid_actions)
    
    # تنفيذ
    state, reward, done, info = env.step(action)
    
    print(f"Step {step+1}: {action:12s} | "
          f"Battery: {state['battery']:5.1f}% | "
          f"Distance: {state['distance_to_target']:4.1f} | "
          f"Reward: {reward:6.1f}")
    
    if done:
        print(f"\nMission ended: {info['mission_status']}")
        break

# معلومات البيئة
info = env.get_env_info()
print(f"\nEnvironment Info:")
print(f"  Buildings: {info['obstacles']['num_buildings']}")
print(f"  Weather: {info['weather']['condition']}")
```

---

## 🎮 الخطوات التالية

### للمطورين:
1. **تنفيذ Q-Learning** في `src/ai/q_learning.py`
2. **إنشاء Logic Engine** في `src/ai/logic_engine.py`
3. **بناء الواجهة** في `src/gui/`

### للمستخدمين:
1. انتظر اكتمال الواجهة الرسومية
2. ستتمكن من:
   - مشاهدة الطائرة تطير في 3D
   - رؤية قرارات الذكاء الاصطناعي
   - تتبع الأداء والإحصائيات

---

## 🐛 استكشاف الأخطاء

### المشكلة: ModuleNotFoundError
```bash
# الحل: تأكد من تثبيت المكتبات
pip install -r requirements.txt
```

### المشكلة: Import Error
```python
# الحل: أضف المسار
import sys
sys.path.insert(0, 'src')
```

### المشكلة: بطء التنفيذ
```python
# الحل: قلل حجم الشبكة
env = CityEnvironment(grid_size=20)  # بدلاً من 50
```

---

## 📚 موارد إضافية

- **DESIGN_DOCUMENT.md**: التصميم الكامل
- **PROJECT_STATUS.md**: حالة التقدم
- **README.md**: دليل شامل
- **Logs**: `data/logs/` لسجلات التشغيل

---

## 💬 أسئلة شائعة

**Q: كم يستغرق تدريب الوكيل؟**
A: حوالي 10,000 حلقة، قد يستغرق 1-2 ساعة حسب الجهاز.

**Q: هل يمكن تغيير حجم المدينة؟**
A: نعم، في `config.py` غير `GRID_SIZE`.

**Q: كيف أضيف خوارزمية جديدة؟**
A: أضف ملف في `src/ai/` واتبع نفس البنية.

**Q: هل يدعم GPU؟**
A: نعم، للـ DQN سيستخدم CUDA تلقائياً إن وجد.

---

## 🎯 الهدف النهائي

```
┌─────────────────────────────────────┐
│  🚁 Autonomous Drone Delivery       │
│                                     │
│  [3D City View]    [Control Panel]  │
│                                     │
│  • Learning in real-time            │
│  • Safety rules enforced            │
│  • Beautiful visualization          │
│  • Performance metrics              │
└─────────────────────────────────────┘
```

---

**Happy Coding! 🚀**
