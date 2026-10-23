#!/usr/bin/env python3
"""
Gravity Simulator - Planetary Orbits with Trails
"""

import curses
import math
import random
import time

class Body:
    def __init__(self, x, y, vx, vy, mass, color, char, name, trail_color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.color = color
        self.char = char
        self.name = name
        self.trail = []
        self.max_trail = 100
        self.trail_color = trail_color or color
        
    def update_position(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
    def apply_force(self, fx, fy, dt):
        ax = fx / self.mass
        ay = fy / self.mass
        self.vx += ax * dt
        self.vy += ay * dt

class GravitySim:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)   # Sun
        curses.init_pair(2, curses.COLOR_BLUE, -1)     # Earth
        curses.init_pair(3, curses.COLOR_RED, -1)      # Mars
        curses.init_pair(4, curses.COLOR_GREEN, -1)    # Venus
        curses.init_pair(5, curses.COLOR_CYAN, -1)     # Mercury
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)  # Jupiter
        curses.init_pair(7, curses.COLOR_WHITE, -1)    # Text
        curses.init_pair(8, 8, -1)                     # Trail dim
        
        self.G = 100.0
        self.dt = 0.1
        self.paused = False
        self.show_trails = True
        self.show_vectors = False
        self.time_scale = 1.0
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
        self.bodies = []
        self.create_solar_system()
        
    def create_solar_system(self):
        cx, cy = self.width // 2, self.height // 2
        
        self.bodies.append(Body(cx, cy, 0, 0, 1000, 1, '☀', 'SUN', 1))
        
        planets = [
            (50, 0, 0, 2.5, 1, 5, '☿', 'MERCURY', 5),
            (80, 0, 0, 2.0, 2, 4, '♀', 'VENUS', 4),
            (120, 0, 0, 1.6, 5, 2, '♁', 'EARTH', 2),
            (160, 0, 0, 1.3, 1, 3, '♂', 'MARS', 3),
            (250, 0, 0, 0.8, 100, 6, '♃', 'JUPITER', 6),
        ]
        
        for r, vx, vy, mass, color, char, name, trail_color in planets:
            angle = random.uniform(0, 2 * math.pi)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            vx_rot = -vy * math.sin(angle) + vx * math.cos(angle)
            vy_rot = vy * math.cos(angle) + vx * math.sin(angle)
            self.bodies.append(Body(x, y, vx_rot, vy_rot, mass, color, char, name, trail_color))
            
        for _ in range(20):
            r = random.uniform(300, 500)
            angle = random.uniform(0, 2 * math.pi)
            speed = math.sqrt(self.G * 1000 / r) * 0.5
            self.bodies.append(Body(
                cx + r * math.cos(angle),
                cy + r * math.sin(angle),
                -speed * math.sin(angle),
                speed * math.cos(angle),
                0.1, 7, '·', 'ASTEROID', 8
            ))
            
    def compute_forces(self):
        for i, b1 in enumerate(self.bodies):
            fx, fy = 0, 0
            for j, b2 in enumerate(self.bodies):
                if i == j:
                    continue
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist_sq = dx*dx + dy*dy + 100
                dist = math.sqrt(dist_sq)
                force = self.G * b1.mass * b2.mass / dist_sq
                fx += force * dx / dist
                fy += force * dy / dist
            b1.apply_force(fx, fy, self.dt * self.time_scale)
            
    def update(self):
        if not self.paused:
            self.compute_forces()
            for b in self.bodies:
                b.update_position(self.dt * self.time_scale)
                
    def world_to_screen(self, x, y):
        sx = int((x - self.camera_x) * self.zoom + self.width // 2)
        sy = int((y - self.camera_y) * self.zoom + self.height // 2)
        return sx, sy
        
    def draw_trail(self, body):
        if not self.show_trails or len(body.trail) < 2:
            return
        for i in range(1, len(body.trail)):
            x1, y1 = self.world_to_screen(*body.trail[i-1])
            x2, y2 = self.world_to_screen(*body.trail[i])
            if 0 <= x1 < self.width and 0 <= y1 < self.height:
                alpha = i / len(body.trail)
                if alpha > 0.3:
                    try:
                        self.stdscr.addch(y1, x1, '·', curses.color_pair(body.trail_color) | curses.A_DIM)
                    except curses.error:
                        pass
                        
    def draw_body(self, body):
        sx, sy = self.world_to_screen(body.x, body.y)
        if 0 <= sx < self.width and 0 <= sy < self.height:
            size = max(1, int(math.log10(body.mass) * 2))
            try:
                self.stdscr.addch(sy, sx, body.char, curses.color_pair(body.color) | curses.A_BOLD)
                if body.mass > 10:
                    self.stdscr.addstr(sy - 1, sx - len(body.name)//2, body.name, curses.color_pair(7))
            except curses.error:
                pass
                
            if self.show_vectors:
                vx_s, vy_s = self.world_to_screen(body.x + body.vx * 10, body.y + body.vy * 10)
                try:
                    self.stdscr.addch(vy_s, vx_s, '→', curses.color_pair(3))
                except curses.error:
                    pass
                    
    def handle_input(self):
        key = self.stdscr.getch()
        if key in (ord('q'), 27):
            return False
        elif key == ord(' '):
            self.paused = not self.paused
        elif key == ord('t'):
            self.show_trails = not self.show_trails
        elif key == ord('v'):
            self.show_vectors = not self.show_vectors
        elif key == ord('+'):
            self.time_scale = min(5.0, self.time_scale * 1.2)
        elif key == ord('-'):
            self.time_scale = max(0.1, self.time_scale / 1.2)
        elif key == ord('r'):
            self.create_solar_system()
        elif key == ord('w'):
            self.camera_y -= 20 / self.zoom
        elif key == ord('s'):
            self.camera_y += 20 / self.zoom
        elif key == ord('a'):
            self.camera_x -= 20 / self.zoom
        elif key == ord('d'):
            self.camera_x += 20 / self.zoom
        elif key == ord('z'):
            self.zoom = min(3.0, self.zoom * 1.1)
        elif key == ord('x'):
            self.zoom = max(0.3, self.zoom / 1.1)
        return True
        
    def render(self):
        self.stdscr.erase()
        
        for b in self.bodies:
            self.draw_trail(b)
            
        for b in self.bodies:
            self.draw_body(b)
            
        info = [
            " GRAVITY SIMULATOR ",
            f"Time: {self.time_scale:.1f}x | {'PAUSED' if self.paused else 'RUNNING'}",
            f"Bodies: {len(self.bodies)}",
            "SPACE=Pause T=Trails V=Vectors +/-=Time WASD=Pan Z/X=Zoom R=Reset Q=Quit"
        ]
        for i, line in enumerate(info):
            try:
                self.stdscr.addstr(i, 2, line, curses.color_pair(7) | (curses.A_BOLD if i == 0 else 0))
            except curses.error:
                pass
                
        self.stdscr.refresh()
        
    def run(self):
        while True:
            if not self.handle_input():
                break
            self.update()
            self.render()
            time.sleep(0.02)

def main(stdscr):
    sim = GravitySim(stdscr)
    sim.run()

if __name__ == '__main__':
    curses.wrapper(main)