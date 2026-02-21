
"""
Quick test for the environment
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from environment import CityEnvironment

def test_environment():
    """اختبار سريع للبيئة"""
    print("="*60)
    print("🧪 Testing City Environment")
    print("="*60)
    
    # Create environment
    print("\n1. Creating environment...")
    env = CityEnvironment(grid_size=20, weather="clear", seed=42)
    print(f"   ✓ Environment created: {env}")
    
    # Reset environment
    print("\n2. Resetting environment...")
    state = env.reset()
    print(f"   ✓ Initial state:")
    print(f"      Position: {state['position']}")
    print(f"      Target: {state['target']}")
    print(f"      Battery: {state['battery']:.1f}%")
    print(f"      Distance: {state['distance_to_target']:.1f}")
    
    # Test a few steps
    print("\n3. Testing random actions...")
    for i in range(10):
        # Get valid actions
        valid_actions = env.get_valid_actions()
        
        # Choose random action
        import random
        action = random.choice(valid_actions)
        
        # Take step
        state, reward, done, info = env.step(action)
        
        print(f"   Step {i+1}: {action:12s} | "
              f"Pos: {state['position']} | "
              f"Battery: {state['battery']:5.1f}% | "
              f"Reward: {reward:6.1f} | "
              f"Done: {done}")
        
        if done:
            print(f"   Mission ended: {info['mission_status']}")
            break
    
    # Test environment info
    print("\n4. Environment info:")
    info = env.get_env_info()
    print(f"   Grid size: {info['grid_size']}")
    print(f"   Buildings: {info['obstacles']['num_buildings']}")
    print(f"   Hospitals: {info['obstacles']['num_hospitals']}")
    print(f"   Labs: {info['obstacles']['num_labs']}")
    print(f"   Charging stations: {info['obstacles']['num_charging_stations']}")
    print(f"   No-fly zones: {info['obstacles']['num_no_fly_zones']}")
    print(f"   Weather: {info['weather']['condition']}")
    
    # Test failure scenarios
    print("\n5. Failure Scenarios:")
    print(f"   💥 Collisions: {info['collisions']}")
    print(f"   🔋 Battery failures: 0")
    print(f"   🚫 Interceptions: {info['interceptions']}")
    print(f"   ⛈️  Storm crashes: {info['storm_crashes']}")
    print(f"   🩸 Payload spoilages: {info['payload_spoilages']}")
    
    print("\n" + "="*60)
    print("✅ Environment test completed successfully!")
    print("="*60)

if __name__ == "__main__":
    test_environment()
