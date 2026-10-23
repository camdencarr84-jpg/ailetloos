#!/usr/bin/env python3
"""
Cellular Automata Laboratory - Multiple Rule Sets
"""

import curses
import random
import time

class CellularLab:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 16):
            curses.init_pair(i, i % 7 + 1, -1)
            
        self.grid_w = self.width - 2
        self.grid_h = self.height - 6
        self.grid = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.next_grid = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        
        self.rules = {
            'Conway': {'birth': [3], 'survive': [2, 3], 'states': 2},
            'HighLife': {'birth': [3, 6], 'survive': [2, 3], 'states': 2},
            'DayNight': {'birth': [3, 6, 7, 8], 'survive': [3, 4, 6, 7, 8], 'states': 2},
            'Morley': {'birth': [3, 6, 8], 'survive': [2, 3, 4, 5], 'states': 2},
            'Replicator': {'birth': [1, 3, 5, 7], 'survive': [1, 3, 5, 7], 'states': 2},
            'Seeds': {'birth': [2], 'survive': [], 'states': 2},
            'Maze': {'birth': [3], 'survive': [1, 2, 3, 4, 5], 'states': 2},
            'Brian\'s Brain': {'birth': [2], 'survive': [], 'states': 3},
            'WireWorld': {'birth': [], 'survive': [], 'states': 4, 'special': 'wireworld'},
            'Langton\'s Ant': {'special': 'langton', 'states': 2},
        }
        
        self.rule_names = list(self.rules.keys())
        self.current_rule = 0
        self.rule = self.rules[self.rule_names[self.current_rule]]
        self.running = True
        self.generation = 0
        self.brush = 1
        self.brush_size = 1
        
        self.ant_x = self.grid_w // 2
        self.ant_y = self.grid_h // 2
        self.ant_dir = 0
        
        self.randomize()
        
    def randomize(self, density=0.3):
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                if self.rule['states'] == 2:
                    self.grid[y][x] = 1 if random.random() < density else 0
                elif self.rule['states'] == 3:
                    self.grid[y][x] = random.choice([0, 1, 2]) if random.random() < density else 0
                elif self.rule['states'] == 4:
                    self.grid[y][x] = random.choice([0, 1, 2, 3]) if random.random() < density else 0
                    
    def count_neighbors(self, x, y, state=1):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.grid_w
                ny = (y + dy) % self.grid_h
                if self.grid[ny][nx] == state:
                    count += 1
        return count
        
    def count_neighbors_any(self, x, y):
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.grid_w
                ny = (y + dy) % self.grid_h
                if self.grid[ny][nx] != 0:
                    count += 1
        return count
        
    def step_conway_like(self):
        birth = self.rule['birth']
        survive = self.rule['survive']
        
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                neighbors = self.count_neighbors_any(x, y)
                cell = self.grid[y][x]
                
                if cell == 0:
                    if neighbors in birth:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 0
                else:
                    if neighbors in survive:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 0
                        
    def step_brians_brain(self):
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                cell = self.grid[y][x]
                if cell == 0:
                    neighbors = self.count_neighbors(x, y, 1)
                    if neighbors == 2:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 0
                elif cell == 1:
                    self.next_grid[y][x] = 2
                elif cell == 2:
                    self.next_grid[y][x] = 0
                    
    def step_wireworld(self):
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                cell = self.grid[y][x]
                if cell == 0:
                    self.next_grid[y][x] = 0
                elif cell == 1:
                    self.next_grid[y][x] = 2
                elif cell == 2:
                    self.next_grid[y][x] = 3
                elif cell == 3:
                    neighbors = self.count_neighbors(x, y, 1)
                    if neighbors in [1, 2]:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 3
                        
    def step_langton(self):
        self.next_grid = [row[:] for row in self.grid]
        
        for _ in range(10):
            cell = self.grid[self.ant_y][self.ant_x]
            if cell == 0:
                self.ant_dir = (self.ant_dir + 1) % 4
                self.next_grid[self.ant_y][self.ant_x] = 1
            else:
                self.ant_dir = (self.ant_dir - 1) % 4
                self.next_grid[self.ant_y][self.ant_x] = 0
                
            if self.ant_dir == 0:
                self.ant_y = (self.ant_y - 1) % self.grid_h
            elif self.ant_dir == 1:
                self.ant_x = (self.ant_x + 1) % self.grid_w
            elif self.ant_dir == 2:
                self.ant_y = (self.ant_y + 1) % self.grid_h
            else:
                self.ant_x = (self.ant_x - 1) % self.grid_w
                
    def step(self):
        special = self.rule.get('special', '')
        
        if special == 'wireworld':
            self.step_wireworld()
        elif special == 'langton':
            self.step_langton()
        else:
            self.step_conway_like()
            
        self.grid, self.next_grid = self.next_grid, self.grid
        self.generation += 1
        
    def handle_input(self):
        key = self.stdscr.getch()
        if key in (ord('q'), 27):
            return False
        elif key == ord(' '):
            self.running = not self.running
        elif key == ord('r'):
            self.randomize()
        elif key == ord('c'):
            self.grid = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]
            self.generation = 0
            if 'langton' in str(self.rule.get('special', '')):
                self.ant_x = self.grid_w // 2
                self.ant_y = self.grid_h // 2
                self.ant_dir = 0
        elif key == ord('n'):
            self.current_rule = (self.current_rule + 1) % len(self.rule_names)
            self.rule = self.rules[self.rule_names[self.current_rule]]
            self.randomize()
            self.generation = 0
        elif key == ord('p'):
            self.current_rule = (self.current_rule - 1) % len(self.rule_names)
            self.rule = self.rules[self.rule_names[self.current_rule]]
            self.randomize()
            self.generation = 0
        elif key == ord('g'):
            self.add_glider()
        elif key == ord('o'):
            self.add_oscillator()
        elif key == ord('+'):
            self.stdscr.timeout(max(10, self.stdscr.timeout() - 10))
        elif key == ord('-'):
            self.stdscr.timeout(self.stdscr.timeout() + 10)
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, bstate = curses.getmouse()
            if bstate & curses.BUTTON1_PRESSED:
                gx, gy = mx - 1, my - 2
                if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
                    self.grid[gy][gx] = self.brush
            elif bstate & curses.BUTTON3_PRESSED:
                gx, gy = mx - 1, my - 2
                if 0 <= gx < self.grid_w and 0 <= gy < self.grid_h:
                    self.grid[gy][gx] = 0
        elif key >= ord('0') and key <= ord('9'):
            self.brush = key - ord('0')
            if self.brush >= self.rule['states']:
                self.brush = self.rule['states'] - 1
        return True
        
    def add_glider(self):
        cx, cy = self.grid_w // 2, self.grid_h // 2
        pattern = [(0,1), (1,2), (2,0), (2,1), (2,2)]
        for dx, dy in pattern:
            x = (cx + dx) % self.grid_w
            y = (cy + dy) % self.grid_h
            self.grid[y][x] = 1
            
    def add_oscillator(self):
        cx, cy = self.grid_w // 2, self.grid_h // 2
        for i in range(3):
            self.grid[cy][(cx + i) % self.grid_w] = 1
            
    def draw(self):
        self.stdscr.erase()
        
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                cell = self.grid[y][x]
                if cell != 0:
                    color = cell % 7 + 1
                    chars = ['·', '█', '◆', '●', '▲', '■', '★']
                    char = chars[min(cell, len(chars)-1)]
                    try:
                        self.stdscr.addch(y + 1, x + 1, char, curses.color_pair(color) | curses.A_BOLD)
                    except curses.error:
                        pass
                        
        if self.rule.get('special') == 'langton':
            try:
                self.stdscr.addch(self.ant_y + 1, self.ant_x + 1, '▲', curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass
                
        rule_name = self.rule_names[self.current_rule]
        info = [
            f" CELLULAR AUTOMATA LAB - {rule_name} ",
            f"Gen: {self.generation} | Rule: {self.rule.get('birth', 'N/A')}/{self.rule.get('survive', 'N/A')} | States: {self.rule['states']} | Brush: {self.brush} | Speed: {110-self.stdscr.timeout()}ms",
            "SPACE=Run/Pause R=Random C=Clear N/P=Next/Prev Rule G=Glider O=Oscillator 0-9=Brush +/-=Speed Click=Draw Q=Quit"
        ]
        for i, line in enumerate(info):
            try:
                self.stdscr.addstr(self.grid_h + 1 + i, 1, line[:self.width-2], curses.color_pair(7) | (curses.A_BOLD if i == 0 else 0))
            except curses.error:
                pass
                
        self.stdscr.refresh()
        
    def run(self):
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        while True:
            if not self.handle_input():
                break
            if self.running:
                self.step()
            self.draw()
            time.sleep(0.01)

def main(stdscr):
    lab = CellularLab(stdscr)
    lab.run()

if __name__ == '__main__':
    curses.wrapper(main)