#!/usr/bin/env python3
import time, os, sys, threading, json, termios, tty, subprocess, random, datetime
from pathlib import Path

COLORS = {
    "cosmic": "\033[38;5;141m", "solar": "\033[38;5;220m",
    "pink": "\033[38;5;213m", "reset": "\033[0m", "cyan": "\033[36m",
    "green": "\033[92m", "red": "\033[91m"
}

# THE UNIVERSAL CATALOG: 2026 Edition
QUOTES = {
    'iro': ['Tea is just hot leaf juice!', 'Hope is something you give yourself.', 'Protection and power are overrated.'],
    'mj': ['Heal the world, make it a better place.', 'Lies run sprints, but the truth runs marathons.', 'In a world filled with hate, we must still dare to hope.'],
    'lana': ['Live fast, die young, be wild and have fun.', 'I believe in the person I want to become.', 'Being brave means knowing that when you fail, you don’t fail forever.'],
    'bronte': ['I am no bird; and no net ensnares me.', 'I would always rather be happy than dignified.', 'The soul has an interpreter in the eye.'],
    'kant': ['Science is organized knowledge. Wisdom is organized life.', 'Two things fill the mind with wonder: the starry heavens and the moral law.', 'Act only according to that maxim...'],
    'heroic': ['Marcus Aurelius: The impediment to action advances action.', 'Churchill: Success is not final, failure is not fatal.', 'Seneca: Luck is what happens when preparation meets opportunity.', 'Leonidas: Molon Labe.'],
    'lyrics': ['Bowie: Ground Control to Major Tom.', 'Billie: You should see me in a crown.', 'CAS: K. - I am always thinking of you.', 'Bee Gees: Stayin alive.'],
    'vibe': ['Main Character Energy detected. 📈', 'Vibe check: ABSOLUTE LEGEND.', 'No cap, your productivity is skyrocketing.']
}

class PomodoroTimer:
    def __init__(self):
        self.user_name = 'Cosmic Kirbs'
        self.history_file = Path('/workspaces/timetodime2/session_history.json')
        self.elapsed = 0
        self.paused = True
        self.mood = 'Hype'
        self.remind_interval = 10
        self.in_menu = False

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def save_log(self, completed=True):
        entry = {
            "pilot": self.user_name, 
            "timestamp": str(datetime.datetime.now()), 
            "duration_mins": self.elapsed // 60, 
            "mood": self.mood, 
            "status": "Finished" if completed else "Aborted"
        }
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                try: history = json.load(f)
                except: pass
        history.append(entry)
        with open(self.history_file, 'w') as f: json.dump(history, f, indent=4)

    def chat_menu(self):
        self.in_menu = True
        self.clear_screen()
        print(f"{COLORS['pink']}💬 CATALOG: iro, mj, lana, bronte, kant, heroic, lyrics, vibe, or back{COLORS['reset']}")
        while True:
            cmd = input(f"{self.user_name} > ").lower().strip()
            if cmd == 'back': break
            if cmd in QUOTES:
                print(f"{COLORS['cyan']}Reflect: {random.choice(QUOTES[cmd])}{COLORS['reset']}")
            else:
                print("Poyo! (Try: heroic, kant, or mj)")
        self.in_menu = False

    def settings_menu(self):
        self.in_menu = True
        self.clear_screen()
        print(f"{COLORS['cosmic']}🛠️ CONFIGURATION{COLORS['reset']}")
        print(f"[1] Hydration Reminder: {self.remind_interval}m")
        print(f"[2] Pilot Mood: {self.mood}")
        print(f"[3] Back")
        choice = input("\nSelect: ")
        if choice == '1': 
            try: self.remind_interval = int(input("New Interval (mins): "))
            except: pass
        elif choice == '2': self.mood = "Calm" if self.mood == "Hype" else "Hype"
        self.in_menu = False

    def stats_menu(self):
        self.in_menu = True
        self.clear_screen()
        print(f"{COLORS['solar']}📊 MISSION HISTORY: {self.user_name.upper()}{COLORS['reset']}")
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                for entry in history[-10:]:
                    print(f" {COLORS['green']}√{COLORS['reset']} {entry['timestamp'][:16]} | {entry['duration_mins']}m | {entry['mood']}")
        else: print("No flight data recorded.")
        input("\nPress Enter to return...")
        self.in_menu = False

    def draw_ui(self):
        if self.in_menu: return
        self.clear_screen()
        mins, secs = divmod(self.elapsed, 60)
        print(f"{COLORS['cosmic']}🚀 COSMIC MISSION | PILOT: {self.user_name}{COLORS['reset']}")
        print(f"{COLORS['solar']}TIME: {mins:02d}:{secs:02d} | MOOD: {self.mood}{COLORS['reset']}")
        # Animated Kirby
        print("\n" + " " * (self.elapsed % 30) + "<( \" )> *poyo*")
        print("-" * 55)
        print(f"{COLORS['cyan']}[Space] Pause | [C] Chat | [A] Config | [S] Stats | [M] Music | [Q] Quit{COLORS['reset']}")

    def run(self):
        self.clear_screen()
        self.paused = False
        
        def listen():
            fd = sys.stdin.fileno()
            while True:
                if not self.in_menu:
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setcbreak(fd)
                        key = sys.stdin.read(1).lower()
                        if key == ' ': self.paused = not self.paused
                        elif key == 'c': 
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            self.chat_menu()
                        elif key == 'a': 
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            self.settings_menu()
                        elif key == 's': 
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            self.stats_menu()
                        elif key == 'm' or key == 'q':
                            if key == 'q': self.save_log()
                            try:
                                with open('music_signal.txt', 'w') as f: f.write('toggle')
                            except: pass
                            if key == 'q': os._exit(0)
                    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                time.sleep(0.1)

        threading.Thread(target=listen, daemon=True).start()

        while True:
            if not self.paused and not self.in_menu:
                self.elapsed += 1
                if self.elapsed % (self.remind_interval * 60) == 0:
                    subprocess.run(['notify-send', 'KIRBY', '💧 Hydrate!'], stderr=subprocess.DEVNULL)
            self.draw_ui()
            time.sleep(1)

if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
