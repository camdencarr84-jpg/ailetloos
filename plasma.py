#!/usr/bin/env python3
"""
Plasma Effect - Classic Demo Scene Animation
"""

import curses
import math
import time

class Plasma:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 256):
            try:
                curses.init_color(i, 
                    int(500 + 500 * math.sin(i * 0.1)),
                    int(500 + 500 * math.sin(i * 0.1 + 2)),
                    int(500 + 500 * math.sin(i * 0.1 + 4))
                )
                curses.init_pair(i, i, -1)
            except curses.error:
                pass
                
        self.time = 0
        self.palette = self.generate_palette()
        
    def generate_palette(self):
        palette = []
        for i in range(256):
            r = int(128 + 127 * math.sin(i * 0.05))
            g = int(128 + 127 * math.sin(i * 0.05 + 2.1))
            b = int(128 + 127 * math.sin(i * 0.05 + 4.2))
            palette.append((r, g, b))
        return palette
        
    def plasma_value(self, x, y, t):
        v = 0
        v += math.sin(x * 0.1 + t)
        v += math.sin(y * 0.1 + t)
        v += math.sin((x + y) * 0.1 + t)
        v += math.sin(math.sqrt(x*x + y*y) * 0.1 + t)
        v += math.sin(math.sqrt((x - self.width/2)**2 + (y - self.height/2)**2) * 0.1 + t)
        return (v * 32 + 128) % 256
        
    def render(self):
        self.stdscr.erase()
        
        for y in range(self.height - 1):
            line = ""
            for x in range(self.width):
                val = int(self.plasma_value(x, y, self.time))
                try:
                    color = (val % 255) + 1
                    self.stdscr.addch(y, x, '█', curses.color_pair(color))
                except curses.error:
                    pass
                    
        info = " PLASMA EFFECT | Classic Demo Scene | Q=Quit | +/-=Speed | M=Mode"
        try:
            self.stdscr.addstr(self.height - 1, 0, info[:self.width-1], curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass
            
        self.stdscr.refresh()
        
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            self.time += 0.05
            self.render()
            time.sleep(0.02)

def main(stdscr):
    plasma = Plasma(stdscr)
    plasma.run()

if __name__ == '__main__':
    curses.wrapper(main)