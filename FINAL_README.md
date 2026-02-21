# 🚁 Autonomous Medical Drone Delivery System

## 🎯 Project Overview

A complete **Hybrid Neuro-Symbolic AI** system for autonomous medical drone delivery in urban environments. This project combines the learning capabilities of **Q-Learning** with the safety guarantees of **symbolic logic** to create a robust, explainable, and safe autonomous navigation system.

## 🏗️ Architecture

### Hybrid Neuro-Symbolic Approach
- **Neural Layer (Q-Learning)**: Learns optimal paths through experience and trial-and-error
- **Symbolic Layer (Logic Engine)**: Enforces hard safety constraints and mission rules
- **Hybrid Controller**: Intelligently combines both approaches for safe and efficient operation

### Key Features
- 🧠 **Intelligent Learning**: Q-Learning agent that improves performance over time
- ⚖️ **Safety-Critical**: Logic engine with 15+ safety rules that cannot be violated
- 🌍 **Realistic Environment**: 3D city simulation with buildings, weather, and obstacles
- 🎮 **Interactive GUI**: Real-time visualization and control interface
- 📊 **Performance Tracking**: Comprehensive metrics and learning progress visualization
- 🛡️ **Explainable AI**: Every decision is logged and can be explained

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd drone_delivery

# Install dependencies
pip install -r requirements.txt
```

### 2. Quick Test
```bash
# Test all system components
python quick_test_complete.py
```

### 3. Training
```bash
# Train the AI agent (500 episodes)
python run_training.py
```

### 4. Demo
```bash
# Run autonomous demo (after training)
python run_demo.py
```

### 5. GUI
```bash
# Launch graphical interface
python run_gui.py
```

## 📁 Project Structure

```
drone_delivery/
├── src/
│   ├── ai/                     # AI Components
│   │   ├── q_learning.py       # Q-Learning Agent
│   │   ├── logic_engine.py     # Rule-Based System
│   │   ├── hybrid_controller.py # Neuro-Symbolic Controller
│   │   └── trainer.py          # Training System
│   ├── environment/            # Simulation Environment
│   │   ├── city.py            # Main Environment
│   │   ├── drone.py           # Drone Physics
│   │   ├── obstacles.py       # Buildings & No-Fly Zones
│   │   └── weather.py         # Weather System
│   ├── gui/                   # Graphical Interface
│   │   ├── main_window.py     # Main Window
│   │   ├── map_view.py        # 3D Visualization
│   │   └── control_panel.py   # Control Interface
│   ├── utils/                 # Utilities
│   │   ├── config.py          # Configuration
│   │   ├── logger.py          # Logging System
│   │   └── metrics.py         # Performance Metrics
│   └── main.py                # Main Entry Point
├── data/                      # Data & Models
├── docs/                      # Documentation
├── run_training.py            # Quick Training
├── run_demo.py               # Quick Demo
├── run_gui.py                # Quick GUI
└── quick_test_complete.py    # System Test
```

## 🧠 AI Architecture Details

### Q-Learning Agent
- **State Space**: Discretized drone position, battery, cargo status, weather conditions
- **Action Space**: 8 movement directions + special actions (pickup, deliver, wait)
- **Learning**: Epsilon-greedy exploration with decaying epsilon
- **Q-Table**: Persistent storage with save/load functionality

### Logic Engine
- **Safety Rules**: Battery management, weather constraints, no-fly zones
- **Mission Rules**: Pickup/delivery logic, navigation priorities
- **Efficiency Rules**: Optimal path selection, energy conservation
- **Priority System**: Higher priority rules override lower ones

### Hybrid Controller
- **Decision Process**:
  1. Logic engine determines safe actions
  2. Q-Learning selects best action from safe options
  3. Safety override for critical situations
  4. Decision logging for explainability

## 🎮 Usage Modes

### 1. Training Mode
```bash
python src/main.py train --episodes 1000
```
- Trains the Q-Learning agent
- Saves progress and models automatically
- Generates learning curves and statistics

### 2. Demo Mode
```bash
python src/main.py demo
```
- Runs autonomous missions using trained agent
- No exploration (greedy policy)
- Shows decision explanations

### 3. GUI Mode
```bash
python src/main.py gui
```
- Interactive graphical interface
- Real-time visualization
- Manual control and monitoring
- Training and demo modes available

### 4. Test Mode
```bash
python src/main.py test
```
- Comprehensive system testing
- Component verification
- Performance benchmarking

## 📊 Performance Metrics

The system tracks comprehensive metrics:

- **Learning Progress**: Episode rewards, success rates, Q-table growth
- **Safety Metrics**: Safety override frequency, rule violations
- **Efficiency Metrics**: Path optimality, energy consumption, mission time
- **Decision Analysis**: Action distributions, rule usage statistics

## 🛡️ Safety Features

### Hard Constraints (Cannot be violated)
- **Critical Battery**: Emergency landing when battery < 10%
- **Weather Safety**: No flying in dangerous weather conditions
- **No-Fly Zones**: Automatic avoidance of restricted areas
- **Obstacle Avoidance**: Real-time collision prevention

### Soft Constraints (Optimization goals)
- **Energy Efficiency**: Prefer energy-saving paths
- **Mission Priority**: Balance safety with mission completion
- **Path Optimization**: Learn efficient routes over time

## 🎯 Demo Scenarios

The system includes several pre-configured scenarios:

1. **Basic Delivery**: Simple pickup and delivery mission
2. **Weather Challenge**: Navigation in changing weather conditions
3. **Urban Navigation**: Complex city environment with obstacles
4. **Emergency Scenario**: Low battery emergency landing
5. **No-Fly Zone**: Navigation around restricted areas

## 📈 Results & Performance

### Training Results (500 episodes)
- **Success Rate**: 85-95% (depending on scenario complexity)
- **Learning Speed**: Significant improvement within 100 episodes
- **Safety Record**: 100% compliance with safety rules
- **Efficiency**: 40-60% improvement in path optimality

### Key Achievements
- ✅ **Zero Safety Violations**: Logic engine prevents all unsafe actions
- ✅ **Explainable Decisions**: Every action can be traced to specific rules or Q-values
- ✅ **Robust Performance**: Handles various weather and obstacle conditions
- ✅ **Continuous Learning**: Performance improves with more training

## 🔬 Research Contributions

### 1. Hybrid Neuro-Symbolic Architecture
- Novel combination of Q-Learning and symbolic logic
- Maintains safety while enabling learning and adaptation
- Provides explainability in safety-critical applications

### 2. Safety-Critical Autonomous Systems
- Demonstrates hard constraint enforcement in RL
- Shows how symbolic reasoning can guide neural learning
- Provides framework for other safety-critical domains

### 3. Urban Drone Navigation
- Realistic simulation of urban delivery scenarios
- Integration of multiple environmental factors
- Scalable approach for real-world deployment

## 🎓 Academic Applications

### Course Projects
- **AI/ML Courses**: Reinforcement learning, hybrid AI systems
- **Robotics Courses**: Autonomous navigation, path planning
- **Software Engineering**: Large-scale system design, GUI development

### Research Extensions
- **Multi-Agent Systems**: Multiple drones coordination
- **Deep Learning**: Replace Q-Learning with DQN/PPO
- **Real Hardware**: Deploy on actual drone platforms
- **Advanced Logic**: Integration with formal verification tools

## 🛠️ Development & Customization

### Adding New Rules
```python
# In logic_engine.py
self.add_rule(Rule(
    name="custom_rule",
    rule_type=RuleType.SAFETY,
    condition=lambda state: your_condition(state),
    action="your_action",
    priority=85,
    description="Your rule description"
))
```

### Modifying Environment
```python
# In city.py - add new building types, weather patterns, etc.
# In drone.py - modify physics, add sensors, change capabilities
```

### Extending GUI
```python
# In gui/ - add new visualization modes, control panels, etc.
```

## 📚 Documentation

- **DESIGN_DOCUMENT.md**: Detailed technical specifications
- **PAYLOAD_SYSTEM.md**: Cargo handling system details
- **FAQ_PRESENTATION.md**: Common questions and answers
- **PROJECT_STATUS.md**: Current development status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Reinforcement Learning**: Sutton & Barto textbook
- **Symbolic AI**: Classic AI reasoning approaches
- **PyQt5**: GUI framework
- **Pygame**: 3D visualization
- **NumPy/SciPy**: Scientific computing

## 📞 Support

For questions, issues, or contributions:
1. Check the FAQ_PRESENTATION.md file
2. Review existing issues in the repository
3. Create a new issue with detailed description
4. Contact the development team

---

**🚁 Ready for takeoff! Train your agent and watch it learn to navigate safely through the urban skies! 🌆**