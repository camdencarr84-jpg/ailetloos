#!/usr/bin/env python3
"""
Reaction-Diffusion Simulation (Gray-Scott Model)
Generates beautiful organic patterns that evolve over time.
Press 'r' to reset, 'p' to pause, 's' to save frame, 'q' to quit.
"""

import curses
import random
import time
import math
from dataclasses import dataclass
from typing import List
import colorsys


@dataclass
class Config:
    feed_rate: float = 0.055
    kill_rate: float = 0.062
    diffusion_a: float = 1.0
    diffusion_b: float = 0.5
    dt: float = 1.0


class ReactionDiffusion:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.height -= 2
        self.width -= 2
        
        self.grid_a = [[1.0 for _ in range(self.width)] for _ in range(self.height)]
        self.grid_b = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_a = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_b = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        
        self.config = Config()
        self.paused = False
        self.frame = 0
        self.color_mode = 0
        self.color_modes = ['rainbow', 'fire', 'ocean', 'forest', 'sunset', 'monochrome', 'neon', 'pastel']
        self.show_stats = True
        self.auto_seed = True
        self.seed_timer = 0
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(16)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            self.init_color_pairs()
        
        self.seed_center()
        self.seed_random(5)
    
    def init_color_pairs(self):
        for i in range(1, 256):
            curses.init_pair(i, i, -1)
    
    def get_color(self, value: float, mode: str) -> int:
        value = max(0.0, min(1.0, value))
        
        if mode == 'rainbow':
            hue = value * 0.85
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, value)
        elif mode == 'fire':
            hue = value * 0.1
            sat = 1.0 - value * 0.3
            r, g, b = colorsys.hsv_to_rgb(hue, sat, value)
        elif mode == 'ocean':
            hue = 0.55 + value * 0.15
            sat = 0.7 + value * 0.3
            r, g, b = colorsys.hsv_to_rgb(hue, sat, value)
        elif mode == 'forest':
            hue = 0.25 + value * 0.15
            sat = 0.6 + value * 0.4
            r, g, b = colorsys.hsv_to_rgb(hue, sat, 0.3 + value * 0.7)
        elif mode == 'sunset':
            hue = value * 0.12
            sat = 0.8
            r, g, b = colorsys.hsv_to_rgb(hue, sat, value)
        elif mode == 'monochrome':
            r = g = b = value
        elif mode == 'neon':
            hue = (value * 0.8 + self.frame * 0.002) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        elif mode == 'pastel':
            hue = value * 0.6
            r, g, b = colorsys.hsv_to_rgb(hue, 0.4, 0.6 + value * 0.4)
        else:
            r = g = b = value
        
        r, g, b = int(r * 1000), int(g * 1000), int(b * 1000)
        color_id = 16 + (r // 40) * 36 + (g // 40) * 6 + (b // 40)
        return min(255, max(16, color_id))
    
    def laplacian(self, grid: List[List[float]], y: int, x: int) -> float:
        h, w = self.height, self.width
        val = grid[y][x]
        
        neighbors = (
            grid[(y-1)%h][x] + grid[(y+1)%h][x] +
            grid[y][(x-1)%w] + grid[y][(x+1)%w]
        ) * 0.20
        
        diagonals = (
            grid[(y-1)%h][(x-1)%w] + grid[(y-1)%h][(x+1)%w] +
            grid[(y+1)%h][(x-1)%w] + grid[(y+1)%h][(x+1)%w]
        ) * 0.05
        
        return neighbors + diagonals - val
    
    def seed_center(self):
        cy, cx = self.height // 2, self.width // 2
        radius = min(self.height, self.width) // 10
        for y in range(max(0, cy-radius), min(self.height, cy+radius)):
            for x in range(max(0, cx-radius), min(self.width, cx+radius)):
                if (y-cy)**2 + (x-cx)**2 < radius**2:
                    self.grid_b[y][x] = 1.0
    
    def seed_random(self, count: int):
        for _ in range(count):
            y = random.randint(5, self.height - 6)
            x = random.randint(5, self.width - 6)
            r = random.randint(3, 8)
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    if dy*dy + dx*dx < r*r:
                        ny, nx = (y+dy) % self.height, (x+dx) % self.width
                        self.grid_b[ny][nx] = 1.0
    
    def step(self):
        if self.paused:
            return
        
        c = self.config
        
        for y in range(self.height):
            for x in range(self.width):
                a = self.grid_a[y][x]
                b = self.grid_b[y][x]
                
                laplace_a = self.laplacian(self.grid_a, y, x)
                laplace_b = self.laplacian(self.grid_b, y, x)
                
                reaction = a * b * b
                
                self.next_a[y][x] = a + (c.diffusion_a * laplace_a - reaction + c.feed_rate * (1 - a)) * c.dt
                self.next_b[y][x] = b + (c.diffusion_b * laplace_b + reaction - (c.kill_rate + c.feed_rate) * b) * c.dt
                
                self.next_a[y][x] = max(0.0, min(1.0, self.next_a[y][x]))
                self.next_b[y][x] = max(0.0, min(1.0, self.next_b[y][x]))
        
        self.grid_a, self.next_a = self.next_a, self.grid_a
        self.grid_b, self.next_b = self.next_b, self.grid_b
        
        self.frame += 1
        self.seed_timer += 1
        
        if self.auto_seed and self.seed_timer > 300:
            self.seed_random(1)
            self.seed_timer = 0
    
    def draw(self):
        self.stdscr.erase()
        
        mode = self.color_modes[self.color_mode]
        
        for y in range(self.height):
            for x in range(self.width):
                b = self.grid_b[y][x]
                
                if b > 0.01:
                    color = self.get_color(b, mode)
                    char = self.get_char(b)
                    try:
                        self.stdscr.addstr(y, x, char, curses.color_pair(color))
                    except curses.error:
                        pass
        
        if self.show_stats:
            self.draw_stats(mode)
        
        self.stdscr.refresh()
    
    def get_char(self, value: float) -> str:
        if value < 0.1:
            return ' '
        elif value < 0.2:
            return '·'
        elif value < 0.3:
            return '◦'
        elif value < 0.4:
            return '●'
        elif value < 0.5:
            return '◉'
        elif value < 0.6:
            return '◎'
        elif value < 0.7:
            return '⊙'
        elif value < 0.8:
            return '◯'
        elif value < 0.9:
            return '⬤'
        else:
            return '█'
    
    def draw_stats(self, mode: str):
        try:
            stats = [
                f" Mode: {mode.upper()} ",
                f" Frame: {self.frame} ",
                f" F: {self.config.feed_rate:.4f} K: {self.config.kill_rate:.4f} ",
                f" Da: {self.config.diffusion_a:.1f} Db: {self.config.diffusion_b:.1f} ",
                f" {'PAUSED' if self.paused else 'RUNNING'} ",
            ]
            
            for i, stat in enumerate(stats):
                self.stdscr.addstr(self.height + 1, i * 22, stat, curses.color_pair(240) | curses.A_BOLD)
            
            help_text = " [r]eset [p]ause [s]ave [c]olor [+/-]feed [</>]kill [d/D]iffusion [a]uto-seed [h]ide stats [q]uit"
            self.stdscr.addstr(self.height + 1, max(0, self.width - len(help_text)), help_text, curses.color_pair(240))
        except curses.error:
            pass
    
    def handle_input(self, key: int):
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('r') or key == ord('R'):
            self.reset()
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('c') or key == ord('C'):
            self.color_mode = (self.color_mode + 1) % len(self.color_modes)
        elif key == ord('h') or key == ord('H'):
            self.show_stats = not self.show_stats
        elif key == ord('a') or key == ord('A'):
            self.auto_seed = not self.auto_seed
        elif key == ord('+') or key == ord('='):
            self.config.feed_rate = min(0.1, self.config.feed_rate + 0.001)
        elif key == ord('-') or key == ord('_'):
            self.config.feed_rate = max(0.01, self.config.feed_rate - 0.001)
        elif key == ord('>') or key == ord('.'):
            self.config.kill_rate = min(0.1, self.config.kill_rate + 0.001)
        elif key == ord('<') or key == ord(','):
            self.config.kill_rate = max(0.01, self.config.kill_rate - 0.001)
        elif key == ord('d'):
            self.config.diffusion_a = min(2.0, self.config.diffusion_a + 0.05)
        elif key == ord('D'):
            self.config.diffusion_a = max(0.1, self.config.diffusion_a - 0.05)
        elif key == ord('b'):
            self.config.diffusion_b = min(2.0, self.config.diffusion_b + 0.05)
        elif key == ord('B'):
            self.config.diffusion_b = max(0.1, self.config.diffusion_b - 0.05)
        elif key == ord('s') or key == ord('S'):
            self.save_frame()
        elif key == ord(' '):
            self.seed_random(3)
        elif key == curses.KEY_RESIZE:
            self.handle_resize()
        return True
    
    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.height -= 2
        self.width -= 2
        self.reset()
    
    def reset(self):
        self.grid_a = [[1.0 for _ in range(self.width)] for _ in range(self.height)]
        self.grid_b = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_a = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_b = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.frame = 0
        self.seed_center()
        self.seed_random(5)
    
    def save_frame(self):
        filename = f"rd_frame_{self.frame:06d}.txt"
        try:
            with open(filename, 'w') as f:
                mode = self.color_modes[self.color_mode]
                f.write(f"Reaction-Diffusion Frame {self.frame}\n")
                f.write(f"Mode: {mode}\n")
                f.write(f"Feed: {self.config.feed_rate}, Kill: {self.config.kill_rate}\n")
                f.write(f"Diffusion A: {self.config.diffusion_a}, B: {self.config.diffusion_b}\n\n")
                for y in range(self.height):
                    line = ''
                    for x in range(self.width):
                        line += self.get_char(self.grid_b[y][x])
                    f.write(line + '\n')
        except Exception:
            pass
    
    def run(self):
        while True:
            self.step()
            self.draw()
            key = self.stdscr.getch()
            if key != -1:
                if not self.handle_input(key):
                    break


def main(stdscr):
    rd = ReactionDiffusion(stdscr)
    rd.run()


if __name__ == '__main__':
    curses.wrapper(main)