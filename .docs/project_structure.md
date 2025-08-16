# 📁 Project Structure

This document outlines the recommended project structure for the Googley Fighter built with Python and PyGame.

## 🏗️ Directory Layout

```
googley_fighter/
│
├── assets/                 # Game assets (images, sprites, sounds, fonts)
│   ├── images/             # Character sprites, backgrounds, UI icons
│   ├── sounds/             # Sound effects and background music
│   └── fonts/              # Custom fonts used in the game
│
├── src/                    # Core source code
│   ├── __init__.py
│   ├── main.py             # Game entry point
│   ├── sprite.py           # Sprite and character handling (animations, states)
│   ├── gamecanvas.py       # Main game loop, rendering, and input handling
│   ├── ai.py               # AI logic for single player opponents
│   ├── controls.py         # Input mapping and event handling
│   ├── networking.py       # Multiplayer networking (asyncio, sockets)
│   ├── config.py           # Global configuration (constants, settings)
│   └── utils/              # Helper functions and utilities
│       └── __init__.py
│
├── tests/                  # Unit and integration tests
│   ├── test_sprite.py
│   ├── test_gamecanvas.py
│   └── test_ai.py
│
├── requirements.txt        # Python dependencies
├── README.md               # Project overview and instructions
└── project_structure.md    # This file
```

---

## ⚙️ Module Responsibilities

### 🎨 Assets (`assets/`)
Holds all **media resources** used in the game:
- **images/** → Sprites, backgrounds, UI elements  
- **sounds/** → Sound effects, music, victory jingles  
- **fonts/** → Custom typography for menus, health bars, HUD   

---

### 🕹️ Source Code (`src/`)
The heart of the game containing all **game logic**:

- **main.py** → Initializes the game, loads assets, and starts the game loop  
- **sprite.py** → Handles character and object sprites, animations, and state transitions  
- **gamecanvas.py** → Manages the rendering loop, screen updates, and core gameplay flow  
- **ai.py** → Implements AI decision-making for single-player mode  
- **controls.py** → Maps keyboard/controller inputs into game actions  
- **networking.py** → Enables multiplayer functionality (sockets + asyncio for async networking)  
- **config.py** → Stores constants, global settings, and configuration variables  
- **utils/** → Helper functions and reusable utilities for cleaner code  

---

### ✅ Tests (`tests/`)
Unit and integration tests to ensure the game runs reliably:
- **test_sprite.py** → Tests sprite states and animations  
- **test_gamecanvas.py** → Tests rendering loop and core game loop functions  
- **test_ai.py** → Verifies AI logic and adaptive difficulty  

---

### 📦 Root Files
- **requirements.txt** → Lists required Python dependencies  
- **README.md** → Main documentation with overview, features, and setup instructions  
- **project_structure.md** → Defines and documents the project layout  

---

## 🧩 Architectural Flow

1. **Initialization** → `main.py` loads assets, initializes PyGame, sets configurations.  
2. **Game Loop** → `gamecanvas.py` runs the main loop, handling rendering, input, and updates.  
3. **Input Handling** → `controls.py` interprets player commands.  
4. **Character Logic** → `sprite.py` updates character animations, moves, and states.  
5. **AI / Multiplayer** → Depending on mode, either `ai.py` controls the opponent or `networking.py` manages remote player interactions.  
6. **Rendering** → Updated sprites and game states are drawn to screen in `gamecanvas.py`.  
7. **Testing** → Automated tests ensure stability across modules.  

---

## 🚀 Summary
The **Googley Fighter** architecture separates **assets**, **game logic**, **networking**, and **testing** into well-defined modules. This modular design makes the game **extensible**, **testable**, and easier to maintain for future enhancements such as new fighters, stages, or online play.  
