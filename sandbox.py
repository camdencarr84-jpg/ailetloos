#!/usr/bin/env python3
"""
INTERACTIVE PARTICLE PLAYGROUND
A fun physics sandbox with multiple particle types, forces, and tools.
"""

import curses
import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Tuple
from enum import Enum

class ParticleType(Enum):
    SAND = 0
    WATER = 1
    FIRE = 2
    SMOKE = 3
    STONE = 4
    WOOD = 5
    ACID = 6
    LAVA = 7
    ICE = 8
    OIL = 9

@dataclass
class Particle:
    x: int
    y: int
    ptype: ParticleType
    vx: float = 0
    vy: float = 0
    temp: float = 20
    life: int = 255
    color_offset: int = 0

class Tool(Enum):
    BRUSH = 0
    ERASER = 1
    WIND = 2
    HEAT = 3
    COOL = 4
    GRAVITY = 5
    EXPLOSION = 6

TOOL_NAMES = {
    Tool.BRUSH: "BRUSH",
    Tool.ERASER: "ERASER",
    Tool.WIND: "WIND",
    Tool.HEAT: "HEAT",
    Tool.COOL: "COOL",
    Tool.GRAVITY: "GRAVITY",
    Tool.EXPLOSION: "EXPLOSION",
}

PARTICLE_PROPS = {
    ParticleType.SAND: {'density': 2.5, 'color_base': 208, 'chars': '▓▒░', 'flammable': False},
    ParticleType.WATER: {'density': 1.0, 'color_base': 27, 'chars': '░▒▓', 'flammable': False},
    ParticleType.FIRE: {'density': 0.1, 'color_base': 196, 'chars': '▲▼◆', 'flammable': False, 'temp': 800},
    ParticleType.SMOKE: {'density': 0.3, 'color_base': 240, 'chars': '·∘○', 'flammable': False},
    ParticleType.STONE: {'density': 5.0, 'color_base': 242, 'chars': '███', 'flammable': False},
    ParticleType.WOOD: {'density': 0.7, 'color_base': 130, 'chars': '▓▓▓', 'flammable': True, 'burn_temp': 300},
    ParticleType.ACID: {'density': 1.2, 'color_base': 118, 'chars': '~~~', 'flammable': False, 'corrosive': True},
    ParticleType.LAVA: {'density': 3.0, 'color_base': 202, 'chars': '▓▓▓', 'flammable': False, 'temp': 1000},
    ParticleType.ICE: {'density': 0.9, 'color_base': 39, 'chars': '░░░', 'flammable': False, 'temp': -50},
    ParticleType.OIL: {'density': 0.8, 'color_base': 234, 'chars': '~~~', 'flammable': True, 'burn_temp': 200},
}

class Sandbox:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.grid_w = self.width - 2
        self.grid_h = self.height - 4
        self.offset_x = 1
        self.offset_y = 2
        
        self.grid: List[List[Optional[Particle]]] = [[None for _ in range(self.grid_w)] for _ in range(self.grid_h)]
        self.particles: List[Particle] = []
        
        self.current_type = ParticleType.SAND
        self.current_tool = Tool.BRUSH
        self.brush_size = 3
        self.paused = False
        self.show_help = True
        self.gravity = 0.5
        self.wind_x = 0
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(16)
        stdscr.keypad(True)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, 256):
                curses.init_pair(i, i, -1)
    
    def in_bounds(self, x, y):
        return 0 <= x < self.grid_w and 0 <= y < self.grid_h
    
    def get_cell(self, x, y):
        if self.in_bounds(x, y):
            return self.grid[y][x]
        return None
    
    def set_cell(self, x, y, particle):
        if self.in_bounds(x, y):
            self.grid[y][x] = particle
    
    def add_particle(self, x, y, ptype, vx=0, vy=0):
        if not self.in_bounds(x, y) or self.get_cell(x, y):
            return
        props = PARTICLE_PROPS[ptype]
        p = Particle(x, y, ptype, vx, vy, props.get('temp', 20))
        p.color_offset = random.randint(-10, 10)
        self.set_cell(x, y, p)
        self.particles.append(p)
    
    def remove_particle(self, x, y):
        p = self.get_cell(x, y)
        if p:
            self.set_cell(x, y, None)
            if p in self.particles:
                self.particles.remove(p)
    
    def move_particle(self, p, nx, ny):
        if self.in_bounds(nx, ny) and not self.get_cell(nx, ny):
            self.set_cell(p.x, p.y, None)
            p.x, p.y = nx, ny
            self.set_cell(nx, ny, p)
            return True
        return False
    
    def swap_particles(self, p1, p2):
        self.grid[p1.y][p1.x], self.grid[p2.y][p2.x] = p2, p1
        p1.x, p1.y, p2.x, p2.y = p2.x, p2.y, p1.x, p1.y
    
    def try_move_down(self, p):
        if self.move_particle(p, p.x, p.y + 1):
            return True
        for dx in [-1, 1]:
            if self.move_particle(p, p.x + dx, p.y + 1):
                return True
        return False
    
    def try_move_side(self, p, dx):
        if self.move_particle(p, p.x + dx, p.y):
            return True
        if self.move_particle(p, p.x + dx, p.y + 1):
            return True
        return False
    
    def update_sand(self, p):
        if not self.try_move_down(p):
            p.vx *= 0.5
    
    def update_water(self, p):
        p.vx += self.wind_x * 0.1
        moved = False
        if random.random() < 0.7:
            moved = self.try_move_down(p)
        if not moved:
            dx = 1 if p.vx > 0 else -1 if p.vx < 0 else random.choice([-1, 1])
            moved = self.try_move_side(p, dx)
        if not moved and random.random() < 0.3:
            dx = random.choice([-1, 1])
            self.try_move_side(p, dx)
        p.vx *= 0.9
    
    def update_fire(self, p):
        p.life -= random.randint(3, 8)
        p.y -= 1 if random.random() < 0.7 else 0
        p.x += random.choice([-1, 0, 1])
        if p.life <= 0 or p.y < 0:
            self.remove_particle(p.x, p.y)
            return
        if random.random() < 0.1:
            self.add_particle(p.x + random.choice([-1, 1]), p.y, ParticleType.SMOKE)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = p.x + dx, p.y + dy
            target = self.get_cell(nx, ny)
            if target and PARTICLE_PROPS[target.ptype].get('flammable'):
                if target.temp >= PARTICLE_PROPS[target.ptype].get('burn_temp', 300):
                    self.remove_particle(nx, ny)
                    self.add_particle(nx, ny, ParticleType.FIRE)
    
    def update_smoke(self, p):
        p.life -= random.randint(1, 3)
        p.y -= 1 if random.random() < 0.5 else 0
        p.x += random.choice([-1, 0, 1])
        p.vx += self.wind_x * 0.2
        if p.life <= 0 or p.y < 0:
            self.remove_particle(p.x, p.y)
    
    def update_lava(self, p):
        p.vy += self.gravity * 0.3
        if self.try_move_down(p):
            pass
        else:
            for dx in [-1, 1]:
                if self.try_move_side(p, dx):
                    break
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = p.x + dx, p.y + dy
            target = self.get_cell(nx, ny)
            if target and target.ptype == ParticleType.WATER:
                self.remove_particle(nx, ny)
                self.add_particle(nx, ny, ParticleType.SMOKE)
                self.add_particle(nx, ny, ParticleType.STONE)
            elif target and target.ptype == ParticleType.ICE:
                self.remove_particle(nx, ny)
                self.add_particle(nx, ny, ParticleType.WATER)
                self.add_particle(nx, ny, ParticleType.SMOKE)
    
    def update_ice(self, p):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = p.x + dx, p.y + dy
            target = self.get_cell(nx, ny)
            if target and target.ptype == ParticleType.WATER:
                target.temp = min(target.temp, 0)
            elif target and target.ptype == ParticleType.LAVA:
                self.remove_particle(nx, ny)
                self.add_particle(nx, ny, ParticleType.WATER)
                self.add_particle(nx, ny, ParticleType.SMOKE)
    
    def update_acid(self, p):
        if self.try_move_down(p):
            pass
        else:
            for dx in [-1, 1]:
                if self.try_move_side(p, dx):
                    break
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = p.x + dx, p.y + dy
            target = self.get_cell(nx, ny)
            if target and target.ptype not in [ParticleType.STONE, ParticleType.ACID]:
                if random.random() < 0.05:
                    self.remove_particle(nx, ny)
    
    def update_oil(self, p):
        p.vx += self.wind_x * 0.15
        if self.try_move_down(p):
            pass
        else:
            dx = 1 if p.vx > 0 else -1 if p.vx < 0 else random.choice([-1, 1])
            self.try_move_side(p, dx)
        p.vx *= 0.95
    
    def update_particle(self, p):
        if p.ptype == ParticleType.SAND:
            self.update_sand(p)
        elif p.ptype == ParticleType.WATER:
            self.update_water(p)
        elif p.ptype == ParticleType.FIRE:
            self.update_fire(p)
        elif p.ptype == ParticleType.SMOKE:
            self.update_smoke(p)
        elif p.ptype == ParticleType.LAVA:
            self.update_lava(p)
        elif p.ptype == ParticleType.ICE:
            self.update_ice(p)
        elif p.ptype == ParticleType.ACID:
            self.update_acid(p)
        elif p.ptype == ParticleType.OIL:
            self.update_oil(p)
        elif p.ptype in [ParticleType.STONE, ParticleType.WOOD]:
            pass
    
    def apply_tool(self, mx, my):
        gx, gy = mx - self.offset_x, my - self.offset_y
        if not self.in_bounds(gx, gy):
            return
        
        if self.current_tool == Tool.BRUSH:
            for dy in range(-self.brush_size, self.brush_size + 1):
                for dx in range(-self.brush_size, self.brush_size + 1):
                    if dx*dx + dy*dy <= self.brush_size*self.brush_size:
                        nx, ny = gx + dx, gy + dy
                        if self.in_bounds(nx, ny) and not self.get_cell(nx, ny) and random.random() < 0.6:
                            self.add_particle(nx, ny, self.current_type)
        
        elif self.current_tool == Tool.ERASER:
            for dy in range(-self.brush_size, self.brush_size + 1):
                for dx in range(-self.brush_size, self.brush_size + 1):
                    if dx*dx + dy*dy <= self.brush_size*self.brush_size:
                        self.remove_particle(gx + dx, gy + dy)
        
        elif self.current_tool == Tool.WIND:
            for p in self.particles:
                dx, dy = p.x - gx, p.y - gy
                dist = math.hypot(dx, dy)
                if dist < self.brush_size * 2 and dist > 0:
                    force = (self.brush_size * 2 - dist) * 0.1
                    p.vx += (dx / dist) * force
                    p.vy += (dy / dist) * force * 0.5
        
        elif self.current_tool == Tool.HEAT:
            for p in self.particles:
                dx, dy = p.x - gx, p.y - gy
                dist = math.hypot(dx, dy)
                if dist < self.brush_size * 2:
                    p.temp += (self.brush_size * 2 - dist) * 5
                    if p.ptype == ParticleType.ICE and p.temp > 0:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.WATER)
                    elif p.ptype == ParticleType.WOOD and p.temp > 300:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.FIRE)
                    elif p.ptype == ParticleType.OIL and p.temp > 200:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.FIRE)
        
        elif self.current_tool == Tool.COOL:
            for p in self.particles:
                dx, dy = p.x - gx, p.y - gy
                dist = math.hypot(dx, dy)
                if dist < self.brush_size * 2:
                    p.temp -= (self.brush_size * 2 - dist) * 5
                    if p.ptype == ParticleType.WATER and p.temp < 0:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.ICE)
                    elif p.ptype == ParticleType.LAVA and p.temp < 500:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.STONE)
                    elif p.ptype == ParticleType.FIRE:
                        self.remove_particle(p.x, p.y)
                        self.add_particle(p.x, p.y, ParticleType.SMOKE)
        
        elif self.current_tool == Tool.GRAVITY:
            for p in self.particles:
                dx, dy = p.x - gx, p.y - gy
                dist = math.hypot(dx, dy)
                if dist < self.brush_size * 3 and dist > 0:
                    force = (self.brush_size * 3 - dist) * 0.2
                    p.vy += force
        
        elif self.current_tool == Tool.EXPLOSION:
            for p in self.particles[:]:
                dx, dy = p.x - gx, p.y - gy
                dist = math.hypot(dx, dy)
                if dist < self.brush_size * 3:
                    if dist > 0:
                        p.vx += (dx / dist) * 10
                        p.vy += (dy / dist) * 10
                    else:
                        p.vx += random.uniform(-5, 5)
                        p.vy += random.uniform(-5, 5)
    
    def update(self):
        if self.paused:
            return
        
        random.shuffle(self.particles)
        for p in self.particles[:]:
            if p not in self.particles:
                continue
            self.update_particle(p)
        
        for p in self.particles:
            p.vy += self.gravity * 0.1
            p.vx *= 0.99
    
    def handle_input(self):
        key = self.stdscr.getch()
        mx, my = -1, -1
        try:
            _, mx, my = curses.getmouse()
            if curses.getmouse()[4] & curses.BUTTON1_PRESSED:
                self.apply_tool(mx, my)
        except:
            pass
        
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord(' '):
            self.paused = not self.paused
        elif key == ord('h') or key == ord('H'):
            self.show_help = not self.show_help
        elif key == ord('c') or key == ord('C'):
            self.grid = [[None for _ in range(self.grid_w)] for _ in range(self.grid_h)]
            self.particles.clear()
        elif key == ord('['):
            self.brush_size = max(1, self.brush_size - 1)
        elif key == ord(']'):
            self.brush_size = min(15, self.brush_size + 1)
        elif key == curses.KEY_UP:
            types = list(ParticleType)
            idx = types.index(self.current_type)
            self.current_type = types[(idx - 1) % len(types)]
        elif key == curses.KEY_DOWN:
            types = list(ParticleType)
            idx = types.index(self.current_type)
            self.current_type = types[(idx + 1) % len(types)]
        elif key == curses.KEY_LEFT:
            tools = list(Tool)
            idx = tools.index(self.current_tool)
            self.current_tool = tools[(idx - 1) % len(tools)]
        elif key == curses.KEY_RIGHT:
            tools = list(Tool)
            idx = tools.index(self.current_tool)
            self.current_tool = tools[(idx + 1) % len(tools)]
        elif key == ord('g') or key == ord('G'):
            self.gravity = -self.gravity
        elif key == ord('w') or key == ord('W'):
            self.wind_x = -self.wind_x if self.wind_x else 1
        elif key >= ord('1') and key <= ord('9'):
            types = list(ParticleType)
            idx = key - ord('1')
            if idx < len(types):
                self.current_type = types[idx]
                self.current_tool = Tool.BRUSH
        
        return True
    
    def get_particle_char(self, p):
        props = PARTICLE_PROPS[p.ptype]
        chars = props['chars']
        idx = min(len(chars) - 1, int((255 - p.life) / 255 * (len(chars) - 1)) if p.life < 255 else 0)
        return chars[idx]
    
    def get_particle_color(self, p):
        props = PARTICLE_PROPS[p.ptype]
        base = props['color_base']
        
        if p.ptype == ParticleType.FIRE:
            intensity = p.life / 255
            if intensity > 0.7:
                return 196
            elif intensity > 0.4:
                return 202
            else:
                return 208
        elif p.ptype == ParticleType.LAVA:
            return 202 + int((p.temp - 500) / 500 * 20)
        elif p.ptype == ParticleType.SMOKE:
            return 232 + int((255 - p.life) / 255 * 20)
        else:
            return base + p.color_offset
    
    def render(self):
        self.stdscr.erase()
        
        for y in range(self.grid_h):
            for x in range(self.grid_w):
                p = self.grid[y][x]
                if p:
                    ch = self.get_particle_char(p)
                    color = self.get_particle_color(p)
                    try:
                        self.stdscr.addch(self.offset_y + y, self.offset_x + x, ch, curses.color_pair(color))
                    except curses.error:
                        pass
        
        if self.show_help:
            help_lines = [
                "PARTICLE PLAYGROUND - Physics Sandbox",
                "",
                "MATERIALS (1-9, ↑↓):",
                "  1:SAND  2:WATER  3:FIRE  4:SMOKE  5:STONE",
                "  6:WOOD  7:ACID   8:LAVA  9:ICE    0:OIL",
                "",
                "TOOLS (←→):",
                "  BRUSH    - Place material",
                "  ERASER   - Remove particles",
                "  WIND     - Blow particles",
                "  HEAT     - Increase temperature",
                "  COOL     - Decrease temperature",
                "  GRAVITY  - Pull particles down",
                "  EXPLOSION- Push particles away",
                "",
                "CONTROLS:",
                "  SPACE    - Pause/Resume",
                "  C        - Clear all",
                "  G        - Flip gravity",
                "  W        - Toggle wind",
                "  [ / ]    - Brush size: " + str(self.brush_size),
                "  H        - Toggle help",
                "  Q        - Quit",
                "",
                f"Current: {self.current_type.name} | Tool: {TOOL_NAMES[self.current_tool]} | Gravity: {self.gravity:.1f} | Particles: {len(self.particles)}"
            ]
            
            for i, line in enumerate(help_lines):
                try:
                    color = 7 if i < 2 else (8 if line.startswith("  ") else 7)
                    self.stdscr.addstr(i, 0, line[:self.width-1], curses.color_pair(color))
                except curses.error:
                    pass
        
        try:
            status = f" {self.current_type.name} | {TOOL_NAMES[self.current_tool]} | Size:{self.brush_size} | {'PAUSED' if self.paused else 'RUNNING'} "
            self.stdscr.addstr(self.height - 1, 0, status[:self.width-1], curses.color_pair(7) | curses.A_REVERSE)
        except curses.error:
            pass
        
        self.stdscr.refresh()

def main(stdscr):
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    sandbox = Sandbox(stdscr)
    while sandbox.handle_input():
        sandbox.update()
        sandbox.render()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass