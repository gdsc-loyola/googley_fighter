# Googley Fighter 🎮

## Documentation

### Overview
**Googley Street Fighter** is a 2D, head-to-head fighting game where players select from a diverse roster of fighters—each with their own unique combat style, special moves, and ultimate abilities.  
The game emphasizes **precision timing**, **strategic combos**, and **reading your opponent’s moves** to secure victory.  

---

### Features
- **Multiplayer Gameplay** – Challenge a friend in real-time, either locally or over the network. Matches are designed for fast-paced action with responsive controls to ensure competitive balance.  
- **Single Player Gameplay** – Fight against AI opponents with adjustable difficulty levels. The AI is programmed to adapt to your playstyle, providing both beginners and veterans with an engaging challenge.  
- **Cross-Platform Play (if supported)** – Play with friends regardless of operating system via **PythonAnywhere** server hosting.  

---

### Project Structure

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
├── README.md               # This file
└── project_structure.md    # Project structure and overview
```

---

### Tech Stack
- **Python 3.12**  
- **Asyncio Library** – for asynchronous networking and event handling  
- **PyGame Library** – for graphics, input, and game loop  
- **PyBag Library** – for structured game state and asset management  
- **PythonAnywhere** – for server hosting and deployment  

---

### Learning Resources
- [PyGame Documentation](https://www.pygame.org/docs/)  
- [PyBag Documentation](https://pybag.readthedocs.io/)  
- [PythonAnywhere Documentation](https://help.pythonanywhere.com/)  
- [How to deploy on PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)  
- [Export PyGame to the Web using WebAssembly](https://github.com/pygame-web/pygbag)  

---

### Project Structure
For developers, see [project_structure.md](./project_structure.md) to understand the directory layout and contribution guidelines.  

---

🚀 *Googley Fighter is a learning + experimental project that blends gameplay design and technical implementation. Contributions and feedback are welcome!*  
