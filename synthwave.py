#!/usr/bin/env python3
"""
Synthwave Grid - Retro Terminal Animation
"""

import curses
import math
import time
import random

class SynthwaveGrid:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_BLUE, -1)
        curses.init_pair(6, curses.COLOR_WHITE, -1)
        
        self.time = 0
        self.grid_size = 20
        self.horizon = self.height // 2
        self.sun_y = self.horizon - 5
        self.sun_x = self.width // 2
        self.particles = []
        self.scanline = 0
        self.scanline_dir = 1
        
    def generate_grid_points(self):
        points = []
        for z in range(0, 100, self.grid_size):
            row = []
            for x in range(-self.width, self.width * 2, self.grid_size):
                px = x
                pz = z + self.time * 50
                row.append((px, pz))
            points.append(row)
        return points
        
    def project(self, x, z):
        if z <= 0:
            return None
        fov = self.width * 0.5
        px = int(self.width // 2 + (x * fov) / z)
        py = int(self.horizon - (self.horizon * 0.8) / (z * 0.01 + 1))
        return px, py, z
        
    def draw_sun(self):
        for r in range(15, 0, -1):
            color = 1 if r > 10 else (3 if r > 5 else 6)
            for angle in range(0, 360, 10):
                x = int(self.sun_x + r * math.cos(math.radians(angle)))
                y = int(self.sun_y + r * math.sin(math.radians(angle)) * 0.5)
                if 0 <= x < self.width and 0 <= y < self.height:
                    try:
                        self.stdscr.addch(y, x, '●', curses.color_pair(color))
                    except curses.error:
                        pass
                        
    def draw_grid(self):
        grid = self.generate_grid_points()
        
        for row_idx, row in enumerate(grid):
            prev = None
            for px, pz in row:
                proj = self.project(px, pz)
                if proj:
                    x, y, z = proj
                    if 0 <= x < self.width and 0 <= y < self.height:
                        color = 1 if row_idx % 2 == 0 else 2
                        if z < 100:
                            color = 4
                        try:
                            self.stdscr.addch(y, x, '▓', curses.color_pair(color))
                        except curses.error:
                            pass
                    if prev:
                        px2, py2, _ = self.project(*prev) if self.project(*prev) else (0,0,0)
                        if proj and self.project(*prev):
                            x2, y2, _ = self.project(*prev)
                            self.draw_line(x2, y2, x, y, color)
                    prev = (px, pz)
                    
        for col in range(len(grid[0])):
            prev = None
            for row in grid:
                px, pz = row[col]
                proj = self.project(px, pz)
                if proj:
                    x, y, z = proj
                    if prev and self.project(*prev):
                        x2, y2, _ = self.project(*prev)
                        color = 1 if col % 2 == 0 else 2
                        self.draw_line(x2, y2, x, y, color)
                    prev = (px, pz)
                    
    def draw_line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy)
        if steps == 0:
            return
        for i in range(steps + 1):
            t = i / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < self.width and 0 <= y < self.height:
                try:
                    self.stdscr.addch(y, x, '═' if dx > dy else '║', curses.color_pair(color))
                except curses.error:
                    pass
                    
    def update_particles(self):
        if random.random() < 0.3:
            self.particles.append({
                'x': random.randint(0, self.width - 1),
                'y': random.randint(0, self.horizon),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(0.2, 1.0),
                'life': random.randint(50, 150),
                'char': random.choice(['★', '✦', '✧', '·', '•']),
                'color': random.randint(1, 6)
            })
            
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0 or p['y'] >= self.height:
                self.particles.remove(p)
                
    def draw_particles(self):
        for p in self.particles:
            if 0 <= p['x'] < self.width and 0 <= p['y'] < self.height:
                try:
                    self.stdscr.addch(int(p['y']), int(p['x']), p['char'], curses.color_pair(p['color']) | curses.A_BOLD)
                except curses.error:
                    pass
                    
    def draw_scanlines(self):
        self.scanline += self.scanline_dir * 2
        if self.scanline >= self.height:
            self.scanline = 0
        for x in range(0, self.width, 4):
            try:
                self.stdscr.addch(self.scanline, x, '░', curses.color_pair(6) | curses.A_DIM)
            except curses.error:
                pass
                
    def draw_text(self):
        texts = [
            ("SYNTHWAVE GRID", self.width // 2 - 7, 2, 6),
            ("RETRO TERMINAL", self.width // 2 - 7, 4, 3),
            ("▲ ▼ ▲ ▼ ▲", self.width // 2 - 5, self.height - 3, 1),
        ]
        for text, x, y, color in texts:
            try:
                self.stdscr.addstr(y, x, text, curses.color_pair(color) | curses.A_BOLD)
            except curses.error:
                pass
                
    def update(self):
        self.time += 0.01
        self.sun_x += math.sin(self.time * 0.5) * 0.5
        self.update_particles()
        
    def render(self):
        self.stdscr.erase()
        self.draw_sun()
        self.draw_grid()
        self.draw_particles()
        self.draw_scanlines()
        self.draw_text()
        
        info = "SYNTHWAVE GRID | Q=Quit | [ ]=Speed"
        try:
            self.stdscr.addstr(self.height - 1, 0, info[:self.width-1], curses.color_pair(6))
        except curses.error:
            pass
        self.stdscr.refresh()
        
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            elif key == ord('['):
                pass
            elif key == ord(']'):
                pass
            self.update()
            self.render()
            time.sleep(0.02)

def main(stdscr):
    grid = SynthwaveGrid(stdscr)
    grid.run()

if __name__ == '__main__':
    curses.wrapper(main)