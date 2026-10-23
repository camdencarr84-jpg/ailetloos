#!/usr/bin/env python3
"""
BOUNCING BALLS - Simple terminal animation with physics
No curses needed - just stdout!
"""

import sys
import time
import random
import math
import os

WIDTH = 80
HEIGHT = 24

class Ball:
    def __init__(self, x, y, vx, vy, char, color, trail=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.char = char
        self.color = color
        self.trail = trail
        self.trail_positions = []
        self.radius = 1

def hsv_to_rgb(h, s, v):
    h = h / 360.0
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def rgb_to_256(r, g, b):
    if r == g == b:
        if r < 8: return 16
        if r > 248: return 231
        return 232 + (r - 8) * 24 // 247
    return 16 + (r * 6 // 256) * 36 + (g * 6 // 256) * 6 + (b * 6 // 256)

def color(h, s=1.0, v=1.0):
    r, g, b = hsv_to_rgb(h, s, v)
    return rgb_to_256(r, g, b)

def clear_screen():
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def move_cursor(y, x):
    sys.stdout.write(f'\033[{y};{x}H')

def set_color(c):
    sys.stdout.write(f'\033[38;5;{c}m')

def reset_color():
    sys.stdout.write('\033[0m')

def draw_frame(balls, frame_count):
    # Clear using ANSI escape codes
    sys.stdout.write('\033[H')
    
    # Create frame buffer
    buffer = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    color_buffer = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    # Draw trails first
    for ball in balls:
        if ball.trail:
            for i, (tx, ty) in enumerate(ball.trail_positions):
                if 0 <= int(tx) < WIDTH and 0 <= int(ty) < HEIGHT:
                    alpha = (i + 1) / len(ball.trail_positions)
                    trail_char = '·' if alpha < 0.3 else '∘' if alpha < 0.6 else '●'
                    buffer[int(ty)][int(tx)] = trail_char
                    color_buffer[int(ty)][int(tx)] = ball.color
    
    # Draw balls
    for ball in balls:
        x, y = int(ball.x), int(ball.y)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            buffer[y][x] = ball.char
            color_buffer[y][x] = ball.color
    
    # Render buffer
    output = []
    current_color = -1
    for y in range(HEIGHT):
        line = []
        for x in range(WIDTH):
            c = color_buffer[y][x]
            ch = buffer[y][x]
            if c != current_color:
                if current_color != -1:
                    line.append('\033[0m')
                if c != 0:
                    line.append(f'\033[38;5;{c}m')
                current_color = c
            line.append(ch)
        if current_color != -1:
            line.append('\033[0m')
            current_color = -1
        output.append(''.join(line))
    
    # Add stats
    output.append(f'\033[38;5;7mBalls: {len(balls)} | Frame: {frame_count} | FPS: ~60\033[0m')
    
    sys.stdout.write('\n'.join(output))
    sys.stdout.flush()

def simulate_physics(balls, dt=1/60):
    gravity = 200
    
    for ball in balls:
        # Apply gravity
        ball.vy += gravity * dt
        
        # Update position
        ball.x += ball.vx * dt
        ball.y += ball.vy * dt
        
        # Trail
        if ball.trail:
            ball.trail_positions.append((ball.x, ball.y))
            if len(ball.trail_positions) > 8:
                ball.trail_positions.pop(0)
        
        # Bounce off walls
        if ball.x <= ball.radius:
            ball.x = ball.radius
            ball.vx = abs(ball.vx) * 0.85
        elif ball.x >= WIDTH - 1 - ball.radius:
            ball.x = WIDTH - 1 - ball.radius
            ball.vx = -abs(ball.vx) * 0.85
        
        if ball.y <= ball.radius:
            ball.y = ball.radius
            ball.vy = abs(ball.vy) * 0.8
        elif ball.y >= HEIGHT - 1 - ball.radius:
            ball.y = HEIGHT - 1 - ball.radius
            ball.vy = -abs(ball.vy) * 0.8
            ball.vx *= 0.95  # Friction on ground
        
        # Ball-to-ball collision
        for other in balls:
            if other is ball:
                continue
            dx = other.x - ball.x
            dy = other.y - ball.y
            dist = math.hypot(dx, dy)
            min_dist = ball.radius + other.radius
            if dist < min_dist and dist > 0:
                # Separate
                overlap = min_dist - dist
                nx, ny = dx / dist, dy / dist
                ball.x -= nx * overlap * 0.5
                ball.y -= ny * overlap * 0.5
                other.x += nx * overlap * 0.5
                other.y += ny * overlap * 0.5
                
                # Exchange velocities (elastic collision)
                dvx = ball.vx - other.vx
                dvy = ball.vy - other.vy
                if dvx * nx + dvy * ny < 0:  # Moving towards each other
                    impulse = 2 * (dvx * nx + dvy * ny) / 2  # Equal mass
                    ball.vx -= impulse * nx * 0.9
                    ball.vy -= impulse * ny * 0.9
                    other.vx += impulse * nx * 0.9
                    other.vy += impulse * ny * 0.9

def create_balls(count):
    balls = []
    chars = ['●', '◆', '■', '▲', '★', '✦', '⬤', '◉', '◯', '◎']
    for _ in range(count):
        balls.append(Ball(
            x=random.uniform(10, WIDTH - 10),
            y=random.uniform(5, HEIGHT // 2),
            vx=random.uniform(-50, 50),
            vy=random.uniform(-100, 0),
            char=random.choice(chars),
            color=color(random.uniform(0, 360), 0.9, 0.9),
            trail=random.random() < 0.7
        ))
    return balls

def main():
    hide_cursor()
    balls = create_balls(12)
    frame = 0
    last_spawn = time.time()
    
    try:
        while True:
            frame += 1
            simulate_physics(balls)
            draw_frame(balls, frame)
            
            # Occasionally add a new ball
            if time.time() - last_spawn > 3 and len(balls) < 25 and random.random() < 0.3:
                balls.append(Ball(
                    x=WIDTH // 2,
                    y=2,
                    vx=random.uniform(-80, 80),
                    vy=random.uniform(-50, 50),
                    char=random.choice(['●', '◆', '■', '▲', '★']),
                    color=color(random.uniform(0, 360), 0.9, 0.9),
                    trail=True
                ))
                last_spawn = time.time()
            
            time.sleep(1/60)
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()
        print("Thanks for watching! 👋")

if __name__ == '__main__':
    main()