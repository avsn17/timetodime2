#!/usr/bin/env python3
import time, os, sys, threading, json, termios, tty, subprocess, random, datetime
from pathlib import Path

COLORS = {
    "cosmic": "\033[38;5;141m", "solar": "\033[38;5;220m",
    "pink": "\033[38;5;213m", "reset": "\033[0m", "cyan": "\033[36m",
    "green": "\033[92m", "white": "\033[97m"
}

QUOTES = {
    'iro': ['Tea is just hot leaf juice!', 'Hope is something you give yourself.'],
    'mj': ['Heal the world.', 'Lies run sprints, truth runs marathons.'],
    'lana': ['Live fast, die young.', 'I believe in the person I want to become.'],
    'bronte': ['I am no bird; and no net ensnares me.', 'I would always rather be happy than dignified.'],
    'kant': ['Science is organized knowledge.', 'The starry heavens above me and the moral law within me.'],
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
        self.in_menu = False
        self.star_offset = 0

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def draw_stars(self, width, height):
        star_chars = ['·', '∙', '•', '*', '✧']
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        random.seed(42) # Fixed seed for stable star positions
        for _ in range((width * height) // 25):
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            char = random.choice(star_chars)
            # Shift stars based on elapsed time
            new_x = (x - self.star_offset) % width
            grid[y][new_x] = f"{COLORS['white']}{char}{COLORS['reset']}"
        return grid

    def chat_menu(self):
        self.in_menu = True
        self.clear_screen()
        print(f"{COLORS['pink']}💬 CATALOG: iro, mj, lana, bronte, kant, heroic, lyrics, vibe, or back{COLORS['reset']}")
        while True:
            cmd = input(f"{self.user_name} > ").lower().strip()
            if cmd == 'back': break
            print(f"{COLORS['cyan']}Reflect: {random.choice(QUOTES.get(cmd, ['Poyo!']))}{COLORS['reset']}")
        self.in_menu = False

    def stats_menu(self):
        self.in_menu = True
        self.clear_screen()
        print(f"{COLORS['solar']}📊 MISSION HISTORY: {self.user_name.upper()}{COLORS['reset']}")
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
                for entry in history[-8:]:
                    print(f" {COLORS['green']}√{COLORS['reset']} {entry['timestamp'][:16]} | {entry['duration_mins']}m")
        input("\nPress Enter...")
        self.in_menu = False

    def draw_ui(self):
        if self.in_menu: return
        try: cols, rows = os.get_terminal_size()
        except: cols, rows = 80, 24
        
        grid = self.draw_stars(cols, rows - 1)
        mins, secs = divmod(self.elapsed, 60)
        
        # Overlay UI text onto the star grid
        header = f" 🚀 COSMIC MISSION | PILOT: {self.user_name} "
        timer = f" TIME: {mins:02d}:{secs:02d} | MOOD: {self.mood} "
        kirby = "<( \" )> *poyo*"
        
        for i, char in enumerate(header): grid[1][i+2] = f"{COLORS['cosmic']}{char}{COLORS['reset']}"
        for i, char in enumerate(timer): grid[3][i+2] = f"{COLORS['solar']}{char}{COLORS['reset']}"
        
        k_pos = (self.elapsed % (cols - 15)) + 2
        for i, char in enumerate(kirby): grid[6][k_pos+i] = f"{COLORS['pink']}{char}{COLORS['reset']}"
        
        self.clear_screen()
        for row in grid: print("".join(row))
        print(f"{COLORS['cyan']}[Space] Pause | [C] Chat | [S] Stats | [M] Music | [Q] Quit{COLORS['reset']}", end="")
        sys.stdout.flush()

    def run(self):
        self.paused = False
        def listen():
            fd = sys.stdin.fileno()
            while True:
                if not self.in_menu:
                    old = termios.tcgetattr(fd)
                    try:
                        tty.setcbreak(fd)
                        key = sys.stdin.read(1).lower()
                        if key == ' ': self.paused = not self.paused
                        elif key == 'c': termios.tcsetattr(fd, termios.TCSADRAIN, old); self.chat_menu()
                        elif key == 's': termios.tcsetattr(fd, termios.TCSADRAIN, old); self.stats_menu()
                        elif key == 'm' or key == 'q':
                            with open('music_signal.txt', 'w') as f: f.write('toggle')
                            if key == 'q': os._exit(0)
                    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
                time.sleep(0.1)

        threading.Thread(target=listen, daemon=True).start()
        while True:
            if not self.paused and not self.in_menu:
                self.elapsed += 1
                self.star_offset = (self.star_offset + 1) % 1000
            self.draw_ui()
            time.sleep(1)

if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
