#!/usr/bin/env python3
"""
Raycaster 3D Engine - Wolfenstein-style FPS in Terminal
"""

import curses
import math
import time

class Raycaster:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        
        self.map_width = 16
        self.map_height = 16
        self.map_data = [
            "################",
            "#..............#",
            "#..............#",
            "#....####......#",
            "#....#..#......#",
            "#....#..#......#",
            "#....####......#",
            "#..............#",
            "#..............#",
            "#......##......#",
            "#......##......#",
            "#..............#",
            "#..............#",
            "#....########..#",
            "#..............#",
            "################",
        ]
        
        self.player_x = 2.5
        self.player_y = 2.5
        self.player_angle = 0
        self.fov = math.pi / 3
        self.max_depth = 20
        self.move_speed = 0.1
        self.rot_speed = 0.05
        
        self.shades = " ░▒▓█"
        self.wall_colors = {
            '#': [1, 2, 3, 4, 5, 6],
        }
        
    def cast_ray(self, angle):
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        for depth in range(int(self.max_depth * 10)):
            d = depth / 10.0
            x = self.player_x + cos_a * d
            y = self.player_y + sin_a * d
            
            mx, my = int(x), int(y)
            
            if 0 <= mx < self.map_width and 0 <= my < self.map_height:
                if self.map_data[my][mx] == '#':
                    hit_x = x - mx
                    hit_y = y - my
                    return d, '#', hit_x, hit_y
                    
        return self.max_depth, ' ', 0, 0
        
    def update(self):
        key = self.stdscr.getch()
        
        new_x, new_y = self.player_x, self.player_y
        
        if key == ord('w'):
            new_x += math.cos(self.player_angle) * self.move_speed
            new_y += math.sin(self.player_angle) * self.move_speed
        elif key == ord('s'):
            new_x -= math.cos(self.player_angle) * self.move_speed
            new_y -= math.sin(self.player_angle) * self.move_speed
        elif key == ord('a'):
            self.player_angle -= self.rot_speed
        elif key == ord('d'):
            self.player_angle += self.rot_speed
        elif key in (ord('q'), 27):
            return False
            
        mx, my = int(new_x), int(new_y)
        if 0 <= mx < self.map_width and 0 <= my < self.map_height:
            if self.map_data[my][mx] != '#':
                self.player_x, self.player_y = new_x, new_y
                
        return True
        
    def render(self):
        self.stdscr.erase()
        
        half_height = self.height // 2
        
        for col in range(self.width):
            ray_angle = self.player_angle - self.fov/2 + (col / self.width) * self.fov
            distance, wall_type, hit_x, hit_y = self.cast_ray(ray_angle)
            
            distance *= math.cos(ray_angle - self.player_angle)
            
            wall_height = int(self.height / (distance + 0.1))
            
            start = max(0, half_height - wall_height // 2)
            end = min(self.height - 1, half_height + wall_height // 2)
            
            shade_idx = min(len(self.shades) - 1, int(distance / self.max_depth * (len(self.shades) - 1)))
            shade = self.shades[shade_idx]
            
            color = 7
            if wall_type == '#':
                color = self.wall_colors['#'][int(hit_x * 6) % 6]
                
            for row in range(start, end):
                try:
                    self.stdscr.addch(row, col, shade, curses.color_pair(color))
                except curses.error:
                    pass
                    
        try:
            self.stdscr.addstr(0, 0, " WASD=Move Q=Quit | Raycaster 3D Engine ", curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass
            
        self.stdscr.refresh()
        
    def run(self):
        while True:
            if not self.update():
                break
            self.render()
            time.sleep(0.02)

def main(stdscr):
    game = Raycaster(stdscr)
    game.run()

if __name__ == '__main__':
    curses.wrapper(main)