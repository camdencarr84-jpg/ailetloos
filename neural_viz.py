#!/usr/bin/env python3
"""
Neural Network Visualization - Watch a neural network learn in real-time
"""

import curses
import random
import math
import time

class NeuralViz:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_CYAN, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        
        self.layers = [4, 8, 8, 4, 2]
        self.neurons = []
        self.connections = []
        self.build_network()
        
        self.inputs = [0.0] * self.layers[0]
        self.targets = [0.0] * self.layers[-1]
        self.epoch = 0
        self.loss = 1.0
        self.auto_train = True
        
    def build_network(self):
        self.neurons = []
        layer_spacing = (self.width - 4) / (len(self.layers) - 1)
        
        for li, layer_size in enumerate(self.layers):
            layer = []
            x = int(2 + li * layer_spacing)
            spacing = (self.height - 4) / (layer_size + 1)
            for ni in range(layer_size):
                y = int(2 + (ni + 1) * spacing)
                layer.append({
                    'x': x, 'y': y,
                    'value': 0.0,
                    'bias': random.uniform(-1, 1),
                    'layer': li,
                    'index': ni
                })
            self.neurons.append(layer)
            
        self.connections = []
        for li in range(len(self.layers) - 1):
            conns = []
            for n1 in self.neurons[li]:
                for n2 in self.neurons[li + 1]:
                    conns.append({
                        'from': n1,
                        'to': n2,
                        'weight': random.uniform(-1, 1),
                        'signal': 0.0
                    })
            self.connections.append(conns)
            
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-max(-10, min(10, x))))
        
    def forward(self):
        for li, layer in enumerate(self.neurons):
            if li == 0:
                for ni, n in enumerate(layer):
                    n['value'] = self.inputs[ni]
            else:
                for n in layer:
                    total = n['bias']
                    for c in self.connections[li - 1]:
                        if c['to'] == n:
                            total += c['from']['value'] * c['weight']
                    n['value'] = self.sigmoid(total)
                    
    def get_output(self):
        return [n['value'] for n in self.neurons[-1]]
        
    def train_step(self):
        self.forward()
        outputs = self.get_output()
        
        self.loss = sum((o - t) ** 2 for o, t in zip(outputs, self.targets)) / len(outputs)
        
        lr = 0.3
        for li in range(len(self.connections) - 1, -1, -1):
            for c in self.connections[li]:
                if li == len(self.connections) - 1:
                    error = (c['to']['value'] - self.targets[c['to']['index']]) * c['to']['value'] * (1 - c['to']['value'])
                else:
                    error = sum(c2['weight'] * c2['signal'] for c2 in self.connections[li + 1] if c2['from'] == c['to']) * c['to']['value'] * (1 - c['to']['value'])
                c['signal'] = error
                c['weight'] -= lr * error * c['from']['value']
                
        for li, layer in enumerate(self.neurons):
            for n in layer:
                if li > 0:
                    total = n['bias']
                    for c in self.connections[li - 1]:
                        if c['to'] == n:
                            total += c['from']['value'] * c['weight']
                    n['value'] = self.sigmoid(total)
                    
    def generate_task(self):
        self.epoch += 1
        pattern = self.epoch % 4
        if pattern == 0:
            self.inputs = [1, 0, 0, 0]
            self.targets = [1, 0]
        elif pattern == 1:
            self.inputs = [0, 1, 0, 0]
            self.targets = [1, 0]
        elif pattern == 2:
            self.inputs = [0, 0, 1, 0]
            self.targets = [0, 1]
        else:
            self.inputs = [0, 0, 0, 1]
            self.targets = [0, 1]
            
    def update(self):
        if self.auto_train:
            self.train_step()
            if self.epoch % 10 == 0:
                self.generate_task()
                
    def draw_neuron(self, n, color=7):
        val = n['value']
        size = max(1, int(3 * val))
        chars = ['·', '●', '◆', '█']
        char = chars[min(len(chars) - 1, int(val * (len(chars) - 1)))]
        try:
            self.stdscr.addch(n['y'], n['x'], char, curses.color_pair(color) | curses.A_BOLD)
        except curses.error:
            pass
            
    def draw_connection(self, c, color=7):
        fx, fy = c['from']['x'], c['from']['y']
        tx, ty = c['to']['x'], c['to']['y']
        weight = abs(c['weight'])
        signal = abs(c.get('signal', 0))
        
        steps = max(abs(tx - fx), abs(ty - fy))
        if steps == 0:
            return
            
        for i in range(steps + 1):
            t = i / steps
            x = int(fx + (tx - fx) * t)
            y = int(fy + (ty - fy) * t)
            
            intensity = weight * (1 + signal * 2)
            if intensity > 0.7:
                char = '█'
            elif intensity > 0.4:
                char = '▓'
            elif intensity > 0.2:
                char = '▒'
            else:
                char = '░'
                
            ccolor = 2 if c['weight'] > 0 else 1
            try:
                self.stdscr.addch(y, x, char, curses.color_pair(ccolor) | curses.A_DIM)
            except curses.error:
                pass
                
    def render(self):
        self.stdscr.erase()
        
        for li, conns in enumerate(self.connections):
            for c in conns:
                self.draw_connection(c)
                
        for li, layer in enumerate(self.neurons):
            for n in layer:
                if li == 0:
                    color = 4 if self.inputs[n['index']] > 0.5 else 7
                elif li == len(self.layers) - 1:
                    color = 2 if n['value'] > 0.5 else 1
                else:
                    color = 3 if n['value'] > 0.7 else (6 if n['value'] > 0.4 else 7)
                self.draw_neuron(n, color)
                
        info = [
            f"NEURAL NETWORK VISUALIZATION",
            f"Architecture: {'-'.join(map(str, self.layers))}",
            f"Epoch: {self.epoch} | Loss: {self.loss:.4f}",
            f"Input:  [{' '.join(f'{v:.1f}' for v in self.inputs)}]",
            f"Output: [{' '.join(f'{v:.2f}' for v in self.get_output())}]",
            f"Target: [{' '.join(f'{v:.1f}' for v in self.targets)}]",
            "SPACE=Toggle Auto  N=New Task  +/-=Speed  Q=Quit"
        ]
        for i, line in enumerate(info):
            try:
                self.stdscr.addstr(i, self.width - 40, line[:38], curses.color_pair(7) | (curses.A_BOLD if i < 2 else 0))
            except curses.error:
                pass
                
        layer_names = ["INPUT", "HIDDEN 1", "HIDDEN 2", "HIDDEN 3", "OUTPUT"]
        for li, name in enumerate(layer_names):
            if li < len(self.neurons):
                x = self.neurons[li][0]['x']
                try:
                    self.stdscr.addstr(self.height - 2, x - len(name)//2, name, curses.color_pair(7))
                except curses.error:
                    pass
                    
        self.stdscr.refresh()
        
    def run(self):
        self.generate_task()
        while True:
            key = self.stdscr.getch()
            if key in (ord('q'), 27):
                break
            elif key == ord(' '):
                self.auto_train = not self.auto_train
            elif key == ord('n'):
                self.generate_task()
            elif key == ord('+'):
                pass
            elif key == ord('-'):
                pass
            self.update()
            self.render()
            time.sleep(0.05)

def main(stdscr):
    viz = NeuralViz(stdscr)
    viz.run()

if __name__ == '__main__':
    curses.wrapper(main)