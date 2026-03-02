#!/usr/bin/env python3
import time, os, sys, threading, json, termios, tty, subprocess, random, datetime
from pathlib import Path

COLORS = {"cosmic": "\033[38;5;141m", "solar": "\033[38;5;220m", "pink": "\033[38;5;213m", "reset": "\033[0m", "cyan": "\033[36m"}

QUOTES = {
    'iro': ['Tea is just hot leaf juice!', 'Hope is something you give yourself.'],
    'mj': ['Heal the world.', 'Lies run sprints, truth runs marathons.'],
    'lana': ['Live fast, die young.', 'I believe in the person I want to become.'],
    'bronte': ['I am no bird; and no net ensnares me.', 'I would always rather be happy than dignified.'],
    'kant': ['Science is organized knowledge. Wisdom is organized life.', 'Act only according to that maxim...'],
    'heroic': ['Marcus Aurelius: The impediment to action advances action.', 'Churchill: Success is not final.'],
    'lyrics': ['Bowie: Ground Control to Major Tom.', 'Billie: You should see me in a crown.'],
    'vibe': ['Main Character Energy detected. 📈', 'No cap, your productivity is skyrocketing.']
}

class PomodoroTimer:
    def __init__(self):
        self.user_name = 'Cosmic Kirbs'
        self.history_file = Path('/workspaces/timetodime2/session_history.json')
        self.elapsed = 0
        self.paused = True
        self.mood = 'Hype'
        self.in_chat = False  # Critical lock for input

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def chat(self):
        self.in_chat = True
        self.clear_screen()
        print(f"{COLORS['pink']}💬 CATALOG: iro, mj, lana, bronte, kant, heroic, lyrics, vibe, or back{COLORS['reset']}")
        while True:
            # Cooked mode is active here
            cmd = input(f"{self.user_name} > ").lower().strip()
            if cmd == 'back': break
            if cmd in QUOTES:
                print(f"{COLORS['cyan']}Reflect: {random.choice(QUOTES[cmd])}{COLORS['reset']}")
            else:
                print("Poyo! (Try: kant, bronte, heroic, or mj)")
        self.in_chat = False

    def run(self):
        self.clear_screen()
        self.paused = False
        
        def listen():
            fd = sys.stdin.fileno()
            while True:
                if not self.in_chat:
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setcbreak(fd)
                        key = sys.stdin.read(1).lower()
                        if key == ' ': self.paused = not self.paused
                        elif key == 'c': 
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            self.chat()
                        elif key == 'q':
                            print(f"\n🎵 Autoplay Active for {self.user_name}...")
                            os._exit(0)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                time.sleep(0.1)

        threading.Thread(target=listen, daemon=True).start()

        while True:
            if not self.paused and not self.in_chat:
                self.elapsed += 1
            self.draw_ui()
            time.sleep(1)

    def draw_ui(self):
        if self.in_chat: return
        self.clear_screen()
        mins, secs = divmod(self.elapsed, 60)
        print(f"{COLORS['cosmic']}🚀 COSMIC MISSION | PILOT: {self.user_name}{COLORS['reset']}")
        print(f"{COLORS['solar']}TIME: {mins:02d}:{secs:02d} | MOOD: {self.mood}{COLORS['reset']}")
        print("\n" + " " * (self.elapsed % 20) + "<( \" )> *poyo*")
        print("-" * 50)
        print(f"{COLORS['cyan']}[Space] Pause | [C] Chat (Heroic/Kant) | [Q] Quit & Log{COLORS['reset']}")

if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
