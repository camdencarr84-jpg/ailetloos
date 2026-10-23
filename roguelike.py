#!/usr/bin/env python3
"""
Roguelike Dungeon Crawler - ASCII Adventure
"""

import curses
import random
import time

class Roguelike:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)   # Floor
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Wall
        curses.init_pair(3, curses.COLOR_GREEN, -1)   # Player
        curses.init_pair(4, curses.COLOR_RED, -1)     # Enemy
        curses.init_pair(5, curses.COLOR_CYAN, -1)    # Items
        curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Stairs
        curses.init_pair(7, curses.COLOR_WHITE, -1)   # UI
        
        self.map_w = self.width - 2
        self.map_h = self.height - 10
        self.level = 1
        self.score = 0
        self.game_over = False
        self.victory = False
        self.message = "Welcome to the dungeon!"
        self.messages = []
        
        self.player = None
        self.entities = []
        self.items = []
        self.stairs = None
        self.fov_map = []
        
        self.generate_level()
        
    def generate_level(self):
        self.map = [[1 for _ in range(self.map_w)] for _ in range(self.map_h)]
        self.entities = []
        self.items = []
        
        rooms = []
        num_rooms = random.randint(5, 10)
        
        for _ in range(num_rooms):
            w = random.randint(5, 12)
            h = random.randint(4, 8)
            x = random.randint(1, self.map_w - w - 1)
            y = random.randint(1, self.map_h - h - 1)
            
            overlap = False
            for rx, ry, rw, rh in rooms:
                if x < rx + rw + 1 and x + w + 1 > rx and y < ry + rh + 1 and y + h + 1 > ry:
                    overlap = True
                    break
            if overlap:
                continue
                
            for iy in range(y, y + h):
                for ix in range(x, x + w):
                    self.map[iy][ix] = 0
            rooms.append((x, y, w, h))
            
        for i in range(len(rooms) - 1):
            x1, y1 = rooms[i][0] + rooms[i][2] // 2, rooms[i][1] + rooms[i][3] // 2
            x2, y2 = rooms[i+1][0] + rooms[i+1][2] // 2, rooms[i+1][1] + rooms[i+1][3] // 2
            
            if random.random() < 0.5:
                for ix in range(min(x1, x2), max(x1, x2) + 1):
                    self.map[y1][ix] = 0
                for iy in range(min(y1, y2), max(y1, y2) + 1):
                    self.map[iy][x2] = 0
            else:
                for iy in range(min(y1, y2), max(y1, y2) + 1):
                    self.map[iy][x1] = 0
                for ix in range(min(x1, x2), max(x1, x2) + 1):
                    self.map[y2][ix] = 0
                    
        if rooms:
            px, py = rooms[0][0] + rooms[0][2] // 2, rooms[0][1] + rooms[0][3] // 2
            self.player = Entity(px, py, '@', 3, "Player", hp=20, max_hp=20, atk=5, defense=2)
            
            for i, (rx, ry, rw, rh) in enumerate(rooms[1:], 1):
                ex = rx + rw // 2
                ey = ry + rh // 2
                if random.random() < 0.7:
                    enemy = Entity(ex, ey, random.choice(['g','o','O','D','@']), 4, 
                                 random.choice(['Goblin','Orc','Troll','Dragon']), 
                                 hp=5+self.level*2, max_hp=5+self.level*2, 
                                 atk=2+self.level, defense=1)
                    self.entities.append(enemy)
                    
                if random.random() < 0.5:
                    item = Item(rx + random.randint(1, rw-2), ry + random.randint(1, rh-2),
                              random.choice(['!', '?', ')', '[', '/', '=']),
                              random.choice(['Potion','Scroll','Ring','Amulet','Weapon','Armor']))
                    self.items.append(item)
                    
            last_room = rooms[-1]
            self.stairs = (last_room[0] + last_room[2] // 2, last_room[1] + last_room[3] // 2)
            
        self.compute_fov()
        
    def compute_fov(self):
        self.fov_map = [[False for _ in range(self.map_w)] for _ in range(self.map_h)]
        if not self.player:
            return
            
        px, py = self.player.x, self.player.y
        radius = 8
        
        for y in range(max(0, py-radius), min(self.map_h, py+radius+1)):
            for x in range(max(0, px-radius), min(self.map_w, px+radius+1)):
                dx, dy = x - px, y - py
                if dx*dx + dy*dy <= radius*radius:
                    if self.line_of_sight(px, py, x, y):
                        self.fov_map[y][x] = True
                        
    def line_of_sight(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if x != x2 or y != y2:
                if self.map[y][x] == 1:
                    return False
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return True
        
    def add_message(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 4:
            self.messages.pop(0)
        self.message = msg
        
    def move_player(self, dx, dy):
        if self.game_over:
            return
            
        nx, ny = self.player.x + dx, self.player.y + dy
        
        if nx < 0 or nx >= self.map_w or ny < 0 or ny >= self.map_h:
            return
            
        if self.map[ny][nx] == 1:
            return
            
        target = None
        for e in self.entities:
            if e.x == nx and e.y == ny:
                target = e
                break
                
        if target:
            self.attack(self.player, target)
        else:
            self.player.x, self.player.y = nx, ny
            self.compute_fov()
            self.check_items()
            self.check_stairs()
            
    def attack(self, attacker, defender):
        dmg = max(1, attacker.atk - defender.defense + random.randint(-1, 1))
        defender.hp -= dmg
        self.add_message(f"{attacker.name} hits {defender.name} for {dmg} damage!")
        
        if defender.hp <= 0:
            self.add_message(f"{defender.name} is defeated!")
            self.score += 10 * self.level
            if defender in self.entities:
                self.entities.remove(defender)
                
    def check_items(self):
        for item in self.items[:]:
            if item.x == self.player.x and item.y == self.player.y:
                self.add_message(f"You found a {item.name}!")
                self.score += 5
                self.items.remove(item)
                
    def check_stairs(self):
        if self.stairs and self.player.x == self.stairs[0] and self.player.y == self.stairs[1]:
            self.level += 1
            self.add_message(f"Descending to level {self.level}...")
            self.generate_level()
            
    def enemy_turn(self):
        for enemy in self.entities[:]:
            if enemy.hp <= 0:
                continue
                
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = abs(dx) + abs(dy)
            
            if dist <= 6:
                if abs(dx) > abs(dy):
                    nx = enemy.x + (1 if dx > 0 else -1)
                    ny = enemy.y
                else:
                    nx = enemy.x
                    ny = enemy.y + (1 if dy > 0 else -1)
                    
                if 0 <= nx < self.map_w and 0 <= ny < self.map_h and self.map[ny][nx] == 0:
                    blocked = False
                    for e in self.entities:
                        if e != enemy and e.x == nx and e.y == ny:
                            blocked = True
                            break
                    if not blocked:
                        if nx == self.player.x and ny == self.player.y:
                            self.attack(enemy, self.player)
                            if self.player.hp <= 0:
                                self.game_over = True
                                self.add_message("YOU DIED!")
                        else:
                            enemy.x, enemy.y = nx, ny
                            
    def handle_input(self):
        key = self.stdscr.getch()
        if key in (ord('q'), 27):
            return False
        elif key in (curses.KEY_UP, ord('w'), ord('k')):
            self.move_player(0, -1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('j')):
            self.move_player(0, 1)
        elif key in (curses.KEY_LEFT, ord('a'), ord('h')):
            self.move_player(-1, 0)
        elif key in (curses.KEY_RIGHT, ord('d'), ord('l')):
            self.move_player(1, 0)
        elif key in (ord('.'), ord('>')):
            self.check_stairs()
        elif key == ord('r') and self.game_over:
            self.__init__(self.stdscr)
        self.enemy_turn()
        return True
        
    def draw(self):
        self.stdscr.erase()
        
        for y in range(self.map_h):
            for x in range(self.map_w):
                if self.fov_map[y][x]:
                    if self.map[y][x] == 1:
                        try:
                            self.stdscr.addch(y, x, '#', curses.color_pair(2))
                        except curses.error:
                            pass
                    else:
                        try:
                            self.stdscr.addch(y, x, '.', curses.color_pair(1))
                        except curses.error:
                            pass
                elif self.map[y][x] == 1:
                    try:
                        self.stdscr.addch(y, x, '#', curses.color_pair(2) | curses.A_DIM)
                    except curses.error:
                        pass
                        
        for item in self.items:
            if self.fov_map[item.y][item.x]:
                try:
                    self.stdscr.addch(item.y, item.x, item.char, curses.color_pair(5) | curses.A_BOLD)
                except curses.error:
                    pass
                    
        if self.stairs and self.fov_map[self.stairs[1]][self.stairs[0]]:
            try:
                self.stdscr.addch(self.stairs[1], self.stairs[0], '>', curses.color_pair(6) | curses.A_BOLD)
            except curses.error:
                pass
                
        for enemy in self.entities:
            if self.fov_map[enemy.y][enemy.x]:
                try:
                    self.stdscr.addch(enemy.y, enemy.x, enemy.char, curses.color_pair(4) | curses.A_BOLD)
                except curses.error:
                    pass
                    
        if self.player:
            try:
                self.stdscr.addch(self.player.y, self.player.x, self.player.char, curses.color_pair(3) | curses.A_BOLD)
            except curses.error:
                pass
                
        ui_y = self.map_h
        try:
            self.stdscr.addstr(ui_y, 0, f" Level: {self.level}  HP: {self.player.hp}/{self.player.max_hp}  Atk: {self.player.atk}  Def: {self.player.defense}  Score: {self.score} ", curses.color_pair(7) | curses.A_BOLD)
            self.stdscr.addstr(ui_y + 1, 0, f" {self.message}", curses.color_pair(7))
            for i, msg in enumerate(self.messages[-3:]):
                self.stdscr.addstr(ui_y + 2 + i, 0, f" > {msg}", curses.color_pair(7))
            self.stdscr.addstr(ui_y + 5, 0, " Arrow/WASD=Move .=Stairs R=Restart Q=Quit", curses.color_pair(7))
        except curses.error:
            pass
            
        if self.game_over:
            msg = "GAME OVER - Press R to restart"
            try:
                self.stdscr.addstr(self.map_h // 2, (self.map_w - len(msg)) // 2, msg, curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
                
        self.stdscr.refresh()
        
    def run(self):
        while True:
            if not self.handle_input():
                break
            self.draw()
            time.sleep(0.05)

class Entity:
    def __init__(self, x, y, char, color, name, hp, max_hp, atk, defense):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.atk = atk
        self.defense = defense

class Item:
    def __init__(self, x, y, char, name):
        self.x = x
        self.y = y
        self.char = char
        self.name = name

def main(stdscr):
    game = Roguelike(stdscr)
    game.run()

if __name__ == '__main__':
    curses.wrapper(main)