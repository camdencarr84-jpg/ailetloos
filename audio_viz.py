#!/usr/bin/env python3
"""
Audio Visualizer - Generates and visualizes procedural music
"""

import curses
import math
import random
import time
import threading

class AudioViz:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(30)
        
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 8):
            curses.init_pair(i, i, -1)
            
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.time = 0
        self.playing = True
        self.mode = 0
        self.modes = ['Spectrum', 'Waveform', 'Circular', 'Waterfall', 'Particles']
        
        self.frequencies = [65.41, 82.41, 98.00, 110.00, 123.47, 146.83, 164.81, 196.00]
        self.notes = ['C2', 'E2', 'G2', 'C3', 'D3', 'E3', 'G3', 'C4']
        self.phases = [0] * len(self.frequencies)
        self.amplitudes = [0.5] * len(self.frequencies)
        self.target_amps = [0.5] * len(self.frequencies)
        
        self.waterfall = []
        self.max_waterfall = self.height - 5
        
        self.particles = []
        self.beat_counter = 0
        self.beat_interval = 0
        self.next_beat = 0
        
    def generate_audio(self):
        while self.playing:
            self.time += self.buffer_size / self.sample_rate
            time.sleep(0.01)
            
    def update_music(self):
        self.beat_counter += 1
        if self.beat_counter >= self.next_beat:
            self.beat_counter = 0
            self.next_beat = random.randint(30, 60)
            self.trigger_beat()
            
        for i in range(len(self.amplitudes)):
            self.amplitudes[i] += (self.target_amps[i] - self.amplitudes[i]) * 0.1
            self.target_amps[i] *= 0.98
            self.target_amps[i] = max(0.05, self.target_amps[i])
            
    def trigger_beat(self):
        note = random.randint(0, len(self.frequencies) - 1)
        self.target_amps[note] = 1.0
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': self.width // 2,
                'y': self.height // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(20, 50),
                'color': random.randint(1, 6),
                'char': random.choice(['♪', '♫', '♬', '♩', '★', '✦'])
            })
            
    def get_spectrum(self):
        spectrum = [0] * (self.width // 2)
        for i, (freq, amp) in enumerate(zip(self.frequencies, self.amplitudes)):
            bin_idx = int(freq / self.sample_rate * self.buffer_size * 2)
            if bin_idx < len(spectrum):
                spectrum[bin_idx] = amp
        for i in range(1, len(spectrum) - 1):
            spectrum[i] = max(spectrum[i], (spectrum[i-1] + spectrum[i+1]) * 0.3)
        return spectrum
        
    def update(self):
        self.update_music()
        
        spectrum = self.get_spectrum()
        self.waterfall.insert(0, spectrum)
        if len(self.waterfall) > self.max_waterfall:
            self.waterfall.pop()
            
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
                
    def draw_spectrum(self, spectrum):
        bar_width = max(1, self.width // len(spectrum))
        for i, val in enumerate(spectrum):
            h = int(val * (self.height - 5))
            x = i * bar_width
            color = 1 + (i * 6 // len(spectrum))
            for y in range(h):
                sy = self.height - 2 - y
                if 0 <= sy < self.height - 1:
                    try:
                        char = '█' if y > h * 0.7 else ('▓' if y > h * 0.4 else '░')
                        self.stdscr.addch(sy, x, char, curses.color_pair(color))
                    except curses.error:
                        pass
                        
    def draw_waveform(self):
        points = []
        for i in range(self.width):
            x = i
            y = self.height // 2
            val = 0
            for freq, amp, phase in zip(self.frequencies, self.amplitudes, self.phases):
                val += amp * math.sin(2 * math.pi * freq * self.time + phase)
            y += int(val * (self.height // 4))
            points.append((x, y))
            
        for i in range(1, len(points)):
            x1, y1 = points[i-1]
            x2, y2 = points[i]
            if 0 <= y1 < self.height and 0 <= y2 < self.height:
                try:
                    self.stdscr.addch(y1, x1, '█', curses.color_pair(4) | curses.A_BOLD)
                except curses.error:
                    pass
                    
    def draw_circular(self, spectrum):
        cx, cy = self.width // 2, self.height // 2
        for i, val in enumerate(spectrum):
            angle = (i / len(spectrum)) * 2 * math.pi
            r = int(val * min(cx, cy) * 0.8)
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle) * 0.5)
            if 0 <= x < self.width and 0 <= y < self.height:
                color = 1 + (i * 6 // len(spectrum))
                try:
                    self.stdscr.addch(y, x, '●', curses.color_pair(color) | curses.A_BOLD)
                except curses.error:
                    pass
                    
    def draw_waterfall(self):
        for row_idx, spectrum in enumerate(self.waterfall):
            y = row_idx
            if y >= self.height - 1:
                break
            for i, val in enumerate(spectrum):
                x = i * max(1, self.width // len(spectrum))
                if x < self.width:
                    intensity = int(val * 7)
                    if intensity > 0:
                        try:
                            self.stdscr.addch(y, x, ' ░▒▓█'[min(5, intensity)], curses.color_pair(1 + intensity % 6))
                        except curses.error:
                            pass
                            
    def draw_particles(self):
        for p in self.particles:
            if 0 <= p['x'] < self.width and 0 <= p['y'] < self.height:
                try:
                    self.stdscr.addch(int(p['y']), int(p['x']), p['char'], curses.color_pair(p['color']) | curses.A_BOLD)
                except curses.error:
                    pass
                    
    def draw_ui(self):
        mode_name = self.modes[self.mode]
        info = [
            f" AUDIO VISUALIZER - {mode_name} ",
            f"Notes: {' '.join(f'{n}:{a:.2f}' for n, a in zip(self.notes, self.amplitudes))}",
            "1-5=Mode SPACE=Play/Pause R=Random Beat +=Vol -=Vol Q=Quit"
        ]
        for i, line in enumerate(info):
            try:
                self.stdscr.addstr(i, 2, line[:self.width-4], curses.color_pair(7) | (curses.A_BOLD if i == 0 else 0))
            except curses.error:
                pass
                
    def render(self):
        self.stdscr.erase()
        
        spectrum = self.get_spectrum()
        
        if self.mode == 0:
            self.draw_spectrum(spectrum)
        elif self.mode == 1:
            self.draw_waveform()
        elif self.mode == 2:
            self.draw_circular(spectrum)
        elif self.mode == 3:
            self.draw_waterfall()
        elif self.mode == 4:
            self.draw_particles()
            self.draw_spectrum(spectrum)
            
        self.draw_ui()
        self.stdscr.refresh()
        
    def handle_input(self):
        key = self.stdscr.getch()
        if key in (ord('q'), 27):
            return False
        elif key == ord(' '):
            self.playing = not self.playing
        elif key in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5')):
            self.mode = key - ord('1')
        elif key == ord('r'):
            self.trigger_beat()
        elif key == ord('+'):
            for i in range(len(self.target_amps)):
                self.target_amps[i] = min(1.0, self.target_amps[i] * 1.2)
        elif key == ord('-'):
            for i in range(len(self.target_amps)):
                self.target_amps[i] *= 0.8
        return True
        
    def run(self):
        while True:
            if not self.handle_input():
                break
            self.update()
            self.render()
            time.sleep(0.03)

def main(stdscr):
    viz = AudioViz(stdscr)
    viz.run()

if __name__ == '__main__':
    curses.wrapper(main)