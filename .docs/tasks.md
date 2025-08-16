# ✅ Googley Fighter – Development Tasks

This document lists the key development tasks based on the project structure.  
Mark tasks with `[x]` once completed.

---

## 🏗️ Core Game Logic (`src/`)
- [ ] Create **main.py** to initialize PyGame, load assets, and start the game loop  
- [ ] Implement **sprite.py** for character sprites, animations, states, and collision detection  
- [ ] Build **gamecanvas.py** to handle rendering, frame updates, and game loop flow  
- [ ] Develop **ai.py** for adaptive AI logic with difficulty scaling  
- [ ] Implement **controls.py** for keyboard/controller input mapping  
- [ ] Add **networking.py** for multiplayer support using asyncio (host/join, sync states)  
- [ ] Define **config.py** with constants (screen size, FPS, controls, etc.)  
- [ ] Add **utils/** for helper functions (math, collision, asset loaders)  

---

## 🎨 Assets (`assets/`)
- [ ] Prepare **images/**: spritesheets, character art, backgrounds, UI icons  
- [ ] Add **sounds/**: attack SFX, hits, KO jingles, background music  
- [ ] Include **fonts/**: custom fonts for menus, HUD, and health bars  
- [ ] Write **README.md** in assets/ documenting sources, formats, and credits  

---

## ✅ Testing (`tests/`)
- [ ] Create **test_sprite.py** to verify animations, states, and collisions  
- [ ] Write **test_gamecanvas.py** to test rendering loop and frame updates  
- [ ] Implement **test_ai.py** to confirm AI difficulty scaling and logic correctness  

---

## 📦 Root / Project Setup
- [ ] Finalize **requirements.txt** with all dependencies (pygame, pybag, asyncio, etc.)  
- [ ] Write **README.md** with overview, setup, and gameplay instructions  
- [ ] Maintain **project_structure.md** to reflect the current project layout  
- [ ] Maintain **tasks.md** as a developer progress checklist  

---

## 🚀 Future Enhancements
- [ ] Add **special moves & ultimate abilities** system  
- [ ] Implement **dynamic arenas** with stage hazards or interactive elements  
- [ ] Create **menu system** (main menu, character select, pause, victory screen)  
- [ ] Support **web deployment** using PyBag (WebAssembly export)  
- [ ] Enable **cross-platform multiplayer** with stable netcode  
