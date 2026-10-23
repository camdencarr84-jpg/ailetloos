#!/usr/bin/env python3
"""
Matrix Digital Rain - Terminal Animation
"""

import curses
import random
import time

class MatrixRain:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_WHITE, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        
        self.columns = []
        self.init_columns()
        
    def init_columns(self):
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
        for x in range(self.width):
            if random.random() < 0.3:
                length = random.randint(5, 20)
                speed = random.uniform(0.3, 1.0)
                self.columns.append({
                    'x': x,
                    'y': random.randint(-self.height, 0),
                    'length': length,
                    'speed': speed,
                    'chars': [random.choice(chars) for _ in range(length)],
                    'counter': 0
                })
                
    def update(self):
        for col in self.columns:
            col['counter'] += col['speed']
            if col['counter'] >= 1:
                col['y'] += int(col['counter'])
                col['counter'] -= int(col['counter'])
                if col['y'] - col['length'] > self.height:
                    col['y'] = random.randint(-20, 0)
                    col['length'] = random.randint(5, 20)
                    col['speed'] = random.uniform(0.3, 1.0)
                    col['chars'] = [random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()") for _ in range(col['length'])]
                    
        if random.random() < 0.02 and len(self.columns) < self.width:
            x = random.randint(0, self.width - 1)
            if not any(c['x'] == x for c in self.columns):
                length = random.randint(5, 20)
                speed = random.uniform(0.3, 1.0)
                self.columns.append({
                    'x': x,
                    'y': random.randint(-self.height, 0),
                    'length': length,
                    'speed': speed,
                    'chars': [random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()") for _ in range(length)],
                    'counter': 0
                })
                
    def draw(self):
        self.stdscr.erase()
        for col in self.columns:
            for i in range(col['length']):
                y = col['y'] - i
                if 0 <= y < self.height - 1:
                    char = col['chars'][i]
                    if i == 0:
                        color = curses.color_pair(2) | curses.A_BOLD
                    elif i < 3:
                        color = curses.color_pair(3) | curses.A_BOLD
                    else:
                        color = curses.color_pair(1)
                    try:
                        self.stdscr.addch(y, col['x'], char, color)
                    except curses.error:
                        pass
        self.stdscr.refresh()
        
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            self.update()
            self.draw()
            time.sleep(0.03)

def main(stdscr):
    rain = MatrixRain(stdscr)
    rain.run()

if __name__ == '__main__':
    curses.wrapper(main)