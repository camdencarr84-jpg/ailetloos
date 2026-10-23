#!/usr/bin/env python3
"""
Game Launcher - Play all the fun games!
"""

import subprocess
import sys
import os

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗ ██████╗ ███████╗███████╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗      ║
║    ██╔══██╗██╔══██╗██╔════╝██╔════╝██║  ██║██╔══██╗████╗  ██║██╔═══██╗     ║
║    ██████╔╝██████╔╝█████╗  ███████╗███████║███████║██╔██╗ ██║██║   ██║     ║
║    ██╔═══╝ ██╔══██╗██╔══╝  ╚════██║██╔══██║██╔══██║██║╚██╗██║██║   ██║     ║
║    ██║     ██║  ██║███████╗███████║██║  ██║██║  ██║██║ ╚████║╚██████╔╝     ║
║    ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝      ║
║                                                                              ║
║    ██████╗ ██████╗ ██████╗ ███████╗     ██████╗ ██████╗ ███╗   ██╗███████╗  ║
║    ██╔══██╗██╔══██╗██╔══██╗██╔════╝    ██╔══██╗██╔══██╗████╗  ██║██╔════╝  ║
║    ██████╔╝██████╔╝██████╔╝█████╗      ██████╔╝██████╔╝██╔██╗ ██║█████╗    ║
║    ██╔═══╝ ██╔══██╗██╔══██╗██╔══╝      ██╔═══╝ ██╔══██╗██║╚██╗██║██╔══╝    ║
║    ██║     ██║  ██║██║  ██║███████╗    ██║     ██║  ██║██║ ╚████║███████╗  ║
║    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_menu():
    print("""
┌──────────────────────────────────────────────────────────────────────────────┐
│                            🎮 GAME MENU 🎮                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  GAMES:                                                                      │
│    1. 🐍 SNAKE GAME           - Classic snake with colors & high scores      │
│    2. 🌧️  MATRIX RAIN           - Mesmerizing digital rain animation         │
│    3. 📜 TEXT ADVENTURE       - Explore the Lost Temple!                    │
│    4. 🎨 ASCII ART GENERATOR  - Create cool ASCII art & banners             │
│                                                                              │
│  VISUALIZATIONS:                                                             │
│    5. 🎆 FIREWORKS           - Particle fireworks show                       │
│    6. 🧊 3D CUBE             - Rotating 3D wireframe cube                   │
│    7. 🌈 SYNTHWAVE GRID      - Retro grid with sun & scanlines              │
│    8. 🧬 DNA HELIX           - Animated DNA double helix                    │
│    9. 💻 HACKER DASHBOARD    - Fake system monitor with logs                │
│    0. 🌈 PLASMA EFFECT       - Classic demo scene plasma                    │
│                                                                              │
│    A. 🎲 RUN ALL GAMES       - Play everything in sequence!                 │
│                                                                              │
│    Q. Quit                                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
""")

def run_game(script_name, args=None):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\nReturning to menu...")
    except Exception as e:
        print(f"\nError running {script_name}: {e}")
        input("Press Enter to continue...")

def main():
    games = {
        '1': ('snake.py', 'Snake Game'),
        '2': ('matrix_rain.py', 'Matrix Rain'),
        '3': ('adventure.py', 'Text Adventure'),
        '4': ('ascii_art.py', 'ASCII Art Generator', ['list']),
        '5': ('fireworks.py', 'Fireworks Show'),
        '6': ('cube3d.py', '3D Cube'),
        '7': ('synthwave.py', 'Synthwave Grid'),
        '8': ('dna_helix.py', 'DNA Helix'),
        '9': ('hacker_dash.py', 'Hacker Dashboard'),
        '0': ('plasma.py', 'Plasma Effect'),
    }
    
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = input("Select (0-9, A, Q): ").strip().upper()
        
        if choice == 'Q':
            print("\nThanks for playing! Goodbye! 👋\n")
            break
        elif choice == 'A':
            print("\n🎮 Running all games in sequence! Press Ctrl+C to skip any game.\n")
            input("Press Enter to start...")
            for key in sorted(games.keys()):
                script, name, *args = games[key]
                print(f"\n{'='*60}")
                print(f"Starting: {name}")
                print(f"{'='*60}\n")
                run_game(script, args[0] if args else None)
                if key != '0':
                    input("\nPress Enter for next game...")
        elif choice in games:
            script, name, *args = games[choice]
            clear_screen()
            print(f"\nStarting {name}...\n")
            if choice == '4':
                print("ASCII Art Generator - showing available items:")
                run_game(script, ['list'])
                print("\nTry: python ascii_art.py text \"HELLO\" standard")
                print("     python ascii_art.py animal cat")
                print("     python ascii_art.py shape heart")
                print("     python ascii_art.py banner welcome")
                input("\nPress Enter to return to menu...")
            else:
                run_game(script, args[0] if args else None)
        else:
            print("\nInvalid choice! Press Enter to try again...")
            input()

if __name__ == '__main__':
    main()