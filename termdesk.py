#!/usr/bin/env python3
"""
Terminal Desktop Environment - Window Manager in Terminal
"""

import curses
import time
import random
import math
from datetime import datetime

class Window:
    def __init__(self, x, y, w, h, title, content_func):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.content_func = content_func
        self.visible = True
        self.focused = False
        self.minimized = False
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
    def contains(self, mx, my):
        return self.x <= mx < self.x + self.w and self.y <= my < self.y + self.h
        
    def draw(self, stdscr, z_index):
        if not self.visible or self.minimized:
            return
            
        border_color = 4 if self.focused else 7
        
        for i in range(self.w):
            try:
                stdscr.addch(self.y, self.x + i, '─', curses.color_pair(border_color))
                stdscr.addch(self.y + self.h - 1, self.x + i, '─', curses.color_pair(border_color))
            except curses.error:
                pass
        for i in range(self.h):
            try:
                stdscr.addch(self.y + i, self.x, '│', curses.color_pair(border_color))
                stdscr.addch(self.y + i, self.x + self.w - 1, '│', curses.color_pair(border_color))
            except curses.error:
                pass
                
        try:
            stdscr.addch(self.y, self.x, '┌', curses.color_pair(border_color))
            stdscr.addch(self.y, self.x + self.w - 1, '┐', curses.color_pair(border_color))
            stdscr.addch(self.y + self.h - 1, self.x, '└', curses.color_pair(border_color))
            stdscr.addch(self.y + self.h - 1, self.x + self.w - 1, '┘', curses.color_pair(border_color))
        except curses.error:
            pass
            
        title_str = f" {self.title} "
        try:
            stdscr.addstr(self.y, self.x + 2, title_str[:self.w-4], curses.color_pair(border_color) | curses.A_BOLD)
        except curses.error:
            pass
            
        btns = " ● ▲ ✕ "
        try:
            stdscr.addstr(self.y, self.x + self.w - len(btns) - 1, btns, curses.color_pair(border_color))
        except curses.error:
            pass
            
        if self.content_func:
            self.content_func(stdscr, self.x + 1, self.y + 1, self.w - 2, self.h - 2)

class TermDesk:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
            
        self.windows = []
        self.focused_idx = -1
        self.clock_time = 0
        self.create_default_windows()
        
    def create_default_windows(self):
        self.add_window(Window(5, 3, 40, 15, "System Monitor", self.draw_sysmon))
        self.add_window(Window(50, 3, 35, 15, "Matrix Rain", self.draw_matrix))
        self.add_window(Window(5, 20, 40, 12, "Calculator", self.draw_calc))
        self.add_window(Window(50, 20, 35, 12, "Notepad", self.draw_notepad))
        self.add_window(Window(90, 3, 30, 29, "File Manager", self.draw_files))
        
    def add_window(self, win):
        self.windows.append(win)
        self.focus_window(len(self.windows) - 1)
        
    def focus_window(self, idx):
        for i, w in enumerate(self.windows):
            w.focused = (i == idx)
        if 0 <= idx < len(self.windows):
            self.focused_idx = idx
            w = self.windows[idx]
            self.windows.pop(idx)
            self.windows.append(w)
            
    def draw_sysmon(self, stdscr, x, y, w, h):
        info = [
            f"CPU:  {'█' * random.randint(0, w//2)}",
            f"RAM:  {'█' * random.randint(0, w//2)}",
            f"DISK: {'█' * random.randint(0, w//2)}",
            f"NET:  ↑{random.randint(0,999)}K ↓{random.randint(0,999)}K",
            "",
            "Processes:",
            "  PID   NAME        CPU%  MEM%",
        ]
        for i, line in enumerate(info):
            if y + i < self.height:
                try:
                    stdscr.addstr(y + i, x, line[:w], curses.color_pair(7))
                except curses.error:
                    pass
                    
        procs = [
            ("1234", "systemd", "2.1", "1.5"),
            ("5678", "chrome", "15.3", "245.2"),
            ("9012", "python", "5.7", "89.1"),
            ("3456", "code", "12.4", "312.5"),
        ]
        for i, (pid, name, cpu, mem) in enumerate(procs):
            if y + 7 + i < self.height:
                try:
                    stdscr.addstr(y + 7 + i, x, f"  {pid}   {name:<10} {cpu:>5}  {mem:>5}", curses.color_pair(2))
                except curses.error:
                    pass
                    
    def draw_matrix(self, stdscr, x, y, w, h):
        for i in range(h - 1):
            line = ""
            for j in range(w - 1):
                if random.random() < 0.1:
                    line += random.choice("01アイウエオカキクケコ")
                else:
                    line += " "
            try:
                stdscr.addstr(y + i, x, line[:w-1], curses.color_pair(2))
            except curses.error:
                pass
                
    def draw_calc(self, stdscr, x, y, w, h):
        keys = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]
        for i, row in enumerate(keys):
            line = " ".join(f"[{k}]" for k in row)
            try:
                stdscr.addstr(y + i + 2, x, line[:w], curses.color_pair(6))
            except curses.error:
                pass
        try:
            stdscr.addstr(y, x, "Display: 0", curses.color_pair(7))
        except curses.error:
            pass
            
    def draw_notepad(self, stdscr, x, y, w, h):
        lines = [
            "Welcome to Notepad!",
            "",
            "Type your notes here...",
            "",
            "Keyboard shortcuts:",
            "  Ctrl+S - Save",
            "  Ctrl+N - New",
            "  Esc - Close window",
        ]
        for i, line in enumerate(lines):
            if y + i < self.height:
                try:
                    stdscr.addstr(y + i, x, line[:w], curses.color_pair(7))
                except curses.error:
                    pass
                    
    def draw_files(self, stdscr, x, y, w, h):
        files = [
            "📁 Documents",
            "  📄 readme.txt",
            "  📄 todo.md",
            "📁 Pictures",
            "  🖼️  screenshot.png",
            "  🖼️  wallpaper.jpg",
            "📁 Projects",
            "  📁 ailetloos",
            "    🐍 snake.py",
            "    🎨 ascii_art.py",
            "    📜 adventure.py",
            "  📁 other",
            "    📄 main.py",
            "📁 Downloads",
            "  📦 package.tar.gz",
        ]
        for i, line in enumerate(files):
            if y + i < self.height:
                color = 4 if line.startswith("📁") else 7
                try:
                    stdscr.addstr(y + i, x, line[:w], curses.color_pair(color))
                except curses.error:
                    pass
                    
    def draw_desktop(self):
        self.stdscr.erase()
        
        for i in range(self.height):
            for j in range(0, self.width, 4):
                try:
                    self.stdscr.addch(i, j, '·', curses.color_pair(8) | curses.A_DIM)
                except curses.error:
                    pass
                    
        for i, win in enumerate(self.windows):
            win.draw(self.stdscr, i)
            
        taskbar_y = self.height - 1
        try:
            self.stdscr.addstr(taskbar_y, 0, " ▣ " + " " * (self.width - 40), curses.color_pair(7) | curses.A_REVERSE)
            now = datetime.now().strftime("%H:%M:%S")
            self.stdscr.addstr(taskbar_y, self.width - 20, f" {now} ", curses.color_pair(7) | curses.A_REVERSE)
        except curses.error:
            pass
            
        try:
            self.stdscr.addstr(0, 2, " TERMINAL DESKTOP ", curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(0, self.width - 50, " F1=New Term F2=Calc F3=Notes F4=Files ", curses.color_pair(7))
        except curses.error:
            pass
            
        self.stdscr.refresh()
        
    def handle_mouse(self, mx, my, bstate):
        if bstate & curses.BUTTON1_PRESSED:
            if my == self.height - 1:
                return
            for i, win in enumerate(self.windows):
                if win.contains(mx, my):
                    if my == win.y and mx >= win.x + win.w - 10:
                        btn_x = mx - (win.x + win.w - 10)
                        if btn_x == 1:
                            win.minimized = True
                        elif btn_x == 3:
                            win.minimized = not win.minimized
                        elif btn_x >= 5:
                            self.windows.pop(i)
                        return
                    self.focus_window(i)
                    win.dragging = True
                    win.drag_offset_x = mx - win.x
                    win.drag_offset_y = my - win.y
                    return
        elif bstate & curses.BUTTON1_RELEASED:
            for win in self.windows:
                win.dragging = False
                
        for win in self.windows:
            if win.dragging:
                win.x = mx - win.drag_offset_x
                win.y = my - win.drag_offset_y
                win.x = max(0, min(win.x, self.width - win.w))
                win.y = max(1, min(win.y, self.height - win.h - 1))
                
    def handle_input(self):
        key = self.stdscr.getch()
        if key in (ord('q'), 27):
            return False
        elif key == curses.KEY_F1:
            self.add_window(Window(
                random.randint(5, self.width - 50),
                random.randint(3, self.height - 20),
                50, 15, "Terminal", self.draw_terminal
            ))
        elif key == curses.KEY_F2:
            self.add_window(Window(
                random.randint(5, self.width - 40),
                random.randint(3, self.height - 15),
                40, 12, "Calculator", self.draw_calc
            ))
        elif key == curses.KEY_F3:
            self.add_window(Window(
                random.randint(5, self.width - 40),
                random.randint(3, self.height - 15),
                40, 12, "Notepad", self.draw_notepad
            ))
        elif key == curses.KEY_F4:
            self.add_window(Window(
                random.randint(5, self.width - 35),
                random.randint(3, self.height - 20),
                35, 18, "Files", self.draw_files
            ))
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, bstate = curses.getmouse()
            self.handle_mouse(mx, my, bstate)
        return True
        
    def draw_terminal(self, stdscr, x, y, w, h):
        lines = [
            "user@termdesk:~$ ",
            "Welcome to the terminal!",
            "Try: ls, pwd, echo hello",
            "",
            "user@termdesk:~$ ",
        ]
        for i, line in enumerate(lines):
            if y + i < self.height:
                try:
                    stdscr.addstr(y + i, x, line[:w], curses.color_pair(2))
                except curses.error:
                    pass
                    
    def run(self):
        while True:
            if not self.handle_input():
                break
            self.draw_desktop()
            time.sleep(0.05)

def main(stdscr):
    desk = TermDesk(stdscr)
    desk.run()

if __name__ == '__main__':
    curses.wrapper(main)