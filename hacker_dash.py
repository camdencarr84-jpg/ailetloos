#!/usr/bin/env python3
"""
Hacker Terminal Dashboard - Fake System Monitor
"""

import curses
import time
import random
import threading
from datetime import datetime

class HackerDashboard:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(100)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_WHITE, -1)
        curses.init_pair(7, curses.COLOR_BLUE, -1)
        
        self.logs = []
        self.max_logs = self.height - 10
        self.cpu_usage = 0
        self.mem_usage = 0
        self.net_up = 0
        self.net_down = 0
        self.processes = []
        self.generate_processes()
        self.last_update = time.time()
        
        self.ips = [f"192.168.1.{i}" for i in range(1, 255)]
        self.ports = [22, 80, 443, 21, 25, 53, 3306, 5432, 6379, 27017]
        self.protocols = ['TCP', 'UDP', 'ICMP']
        self.statuses = ['ESTABLISHED', 'SYN_SENT', 'TIME_WAIT', 'CLOSE_WAIT', 'LISTEN']
        
    def generate_processes(self):
        names = ['systemd', 'kthreadd', 'ksoftirqd', 'migration', 'rcu_sched', 
                 'nginx', 'postgres', 'redis', 'docker', 'kubelet',
                 'python3', 'node', 'chrome', 'firefox', 'code',
                 'ssh', 'bash', 'vim', 'git', 'curl']
        self.processes = []
        for i in range(20):
            self.processes.append({
                'pid': random.randint(1000, 99999),
                'name': random.choice(names),
                'cpu': random.uniform(0, 100),
                'mem': random.uniform(0, 50),
                'user': random.choice(['root', 'www-data', 'postgres', 'docker', 'user'])
            })
            
    def add_log(self, msg, level='info'):
        colors = {'info': 1, 'warn': 3, 'error': 2, 'success': 4, 'debug': 7}
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.logs.append((timestamp, msg, colors.get(level, 1)))
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
            
    def update_stats(self):
        self.cpu_usage = min(100, max(0, self.cpu_usage + random.uniform(-5, 5)))
        self.mem_usage = min(100, max(0, self.mem_usage + random.uniform(-2, 2)))
        self.net_up = random.uniform(0, 100)
        self.net_down = random.uniform(0, 500)
        
        for p in self.processes:
            p['cpu'] = min(100, max(0, p['cpu'] + random.uniform(-10, 10)))
            p['mem'] = min(50, max(0, p['mem'] + random.uniform(-2, 2)))
            
        if random.random() < 0.3:
            events = [
                ("New connection from {ip}:{port}", 'info'),
                ("Port scan detected from {ip}", 'warn'),
                ("Firewall blocked {ip}", 'success'),
                ("SSH login attempt from {ip}", 'warn'),
                ("Database query executed", 'debug'),
                ("Cache miss for key: {key}", 'debug'),
                ("SSL handshake completed", 'success'),
                ("Rate limit exceeded for {ip}", 'error'),
            ]
            evt, level = random.choice(events)
            ip = random.choice(self.ips)
            port = random.choice(self.ports)
            key = f"session:{random.randint(1000,9999)}"
            self.add_log(evt.format(ip=ip, port=port, key=key), level)
            
    def draw_bar(self, y, x, width, percent, label, color):
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        try:
            self.stdscr.addstr(y, x, f"{label}: [{bar}] {percent:5.1f}%", curses.color_pair(color))
        except curses.error:
            pass
            
    def draw_graph(self, y, x, width, height, values, color):
        if not values:
            return
        max_val = max(values) if max(values) > 0 else 1
        for i, val in enumerate(values[-width:]):
            h = int((val / max_val) * height)
            for row in range(h):
                try:
                    self.stdscr.addch(y + height - row, x + i, '▄', curses.color_pair(color))
                except curses.error:
                    pass
                    
    def render(self):
        self.stdscr.erase()
        
        title = " ██╗  ██╗ █████╗ ██╗     ██╗     ██████╗ ███████╗███████╗"
        title2 = " ██║  ██║██╔══██╗██║     ██║     ██╔══██╗██╔════╝██╔════╝"
        title3 = " ███████║███████║██║     ██║     ██████╔╝█████╗  ███████╗"
        title4 = " ██╔══██║██╔══██║██║     ██║     ██╔═══╝ ██╔══╝  ╚════██║"
        title5 = " ██║  ██║██║  ██║███████╗███████╗██║     ███████╗███████║"
        title6 = " ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚══════╝"
        try:
            self.stdscr.addstr(0, (self.width - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(1, (self.width - len(title)) // 2, title2, curses.color_pair(1))
            self.stdscr.addstr(2, (self.width - len(title)) // 2, title3, curses.color_pair(1))
            self.stdscr.addstr(3, (self.width - len(title)) // 2, title4, curses.color_pair(1))
            self.stdscr.addstr(4, (self.width - len(title)) // 2, title5, curses.color_pair(1))
            self.stdscr.addstr(5, (self.width - len(title)) // 2, title6, curses.color_pair(1))
        except curses.error:
            pass
            
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.stdscr.addstr(0, self.width - 30, f" {now} ", curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass
            
        self.draw_bar(7, 2, 40, self.cpu_usage, "CPU", 1 if self.cpu_usage < 80 else 2)
        self.draw_bar(8, 2, 40, self.mem_usage, "MEM", 4 if self.mem_usage < 80 else 2)
        self.draw_bar(9, 2, 40, self.net_up, "NET ↑", 5)
        self.draw_bar(10, 2, 40, self.net_down, "NET ↓", 3)
        
        self.cpu_history = getattr(self, 'cpu_history', [])
        self.cpu_history.append(self.cpu_usage)
        if len(self.cpu_history) > 60:
            self.cpu_history.pop(0)
        self.draw_graph(7, 50, 60, 8, self.cpu_history, 1)
        
        try:
            self.stdscr.addstr(6, 50, " CPU History (60s) ", curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass
            
        try:
            self.stdscr.addstr(16, 2, " PROCESSES ", curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(16, 50, " NETWORK CONNECTIONS ", curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(16, self.width // 2 + 30, " SYSTEM LOGS ", curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass
            
        header = f"{'PID':>6} {'USER':<10} {'CPU%':>6} {'MEM%':>6} {'COMMAND'}"
        try:
            self.stdscr.addstr(17, 2, header[:self.width//3], curses.color_pair(6) | curses.A_BOLD)
        except curses.error:
            pass
            
        sorted_procs = sorted(self.processes, key=lambda x: x['cpu'], reverse=True)[:10]
        for i, p in enumerate(sorted_procs):
            color = 1 if p['cpu'] < 50 else (3 if p['cpu'] < 80 else 2)
            line = f"{p['pid']:>6} {p['user']:<10} {p['cpu']:>6.1f} {p['mem']:>6.1f} {p['name']}"
            try:
                self.stdscr.addstr(18 + i, 2, line[:self.width//3 - 2], curses.color_pair(color))
            except curses.error:
                pass
                
        net_header = f"{'PROTO':<5} {'LOCAL':<20} {'REMOTE':<20} {'STATE'}"
        try:
            self.stdscr.addstr(17, self.width // 3 + 5, net_header[:self.width//3 - 10], curses.color_pair(6) | curses.A_BOLD)
        except curses.error:
            pass
            
        for i in range(10):
            proto = random.choice(self.protocols)
            local = f"0.0.0.0:{random.choice(self.ports)}"
            remote = f"{random.choice(self.ips)}:{random.randint(1024, 65535)}"
            state = random.choice(self.statuses)
            color = 1 if state == 'ESTABLISHED' else (3 if state == 'LISTEN' else 7)
            line = f"{proto:<5} {local:<20} {remote:<20} {state}"
            try:
                self.stdscr.addstr(18 + i, self.width // 3 + 5, line[:self.width//3 - 10], curses.color_pair(color))
            except curses.error:
                pass
                
        for i, (ts, msg, color) in enumerate(self.logs[-(self.height - 20):]):
            try:
                self.stdscr.addstr(18 + i, self.width // 2 + 30, f"[{ts}] {msg}"[:self.width - self.width // 2 - 32], curses.color_pair(color))
            except curses.error:
                pass
                
        footer = " Q=Quit  R=Refresh  C=Clear Logs  S=Stress Test"
        try:
            self.stdscr.addstr(self.height - 1, 0, footer[:self.width-1], curses.color_pair(6))
        except curses.error:
            pass
            
        self.stdscr.refresh()
        
    def run(self):
        self.add_log("System initialized", 'success')
        self.add_log("Loading kernel modules...", 'info')
        self.add_log("Starting network services...", 'info')
        self.add_log("Firewall rules applied", 'success')
        self.add_log("Dashboard ready", 'success')
        
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            elif key in (ord('r'), ord('R')):
                self.generate_processes()
                self.add_log("Process list refreshed", 'info')
            elif key in (ord('c'), ord('C')):
                self.logs.clear()
                self.add_log("Logs cleared", 'warn')
            elif key in (ord('s'), ord('S')):
                self.add_log("STRESS TEST INITIATED", 'error')
                for _ in range(5):
                    self.cpu_usage = min(100, self.cpu_usage + 15)
                    self.render()
                    time.sleep(0.1)
                self.add_log("Stress test completed", 'success')
                
            self.update_stats()
            self.render()
            time.sleep(0.1)

def main(stdscr):
    dash = HackerDashboard(stdscr)
    dash.run()

if __name__ == '__main__':
    curses.wrapper(main)