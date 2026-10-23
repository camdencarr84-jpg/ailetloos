#!/usr/bin/env python3
"""
Kaleidoscope - Symmetric Cellular Automaton
Creates mesmerizing kaleidoscopic patterns with multiple symmetry modes.
Press 'm' for mode, 'c' for colors, 'p' pause, 'r' reset, 'q' quit.
"""

import curses
import random
import time
import math
from dataclasses import dataclass
from typing import List
import colorsys


@dataclass
class Rule:
    birth: List[int]
    survival: List[int]
    states: int
    name: str


class Kaleidoscope:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.height -= 2
        self.width -= 2
        
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.age_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        self.rules = [
            Rule([3], [2, 3], 2, "Conway"),
            Rule([3, 6], [2, 3], 2, "HighLife"),
            Rule([2], [1, 2], 2, "Seeds"),
            Rule([3, 6, 8], [2, 3, 8], 2, "DayNight"),
            Rule([2, 3, 4], [3, 4], 3, "Cyclic3"),
            Rule([2], [1, 2, 3], 4, "Cyclic4"),
            Rule([1, 2], [1, 2, 3, 4], 5, "StarWars"),
            Rule([2, 3], [2, 3], 8, "Generations"),
        ]
        self.rule_idx = 0
        self.rule = self.rules[self.rule_idx]
        
        self.symmetry_modes = [
            ('none', self.apply_none),
            ('horizontal', self.apply_horizontal),
            ('vertical', self.apply_vertical),
            ('quadrant', self.apply_quadrant),
            ('radial4', self.apply_radial4),
            ('radial8', self.apply_radial8),
            ('spiral', self.apply_spiral),
            ('mandala', self.apply_mandala),
        ]
        self.symmetry_idx = 3
        self.symmetry_name, self.apply_symmetry = self.symmetry_modes[self.symmetry_idx]
        
        self.color_modes = [
            'rainbow', 'fire', 'ocean', 'forest', 'sunset',
            'monochrome', 'neon', 'pastel', 'crystalline', 'void'
        ]
        self.color_mode = 0
        
        self.paused = False
        self.generation = 0
        self.speed = 1
        self.max_age = 100
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, 256):
                curses.init_pair(i, i, -1)
        
        self.seed_random()
    
    def seed_random(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.age_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        pattern = random.choice(['random', 'glider', 'pentomino', 'acorn', 'r-pentomino', 'diehard', 'guns'])
        
        if pattern == 'random':
            density = 0.15
            for y in range(self.height):
                for x in range(self.width):
                    if random.random() < density:
                        self.grid[y][x] = random.randint(1, self.rule.states - 1)
        elif pattern == 'glider':
            self.place_pattern(self.width//2, self.height//2, [
                (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
            ])
        elif pattern == 'pentomino':
            self.place_pattern(self.width//2, self.height//2, [
                (0, 1), (1, 1), (1, 0), (1, -1), (2, 0)
            ])
        elif pattern == 'acorn':
            self.place_pattern(self.width//2, self.height//2, [
                (1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2)
            ])
        elif pattern == 'r-pentomino':
            self.place_pattern(self.width//2, self.height//2, [
                (0, 1), (1, 1), (1, 0), (1, -1), (2, 0)
            ])
        elif pattern == 'diehard':
            self.place_pattern(self.width//2, self.height//2, [
                (0, 0), (1, 0), (1, 1), (5, 1), (6, 1), (5, 2), (6, 2)
            ])
        elif pattern == 'guns':
            self.place_gosper_gun(self.width//2 - 15, self.height//2 - 5)
        
        self.apply_symmetry()
        self.generation = 0
    
    def place_pattern(self, cx: int, cy: int, coords: List[tuple]):
        for dx, dy in coords:
            x, y = cx + dx, cy + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = 1
                self.age_grid[y][x] = 1
    
    def place_gosper_gun(self, x: int, y: int):
        gun = [
            (5,1),(5,2),(6,1),(6,2),
            (3,13),(3,14),(4,12),(4,16),(5,11),(5,17),(6,11),(6,15),(6,17),(6,18),(7,11),(7,17),(8,13),(8,14),(9,12),(9,16),
            (1,25),(2,23),(2,25),(3,21),(3,22),(4,21),(4,22),(5,21),(5,22),(6,23),(6,25),(7,25),
            (3,35),(3,36),(4,35),(4,36)
        ]
        for dx, dy in gun:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.grid[ny][nx] = 1
                self.age_grid[ny][nx] = 1
    
    def count_neighbors(self, y: int, x: int, state: int = None) -> int:
        count = 0
        h, w = self.height, self.width
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny, nx = (y + dy) % h, (x + dx) % w
                if state is None:
                    if self.grid[ny][nx] > 0:
                        count += 1
                else:
                    if self.grid[ny][nx] == state:
                        count += 1
        return count
    
    def count_neighbors_multistate(self, y: int, x: int) -> List[int]:
        counts = [0] * self.rule.states
        h, w = self.height, self.width
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny, nx = (y + dy) % h, (x + dx) % w
                val = self.grid[ny][nx]
                if val > 0:
                    counts[val] += 1
        return counts
    
    def step(self):
        if self.paused:
            return
        
        rule = self.rule
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                
                if rule.states == 2:
                    neighbors = self.count_neighbors(y, x)
                    if cell == 0:
                        if neighbors in rule.birth:
                            self.next_grid[y][x] = 1
                            self.age_grid[y][x] = 1
                        else:
                            self.next_grid[y][x] = 0
                            self.age_grid[y][x] = 0
                    else:
                        if neighbors in rule.survival:
                            self.next_grid[y][x] = 1
                            self.age_grid[y][x] = min(self.max_age, self.age_grid[y][x] + 1)
                        else:
                            self.next_grid[y][x] = 0
                            self.age_grid[y][x] = 0
                else:
                    if cell == 0:
                        counts = self.count_neighbors_multistate(y, x)
                        for s in range(1, rule.states):
                            if counts[s] in rule.birth:
                                self.next_grid[y][x] = s
                                self.age_grid[y][x] = 1
                                break
                        else:
                            self.next_grid[y][x] = 0
                            self.age_grid[y][x] = 0
                    else:
                        next_state = (cell + 1) % rule.states
                        if next_state == 0:
                            counts = self.count_neighbors_multistate(y, x)
                            for s in range(1, rule.states):
                                if counts[s] in rule.survival:
                                    self.next_grid[y][x] = s
                                    self.age_grid[y][x] = min(self.max_age, self.age_grid[y][x] + 1)
                                    break
                            else:
                                self.next_grid[y][x] = 0
                                self.age_grid[y][x] = 0
                        else:
                            self.next_grid[y][x] = next_state
                            self.age_grid[y][x] = min(self.max_age, self.age_grid[y][x] + 1)
        
        self.grid, self.next_grid = self.next_grid, self.grid
        self.apply_symmetry()
        self.generation += 1
    
    def apply_none(self):
        pass
    
    def apply_horizontal(self):
        mid = self.height // 2
        for y in range(mid):
            for x in range(self.width):
                self.grid[self.height - 1 - y][x] = self.grid[y][x]
                self.age_grid[self.height - 1 - y][x] = self.age_grid[y][x]
    
    def apply_vertical(self):
        mid = self.width // 2
        for y in range(self.height):
            for x in range(mid):
                self.grid[y][self.width - 1 - x] = self.grid[y][x]
                self.age_grid[y][self.width - 1 - x] = self.age_grid[y][x]
    
    def apply_quadrant(self):
        hmid, wmid = self.height // 2, self.width // 2
        for y in range(hmid):
            for x in range(wmid):
                val = self.grid[y][x]
                age = self.age_grid[y][x]
                self.grid[self.height - 1 - y][x] = val
                self.grid[y][self.width - 1 - x] = val
                self.grid[self.height - 1 - y][self.width - 1 - x] = val
                self.age_grid[self.height - 1 - y][x] = age
                self.age_grid[y][self.width - 1 - x] = age
                self.age_grid[self.height - 1 - y][self.width - 1 - x] = age
    
    def apply_radial4(self):
        cy, cx = self.height // 2, self.width // 2
        for y in range(self.height):
            for x in range(self.width):
                dy, dx = y - cy, x - cx
                if dy*dy + dx*dx > max(cy, cx)**2:
                    continue
                val = self.grid[y][x]
                age = self.age_grid[y][x]
                self.grid[cy - dy][cx + dx] = val
                self.grid[cy + dy][cx - dx] = val
                self.grid[cy - dy][cx - dx] = val
                self.age_grid[cy - dy][cx + dx] = age
                self.age_grid[cy + dy][cx - dx] = age
                self.age_grid[cy - dy][cx - dx] = age
    
    def apply_radial8(self):
        cy, cx = self.height // 2, self.width // 2
        for y in range(self.height):
            for x in range(self.width):
                dy, dx = y - cy, x - cx
                if dy*dy + dx*dx > max(cy, cx)**2:
                    continue
                val = self.grid[y][x]
                age = self.age_grid[y][x]
                self.grid[cy + dx][cx + dy] = val
                self.grid[cy - dx][cx + dy] = val
                self.grid[cy + dx][cx - dy] = val
                self.grid[cy - dx][cx - dy] = val
                self.age_grid[cy + dx][cx + dy] = age
                self.age_grid[cy - dx][cx + dy] = age
                self.age_grid[cy + dx][cx - dy] = age
                self.age_grid[cy - dx][cx - dy] = age
    
    def apply_spiral(self):
        cy, cx = self.height // 2, self.width // 2
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        new_age = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                dy, dx = y - cy, x - cx
                dist = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)
                
                for i in range(4):
                    a = angle + i * math.pi / 2 + self.generation * 0.02
                    nx = int(cx + math.cos(a) * dist)
                    ny = int(cy + math.sin(a) * dist)
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        new_grid[ny][nx] = self.grid[y][x]
                        new_age[ny][nx] = self.age_grid[y][x]
        
        self.grid = new_grid
        self.age_grid = new_age
    
    def apply_mandala(self):
        cy, cx = self.height // 2, self.width // 2
        slices = 12
        
        for y in range(self.height):
            for x in range(self.width):
                dy, dx = y - cy, x - cx
                dist = math.hypot(dx, dy)
                if dist > min(cy, cx):
                    continue
                angle = math.atan2(dy, dx)
                slice_angle = 2 * math.pi / slices
                sector = int((angle + math.pi) / slice_angle)
                base_angle = sector * slice_angle - math.pi
                
                val = self.grid[y][x]
                age = self.age_grid[y][x]
                
                for i in range(slices):
                    a = base_angle + i * slice_angle + 0.01 * self.generation
                    nx = int(cx + math.cos(a) * dist)
                    ny = int(cy + math.sin(a) * dist)
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.grid[ny][nx] = val
                        self.age_grid[ny][nx] = age
    
    def get_color(self, state: int, age: int, mode: str) -> int:
        if state == 0:
            return 0
        
        max_states = self.rule.states - 1
        age_ratio = min(1.0, age / self.max_age)
        state_ratio = state / max_states if max_states > 0 else 0
        
        if mode == 'rainbow':
            hue = (state_ratio * 0.8 + age_ratio * 0.2) % 1.0
            sat = 0.8
            val = 0.4 + 0.6 * age_ratio
        elif mode == 'fire':
            hue = state_ratio * 0.1
            sat = 1.0 - age_ratio * 0.3
            val = 0.3 + 0.7 * age_ratio
        elif mode == 'ocean':
            hue = 0.55 + state_ratio * 0.2
            sat = 0.6 + 0.4 * age_ratio
            val = 0.4 + 0.6 * age_ratio
        elif mode == 'forest':
            hue = 0.25 + state_ratio * 0.15
            sat = 0.5 + 0.5 * age_ratio
            val = 0.3 + 0.5 * age_ratio
        elif mode == 'sunset':
            hue = state_ratio * 0.12
            sat = 0.9
            val = 0.4 + 0.6 * age_ratio
        elif mode == 'monochrome':
            hue = 0
            sat = 0
            val = 0.2 + 0.8 * age_ratio
        elif mode == 'neon':
            hue = (state_ratio * 0.8 + self.generation * 0.005) % 1.0
            sat = 1.0
            val = 1.0
        elif mode == 'pastel':
            hue = state_ratio * 0.6
            sat = 0.3
            val = 0.7 + 0.3 * age_ratio
        elif mode == 'crystalline':
            hue = (state_ratio * 0.7 + age_ratio * 0.1) % 1.0
            sat = 0.5 + 0.5 * age_ratio
            val = 0.6 + 0.4 * age_ratio
        elif mode == 'void':
            hue = (state_ratio + self.generation * 0.001) % 1.0
            sat = 0.3
            val = 0.9
        else:
            hue = state_ratio
            sat = 0.8
            val = 0.5
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        r, g, b = int(r * 1000), int(g * 1000), int(b * 1000)
        color_id = 16 + (r // 40) * 36 + (g // 40) * 6 + (b // 40)
        return min(255, max(16, color_id))
    
    def get_char(self, state: int, age: int) -> str:
        if state == 0:
            return ' '
        age_ratio = min(1.0, age / self.max_age)
        
        if self.rule.states == 2:
            if age_ratio > 0.8: return '█'
            elif age_ratio > 0.6: return '▓'
            elif age_ratio > 0.4: return '▒'
            elif age_ratio > 0.2: return '░'
            else: return '·'
        else:
            chars = [' ', '✦', '✧', '⋆', '✶', '✺', '✹', '✸']
            return chars[min(state, len(chars)-1)]
    
    def draw(self):
        self.stdscr.erase()
        
        mode = self.color_modes[self.color_mode]
        
        for y in range(self.height):
            for x in range(self.width):
                state = self.grid[y][x]
                age = self.age_grid[y][x]
                
                if state > 0:
                    color = self.get_color(state, age, mode)
                    char = self.get_char(state, age)
                    try:
                        self.stdscr.addstr(y, x, char, curses.color_pair(color))
                    except curses.error:
                        pass
        
        self.draw_ui(mode)
        self.stdscr.refresh()
    
    def draw_ui(self, mode: str):
        try:
            stats = [
                f" Rule: {self.rule.name} ",
                f" Symmetry: {self.symmetry_name.upper()} ",
                f" Colors: {mode.upper()} ",
                f" Gen: {self.generation} ",
                f" Speed: {self.speed}x ",
                f" {'PAUSED' if self.paused else 'EVOLVING'} ",
            ]
            for i, stat in enumerate(stats):
                self.stdscr.addstr(self.height, i * 18, stat, curses.color_pair(240) | curses.A_BOLD)
            
            help_text = " [m]ode [s]ymmetry [c]olor [p]ause [r]eset [+/-]speed [n]ext rule [q]uit"
            self.stdscr.addstr(self.height + 1, 2, help_text, curses.color_pair(240))
        except curses.error:
            pass
    
    def handle_input(self, key: int) -> bool:
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('r') or key == ord('R'):
            self.seed_random()
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('m') or key == ord('M'):
            self.rule_idx = (self.rule_idx + 1) % len(self.rules)
            self.rule = self.rules[self.rule_idx]
            self.seed_random()
        elif key == ord('s') or key == ord('S'):
            self.symmetry_idx = (self.symmetry_idx + 1) % len(self.symmetry_modes)
            self.symmetry_name, self.apply_symmetry = self.symmetry_modes[self.symmetry_idx]
            self.seed_random()
        elif key == ord('c') or key == ord('C'):
            self.color_mode = (self.color_mode + 1) % len(self.color_modes)
        elif key == ord('n') or key == ord('N'):
            self.rule_idx = (self.rule_idx + 1) % len(self.rules)
            self.rule = self.rules[self.rule_idx]
        elif key == ord('+') or key == ord('='):
            self.speed = min(10, self.speed + 1)
            self.stdscr.timeout(max(10, 50 // self.speed))
        elif key == ord('-') or key == ord('_'):
            self.speed = max(1, self.speed - 1)
            self.stdscr.timeout(max(10, 50 // self.speed))
        elif key == ord(' ') and self.paused:
            self.step()
        elif key == curses.KEY_RESIZE:
            self.handle_resize()
        return True
    
    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.height -= 2
        self.width -= 2
        self.seed_random()
    
    def run(self):
        while True:
            for _ in range(self.speed):
                self.step()
            self.draw()
            key = self.stdscr.getch()
            if key != -1:
                if not self.handle_input(key):
                    break


def main(stdscr):
    kal = Kaleidoscope(stdscr)
    kal.run()


if __name__ == '__main__':
    curses.wrapper(main)