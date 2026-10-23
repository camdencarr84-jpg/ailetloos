#!/usr/bin/env python3
"""
TERMINAL TAMAGOTCHI - A virtual pet that lives in your terminal
"""

import curses
import time
import random
import json
import os
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import List, Optional

SAVE_FILE = '/tmp/tamagotchi_save.json'

class Mood(Enum):
    ECSTATIC = 5
    HAPPY = 4
    CONTENT = 3
    NEUTRAL = 2
    SAD = 1
    MISERABLE = 0

class Action(Enum):
    FEED = "feed"
    PLAY = "play"
    PET = "pet"
    SLEEP = "sleep"
    MEDICINE = "medicine"
    CLEAN = "clean"
    TRAIN = "train"

@dataclass
class Pet:
    name: str = "Buddy"
    species: str = "blob"
    age: int = 0
    hunger: int = 50
    happiness: int = 50
    energy: int = 50
    health: int = 100
    cleanliness: int = 50
    discipline: int = 0
    weight: int = 10
    money: int = 100
    experience: int = 0
    level: int = 1
    sickness: int = 0
    last_update: float = field(default_factory=time.time)
    birth_time: float = field(default_factory=time.time)
    total_actions: int = 0
    poop_count: int = 0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Tamagotchi:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.pet = self.load_pet()
        self.animation_frame = 0
        self.message = ""
        self.message_timer = 0
        self.menu_open = False
        self.menu_selection = 0
        self.shop_open = False
        self.shop_selection = 0
        self.sleeping = False
        self.minigame = None
        self.minigame_state = {}
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)
        stdscr.keypad(True)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            self.init_colors()
    
    def init_colors(self):
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_BLUE, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.init_pair(8, 208, -1)
        curses.init_pair(9, 201, -1)
        curses.init_pair(10, 118, -1)
        curses.init_pair(11, 226, -1)
    
    def load_pet(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                return Pet.from_dict(data)
            except:
                pass
        return Pet()
    
    def save_pet(self):
        self.pet.last_update = time.time()
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.pet.to_dict(), f)
        except:
            pass
    
    def get_mood(self):
        avg = (self.pet.hunger + self.pet.happiness + self.pet.energy + self.pet.health + self.pet.cleanliness) / 5
        if avg >= 90: return Mood.ECSTATIC
        elif avg >= 75: return Mood.HAPPY
        elif avg >= 60: return Mood.CONTENT
        elif avg >= 40: return Mood.NEUTRAL
        elif avg >= 25: return Mood.SAD
        else: return Mood.MISERABLE
    
    def get_sprite(self):
        mood = self.get_mood()
        frame = self.animation_frame % 4
        
        if self.sleeping:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ ● ● █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ ● ● █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
            ]
            return sprites[frame]
        
        if self.pet.sickness > 50:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ @ @ █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ @ @ █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ @ @ █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ @ @ █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
            ]
            return sprites[frame]
        
        if mood == Mood.ECSTATIC:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ ^ ^ █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ ^ ^ █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ ^ ^ █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ ^ ^ █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        elif mood == Mood.HAPPY:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ > < █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ > < █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ > < █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ > < █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        elif mood == Mood.CONTENT:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ o o █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ o o █ ", " █  -  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ o o █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ o o █ ", " █  -  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        elif mood == Mood.NEUTRAL:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  -  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  ▀  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ - - █ ", " █  -  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        elif mood == Mood.SAD:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ T T █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ T T █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ T T █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ T T █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        else:
            sprites = [
                ["  ▄▄▄▄▄  ", " █ X X █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ X X █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ X X █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
                ["  ▄▄▄▄▄  ", " █ X X █ ", " █  ▄  █ ", " ▀▀▀▀▀▀▀ "],
            ]
        return sprites[frame]
    
    def update_stats(self):
        now = time.time()
        dt = now - self.pet.last_update
        
        if dt > 1:
            hours = dt / 3600
            self.pet.hunger = max(0, self.pet.hunger - hours * 5)
            self.pet.happiness = max(0, self.pet.happiness - hours * 3)
            self.pet.cleanliness = max(0, self.pet.cleanliness - hours * 2)
            
            if not self.sleeping:
                self.pet.energy = max(0, self.pet.energy - hours * 4)
            else:
                self.pet.energy = min(100, self.pet.energy + hours * 20)
            
            if self.pet.hunger < 20 or self.pet.cleanliness < 10:
                self.pet.health = max(0, self.pet.health - hours * 5)
                self.pet.sickness = min(100, self.pet.sickness + hours * 10)
            else:
                self.pet.sickness = max(0, self.pet.sickness - hours * 5)
            
            if random.random() < hours * 0.1:
                self.pet.poop_count = min(5, self.pet.poop_count + 1)
                self.pet.cleanliness = max(0, self.pet.cleanliness - 10)
            
            self.pet.age = int((now - self.pet.birth_time) / 3600)
            self.pet.last_update = now
    
    def perform_action(self, action):
        if self.sleeping and action != Action.SLEEP:
            self.message = f"{self.pet.name} is sleeping!"
            self.message_timer = 60
            return
        
        if action == Action.FEED:
            if self.pet.money >= 10:
                self.pet.money -= 10
                self.pet.hunger = min(100, self.pet.hunger + 30)
                self.pet.weight += 1
                self.pet.happiness = min(100, self.pet.happiness + 5)
                self.message = f"{self.pet.name} ate happily! 🍎"
            else:
                self.message = "Not enough money!"
        
        elif action == Action.PLAY:
            if self.pet.energy >= 10:
                self.pet.energy -= 10
                self.pet.happiness = min(100, self.pet.happiness + 20)
                self.pet.hunger = max(0, self.pet.hunger - 5)
                self.pet.experience += 10
                self.message = f"{self.pet.name} played! 🎮"
                self.start_minigame()
            else:
                self.message = f"{self.pet.name} is too tired!"
        
        elif action == Action.PET:
            self.pet.happiness = min(100, self.pet.happiness + 10)
            self.message = f"{self.pet.name} enjoyed that! 💕"
        
        elif action == Action.SLEEP:
            if self.sleeping:
                self.sleeping = False
                self.message = f"{self.pet.name} woke up refreshed! ☀️"
            else:
                self.sleeping = True
                self.message = f"{self.pet.name} went to sleep... 💤"
        
        elif action == Action.MEDICINE:
            if self.pet.money >= 25:
                self.pet.money -= 25
                self.pet.health = min(100, self.pet.health + 40)
                self.pet.sickness = max(0, self.pet.sickness - 50)
                self.message = f"{self.pet.name} took medicine! 💊"
            else:
                self.message = "Not enough money!"
        
        elif action == Action.CLEAN:
            self.pet.cleanliness = 100
            self.pet.poop_count = 0
            self.pet.happiness = min(100, self.pet.happiness + 5)
            self.message = f"{self.pet.name} is clean now! ✨"
        
        elif action == Action.TRAIN:
            if self.pet.energy >= 15 and self.pet.happiness >= 30:
                self.pet.energy -= 15
                self.pet.discipline = min(100, self.pet.discipline + 10)
                self.pet.experience += 20
                self.message = f"{self.pet.name} trained hard! 💪"
            else:
                self.message = "Not ready to train!"
        
        self.pet.total_actions += 1
        self.check_level_up()
        self.message_timer = 60
        self.save_pet()
    
    def check_level_up(self):
        required = self.pet.level * 100
        if self.pet.experience >= required:
            self.pet.level += 1
            self.pet.experience -= required
            self.pet.health = 100
            self.pet.happiness = 100
            self.message = f"🎉 LEVEL UP! {self.pet.name} is now level {self.pet.level}! 🎉"
            self.message_timer = 120
    
    def start_minigame(self):
        games = ['catch', 'guess', 'reflex']
        self.minigame = random.choice(games)
        if self.minigame == 'catch':
            self.minigame_state = {'x': self.width // 2, 'target_x': random.randint(10, self.width - 10), 'score': 0, 'time': 100}
        elif self.minigame == 'guess':
            self.minigame_state = {'number': random.randint(1, 10), 'guesses': 0, 'max_guesses': 3}
        elif self.minigame == 'reflex':
            self.minigame_state = {'state': 'wait', 'wait_time': random.randint(50, 150), 'start_time': 0}
    
    def update_minigame(self):
        if not self.minigame:
            return
        
        key = self.stdscr.getch()
        
        if self.minigame == 'catch':
            state = self.minigame_state
            if key == curses.KEY_LEFT:
                state['x'] = max(5, state['x'] - 2)
            elif key == curses.KEY_RIGHT:
                state['x'] = min(self.width - 5, state['x'] + 2)
            
            state['time'] -= 1
            if abs(state['x'] - state['target_x']) < 3:
                state['score'] += 1
                state['target_x'] = random.randint(10, self.width - 10)
                self.pet.money += 5
                self.pet.experience += 5
            
            if state['time'] <= 0:
                self.message = f"Minigame over! Earned ${state['score'] * 5}"
                self.message_timer = 60
                self.minigame = None
        
        elif self.minigame == 'guess':
            state = self.minigame_state
            if key >= ord('1') and key <= ord('9'):
                guess = key - ord('0')
                state['guesses'] += 1
                if guess == state['number']:
                    self.message = "Correct! 🎉"
                    self.pet.money += 20
                    self.pet.experience += 10
                    self.minigame = None
                elif state['guesses'] >= state['max_guesses']:
                    self.message = f"Wrong! It was {state['number']}"
                    self.minigame = None
                elif guess < state['number']:
                    self.message = "Higher! ⬆"
                else:
                    self.message = "Lower! ⬇"
                self.message_timer = 30
        
        elif self.minigame == 'reflex':
            state = self.minigame_state
            if state['state'] == 'wait':
                state['wait_time'] -= 1
                if state['wait_time'] <= 0:
                    state['state'] = 'press'
                    state['start_time'] = time.time()
            elif state['state'] == 'press':
                if key != -1:
                    reaction = (time.time() - state['start_time']) * 1000
                    if reaction < 500:
                        self.message = f"Fast! {reaction:.0f}ms 🏆"
                        self.pet.money += 30
                    else:
                        self.message = f"Slow... {reaction:.0f}ms"
                    self.message_timer = 60
                    self.minigame = None
    
    def draw_bar(self, y, x, label, value, max_val=100, color=1, width=20):
        try:
            self.stdscr.addstr(y, x, f"{label}: ", curses.color_pair(7))
            filled = int(value / max_val * width)
            bar = "█" * filled + "░" * (width - filled)
            self.stdscr.addstr(y, x + len(label) + 2, bar, curses.color_pair(color))
            self.stdscr.addstr(f" {value}/{max_val}")
        except curses.error:
            pass
    
    def draw_pet(self):
        sprite = self.get_sprite()
        px = (self.width - 11) // 2
        py = 5
        mood = self.get_mood()
        
        mood_colors = {
            Mood.ECSTATIC: 11, Mood.HAPPY: 1, Mood.CONTENT: 2,
            Mood.NEUTRAL: 7, Mood.SAD: 4, Mood.MISERABLE: 3
        }
        color = mood_colors.get(mood, 7)
        
        if self.pet.sickness > 50:
            color = 3
        
        for i, line in enumerate(sprite):
            try:
                self.stdscr.addstr(py + i, px, line, curses.color_pair(color))
            except curses.error:
                pass
        
        name_str = f" {self.pet.name} "
        try:
            self.stdscr.addstr(py - 1, px + (11 - len(name_str)) // 2, name_str, curses.color_pair(5) | curses.A_BOLD)
        except curses.error:
            pass
        
        mood_str = f" {mood.name} "
        try:
            self.stdscr.addstr(py + 4, px + (11 - len(mood_str)) // 2, mood_str, curses.color_pair(color))
        except curses.error:
            pass
    
    def draw_stats(self):
        sy = 12
        self.draw_bar(sy, 2, "HUNGER", self.pet.hunger, color=8)
        self.draw_bar(sy + 1, 2, "HAPPY", self.pet.happiness, color=9)
        self.draw_bar(sy + 2, 2, "ENERGY", self.pet.energy, color=4)
        self.draw_bar(sy + 3, 2, "HEALTH", self.pet.health, color=1)
        self.draw_bar(sy + 4, 2, "CLEAN", self.pet.cleanliness, color=6)
        self.draw_bar(sy + 5, 2, "DISCIP", self.pet.discipline, color=5)
        
        try:
            info = f" Age: {self.pet.age}h | Level: {self.pet.level} | XP: {self.pet.experience}/{self.pet.level*100} | ${self.pet.money} | Weight: {self.pet.weight}kg "
            self.stdscr.addstr(sy + 7, 2, info[:self.width-4], curses.color_pair(7))
            if self.pet.poop_count > 0:
                self.stdscr.addstr(sy + 8, 2, f" 💩 x{self.pet.poop_count} ", curses.color_pair(8))
            if self.pet.sickness > 0:
                self.stdscr.addstr(sy + 8, 20, f" 🤒 Sickness: {self.pet.sickness}% ", curses.color_pair(3))
        except curses.error:
            pass
    
    def draw_message(self):
        if self.message_timer > 0 and self.message:
            try:
                x = (self.width - len(self.message)) // 2
                self.stdscr.addstr(self.height - 4, max(0, x), self.message, curses.color_pair(11) | curses.A_BOLD)
                self.message_timer -= 1
            except curses.error:
                pass
    
    def draw_menu(self):
        if not self.menu_open:
            return
        
        actions = [
            ("🍎 Feed ($10)", Action.FEED),
            ("🎮 Play", Action.PLAY),
            ("💕 Pet", Action.PET),
            ("💤 Sleep", Action.SLEEP),
            ("💊 Medicine ($25)", Action.MEDICINE),
            ("✨ Clean", Action.CLEAN),
            ("💪 Train", Action.TRAIN),
        ]
        
        mw = 25
        mh = len(actions) + 2
        mx = (self.width - mw) // 2
        my = (self.height - mh) // 2
        
        try:
            for i in range(mh):
                self.stdscr.addstr(my + i, mx, " " * mw, curses.color_pair(7) | curses.A_REVERSE)
            
            self.stdscr.addstr(my, mx + 2, " ACTIONS ", curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            
            for i, (name, action) in enumerate(actions):
                color = 11 if i == self.menu_selection else 7
                prefix = "► " if i == self.menu_selection else "  "
                self.stdscr.addstr(my + 1 + i, mx + 2, f"{prefix}{name}", curses.color_pair(color) | curses.A_REVERSE)
        except curses.error:
            pass
    
    def draw_minigame(self):
        if not self.minigame:
            return
        
        try:
            if self.minigame == 'catch':
                state = self.minigame_state
                self.stdscr.addstr(1, 2, f"CATCH! Time: {state['time']//10}s Score: {state['score']} ←/→ to move", curses.color_pair(11))
                self.stdscr.addstr(self.height - 10, state['target_x'], "★", curses.color_pair(11))
                self.stdscr.addstr(self.height - 8, state['x'], "███", curses.color_pair(4))
            
            elif self.minigame == 'guess':
                state = self.minigame_state
                self.stdscr.addstr(self.height // 2 - 2, (self.width - 30) // 2, "GUESS THE NUMBER (1-9)", curses.color_pair(11))
                self.stdscr.addstr(self.height // 2, (self.width - 30) // 2, f"Guesses left: {state['max_guesses'] - state['guesses']}", curses.color_pair(9))
                self.stdscr.addstr(self.height // 2 + 1, (self.width - 30) // 2, f"Hint: {self.message}", curses.color_pair(8))
            
            elif self.minigame == 'reflex':
                state = self.minigame_state
                if state['state'] == 'wait':
                    self.stdscr.addstr(self.height // 2, (self.width - 30) // 2, "WAIT FOR IT...", curses.color_pair(2))
                else:
                    self.stdscr.addstr(self.height // 2, (self.width - 30) // 2, "PRESS ANY KEY NOW!", curses.color_pair(11) | curses.A_BLINK)
        except curses.error:
            pass
    
    def draw_help(self):
        try:
            help_text = " MENU: M | QUIT: Q "
            self.stdscr.addstr(self.height - 1, self.width - len(help_text) - 1, help_text, curses.color_pair(7) | curses.A_REVERSE)
        except curses.error:
            pass
    
    def handle_input(self):
        key = self.stdscr.getch()
        
        if self.minigame:
            self.update_minigame()
            return True
        
        if self.menu_open:
            actions = [Action.FEED, Action.PLAY, Action.PET, Action.SLEEP, Action.MEDICINE, Action.CLEAN, Action.TRAIN]
            if key == curses.KEY_UP:
                self.menu_selection = (self.menu_selection - 1) % len(actions)
            elif key == curses.KEY_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(actions)
            elif key == ord('\n') or key == ord(' ') or key == 10:
                self.perform_action(actions[self.menu_selection])
                self.menu_open = False
            elif key == ord('m') or key == ord('M') or key == 27:
                self.menu_open = False
            return True
        
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('m') or key == ord('M'):
            self.menu_open = True
            self.menu_selection = 0
        elif key == ord('1'):
            self.perform_action(Action.FEED)
        elif key == ord('2'):
            self.perform_action(Action.PLAY)
        elif key == ord('3'):
            self.perform_action(Action.PET)
        elif key == ord('4'):
            self.perform_action(Action.SLEEP)
        elif key == ord('5'):
            self.perform_action(Action.MEDICINE)
        elif key == ord('6'):
            self.perform_action(Action.CLEAN)
        elif key == ord('7'):
            self.perform_action(Action.TRAIN)
        elif key == ord('s') or key == ord('S'):
            self.save_pet()
            self.message = "Game saved!"
            self.message_timer = 60
        
        return True
    
    def render(self):
        self.stdscr.erase()
        self.draw_pet()
        self.draw_stats()
        self.draw_message()
        self.draw_menu()
        self.draw_minigame()
        self.draw_help()
        self.stdscr.refresh()
    
    def run(self):
        self.animation_frame = 0
        while self.handle_input():
            self.update_stats()
            self.animation_frame += 1
            self.render()
        self.save_pet()

def main(stdscr):
    game = Tamagotchi(stdscr)
    game.run()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass