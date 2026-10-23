# ailetloos - Terminal Toy Collection

A curated collection of fun terminal programs, animations, games, and interactive toys.

## 🎮 Games

| File | Description | Type |
|------|-------------|------|
| `adventure.py` | **The Lost Temple** - Text adventure RPG with combat, inventory, and exploration | Text RPG |
| `snake.py` | **Snake** - Classic with power-ups, levels, high scores, particles | Curses |
| `tamagotchi.py` | **Virtual Pet** - Feed, play, train, and care for your terminal buddy | Curses |

## 🎨 Animations & Visualizations

| File | Description | Type |
|------|-------------|------|
| `ascii_art.py` | **ASCII Art Generator** - Text, animals, shapes, banners, animations | Stdout |
| `bouncing_balls.py` | **Physics Balls** - Colorful bouncing balls with trails & collisions | Stdout |
| `matrix_rain.py` | **Matrix Rain** - Falling katakana characters | Curses |
| `flow_field.py` | **Flow Field** - Particle flow visualization | Curses |
| `reaction_diffusion.py` | **Reaction-Diffusion** - Gray-Scott pattern simulation | Curses |
| `plasma` | **Plasma Effect** - Compiled C plasma animation (run `./plasma`) | Binary |
| `main.py` | **Multi-Mode Show** - 8 cycling visualizations (fireworks, plasma, etc) | Curses |

## 🏗️ Interactive Toys

| File | Description | Type |
|------|-------------|------|
| `sandbox.py` | **Particle Sandbox** - 10 materials, 7 tools, physics simulation | Curses |

## 🚀 Quick Start

```bash
# Text-based (work in any terminal)
python3 adventure.py
python3 ascii_art.py animate "HELLO"
python3 ascii_art.py animal cat
python3 bouncing_balls.py

# Curses-based (need proper terminal)
python3 snake.py
python3 sandbox.py
python3 tamagotchi.py
python3 main.py
python3 matrix_rain.py
python3 flow_field.py
python3 reaction_diffusion.py

# Compiled binary
./plasma
```

## 🎯 Featured Highlights

### The Lost Temple (adventure.py)
A complete text adventure with:
- 7 unique rooms to explore
- Turn-based combat system
- Inventory management (weapons, armor, potions, keys)
- Equipment system
- Boss battle against the Lich King
- Save/load not needed - play in one sitting!

### Particle Sandbox (sandbox.py)
A falling-sand style physics simulator:
- **10 Materials**: Sand, Water, Fire, Smoke, Stone, Wood, Acid, Lava, Ice, Oil
- **7 Tools**: Brush, Eraser, Wind, Heat, Cool, Gravity, Explosion
- Realistic interactions: Fire burns wood/oil, Lava turns water to steam, Acid dissolves things, Heat/Cool cause phase changes
- Mouse support for precise control

### ASCII Art Generator (ascii_art.py)
```
python3 ascii_art.py text "HELLO"      # Big text
python3 ascii_art.py animal cat         # ASCII animals
python3 ascii_art.py shape heart        # Shapes
python3 ascii_art.py banner welcome     # Banner text
python3 ascii_art.py animate "HI"       # Animated!
python3 ascii_art.py list               # Show all options
```

### Snake (snake.py)
Modern Snake with:
- 4 power-ups (Slow, Shrink, 2x Score, Ghost mode)
- Level progression (speeds up every 5 food)
- Golden food (50 pts) and Shrinking food
- Particle effects on eating
- High score persistence
- Pause (P), Restart (R), Quit (Q)

## 🎮 Controls Reference

### Sandbox
- `1-9,0` - Select material
- `↑↓` - Cycle materials  
- `←→` - Cycle tools
- `[ / ]` - Brush size
- `SPACE` - Pause
- `C` - Clear
- `G` - Flip gravity
- `W` - Toggle wind
- `H` - Help
- Mouse click - Use tool

### Snake
- Arrow keys - Move
- `P` - Pause
- `R` - Restart (game over)
- `Q` - Quit

### Tamagotchi
- `M` - Open menu
- `1-7` - Quick actions (feed, play, pet, sleep, medicine, clean, train)
- `S` - Save
- `Q` - Quit

## 🛠️ Requirements

- Python 3.8+
- `curses` (built-in on Linux/macOS)
- Terminal with 256-color support recommended
- For `plasma` binary: Linux x86_64

## 💡 Tips

- Resize your terminal for larger canvas in sandbox/snake
- In sandbox: Mix oil + water, then add fire!
- In sandbox: Use Heat on ice to make water, Cool on lava to make stone
- In adventure: Check `inventory` often, `equip` sword/shield before combat
- The `plasma` binary is written in x86_64 assembly - check `plasma.asm`!

## 📜 License

MIT - Have fun, modify, share, whatever!