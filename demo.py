#!/usr/bin/env python3
"""
DEMO REEL - Showcases the non-curses animations in sequence
"""

import sys
import time
import subprocess
import os

DEMOS = [
    ("ASCII Art - Animal Parade", ["python3", "ascii_art.py", "animal", "cat"]),
    ("ASCII Art - Shapes", ["python3", "ascii_art.py", "shape", "heart"]),
    ("ASCII Art - Animated Text", ["python3", "ascii_art.py", "animate", "DEMO"]),
    ("Bouncing Balls Physics", ["python3", "bouncing_balls.py"]),
    ("Plasma Effect (compiled)", ["./plasma"]),
]

def run_demo(name, cmd, duration=4):
    print(f"\n{'='*60}")
    print(f"  🎬 {name}")
    print(f"{'='*60}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"  Duration: {duration}s (Ctrl+C to skip)")
    print()
    
    try:
        proc = subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
        time.sleep(duration)
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
    except KeyboardInterrupt:
        print("\n  ⏭️  Skipped!")
    except FileNotFoundError:
        print(f"  ❌ Command not found: {cmd[0]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    time.sleep(0.5)

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    AILETLOOS DEMO REEL                           ║
║         Sit back and enjoy the show! 🍿                          ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("This demo shows the non-curses programs (work in any terminal).")
    print("For curses-based apps (snake, sandbox, tamagotchi, etc), run them directly.")
    print("\nStarting in 2 seconds... (Ctrl+C to exit)")
    time.sleep(2)
    
    for name, cmd in DEMOS:
        run_demo(name, cmd)
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                      DEMO COMPLETE! 🎉                           ║
║                                                                  ║
║  Try these other programs:                                       ║
║    python3 adventure.py      - Text RPG adventure                ║
║    python3 snake.py          - Classic Snake with power-ups      ║
║    python3 sandbox.py        - Falling sand physics simulator    ║
║    python3 tamagotchi.py     - Virtual pet                       ║
║    python3 main.py           - 8-mode visualization show         ║
║    python3 matrix_rain.py    - Matrix digital rain               ║
║    python3 flow_field.py     - Particle flow fields              ║
║    python3 reaction_diffusion.py - Gray-Scott patterns           ║
║                                                                  ║
║  See README.md for full details!                                 ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()