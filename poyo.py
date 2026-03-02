#!/usr/bin/env python3
import time, os, sys, threading, json, termios, tty, select, random
from datetime import datetime
from pathlib import Path

# --- Mission Config (2026) ---
USER_ID = "Cosmic Kirbs"
STATS_PATH = Path.home() / '.pomodoro_stats.json'
METERS_PER_MINUTE = 10
SIGNAL_FILE = 'music_signal.txt'

COLORS = {
    'c': '\033[96m', 's': '\033[93m', 'p': '\033[38;5;213m', 
    'g': '\033[92m', 'v': '\033[90m', 'r': '\033[0m', 'bold': '\033[1m'
}

QUOTES = {
    'iro': ['Tea is just hot leaf juice!', 'Hope is something you give yourself.'],
    'mj': ['Heal the world.', 'Lies run sprints, truth runs marathons.'],
    'lana': ['Live fast, die young.', 'I believe in the person I want to become.'],
    'bronte': ['I am no bird; and no net ensnares me.', 'I would always rather be happy than dignified.'],
    'kant': ['Science is organized knowledge.', 'Act only according to that maxim...'],
    'heroic': ['Marcus Aurelius: The impediment to action advances action.', 'Churchill: Success is not final.'],
    'lyrics': ['Bowie: Ground Control to Major Tom.', 'Billie: You should see me in a crown.'],
    'vibe': ['Main Character Energy detected. 📈', 'No cap, your productivity is skyrocketing.']
}

class CosmicTimer:
    def __init__(self):
        self.dist_goal = 0
        self.time_goal_s = 0
        self.elapsed = 0
        self.running = False
        self.paused = False
        self.in_chat = False
        self.stats = self.load_stats()

    def load_stats(self):
        if STATS_PATH.exists():
            try:
                with open(STATS_PATH, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def log_mission(self):
        dist = (self.elapsed / 60) * METERS_PER_MINUTE
        if USER_ID not in self.stats:
            self.stats[USER_ID] = {'total_m': 0, 'sessions': 0, 'history': []}
        
        self.stats[USER_ID]['total_m'] += dist
        self.stats[USER_ID]['sessions'] += 1
        self.stats[USER_ID]['history'].append({
            'ts': datetime.now().isoformat(), 
            'm': round(dist, 2)
        })
        
        with open(STATS_PATH, 'w') as f:
            json.dump(self.stats, f, indent=2)
            
        # Trigger Music Autoplay Signal
        try:
            with open(SIGNAL_FILE, 'w') as f:
                f.write('PLAY_NEXT')
        except Exception as e:
            print(f"Signal Error: {e}")

    def clear(self):
        # ANSI escape to clear screen and move cursor to home (reduces flicker)
        print("\033[H\033[J", end="")

    def chat_mode(self):
        self.in_chat = True
        self.clear()
        print(f"{COLORS['p']}💬 CATALOG: iro, mj, lana, bronte, kant, heroic, lyrics, vibe (type 'back' to exit){COLORS['r']}")
        
        # Temporary switch back to cooked mode for input
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old) 
            while True:
                cmd = input(f"{COLORS['c']}{USER_ID} > {COLORS['r']}").lower().strip()
                if cmd == 'back': break
                if cmd in QUOTES:
                    print(f"{COLORS['s']}Reflect: {random.choice(QUOTES[cmd])}{COLORS['r']}\n")
                else:
                    print(f"{COLORS['v']}Unknown catalog entry.{COLORS['r']}")
        finally:
            tty.setcbreak(fd) # Return to raw for the timer
        self.in_chat = False

    def run(self):
        self.clear()
        print(f"{COLORS['s']}{COLORS['bold']}🌟 COSMIC POMODORO IGNITION (2026) 🌟{COLORS['r']}")
        try:
            val = input(f"\n{COLORS['g']}Enter distance goal in meters: {COLORS['r']}")
            self.dist_goal = int(val)
            self.time_goal_s = (self.dist_goal / METERS_PER_MINUTE) * 60
            self.running = True
        except ValueError:
            print("Invalid input. Mission aborted.")
            return

        def listen():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while self.running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        k = sys.stdin.read(1).lower()
                        if k == ' ': self.paused = not self.paused
                        elif k == 'c': self.chat_mode()
                        elif k == 'q': 
                            self.running = False
                            break
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

        threading.Thread(target=listen, daemon=True).start()

        try:
            while self.running and self.elapsed < self.time_goal_s:
                if not self.in_chat:
                    self.clear()
                    m, s = divmod(int(self.elapsed), 60)
                    cur_dist = (self.elapsed / 60) * METERS_PER_MINUTE
                    
                    status = f"{COLORS['v']}[PAUSED]{COLORS['r']}" if self.paused else f"{COLORS['g']}[ACTIVE]{COLORS['r']}"
                    
                    print(f"{COLORS['c']}🚀 MISSION | PILOT: {USER_ID} {status}{COLORS['r']}")
                    print(f"{COLORS['s']}TIME: {m:02d}:{s:02d} | DIST: {cur_dist:.1f} / {self.dist_goal}m{COLORS['r']}")
                    
                    # Kirby animation
                    pos = (int(self.elapsed) % 20)
                    print(f"\n{' ' * pos}{COLORS['p']}<( \" )> *poyo*{COLORS['r']}")
                    
                    print(f"\n{COLORS['v']}Controls: [Space] Pause | [C] Chat | [Q] Log & Autoplay{COLORS['r']}")
                
                if not self.paused:
                    self.elapsed += 1
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False

        self.log_mission()
        print(f"\n{COLORS['g']}✨ MISSION COMPLETE. Autoplay triggered for {USER_ID}.{COLORS['r']}")
        print(f"{COLORS['c']}Logged {round((self.elapsed/60)*METERS_PER_MINUTE, 2)}m to history.{COLORS['r']}\n")

if __name__ == "__main__":
    CosmicTimer().run()