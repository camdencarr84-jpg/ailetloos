#!/usr/bin/env python3
"""
Flow Field Particle Visualization
Particles follow Perlin-noise-like vector fields creating organic, flowing patterns.
Press 'r' to reset, 'p' to pause, 'c' to cycle color schemes, 'q' to quit.
"""

import curses
import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    hue: float
    life: float
    max_life: float
    size: int
    trail: List[Tuple[float, float]]


@dataclass
class FlowField:
    width: int
    height: int
    scale: float
    time_offset: float
    angles: List[List[float]]
    
    def __init__(self, width: int, height: int, scale: float = 0.02):
        self.width = width
        self.height = height
        self.scale = scale
        self.time_offset = 0.0
        self.angles = [[0.0 for _ in range(width)] for _ in range(height)]
    
    def update(self, dt: float):
        self.time_offset += dt * 0.1
        for y in range(self.height):
            for x in range(self.width):
                nx = x * self.scale
                ny = y * self.scale
                nz = self.time_offset
                
                angle = self.noise3d(nx, ny, nz) * 4 * math.pi
                self.angles[y][x] = angle
    
    def get_angle(self, x: float, y: float) -> float:
        x = int(x) % self.width
        y = int(y) % self.height
        if x < 0: x += self.width
        if y < 0: y += self.height
        return self.angles[y][x]
    
    def noise3d(self, x: float, y: float, z: float) -> float:
        return self._perlin3d(x, y, z)
    
    def _perlin3d(self, x: float, y: float, z: float) -> float:
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        Z = int(math.floor(z)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)
        
        u = self._fade(x)
        v = self._fade(y)
        w = self._fade(z)
        
        p = self._permutation()
        
        A = p[X] + Y
        AA = p[A] + Z
        AB = p[A + 1] + Z
        B = p[X + 1] + Y
        BA = p[B] + Z
        BB = p[B + 1] + Z
        
        return self._lerp(w,
            self._lerp(v,
                self._lerp(u, self._grad(p[AA], x, y, z),
                           self._grad(p[BA], x - 1, y, z)),
                self._lerp(u, self._grad(p[AB], x, y - 1, z),
                           self._grad(p[BB], x - 1, y - 1, z))),
            self._lerp(v,
                self._lerp(u, self._grad(p[AA + 1], x, y, z - 1),
                           self._grad(p[BA + 1], x - 1, y, z - 1)),
                self._lerp(u, self._grad(p[AB + 1], x, y - 1, z - 1),
                           self._grad(p[BB + 1], x - 1, y - 1, z - 1))))
    
    def _fade(self, t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, t: float, a: float, b: float) -> float:
        return a + t * (b - a)
    
    def _grad(self, hash_val: int, x: float, y: float, z: float) -> float:
        h = hash_val & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h in (12, 14) else z)
        return ((u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v))
    
    def _permutation(self) -> List[int]:
        if not hasattr(self, '_p'):
            p = list(range(256))
            random.shuffle(p)
            self._p = p + p
        return self._p


class FlowFieldVisualization:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.height -= 1
        self.width -= 1
        
        self.field = FlowField(self.width, self.height, 0.015)
        self.particles: List[Particle] = []
        self.max_particles = 800
        self.spawn_rate = 15
        
        self.color_schemes = [
            ('rainbow', lambda p: p.hue),
            ('fire', lambda p: 0.0 + (1.0 - p.life/p.max_life) * 0.1),
            ('ocean', lambda p: 0.5 + p.hue * 0.3),
            ('forest', lambda p: 0.25 + p.hue * 0.2),
            ('sunset', lambda p: p.hue * 0.15),
            ('monochrome', lambda p: 0.0),
            ('neon', lambda p: (p.hue + self.field.time_offset * 0.1) % 1.0),
            ('aurora', lambda p: 0.4 + math.sin(p.hue * 6 + self.field.time_offset) * 0.15),
        ]
        self.color_mode = 0
        self.scheme_name, self.color_func = self.color_schemes[0]
        
        self.paused = False
        self.show_field = False
        self.show_trails = True
        self.trail_length = 8
        self.particle_speed = 1.0
        self.field_scale = 0.015
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(16)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, 256):
                curses.init_pair(i, i, -1)
        
        self.spawn_initial()
    
    def spawn_initial(self):
        for _ in range(self.max_particles // 2):
            self.spawn_particle(
                random.uniform(0, self.width),
                random.uniform(0, self.height)
            )
    
    def spawn_particle(self, x: float = None, y: float = None):
        if x is None:
            x = random.uniform(0, self.width)
        if y is None:
            y = random.uniform(0, self.height)
        
        angle = self.field.get_angle(x, y)
        speed = random.uniform(0.5, 2.0) * self.particle_speed
        
        self.particles.append(Particle(
            x=x, y=y,
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
            hue=random.random(),
            life=random.uniform(200, 600),
            max_life=random.uniform(200, 600),
            size=random.choice([1, 1, 1, 2]),
            trail=[]
        ))
    
    def update(self):
        if self.paused:
            return
        
        self.field.update(1.0)
        
        for _ in range(self.spawn_rate):
            if len(self.particles) < self.max_particles:
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                if edge == 'top':
                    self.spawn_particle(random.uniform(0, self.width), 0)
                elif edge == 'bottom':
                    self.spawn_particle(random.uniform(0, self.width), self.height - 1)
                elif edge == 'left':
                    self.spawn_particle(0, random.uniform(0, self.height))
                else:
                    self.spawn_particle(self.width - 1, random.uniform(0, self.height))
        
        new_particles = []
        for p in self.particles:
            if self.show_trails:
                p.trail.append((p.x, p.y))
                if len(p.trail) > self.trail_length:
                    p.trail.pop(0)
            
            angle = self.field.get_angle(p.x, p.y)
            force = 0.15 * self.particle_speed
            p.vx += math.cos(angle) * force
            p.vy += math.sin(angle) * force
            
            speed = math.hypot(p.vx, p.vy)
            max_speed = 3.0 * self.particle_speed
            if speed > max_speed:
                p.vx = p.vx / speed * max_speed
                p.vy = p.vy / speed * max_speed
            
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            
            if p.life > 0 and -10 < p.x < self.width + 10 and -10 < p.y < self.height + 10:
                new_particles.append(p)
            elif random.random() < 0.3 and len(new_particles) < self.max_particles:
                self.spawn_particle()
        
        self.particles = new_particles
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        h = h % 1.0
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i == 0: r, g, b = v, t, p
        elif i == 1: r, g, b = q, v, p
        elif i == 2: r, g, b = p, v, t
        elif i == 3: r, g, b = p, q, v
        elif i == 4: r, g, b = t, p, v
        else: r, g, b = v, p, q
        
        return int(r * 1000), int(g * 1000), int(b * 1000)
    
    def get_color_pair(self, hue: float, life_ratio: float) -> int:
        name, func = self.color_schemes[self.color_mode]
        h = func(self)
        s = 0.8 + 0.2 * life_ratio
        v = 0.3 + 0.7 * life_ratio
        
        if name == 'monochrome':
            v = life_ratio
            s = 0.0
        
        r, g, b = self.hsv_to_rgb(h, s, v)
        color_id = 16 + (r // 40) * 36 + (g // 40) * 6 + (b // 40)
        return min(255, max(16, color_id))
    
    def draw(self):
        self.stdscr.erase()
        
        if self.show_field:
            self.draw_field()
        
        for p in self.particles:
            life_ratio = p.life / p.max_life
            color = self.get_color_pair(p.hue, life_ratio)
            
            if self.show_trails and len(p.trail) > 1:
                for i, (tx, ty) in enumerate(p.trail):
                    trail_ratio = i / len(p.trail) * life_ratio
                    if trail_ratio < 0.1:
                        continue
                    trail_color = self.get_color_pair(p.hue, trail_ratio * 0.5)
                    trail_char = '·' if trail_ratio < 0.5 else '◦'
                    try:
                        if 0 <= int(ty) < self.height and 0 <= int(tx) < self.width:
                            self.stdscr.addstr(int(ty), int(tx), trail_char, curses.color_pair(trail_color))
                    except curses.error:
                        pass
            
            char = self.get_particle_char(life_ratio, p.size)
            try:
                if 0 <= int(p.y) < self.height and 0 <= int(p.x) < self.width:
                    self.stdscr.addstr(int(p.y), int(p.x), char, curses.color_pair(color) | curses.A_BOLD)
            except curses.error:
                pass
        
        self.draw_ui()
        self.stdscr.refresh()
    
    def get_particle_char(self, life_ratio: float, size: int) -> str:
        if size == 1:
            if life_ratio > 0.8: return '⬤'
            elif life_ratio > 0.5: return '●'
            elif life_ratio > 0.3: return '◉'
            else: return '·'
        else:
            if life_ratio > 0.8: return '█'
            elif life_ratio > 0.5: return '▓'
            elif life_ratio > 0.3: return '▒'
            else: return '░'
    
    def draw_field(self):
        step = 4
        for y in range(0, self.height, step):
            for x in range(0, self.width, step):
                angle = self.field.angles[y][x]
                dx = math.cos(angle) * 1.5
                dy = math.sin(angle) * 1.5
                ex, ey = x + dx, y + dy
                try:
                    if 0 <= int(ey) < self.height and 0 <= int(ex) < self.width:
                        char = '→' if abs(dx) > abs(dy) else '↓'
                        if dx < 0: char = '←'
                        if dy < 0: char = '↑'
                        self.stdscr.addstr(int(y), int(x), char, curses.color_pair(240))
                except curses.error:
                    pass
    
    def draw_ui(self):
        try:
            stats = [
                f" {self.scheme_name.upper()} ",
                f" Particles: {len(self.particles)}/{self.max_particles} ",
                f" Speed: {self.particle_speed:.1f}x ",
                f" Scale: {self.field.scale:.4f} ",
                f" {'PAUSED' if self.paused else 'FLOWING'} ",
            ]
            for i, stat in enumerate(stats):
                self.stdscr.addstr(self.height, i * 20, stat, curses.color_pair(240) | curses.A_BOLD)
            
            help_text = " [r]eset [p]ause [c]olor [f]ield [t]rails [+/-]speed [</>]scale [s]pawn [q]uit"
            self.stdscr.addstr(self.height, max(0, self.width - len(help_text)), help_text, curses.color_pair(240))
        except curses.error:
            pass
    
    def handle_input(self, key: int) -> bool:
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('r') or key == ord('R'):
            self.reset()
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('c') or key == ord('C'):
            self.color_mode = (self.color_mode + 1) % len(self.color_schemes)
            self.scheme_name, self.color_func = self.color_schemes[self.color_mode]
        elif key == ord('f') or key == ord('F'):
            self.show_field = not self.show_field
        elif key == ord('t') or key == ord('T'):
            self.show_trails = not self.show_trails
        elif key == ord('+') or key == ord('='):
            self.particle_speed = min(3.0, self.particle_speed + 0.1)
        elif key == ord('-') or key == ord('_'):
            self.particle_speed = max(0.2, self.particle_speed - 0.1)
        elif key == ord('>') or key == ord('.'):
            self.field.scale = min(0.05, self.field.scale + 0.001)
            self.field.angles = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        elif key == ord('<') or key == ord(','):
            self.field.scale = max(0.005, self.field.scale - 0.001)
            self.field.angles = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        elif key == ord('s') or key == ord('S'):
            for _ in range(20):
                self.spawn_particle()
        elif key == ord('['):
            self.trail_length = max(2, self.trail_length - 1)
        elif key == ord(']'):
            self.trail_length = min(30, self.trail_length + 1)
        elif key == curses.KEY_RESIZE:
            self.handle_resize()
        return True
    
    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.height -= 1
        self.width -= 1
        self.field = FlowField(self.width, self.height, self.field.scale)
        self.reset()
    
    def reset(self):
        self.particles.clear()
        self.field.time_offset = 0.0
        self.field.angles = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.spawn_initial()
    
    def run(self):
        while True:
            self.update()
            self.draw()
            key = self.stdscr.getch()
            if key != -1:
                if not self.handle_input(key):
                    break


def main(stdscr):
    viz = FlowFieldVisualization(stdscr)
    viz.run()


if __name__ == '__main__':
    curses.wrapper(main)