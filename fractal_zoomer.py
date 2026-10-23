#!/usr/bin/env python3
"""
Fractal Zoomer - Infinite Mandelbrot/Julia Set Exploration
Navigate the infinite complexity of fractals in real-time.
Controls: Arrow keys=pan, +/-=zoom, j=toggle Julia, c=colors, r=reset, q=quit
"""

import curses
import math
import time
from dataclasses import dataclass
from typing import Tuple
import colorsys


@dataclass
class FractalConfig:
    center_x: float = -0.5
    center_y: float = 0.0
    zoom: float = 1.0
    max_iter: int = 100
    julia_mode: bool = False
    julia_c: complex = complex(-0.7, 0.27015)
    color_mode: int = 0
    smooth: bool = True


class FractalZoomer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.height -= 1
        self.width -= 1
        
        self.config = FractalConfig()
        self.paused = False
        self.auto_zoom = False
        self.zoom_target = None
        self.zoom_speed = 1.02
        
        self.color_modes = [
            'classic', 'rainbow', 'fire', 'ocean', 'forest', 'sunset',
            'monochrome', 'neon', 'pastel', 'bands', 'psychedelic', 'void'
        ]
        
        self.julia_presets = [
            complex(-0.7, 0.27015),
            complex(-0.4, 0.6),
            complex(0.285, 0.01),
            complex(-0.8, 0.156),
            complex(-0.7269, 0.1889),
            complex(-0.835, 0.2321),
            complex(0.45, 0.1428),
            complex(-0.391, -0.587),
            complex(0.3, 0.5),
            complex(-0.1, 0.651),
        ]
        self.julia_preset_idx = 0
        
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(30)
        
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            for i in range(1, 256):
                curses.init_pair(i, i, -1)
        
        self.palette_cache = {}
        self.build_palettes()
    
    def build_palettes(self):
        for mode in self.color_modes:
            palette = []
            for i in range(256):
                t = i / 255.0
                palette.append(self.color_value(t, mode))
            self.palette_cache[mode] = palette
    
    def color_value(self, t: float, mode: str) -> Tuple[int, int, int]:
        if mode == 'classic':
            if t < 0.16:
                r, g, b = t/0.16, 0, 0
            elif t < 0.33:
                r, g, b = 1, (t-0.16)/0.17, 0
            elif t < 0.5:
                r, g, b = 1, 1, (t-0.33)/0.17
            elif t < 0.66:
                r, g, b = 1-(t-0.5)/0.16, 1, 1
            elif t < 0.83:
                r, g, b = 0, 1-(t-0.66)/0.17, 1
            else:
                r, g, b = 0, 0, 1-(t-0.83)/0.17
        elif mode == 'rainbow':
            r, g, b = colorsys.hsv_to_rgb(t * 0.85, 1.0, 1.0)
        elif mode == 'fire':
            r, g, b = colorsys.hsv_to_rgb(t * 0.1, 1.0 - t * 0.3, t)
        elif mode == 'ocean':
            r, g, b = colorsys.hsv_to_rgb(0.55 + t * 0.15, 0.7 + t * 0.3, t)
        elif mode == 'forest':
            r, g, b = colorsys.hsv_to_rgb(0.25 + t * 0.15, 0.6 + t * 0.4, 0.3 + t * 0.7)
        elif mode == 'sunset':
            r, g, b = colorsys.hsv_to_rgb(t * 0.12, 0.8, t)
        elif mode == 'monochrome':
            r = g = b = t
        elif mode == 'neon':
            r, g, b = colorsys.hsv_to_rgb((t + time.time() * 0.05) % 1.0, 1.0, 1.0)
        elif mode == 'pastel':
            r, g, b = colorsys.hsv_to_rgb(t * 0.6, 0.4, 0.6 + t * 0.4)
        elif mode == 'bands':
            band = int(t * 16) / 16.0
            r, g, b = colorsys.hsv_to_rgb(band * 0.8, 0.8, 1.0)
        elif mode == 'psychedelic':
            r, g, b = colorsys.hsv_to_rgb((t * 3.0 + math.sin(time.time() * 2) * 0.1) % 1.0, 1.0, 1.0)
        elif mode == 'void':
            r, g, b = colorsys.hsv_to_rgb((t + time.time() * 0.01) % 1.0, 0.3, 0.9)
        else:
            r = g = b = t
        
        return int(r * 1000), int(g * 1000), int(b * 1000)
    
    def get_color_pair(self, iter_count: int, max_iter: int, smooth_val: float = None) -> int:
        mode = self.color_modes[self.config.color_mode]
        palette = self.palette_cache[mode]
        
        if iter_count == max_iter:
            return 16
        
        if self.config.smooth and smooth_val is not None:
            idx = int(smooth_val * 255) % 256
        else:
            idx = int(iter_count / max_iter * 255) % 256
        
        r, g, b = palette[idx]
        color_id = 16 + (r // 40) * 36 + (g // 40) * 6 + (b // 40)
        return min(255, max(16, color_id))
    
    def mandelbrot(self, c: complex) -> Tuple[int, float]:
        z = 0
        max_iter = self.config.max_iter
        
        for i in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth:
                    smooth = i + 1 - math.log(math.log(abs(z))) / math.log(2)
                    smooth = smooth / max_iter
                    return i, smooth
                return i, 0.0
            z = z * z + c
        
        return max_iter, 0.0
    
    def julia(self, z: complex) -> Tuple[int, float]:
        c = self.config.julia_c
        max_iter = self.config.max_iter
        
        for i in range(max_iter):
            if abs(z) > 2:
                if self.config.smooth:
                    smooth = i + 1 - math.log(math.log(abs(z))) / math.log(2)
                    smooth = smooth / max_iter
                    return i, smooth
                return i, 0.0
            z = z * z + c
        
        return max_iter, 0.0
    
    def screen_to_complex(self, x: int, y: int) -> complex:
        scale = 3.0 / self.config.zoom
        real = self.config.center_x + (x - self.width / 2) * scale / self.width
        imag = self.config.center_y + (y - self.height / 2) * scale / self.height / 2
        return complex(real, imag)
    
    def update(self):
        if self.auto_zoom and self.zoom_target:
            self.config.zoom *= self.zoom_speed
            if self.config.zoom > self.zoom_target:
                self.auto_zoom = False
    
    def draw(self):
        self.stdscr.erase()
        
        mode = 'Julia' if self.config.julia_mode else 'Mandelbrot'
        
        for y in range(self.height):
            for x in range(0, self.width, 2):
                c = self.screen_to_complex(x, y)
                
                if self.config.julia_mode:
                    iter_count, smooth = self.julia(c)
                else:
                    iter_count, smooth = self.mandelbrot(c)
                
                color = self.get_color_pair(iter_count, self.config.max_iter, smooth)
                
                if iter_count == self.config.max_iter:
                    ch = '█'
                else:
                    chars = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
                    idx = int((iter_count / self.config.max_iter) * (len(chars) - 1))
                    ch = chars[idx]
                
                try:
                    self.stdscr.addstr(y, x, ch * 2, curses.color_pair(color))
                except curses.error:
                    pass
        
        self.draw_ui(mode)
        self.stdscr.refresh()
    
    def draw_ui(self, mode: str):
        try:
            color_mode = self.color_modes[self.config.color_mode]
            julia_str = f" c={self.config.julia_c.real:.4f},{self.config.julia_c.imag:.4f}" if self.config.julia_mode else ""
            
            stats = [
                f" {mode}{julia_str} ",
                f" Zoom: {self.config.zoom:.2e} ",
                f" Center: ({self.config.center_x:.6f}, {self.config.center_y:.6f}) ",
                f" Iter: {self.config.max_iter} ",
                f" Colors: {color_mode.upper()} ",
                f" Smooth: {'ON' if self.config.smooth else 'OFF'} ",
                f" {'AUTO-ZOOM' if self.auto_zoom else 'MANUAL'} ",
            ]
            
            for i, stat in enumerate(stats):
                self.stdscr.addstr(self.height, i * 22, stat, curses.color_pair(240) | curses.A_BOLD)
            
            help_text = " Arrows=pan +/-=zoom [j]ulia [c]olors [i]ter [s]mooth [a]uto-zoom [p]reset [r]eset [q]uit"
            self.stdscr.addstr(self.height, max(0, self.width - len(help_text)), help_text, curses.color_pair(240))
        except curses.error:
            pass
    
    def handle_input(self, key: int) -> bool:
        pan_speed = 0.05 / self.config.zoom
        
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord('r') or key == ord('R'):
            self.config = FractalConfig()
        elif key == ord('p') or key == ord('P'):
            self.paused = not self.paused
        elif key == ord('c') or key == ord('C'):
            self.config.color_mode = (self.config.color_mode + 1) % len(self.color_modes)
        elif key == ord('j') or key == ord('J'):
            self.config.julia_mode = not self.config.julia_mode
            if self.config.julia_mode:
                self.config.julia_c = self.julia_presets[self.julia_preset_idx]
        elif key == ord('s') or key == ord('S'):
            self.config.smooth = not self.config.smooth
        elif key == ord('a') or key == ord('A'):
            self.auto_zoom = not self.auto_zoom
            if self.auto_zoom:
                self.zoom_target = self.config.zoom * 1000
        elif key == ord('i') or key == ord('I'):
            self.config.max_iter = min(500, self.config.max_iter + 10)
        elif key == ord('k') or key == ord('K'):
            self.config.max_iter = max(20, self.config.max_iter - 10)
        elif key == ord('p'):  # preset
            self.julia_preset_idx = (self.julia_preset_idx + 1) % len(self.julia_presets)
            if self.config.julia_mode:
                self.config.julia_c = self.julia_presets[self.julia_preset_idx]
        elif key == curses.KEY_UP:
            self.config.center_y -= pan_speed
        elif key == curses.KEY_DOWN:
            self.config.center_y += pan_speed
        elif key == curses.KEY_LEFT:
            self.config.center_x -= pan_speed
        elif key == curses.KEY_RIGHT:
            self.config.center_x += pan_speed
        elif key == ord('+') or key == ord('='):
            self.config.zoom *= 1.5
        elif key == ord('-') or key == ord('_'):
            self.config.zoom /= 1.5
        elif key == ord('z') or key == ord('Z'):
            self.config.zoom *= 0.5
        elif key == ord('x') or key == ord('X'):
            self.config.zoom *= 2.0
        elif key == curses.KEY_RESIZE:
            self.handle_resize()
        return True
    
    def handle_resize(self):
        self.height, self.width = self.stdscr.getmaxyx()
        self.height -= 1
        self.width -= 1
    
    def run(self):
        while True:
            self.update()
            self.draw()
            key = self.stdscr.getch()
            if key != -1:
                if not self.handle_input(key):
                    break


def main(stdscr):
    zoomer = FractalZoomer(stdscr)
    zoomer.run()


if __name__ == '__main__':
    curses.wrapper(main)