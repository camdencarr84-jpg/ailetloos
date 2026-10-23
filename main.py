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
    life: float
    max_life: float
    char: str
    color: int

@dataclass
class Star:
    x: float
    y: float
    speed: float
    brightness: int

class Animation:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.particles: List[Particle] = []
        self.stars: List[Star] = []
        self.frame = 0
        self.mode = 0
        self.modes = ['fireworks', 'matrix', 'plasma', 'particles', 'waves', 'dna', 'galaxy', 'mandelbrot']
        self.last_mode_switch = time.time()
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(30)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, 16):
                curses.init_pair(i, i, -1)
        
        self.init_stars()
    
    def init_stars(self):
        self.stars = [
            Star(
                x=random.uniform(0, self.width - 1),
                y=random.uniform(0, self.height - 1),
                speed=random.uniform(0.1, 0.5),
                brightness=random.randint(1, 3)
            )
            for _ in range(100)
        ]
    
    def add_explosion(self, x: float, y: float):
        colors = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
        chars = ['*', '✦', '✧', '⋆', '✶', '✺', '✹', '✸', '✷', '✵', '✴', '❋', '❊', '❉', '✱', '✲', '✳', '✴']
        for _ in range(random.randint(30, 60)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 3.0)
            self.particles.append(Particle(
                x=x, y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=random.uniform(20, 60),
                max_life=random.uniform(20, 60),
                char=random.choice(chars),
                color=random.choice(colors)
            ))
    
    def update_fireworks(self):
        if random.random() < 0.02:
            self.add_explosion(
                random.uniform(10, self.width - 10),
                random.uniform(5, self.height // 2)
            )
        
        new_particles = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.05
            p.life -= 1
            if p.life > 0 and 0 <= p.x < self.width - 1 and 0 <= p.y < self.height - 1:
                new_particles.append(p)
        self.particles = new_particles
    
    def update_matrix(self):
        if random.random() < 0.1:
            self.particles.append(Particle(
                x=random.uniform(0, self.width - 1),
                y=0,
                vx=0,
                vy=random.uniform(0.2, 0.8),
                life=random.uniform(50, 150),
                max_life=random.uniform(50, 150),
                char=random.choice('アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789'),
                color=2
            ))
        
        new_particles = []
        for p in self.particles:
            p.y += p.vy
            p.life -= 1
            if p.life > 0 and p.y < self.height - 1:
                new_particles.append(p)
        self.particles = new_particles
    
    def update_plasma(self):
        pass
    
    def update_particles(self):
        if random.random() < 0.3:
            self.particles.append(Particle(
                x=random.uniform(0, self.width - 1),
                y=random.uniform(0, self.height - 1),
                vx=random.uniform(-0.5, 0.5),
                vy=random.uniform(-0.5, 0.5),
                life=random.uniform(30, 80),
                max_life=random.uniform(30, 80),
                char=random.choice('●○◐◑◒◓◔◕⬤⬥⬦⬧⬨⬩⬪⬫⬬⬭⬮⬯'),
                color=random.randint(1, 14)
            ))
        
        new_particles = []
        for p in self.particles:
            p.x += p.vx + random.uniform(-0.1, 0.1)
            p.y += p.vy + random.uniform(-0.1, 0.1)
            p.life -= 1
            if p.life > 0 and 0 <= p.x < self.width - 1 and 0 <= p.y < self.height - 1:
                new_particles.append(p)
        self.particles = new_particles
    
    def update_waves(self):
        pass
    
    def update_dna(self):
        pass
    
    def update_galaxy(self):
        if random.random() < 0.05:
            cx, cy = self.width // 2, self.height // 2
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(2, min(self.width, self.height) // 3)
            self.particles.append(Particle(
                x=cx + math.cos(angle) * r,
                y=cy + math.sin(angle) * r * 0.5,
                vx=-math.sin(angle) * random.uniform(0.1, 0.3),
                vy=math.cos(angle) * random.uniform(0.1, 0.3) * 0.5,
                life=random.uniform(100, 300),
                max_life=random.uniform(100, 300),
                char=random.choice('⋆✦✧✶✺✹✸✷✵✴❋❊❉✱✲✳✴'),
                color=random.randint(1, 14)
            ))
        
        new_particles = []
        cx, cy = self.width // 2, self.height // 2
        for p in self.particles:
            dx, dy = p.x - cx, p.y - cy
            dist = math.hypot(dx, dy)
            if dist > 0:
                p.vx += -dy / dist * 0.01
                p.vy += dx / dist * 0.01 * 0.5
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            if p.life > 0 and 0 <= p.x < self.width - 1 and 0 <= p.y < self.height - 1:
                new_particles.append(p)
        self.particles = new_particles
    
    def update_mandelbrot(self):
        pass
    
    def update_stars(self):
        for star in self.stars:
            star.y += star.speed
            if star.y >= self.height - 1:
                star.y = 0
                star.x = random.uniform(0, self.width - 1)
    
    def update(self):
        self.frame += 1
        self.update_stars()
        
        if time.time() - self.last_mode_switch > 15:
            self.mode = (self.mode + 1) % len(self.modes)
            self.particles.clear()
            self.last_mode_switch = time.time()
        
        mode_name = self.modes[self.mode]
        update_method = getattr(self, f'update_{mode_name}', lambda: None)
        update_method()
    
    def draw_plasma(self):
        t = self.frame * 0.05
        for y in range(self.height - 1):
            for x in range(0, self.width - 1, 2):
                v = 0
                v += math.sin(x * 0.1 + t) * 10
                v += math.sin(y * 0.1 + t) * 10
                v += math.sin((x + y) * 0.1 + t) * 10
                v += math.sin(math.hypot(x - self.width//2, y - self.height//2) * 0.1 + t) * 10
                v = int((v + 40) / 80 * 14) + 1
                v = max(1, min(14, v))
                chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
                idx = int((v / 14) * (len(chars) - 1))
                try:
                    self.stdscr.addstr(y, x, chars[idx] * 2, curses.color_pair(v))
                except curses.error:
                    pass
    
    def draw_waves(self):
        t = self.frame * 0.08
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                d = math.hypot(x - self.width//2, y - self.height//2)
                v = math.sin(d * 0.1 - t) * 0.5 + math.sin(x * 0.05 - t) * 0.3 + math.sin(y * 0.05 - t) * 0.3
                v = int((v + 1.1) / 2.2 * 14) + 1
                v = max(1, min(14, v))
                chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
                idx = int((v / 14) * (len(chars) - 1))
                try:
                    self.stdscr.addstr(y, x, chars[idx], curses.color_pair(v))
                except curses.error:
                    pass
    
    def draw_dna(self):
        t = self.frame * 0.1
        cx, cy = self.width // 2, self.height // 2
        for i in range(self.height - 1):
            y = i
            for strand in [0, 1]:
                phase = strand * math.pi
                x = cx + math.sin(y * 0.1 + t + phase) * 15
                x2 = cx + math.sin(y * 0.1 + t + phase + math.pi) * 15
                y_offset = (y - cy) * 0.5
                try:
                    if 0 <= x < self.width - 1:
                        self.stdscr.addstr(y, int(x), '█', curses.color_pair(10 if strand == 0 else 12))
                    if 0 <= x2 < self.width - 1:
                        self.stdscr.addstr(y, int(x2), '█', curses.color_pair(10 if strand == 0 else 12))
                    if abs(x - x2) > 2:
                        mid_x = (x + x2) / 2
                        if 0 <= mid_x < self.width - 1:
                            self.stdscr.addstr(y, int(mid_x), '─', curses.color_pair(14))
                except curses.error:
                    pass
    
    def draw_mandelbrot(self):
        t = self.frame * 0.005
        cx, cy = self.width // 2, self.height // 2
        scale = min(self.width, self.height) * 0.015
        center_x, center_y = -0.5, 0
        zoom = 1.0 + 0.5 * math.sin(t)
        
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                zx = (x - cx) / scale / zoom + center_x
                zy = (y - cy) / scale / zoom / 2 + center_y
                c = complex(zx, zy)
                z = 0
                iter_count = 0
                max_iter = 30
                for i in range(max_iter):
                    if abs(z) > 2:
                        break
                    z = z * z + c
                    iter_count = i
                if iter_count == max_iter - 1:
                    ch = '█'
                    color = 1
                else:
                    v = iter_count / max_iter * 14 + 1
                    color = max(1, min(14, int(v)))
                    chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
                    ch = chars[int(v / 14 * (len(chars) - 1))]
                try:
                    self.stdscr.addstr(y, x, ch, curses.color_pair(color))
                except curses.error:
                    pass
    
    def draw(self):
        self.stdscr.erase()
        
        for star in self.stars:
            try:
                if star.brightness == 1:
                    ch = '.'
                elif star.brightness == 2:
                    ch = '*'
                else:
                    ch = '✦'
                self.stdscr.addstr(int(star.y), int(star.x), ch, curses.color_pair(7))
            except curses.error:
                pass
        
        mode_name = self.modes[self.mode]
        
        if mode_name == 'plasma':
            self.draw_plasma()
        elif mode_name == 'waves':
            self.draw_waves()
        elif mode_name == 'dna':
            self.draw_dna()
        elif mode_name == 'mandelbrot':
            self.draw_mandelbrot()
        else:
            for p in self.particles:
                try:
                    alpha = p.life / p.max_life
                    if alpha > 0.7:
                        ch = p.char
                    elif alpha > 0.4:
                        ch = random.choice(['*', '+', '·', '∘'])
                    else:
                        ch = '.'
                    self.stdscr.addstr(int(p.y), int(p.x), ch, curses.color_pair(p.color) | curses.A_BOLD)
                except curses.error:
                    pass
        
        try:
            mode_display = f" Mode: {mode_name.upper()} "
            self.stdscr.addstr(0, max(0, self.width - len(mode_display) - 2), mode_display, curses.color_pair(14) | curses.A_BOLD)
            self.stdscr.addstr(self.height - 1, 2, "Press 'q' to quit, 'n' for next mode", curses.color_pair(8))
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def run(self):
        while True:
            self.update()
            self.draw()
            key = self.stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('n') or key == ord('N'):
                self.mode = (self.mode + 1) % len(self.modes)
                self.particles.clear()
                self.last_mode_switch = time.time()

def main(stdscr):
    anim = Animation(stdscr)
    anim.run()

if __name__ == '__main__':
    curses.wrapper(main)