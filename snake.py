#!/usr/bin/env python3
"""
SNAKE GAME - Terminal Edition
A classic snake game with smooth animation, high scores, and power-ups.
"""

import sys
import time
import random
import curses
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass
class Point:
    x: int
    y: int
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class PowerUpType(Enum):
    NONE = 0
    SLOW = 1
    SHRINK = 2
    SCORE_MULT = 3
    GHOST = 4

@dataclass
class PowerUp:
    pos: Point
    type: PowerUpType
    timer: int
    char: str
    color: int

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.game_width = min(self.width - 4, 60)
        self.game_height = min(self.height - 4, 30)
        self.offset_x = (self.width - self.game_width) // 2
        self.offset_y = (self.height - self.game_height) // 2
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(80)
        stdscr.keypad(True)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            self.init_colors()
        
        self.reset()
    
    def init_colors(self):
        curses.init_pair(1, curses.COLOR_GREEN, -1)    # Snake head
        curses.init_pair(2, curses.COLOR_CYAN, -1)     # Snake body
        curses.init_pair(3, curses.COLOR_RED, -1)      # Food
        curses.init_pair(4, curses.COLOR_YELLOW, -1)   # Power-up
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Special food
        curses.init_pair(6, curses.COLOR_BLUE, -1)     # Ghost mode
        curses.init_pair(7, curses.COLOR_WHITE, -1)    # Border/UI
        curses.init_pair(8, 208, -1)                   # Orange
        curses.init_pair(9, 201, -1)                   # Pink
    
    def reset(self):
        cx, cy = self.game_width // 2, self.game_height // 2
        self.snake = [Point(cx, cy), Point(cx - 1, cy), Point(cx - 2, cy)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.food_eaten = 0
        self.game_over = False
        self.paused = False
        self.speed = 80
        self.base_speed = 80
        self.ghost_mode = False
        self.ghost_timer = 0
        self.score_multiplier = 1
        self.multiplier_timer = 0
        self.power_ups: List[PowerUp] = []
        self.particles: List[Tuple[Point, str, int, float]] = []
        self.spawn_food()
        self.last_powerup_spawn = time.time()
    
    def load_high_score(self):
        try:
            with open('/tmp/snake_highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('/tmp/snake_highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def spawn_food(self):
        while True:
            self.food = Point(
                random.randint(1, self.game_width - 2),
                random.randint(1, self.game_height - 2)
            )
            if self.food not in self.snake and self.food not in [p.pos for p in self.power_ups]:
                break
        self.food_type = random.choices(['normal', 'golden', 'shrinking'], weights=[0.7, 0.2, 0.1])[0]
    
    def maybe_spawn_powerup(self):
        if time.time() - self.last_powerup_spawn > 15 and random.random() < 0.3:
            types = [
                (PowerUpType.SLOW, '⏱', 4),
                (PowerUpType.SHRINK, '➖', 2),
                (PowerUpType.SCORE_MULT, '✕2', 3),
                (PowerUpType.GHOST, '👻', 6),
            ]
            ptype, char, color = random.choice(types)
            while True:
                pos = Point(
                    random.randint(1, self.game_width - 2),
                    random.randint(1, self.game_height - 2)
                )
                if pos not in self.snake and pos != self.food and pos not in [p.pos for p in self.power_ups]:
                    break
            self.power_ups.append(PowerUp(pos, ptype, 300, char, color))
            self.last_powerup_spawn = time.time()
    
    def add_particles(self, x, y, count, chars, color, speed=1.0):
        for _ in range(count):
            angle = random.uniform(0, 2 * 3.14159)
            v = random.uniform(0.5, 2.0) * speed
            self.particles.append((
                Point(x, y),
                random.choice(chars),
                color,
                1.0
            ))
    
    def update_particles(self):
        new_particles = []
        for pos, ch, col, life in self.particles:
            life -= 0.05
            if life > 0:
                new_particles.append((pos, ch, col, life))
        self.particles = new_particles
    
    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP and self.direction != Direction.DOWN:
            self.next_direction = Direction.UP
        elif key == curses.KEY_DOWN and self.direction != Direction.UP:
            self.next_direction = Direction.DOWN
        elif key == curses.KEY_LEFT and self.direction != Direction.RIGHT:
            self.next_direction = Direction.LEFT
        elif key == curses.KEY_RIGHT and self.direction != Direction.LEFT:
            self.next_direction = Direction.RIGHT
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('r') or key == ord('R') and self.game_over:
            self.reset()
        return True
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        self.direction = self.next_direction
        dx, dy = self.direction.value
        new_head = Point(self.snake[0].x + dx, self.snake[0].y + dy)
        
        if not self.ghost_mode:
            if (new_head.x <= 0 or new_head.x >= self.game_width - 1 or
                new_head.y <= 0 or new_head.y >= self.game_height - 1 or
                new_head in self.snake):
                self.game_over = True
                self.add_particles(self.snake[0].x, self.snake[0].y, 20, '✦✧⋆✶✺', 3)
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return
        else:
            if new_head.x <= 0: new_head.x = self.game_width - 2
            elif new_head.x >= self.game_width - 1: new_head.x = 1
            if new_head.y <= 0: new_head.y = self.game_height - 2
            elif new_head.y >= self.game_height - 1: new_head.y = 1
        
        self.snake.insert(0, new_head)
        
        ate_food = False
        if new_head == self.food:
            ate_food = True
            points = 10 * self.score_multiplier
            if self.food_type == 'golden':
                points = 50 * self.score_multiplier
                self.add_particles(self.food.x, self.food.y, 15, '✦✧⋆✨', 8)
            elif self.food_type == 'shrinking':
                points = 20 * self.score_multiplier
                if len(self.snake) > 3:
                    self.snake.pop()
                    self.snake.pop()
                self.add_particles(self.food.x, self.food.y, 10, '➖➕', 4)
            else:
                self.add_particles(self.food.x, self.food.y, 8, '✦✧', 3)
            
            self.score += points
            self.food_eaten += 1
            
            if self.food_eaten % 5 == 0:
                self.level += 1
                self.base_speed = max(40, self.base_speed - 3)
                self.speed = self.base_speed
                self.add_particles(self.game_width//2, self.game_height//2, 30, '⬆⬆⬆LEVEL UP⬆⬆⬆', 8, 2.0)
            
            self.spawn_food()
        else:
            self.snake.pop()
        
        for pu in self.power_ups[:]:
            if new_head == pu.pos:
                self.activate_powerup(pu.type)
                self.power_ups.remove(pu)
                self.add_particles(pu.pos.x, pu.pos.y, 12, '✨⭐💫', 4, 1.5)
        
        self.update_powerups()
        self.update_timers()
        self.update_particles()
        self.maybe_spawn_powerup()
        self.stdscr.timeout(self.speed)
    
    def activate_powerup(self, ptype):
        if ptype == PowerUpType.SLOW:
            self.speed = min(200, self.speed + 40)
        elif ptype == PowerUpType.SHRINK:
            if len(self.snake) > 3:
                self.snake = self.snake[:-2]
        elif ptype == PowerUpType.SCORE_MULT:
            self.score_multiplier = 2
            self.multiplier_timer = 200
        elif ptype == PowerUpType.GHOST:
            self.ghost_mode = True
            self.ghost_timer = 150
    
    def update_powerups(self):
        self.power_ups = [p for p in self.power_ups if p.timer > 0]
        for p in self.power_ups:
            p.timer -= 1
    
    def update_timers(self):
        if self.ghost_timer > 0:
            self.ghost_timer -= 1
            if self.ghost_timer == 0:
                self.ghost_mode = False
        
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer == 0:
                self.score_multiplier = 1
        
        if self.speed > self.base_speed:
            self.speed = max(self.base_speed, self.speed - 1)
    
    def draw_border(self):
        for x in range(self.game_width):
            self.draw(self.offset_y, self.offset_x + x, '═', 7)
            self.draw(self.offset_y + self.game_height - 1, self.offset_x + x, '═', 7)
        for y in range(self.game_height):
            self.draw(self.offset_y + y, self.offset_x, '║', 7)
            self.draw(self.offset_y + y, self.offset_x + self.game_width - 1, '║', 7)
        
        corners = ['╔', '╗', '╚', '╝']
        self.draw(self.offset_y, self.offset_x, corners[0], 7)
        self.draw(self.offset_y, self.offset_x + self.game_width - 1, corners[1], 7)
        self.draw(self.offset_y + self.game_height - 1, self.offset_x, corners[2], 7)
        self.draw(self.offset_y + self.game_height - 1, self.offset_x + self.game_width - 1, corners[3], 7)
    
    def draw(self, y, x, ch, color=0, bold=False):
        try:
            attr = curses.color_pair(color)
            if bold:
                attr |= curses.A_BOLD
            self.stdscr.addch(y, x, ch, attr)
        except curses.error:
            pass
    
    def draw_snake(self):
        for i, seg in enumerate(self.snake):
            x = self.offset_x + seg.x
            y = self.offset_y + seg.y
            if i == 0:
                ch = '▓' if not self.ghost_mode else '░'
                color = 6 if self.ghost_mode else 1
                self.draw(y, x, ch, color, True)
            else:
                alpha = 1.0 - (i / len(self.snake)) * 0.5
                ch = '▒' if alpha > 0.5 else '░'
                color = 6 if self.ghost_mode else 2
                self.draw(y, x, ch, color)
    
    def draw_food(self):
        x = self.offset_x + self.food.x
        y = self.offset_y + self.food.y
        if self.food_type == 'golden':
            ch = '◆'
            color = 8
        elif self.food_type == 'shrinking':
            ch = '◇'
            color = 4
        else:
            ch = '●'
            color = 3
        self.draw(y, x, ch, color, True)
    
    def draw_powerups(self):
        for pu in self.power_ups:
            x = self.offset_x + pu.pos.x
            y = self.offset_y + pu.pos.y
            blink = (pu.timer // 10) % 2 == 0
            if blink or pu.timer > 30:
                self.draw(y, x, pu.char, pu.color, True)
    
    def draw_particles(self):
        for pos, ch, col, life in self.particles:
            x = self.offset_x + pos.x
            y = self.offset_y + pos.y
            if 0 <= x < self.width and 0 <= y < self.height:
                try:
                    attr = curses.color_pair(col)
                    if life < 0.3:
                        attr |= curses.A_DIM
                    self.stdscr.addch(y, x, ch, attr)
                except curses.error:
                    pass
    
    def draw_ui(self):
        ui_y = self.offset_y - 2
        score_str = f" SCORE: {self.score}  "
        hs_str = f" HIGH: {self.high_score}  "
        level_str = f" LEVEL: {self.level}  "
        len_str = f" LENGTH: {len(self.snake)}  "
        
        self.draw(ui_y, self.offset_x, score_str, 7, True)
        self.draw(ui_y, self.offset_x + len(score_str), hs_str, 7)
        self.draw(ui_y, self.offset_x + len(score_str) + len(hs_str), level_str, 8)
        self.draw(ui_y, self.offset_x + len(score_str) + len(hs_str) + len(level_str), len_str, 2)
        
        if self.ghost_mode:
            self.draw(ui_y, self.width - 20, f" GHOST: {self.ghost_timer//10+1}s ", 6, True)
        if self.score_multiplier > 1:
            self.draw(ui_y, self.width - 35, f" 2x SCORE: {self.multiplier_timer//10+1}s ", 8, True)
        
        if self.paused:
            msg = " ═══ PAUSED - Press P to resume ═══ "
            self.draw(self.height // 2, (self.width - len(msg)) // 2, msg, 8, True)
        
        if self.game_over:
            msg1 = " ═══ GAME OVER ═══ "
            msg2 = f" Final Score: {self.score} "
            msg3 = " Press R to restart, Q to quit "
            cy = self.height // 2
            cx = (self.width - len(msg1)) // 2
            self.draw(cy - 1, cx, msg1, 3, True)
            self.draw(cy, cx, msg2, 8, True)
            self.draw(cy + 1, cx, msg3, 7)
    
    def render(self):
        self.stdscr.erase()
        self.draw_border()
        self.draw_snake()
        self.draw_food()
        self.draw_powerups()
        self.draw_particles()
        self.draw_ui()
        self.stdscr.refresh()
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.render()
        return self.score

def main(stdscr):
    game = SnakeGame(stdscr)
    return game.run()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass