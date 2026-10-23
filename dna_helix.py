#!/usr/bin/env python3
"""
DNA Helix Animation - Terminal Visualization
"""

import curses
import math
import time
import random

class DNAHelix:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        
        self.angle = 0
        self.radius = min(self.width, self.height) // 4
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.strands = 2
        self.base_pairs = 20
        self.speed = 0.05
        
        self.bases = ['A', 'T', 'G', 'C']
        self.pairs = [('A', 'T'), ('T', 'A'), ('G', 'C'), ('C', 'G')]
        self.sequence = [random.choice(self.pairs) for _ in range(self.base_pairs)]
        
    def draw_helix(self):
        self.stdscr.erase()
        
        for i in range(self.base_pairs):
            z = i - self.base_pairs // 2
            scale = 1.0 - abs(z) * 0.02
            
            for strand in range(self.strands):
                phase = strand * math.pi
                x = self.radius * math.cos(self.angle + phase + z * 0.3) * scale
                y = self.radius * 0.4 * math.sin(self.angle + phase + z * 0.3) * scale
                
                screen_x = int(self.center_x + x)
                screen_y = int(self.center_y + y + z * 1.5)
                
                if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                    color = (i % 6) + 1
                    base = self.sequence[i][strand]
                    try:
                        self.stdscr.addch(screen_y, screen_x, base, curses.color_pair(color) | curses.A_BOLD)
                    except curses.error:
                        pass
                        
            if i < self.base_pairs - 1:
                z2 = (i + 1) - self.base_pairs // 2
                scale2 = 1.0 - abs(z2) * 0.02
                
                for strand in range(self.strands):
                    phase = strand * math.pi
                    x1 = self.radius * math.cos(self.angle + phase + z * 0.3) * scale
                    y1 = self.radius * 0.4 * math.sin(self.angle + phase + z * 0.3) * scale
                    x2 = self.radius * math.cos(self.angle + phase + z2 * 0.3) * scale2
                    y2 = self.radius * 0.4 * math.sin(self.angle + phase + z2 * 0.3) * scale2
                    
                    sx1 = int(self.center_x + x1)
                    sy1 = int(self.center_y + y1 + z * 1.5)
                    sx2 = int(self.center_x + x2)
                    sy2 = int(self.center_y + y2 + z2 * 1.5)
                    
                    self.draw_line(sx1, sy1, sx2, sy2, (i % 6) + 1)
                    
        for i in range(0, self.base_pairs, 2):
            z = i - self.base_pairs // 2
            scale = 1.0 - abs(z) * 0.02
            
            x1 = self.radius * math.cos(self.angle + z * 0.3) * scale
            y1 = self.radius * 0.4 * math.sin(self.angle + z * 0.3) * scale
            x2 = self.radius * math.cos(self.angle + math.pi + z * 0.3) * scale
            y2 = self.radius * 0.4 * math.sin(self.angle + math.pi + z * 0.3) * scale
            
            sx1 = int(self.center_x + x1)
            sy1 = int(self.center_y + y1 + z * 1.5)
            sx2 = int(self.center_x + x2)
            sy2 = int(self.center_y + y2 + z * 1.5)
            
            self.draw_line(sx1, sy1, sx2, sy2, 7)
            
            mid_x = (sx1 + sx2) // 2
            mid_y = (sy1 + sy2) // 2
            if 0 <= mid_x < self.width and 0 <= mid_y < self.height:
                try:
                    pair_str = f"{self.sequence[i][0]}-{self.sequence[i][1]}"
                    self.stdscr.addstr(mid_y, mid_x - 1, pair_str, curses.color_pair(7) | curses.A_BOLD)
                except curses.error:
                    pass
                    
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
                    self.stdscr.addch(y, x, '·', curses.color_pair(color))
                except curses.error:
                    pass
                    
    def draw_info(self):
        info = [
            "DNA DOUBLE HELIX",
            f"Base Pairs: {self.base_pairs}",
            f"Rotation: {math.degrees(self.angle):.0f}°",
            "A↔T  G↔C",
            "Q=Quit  +/-=Speed  R=Randomize"
        ]
        for i, line in enumerate(info):
            try:
                self.stdscr.addstr(i, 2, line, curses.color_pair(7) | curses.A_BOLD)
            except curses.error:
                pass
                
    def update(self):
        self.angle += self.speed
        
    def randomize(self):
        self.sequence = [random.choice(self.pairs) for _ in range(self.base_pairs)]
        
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            elif key == ord('+'):
                self.speed = min(0.2, self.speed + 0.01)
            elif key == ord('-'):
                self.speed = max(0.01, self.speed - 0.01)
            elif key == ord('r'):
                self.randomize()
            self.update()
            self.draw_helix()
            self.draw_info()
            self.stdscr.refresh()
            time.sleep(0.03)

def main(stdscr):
    dna = DNAHelix(stdscr)
    dna.run()

if __name__ == '__main__':
    curses.wrapper(main)