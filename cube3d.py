#!/usr/bin/env python3
"""
3D Rotating Cube - Terminal Animation
"""

import curses
import math
import time

class Cube3D:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
            
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        self.distance = 20
        self.scale = min(self.width, self.height) * 0.3
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        
        self.edges = [
            [0,1], [1,2], [2,3], [3,0],
            [4,5], [5,6], [6,7], [7,4],
            [0,4], [1,5], [2,6], [3,7]
        ]
        
        self.faces = [
            [0,1,2,3], [4,5,6,7], [0,1,5,4],
            [2,3,7,6], [0,3,7,4], [1,2,6,5]
        ]
        
        self.chars = " .:-=+*#%@"
        
    def rotate_x(self, x, y, z, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        y_new = y * cos_a - z * sin_a
        z_new = y * sin_a + z * cos_a
        return x, y_new, z_new
        
    def rotate_y(self, x, y, z, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x_new = x * cos_a + z * sin_a
        z_new = -x * sin_a + z * cos_a
        return x_new, y, z_new
        
    def rotate_z(self, x, y, z, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        x_new = x * cos_a - y * sin_a
        y_new = x * sin_a + y * cos_a
        return x_new, y_new, z
        
    def project(self, x, y, z):
        z += self.distance
        if z == 0:
            z = 0.001
        f = self.scale / z
        x_proj = int(self.center_x + x * f)
        y_proj = int(self.center_y - y * f * 0.5)
        return x_proj, y_proj, z
        
    def draw_line(self, x1, y1, x2, y2, color=1):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            if 0 <= x1 < self.width and 0 <= y1 < self.height - 1:
                try:
                    self.stdscr.addch(y1, x1, '█', curses.color_pair(color))
                except curses.error:
                    pass
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
    def update(self):
        self.angle_x += 0.02
        self.angle_y += 0.03
        self.angle_z += 0.01
        
    def render(self):
        self.stdscr.erase()
        
        rotated = []
        for v in self.vertices:
            x, y, z = v
            x, y, z = self.rotate_x(x, y, z, self.angle_x)
            x, y, z = self.rotate_y(x, y, z, self.angle_y)
            x, y, z = self.rotate_z(x, y, z, self.angle_z)
            rotated.append((x, y, z))
            
        projected = []
        for v in rotated:
            projected.append(self.project(*v))
            
        for i, edge in enumerate(self.edges):
            p1 = projected[edge[0]]
            p2 = projected[edge[1]]
            color = (i % 6) + 1
            self.draw_line(p1[0], p1[1], p2[0], p2[1], color)
            
        for i, v in enumerate(projected):
            if 0 <= v[0] < self.width and 0 <= v[1] < self.height - 1:
                try:
                    self.stdscr.addch(v[1], v[0], '●', curses.color_pair((i % 6) + 1) | curses.A_BOLD)
                except curses.error:
                    pass
                    
        info = f"3D Cube | Angles: X={self.angle_x:.2f} Y={self.angle_y:.2f} Z={self.angle_z:.2f} | Q=Quit"
        try:
            self.stdscr.addstr(self.height - 1, 0, info[:self.width-1], curses.color_pair(7))
        except curses.error:
            pass
            
        self.stdscr.refresh()
        
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            self.update()
            self.render()
            time.sleep(0.02)

def main(stdscr):
    cube = Cube3D(stdscr)
    cube.run()

if __name__ == '__main__':
    curses.wrapper(main)