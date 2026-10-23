#!/usr/bin/env python3
"""
Text Adventure Game - The Lost Temple
"""

import sys
import time
import random

class TextAdventure:
    def __init__(self):
        self.rooms = {
            'entrance': {
                'name': 'Temple Entrance',
                'desc': 'Ancient stone pillars covered in vines frame a dark doorway. Faint torchlight flickers from within.',
                'exits': {'north': 'hallway', 'east': 'garden'},
                'items': ['torch', 'map'],
                'enemy': None
            },
            'hallway': {
                'name': 'Long Hallway',
                'desc': 'A narrow corridor stretches into darkness. Strange symbols glow faintly on the walls.',
                'exits': {'south': 'entrance', 'north': 'chamber', 'west': 'armory'},
                'items': ['health_potion'],
                'enemy': None
            },
            'garden': {
                'name': 'Overgrown Garden',
                'desc': 'Once beautiful, now wild. A stone fountain bubbles with clear water. A statue watches silently.',
                'exits': {'west': 'entrance', 'north': 'library'},
                'items': ['mana_potion', 'key'],
                'enemy': None
            },
            'armory': {
                'name': 'Ancient Armory',
                'desc': 'Rusted weapons line the walls. A gleaming sword rests on a pedestal, untouched by time.',
                'exits': {'east': 'hallway'},
                'items': ['sword', 'shield'],
                'enemy': None
            },
            'library': {
                'name': 'Dusty Library',
                'desc': 'Shelves crumble under ancient tomes. One book lies open on a podium, its pages turning on their own.',
                'exits': {'south': 'garden', 'east': 'chamber'},
                'items': ['spellbook', 'scroll'],
                'enemy': None
            },
            'chamber': {
                'name': 'Main Chamber',
                'desc': 'A massive room with a high vaulted ceiling. In the center sits an altar holding a glowing crystal.',
                'exits': {'south': 'hallway', 'west': 'library', 'north': 'boss_room'},
                'items': ['crystal'],
                'enemy': 'guardian'
            },
            'boss_room': {
                'name': 'Throne Room',
                'desc': 'The final chamber. A dark figure sits upon a throne of bones. The air crackles with dark magic.',
                'exits': {'south': 'chamber'},
                'items': ['crown'],
                'enemy': 'lich_king'
            }
        }
        
        self.enemies = {
            'guardian': {'name': 'Stone Guardian', 'hp': 50, 'atk': 8, 'desc': 'An animated statue blocks your path!'},
            'lich_king': {'name': 'Lich King', 'hp': 100, 'atk': 15, 'desc': 'The Lich King rises from his throne!'}
        }
        
        self.items = {
            'torch': {'name': 'Torch', 'type': 'tool', 'desc': 'Provides light in dark places'},
            'map': {'name': 'Old Map', 'type': 'tool', 'desc': 'Shows the temple layout'},
            'health_potion': {'name': 'Health Potion', 'type': 'consumable', 'heal': 30},
            'mana_potion': {'name': 'Mana Potion', 'type': 'consumable', 'mana': 20},
            'key': {'name': 'Rusty Key', 'type': 'key', 'desc': 'Opens locked doors'},
            'sword': {'name': 'Ancient Sword', 'type': 'weapon', 'atk': 15},
            'shield': {'name': 'Iron Shield', 'type': 'armor', 'def': 10},
            'spellbook': {'name': 'Spellbook', 'type': 'weapon', 'atk': 20, 'magic': True},
            'scroll': {'name': 'Scroll of Fireball', 'type': 'consumable', 'dmg': 40},
            'crystal': {'name': 'Power Crystal', 'type': 'quest', 'desc': 'Pulses with energy'},
            'crown': {'name': 'Crown of Power', 'type': 'quest', 'desc': 'The Lich King\'s crown'}
        }
        
        self.player = {
            'hp': 100,
            'max_hp': 100,
            'mana': 50,
            'max_mana': 50,
            'atk': 10,
            'def': 5,
            'inventory': [],
            'equipped_weapon': None,
            'equipped_armor': None,
            'location': 'entrance',
            'gold': 0
        }
        
        self.combat = False
        self.current_enemy = None
        self.game_over = False
        self.won = False
        
    def type_text(self, text, delay=0.02):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
        
    def print_header(self):
        room = self.rooms[self.player['location']]
        print(f"\n{'='*60}")
        print(f"  {room['name']}")
        print(f"{'='*60}")
        
    def look(self):
        room = self.rooms[self.player['location']]
        self.type_text(room['desc'])
        
        if room['items']:
            print("\nYou see:")
            for item in room['items']:
                print(f"  - {self.items[item]['name']}")
                
        if room['enemy'] and room['enemy'] in self.enemies:
            enemy = self.enemies[room['enemy']]
            print(f"\n⚔ {enemy['desc']}")
            
        print(f"\nExits: {', '.join(room['exits'].keys())}")
        
    def move(self, direction):
        room = self.rooms[self.player['location']]
        if direction in room['exits']:
            self.player['location'] = room['exits'][direction]
            self.look()
        else:
            print("You can't go that way!")
            
    def take(self, item_name):
        room = self.rooms[self.player['location']]
        item_key = None
        for item in room['items']:
            if item_name.lower() in item.lower() or item_name.lower() in self.items[item]['name'].lower():
                item_key = item
                break
                
        if item_key:
            room['items'].remove(item_key)
            self.player['inventory'].append(item_key)
            print(f"You picked up: {self.items[item_key]['name']}")
        else:
            print("That item isn't here!")
            
    def inventory(self):
        if not self.player['inventory']:
            print("Your inventory is empty.")
            return
            
        print("\n--- INVENTORY ---")
        for i, item in enumerate(self.player['inventory'], 1):
            item_data = self.items[item]
            equipped = ""
            if self.player['equipped_weapon'] == item:
                equipped = " (equipped)"
            elif self.player['equipped_armor'] == item:
                equipped = " (equipped)"
            print(f"  {i}. {item_data['name']}{equipped} - {item_data.get('desc', '')}")
            
    def equip(self, item_name):
        for item in self.player['inventory']:
            if item_name.lower() in item.lower() or item_name.lower() in self.items[item]['name'].lower():
                item_data = self.items[item]
                if item_data['type'] == 'weapon':
                    self.player['equipped_weapon'] = item
                    self.player['atk'] = 10 + item_data.get('atk', 0)
                    print(f"Equipped: {item_data['name']} (Attack: {self.player['atk']})")
                elif item_data['type'] == 'armor':
                    self.player['equipped_armor'] = item
                    self.player['def'] = 5 + item_data.get('def', 0)
                    print(f"Equipped: {item_data['name']} (Defense: {self.player['def']})")
                else:
                    print("You can't equip that!")
                return
        print("You don't have that item!")
        
    def use(self, item_name):
        for item in self.player['inventory']:
            if item_name.lower() in item.lower() or item_name.lower() in self.items[item]['name'].lower():
                item_data = self.items[item]
                if item_data['type'] == 'consumable':
                    if 'heal' in item_data:
                        heal = min(item_data['heal'], self.player['max_hp'] - self.player['hp'])
                        self.player['hp'] += heal
                        print(f"You drink the {item_data['name']} and recover {heal} HP!")
                    elif 'mana' in item_data:
                        mana = min(item_data['mana'], self.player['max_mana'] - self.player['mana'])
                        self.player['mana'] += mana
                        print(f"You drink the {item_data['name']} and recover {mana} Mana!")
                    elif 'dmg' in item_data and self.combat:
                        print(f"You cast {item_data['name']}!")
                        self.enemy_take_damage(item_data['dmg'])
                    else:
                        print("You can't use that right now!")
                    self.player['inventory'].remove(item)
                else:
                    print("You can't consume that!")
                return
        print("You don't have that item!")
        
    def stats(self):
        p = self.player
        weapon = self.items[p['equipped_weapon']]['name'] if p['equipped_weapon'] else 'None'
        armor = self.items[p['equipped_armor']]['name'] if p['equipped_armor'] else 'None'
        print(f"\n--- STATS ---")
        print(f"  HP: {p['hp']}/{p['max_hp']}  |  Mana: {p['mana']}/{p['max_mana']}")
        print(f"  Attack: {p['atk']}  |  Defense: {p['def']}")
        print(f"  Weapon: {weapon}  |  Armor: {armor}")
        print(f"  Gold: {p['gold']}")
        
    def start_combat(self, enemy_key):
        self.combat = True
        self.current_enemy = enemy_key
        enemy = self.enemies[enemy_key].copy()
        enemy['max_hp'] = enemy['hp']
        self.enemy = enemy
        print(f"\n⚔ COMBAT STARTED: {enemy['name']} ⚔")
        print(f"Enemy HP: {enemy['hp']}/{enemy['max_hp']}")
        
    def enemy_take_damage(self, dmg):
        self.enemy['hp'] -= dmg
        print(f"You deal {dmg} damage! Enemy HP: {max(0, self.enemy['hp'])}/{self.enemy['max_hp']}")
        if self.enemy['hp'] <= 0:
            self.victory()
            
    def player_attack(self):
        dmg = max(1, self.player['atk'] - random.randint(0, 3))
        self.enemy_take_damage(dmg)
        
    def enemy_attack(self):
        if self.enemy['hp'] <= 0:
            return
        dmg = max(1, self.enemy['atk'] - self.player['def'] - random.randint(0, 2))
        self.player['hp'] -= dmg
        print(f"Enemy deals {dmg} damage! Your HP: {max(0, self.player['hp'])}/{self.player['max_hp']}")
        if self.player['hp'] <= 0:
            self.defeat()
            
    def combat_action(self, action):
        if action == 'attack':
            self.player_attack()
            self.enemy_attack()
        elif action == 'defend':
            print("You brace for impact!")
            self.enemy_attack()
        elif action == 'flee':
            if random.random() < 0.5:
                print("You escaped!")
                self.combat = False
                self.current_enemy = None
            else:
                print("You couldn't escape!")
                self.enemy_attack()
        else:
            print("Invalid combat action!")
            
    def victory(self):
        enemy_name = self.enemies[self.current_enemy]['name']
        print(f"\n✨ You defeated the {enemy_name}!")
        xp = 50 if self.current_enemy == 'lich_king' else 20
        gold = 100 if self.current_enemy == 'lich_king' else 30
        self.player['gold'] += gold
        self.player['max_hp'] += 10
        self.player['hp'] = self.player['max_hp']
        print(f"Gained {xp} XP and {gold} Gold! Max HP increased!")
        
        room = self.rooms[self.player['location']]
        room['enemy'] = None
        self.combat = False
        self.current_enemy = None
        
        if self.current_enemy == 'lich_king':
            self.won = True
            self.game_over = True
            
    def defeat(self):
        print("\n☠ YOU HAVE FALLEN ☠")
        self.game_over = True
        
    def help(self):
        print("""
Commands:
  look / l          - Examine current room
  go <dir> / g      - Move (north, south, east, west)
  take <item>       - Pick up an item
  inventory / i     - View inventory
  equip <item>      - Equip weapon/armor
  use <item>        - Use consumable item
  stats / s         - View character stats
  attack / a        - Attack in combat
  defend / d        - Defend in combat
  flee / f          - Try to flee combat
  help / h          - Show this help
  quit / q          - Exit game
        """)
        
    def parse_command(self, cmd):
        parts = cmd.lower().strip().split()
        if not parts:
            return
            
        verb = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if verb in ('quit', 'q', 'exit'):
            self.game_over = True
        elif verb in ('help', 'h', '?'):
            self.help()
        elif verb in ('look', 'l'):
            self.look()
        elif verb in ('go', 'g', 'move'):
            if args:
                self.move(args[0])
            else:
                print("Go where?")
        elif verb in ('take', 'get', 'pick'):
            if args:
                self.take(' '.join(args))
            else:
                print("Take what?")
        elif verb in ('inventory', 'i', 'inv'):
            self.inventory()
        elif verb in ('equip', 'eq'):
            if args:
                self.equip(' '.join(args))
            else:
                print("Equip what?")
        elif verb in ('use', 'u'):
            if args:
                self.use(' '.join(args))
            else:
                print("Use what?")
        elif verb in ('stats', 's', 'stat'):
            self.stats()
        elif verb in ('attack', 'a', 'hit') and self.combat:
            self.combat_action('attack')
        elif verb in ('defend', 'd', 'block') and self.combat:
            self.combat_action('defend')
        elif verb in ('flee', 'f', 'run') and self.combat:
            self.combat_action('flee')
        else:
            print("Unknown command. Type 'help' for commands.")
            
    def check_combat(self):
        room = self.rooms[self.player['location']]
        if room['enemy'] and room['enemy'] in self.enemies and not self.combat:
            self.start_combat(room['enemy'])
            
    def run(self):
        print("""
╔══════════════════════════════════════════════════════════╗
║           THE LOST TEMPLE - TEXT ADVENTURE              ║
║                                                          ║
║  Explore the ancient temple, defeat enemies,            ║
║  find the Crown of Power, and escape alive!             ║
╚══════════════════════════════════════════════════════════╝
        """)
        self.look()
        self.help()
        
        while not self.game_over:
            try:
                cmd = input("\n> ").strip()
                if cmd:
                    self.parse_command(cmd)
                    self.check_combat()
            except (KeyboardInterrupt, EOFError):
                print("\n\nFarewell, adventurer!")
                break
                
        if self.won:
            print("""
╔══════════════════════════════════════════════════════════╗
║                    VICTORY!                              ║
║                                                          ║
║  You claimed the Crown of Power and defeated            ║
║  the Lich King! The temple's secrets are yours.         ║
╚══════════════════════════════════════════════════════════╝
            """)
        elif self.game_over and not self.won:
            print("\nGame Over. Thanks for playing!")

if __name__ == '__main__':
    game = TextAdventure()
    game.run()
