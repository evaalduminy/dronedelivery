"""
Configuration file for the Autonomous Drone Delivery System
Contains all system parameters and settings
"""

# ═══════════════════════════════════════════════════════════
# ENVIRONMENT CONFIGURATION
# ═══════════════════════════════════════════════════════════

# City Grid Settings
GRID_SIZE = 50  # 50x50 grid
CELL_SIZE = 100  # meters per cell
MAX_ALTITUDE = 12  # altitude levels (0-11)
ALTITUDE_STEP = 20  # meters per level

# Building Configuration
MIN_BUILDING_HEIGHT = 2  # levels
MAX_BUILDING_HEIGHT = 8  # levels
BUILDING_DENSITY = 0.15  # 15% of cells have buildings (Wider streets)

# Special Zones
NUM_HOSPITALS = 3
NUM_LABS = 3
NUM_CHARGING_STATIONS = 5
NUM_NO_FLY_ZONES = 4

# ═══════════════════════════════════════════════════════════
# DRONE CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Physical Specifications
MAX_SPEED = 60  # km/h
BATTERY_CAPACITY = 5000  # mAh
ENERGY_PER_KM = 50  # mAh per km
ENERGY_PER_ALTITUDE = 10  # mAh per altitude level change
CARGO_MAX_WEIGHT = 2.0  # kg

# Flight Parameters
HOVER_ENERGY = 5  # mAh per step
CHARGING_RATE = 500  # mAh per step
MIN_SAFE_BATTERY = 15  # % minimum battery to continue
CRITICAL_BATTERY = 5  # % battery for emergency landing

# ═══════════════════════════════════════════════════════════
# AI CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Q-Learning Parameters
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.95
EPSILON_START = 1.0
EPSILON_END = 0.01
EPSILON_DECAY = 0.995

# Training Settings
NUM_EPISODES = 10000
MAX_STEPS_PER_EPISODE = 1000
BATCH_SIZE = 32  # for DQN
MEMORY_SIZE = 10000  # replay buffer size

# Action Space
ACTIONS = [
    'MOVE_NORTH',
    'MOVE_SOUTH',
    'MOVE_EAST',
    'MOVE_WEST',
    'MOVE_UP',
    'MOVE_DOWN',
    'HOVER',
    'CHARGE'
]

# Reward Values
REWARD_DELIVERY_SUCCESS = 1000
REWARD_FAST_DELIVERY_BONUS = 100
REWARD_BATTERY_EFFICIENT = 50
REWARD_COLLISION = -500
REWARD_BATTERY_DEPLETED = -300
REWARD_NO_FLY_VIOLATION = -1000
REWARD_NO_FLY_INTERCEPTION = -800  # إسقاط أمني
REWARD_STORM_CRASH = -600  # تحطم بسبب العاصفة
REWARD_PAYLOAD_SPOILED = -400  # فساد العينة
REWARD_TIME_PENALTY = -1
REWARD_CHARGING = -50

# ═══════════════════════════════════════════════════════════
# LOGIC RULES CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Safety Thresholds
MUST_CHARGE_THRESHOLD = 15  # % battery
CANNOT_FLY_THRESHOLD = 5  # % battery
MIN_BUILDING_CLEARANCE = 50  # meters above building

# Weather Constraints
MAX_WIND_SPEED = 40  # km/h
FORBIDDEN_WEATHER = ['storm', 'heavy_rain', 'thunderstorm']
STORM_DAMAGE_THRESHOLD = 2  # steps in storm before crash
EXTREME_WIND_SPEED = 50  # km/h - instant crash

# Medical Payload Constraints
PAYLOAD_MAX_TIME = 1800  # seconds (30 minutes) - blood sample shelf life
PAYLOAD_SPOILAGE_WARNING = 1200  # seconds (20 minutes) - warning threshold

# Priority Levels
PRIORITY_LEVELS = {
    'urgent_medical': 10,
    'regular_medical': 5,
    'battery_saving': 3,
    'safety': 100  # highest priority
}

# ═══════════════════════════════════════════════════════════
# VISUALIZATION CONFIGURATION
# ═══════════════════════════════════════════════════════════

# Window Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60

# 3D View Settings
MAP_VIEW_WIDTH = 900
MAP_VIEW_HEIGHT = 900
CAMERA_DISTANCE = 1000
CAMERA_ANGLE = 45

# Control Panel Settings
PANEL_WIDTH = 500
PANEL_BG_COLOR = (30, 30, 40)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 150, 255)

# Colors (RGB)
COLOR_SKY = (135, 206, 235)
COLOR_GROUND = (34, 139, 34)
COLOR_BUILDING = (128, 128, 128)
COLOR_HOSPITAL = (255, 0, 0)
COLOR_LAB = (0, 255, 0)
COLOR_CHARGING = (255, 255, 0)
COLOR_NO_FLY = (255, 0, 0, 100)  # with alpha
COLOR_PATH = (255, 165, 0)

# Drone Colors (Visual States)
COLOR_DRONE_EMPTY = (0, 100, 255)      # 🔵 Blue - فارغة
COLOR_DRONE_LOADED = (255, 140, 0)     # 🟠 Orange - محملة
COLOR_DRONE_CHARGING = (255, 215, 0)   # 🟡 Yellow - تشحن
COLOR_DRONE_CRASHED = (220, 20, 60)    # 🔴 Red - محطمة
COLOR_PACKAGE_ICON = (139, 0, 0)       # Dark red for package icon

# ═══════════════════════════════════════════════════════════
# SCENARIO CONFIGURATIONS
# ═══════════════════════════════════════════════════════════

SCENARIOS = {
    'easy': {
        'building_density': 0.2,
        'no_fly_zones': 2,
        'weather': 'clear',
        'wind_speed': 10
    },
    'medium': {
        'building_density': 0.3,
        'no_fly_zones': 4,
        'weather': 'cloudy',
        'wind_speed': 20
    },
    'hard': {
        'building_density': 0.4,
        'no_fly_zones': 6,
        'weather': 'windy',
        'wind_speed': 35
    },
    'storm': {
        'building_density': 0.3,
        'no_fly_zones': 4,
        'weather': 'storm',
        'wind_speed': 50
    }
}

# ═══════════════════════════════════════════════════════════
# PATHS AND FILES
# ═══════════════════════════════════════════════════════════

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(DATA_DIR, 'models')
LOGS_DIR = os.path.join(DATA_DIR, 'logs')
MAPS_DIR = os.path.join(DATA_DIR, 'maps')

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR, MAPS_DIR]:
    os.makedirs(directory, exist_ok=True)

# File paths
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, 'best_agent.pth')
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'training.log')
METRICS_FILE_PATH = os.path.join(LOGS_DIR, 'metrics.csv')

# ═══════════════════════════════════════════════════════════
# DEBUG AND LOGGING
# ═══════════════════════════════════════════════════════════

DEBUG_MODE = True
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
SAVE_FREQUENCY = 100  # save model every N episodes
PRINT_FREQUENCY = 10  # print stats every N episodes

# Training intervals
SAVE_INTERVAL = 500  # حفظ النموذج كل 500 حلقة
PLOT_INTERVAL = 100  # إنشاء رسم بياني كل 100 حلقة

# Safety thresholds for logic engine
MIN_BATTERY_EMERGENCY = 5   # % للهبوط الاضطراري
MIN_BATTERY_RETURN = 20     # % للعودة للقاعدة
SAFETY_MAX_ALTITUDE_M = 200 # أقصى ارتفاع آمن (متر)
SAFETY_MIN_ALTITUDE_M = 10  # أدنى ارتفاع آمن (متر)
EMERGENCY_LANDING_DISTANCE = 100  # مسافة الهبوط الاضطراري (متر)

# ═══════════════════════════════════════════════════════════
# PERFORMANCE SETTINGS
# ═══════════════════════════════════════════════════════════

USE_GPU = True  # use CUDA if available
NUM_WORKERS = 4  # for parallel processing
RENDER_DURING_TRAINING = False  # disable rendering for faster training
FAST_FORWARD_SPEED = 10  # simulation speed multiplier
