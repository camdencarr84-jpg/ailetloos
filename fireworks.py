#!/usr/bin/env python3
"""
Fireworks Particle System - Terminal Animation
"""

import curses
import random
import math
import time

class Particle:
    def __init__(self, x, y, vx, vy, color, char, life, gravity=0.1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.char = char
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.trail = []
        
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.99
        self.life -= 1
        return self.life > 0
        
    def draw(self, stdscr):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail) * (self.life / self.max_life)
            if alpha > 0.3:
                try:
                    stdscr.addch(int(ty), int(tx), self.char, curses.color_pair(self.color) | curses.A_DIM)
                except curses.error:
                    pass
        if self.life > 0:
            try:
                stdscr.addch(int(self.y), int(self.x), self.char, curses.color_pair(self.color) | curses.A_BOLD)
            except curses.error:
                pass

class Firework:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(width // 4, 3 * width // 4)
        self.y = height - 2
        self.target_y = random.randint(height // 4, height // 2)
        self.vy = -random.uniform(1.5, 2.5)
        self.color = random.randint(1, 6)
        self.exploded = False
        self.particles = []
        self.chars = ['*', '·', '✦', '✧', '★', '✩', '•', '○']
        
    def update(self):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.target_y:
                self.explode()
        else:
            self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0 or not self.exploded
        
    def explode(self):
        self.exploded = True
        num_particles = random.randint(30, 60)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(20, 50)
            char = random.choice(self.chars)
            color = self.color
            self.particles.append(Particle(self.x, self.y, vx, vy, color, char, life))
            
    def draw(self, stdscr):
        if not self.exploded:
            try:
                stdscr.addch(int(self.y), int(self.x), '▲', curses.color_pair(self.color) | curses.A_BOLD)
            except curses.error:
                pass
        else:
            for p in self.particles:
                p.draw(stdscr)
                
    def is_dead(self):
        return self.exploded and len(self.particles) == 0

class FireworksShow:
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
        
        self.fireworks = []
        self.spawn_timer = 0
        self.spawn_interval = 20
        
    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.fireworks.append(Firework(self.width, self.height))
            self.spawn_timer = 0
            self.spawn_interval = random.randint(15, 40)
            
        self.fireworks = [fw for fw in self.fireworks if fw.update()]
        
    def draw(self):
        self.stdscr.erase()
        for fw in self.fireworks:
            fw.draw(self.stdscr)
            
        info = "🎆 FIREWORKS SHOW 🎆 | Q=Quit | SPACE=Burst"
        try:
            self.stdscr.addstr(self.height - 1, 0, info[:self.width-1], curses.color_pair(7))
        except curses.error:
            pass
        self.stdscr.refresh()
        
    def burst(self):
        for _ in range(5):
            self.fireworks.append(Firework(self.width, self.height))
            
    def run(self):
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            elif key == ord(' '):
                self.burst()
            self.update()
            self.draw()
            time.sleep(0.03)

def main(stdscr):
    show = FireworksShow(stdscr)
    show.run()

if __name__ == '__main__':
    curses.wrapper(main)