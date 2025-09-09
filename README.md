# Fantastic Four Simulation

A sophisticated multi-agent reinforcement learning simulation where heroes from the Fantastic Four defend Earth against the cosmic threat of Galactus and his herald, the Silver Surfer.

## Project Overview

This project implements a complex strategic environment where autonomous agents with distinct capabilities learn cooperative and competitive behaviors through independent Q-learning. The simulation features a toroidal grid world with specialized heroes, villains, and structural elements that must be protected or destroyed based on role-specific objectives.

## Key Features

- **Toroidal Grid Environment**: 20×20 grid world with wraparound boundaries using Chebyshev distance calculations
- **Multiple Agent Types**: 7 distinct agent classes with unique capabilities and learning approaches
- **Reinforcement Learning**: Independent Q-learning for heroes with state discretization and reward shaping
- **Rule-Based Villains**: Galactus uses strategic targeting rather than learning
- **Special Abilities**: Character-specific powers including force fields, ranged attacks, and proximity bonuses
- **Visualization**: Tkinter-based GUI with real-time rendering and performance metrics
- **Metrics Tracking**: Comprehensive logging of rewards, win rates, and learning progress

## Agent Types

### Heroes
- **Reed Richards**: Strategic leader with enhanced repair capabilities
- **Sue Storm**: Defense specialist with configurable force fields
- **Human Torch**: Offensive specialist with ranged attacks (self-damage penalty)
- **The Thing**: Close-combat specialist with proximity bonuses
- **Franklin Richards**: Non-combat objective requiring protection

### Villains
- **Galactus**: Primary antagonist with rule-based strategic targeting
- **Silver Surfer**: Mobile herald with scanning and attack abilities

### Structures
- **Bridges**: Four strategic locations that must be maintained at full health
- **Headquarters**: Healing and resupply point for heroes

## Installation & Setup

### Using Python Virtual Environment

1. **Clone or download the project files** to your local machine

2. **Create a virtual environment**:
   ```bash
   python -m venv marvel-env
   ```

3. **Activate the environment**:
    - **Linux**:
    ```bash
    source marvel-env/bin/activate
    ```

    - **Windows**:
    ```bash
    . marvel-env/bin/activate
    ```

4. **Install requirements**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the Simulation**:
    ```bash
    python main.py
    ```

