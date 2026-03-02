#!/usr/bin/env python3
import time, os, sys, threading, json, termios, tty, random, datetime, math
from pathlib import Path

# --- 2026 NEON DREAM PALETTE ---
def get_color(code): return f"\033[38;5;{code}m"

COLORS = {
    "reset": "\033[0m", "hide": "\033[?25l", "show": "\033[?25h",
    "pink": get_color(218), "blush": get_color(211), "mint": get_color(121),
    "sky": get_color(153), "lavender": get_color(183), "gold": get_color(220),
    "white": "\033[97m", "void": get_color(234)
}

RAINBOW = [197, 203, 209, 215, 221, 227, 191, 155, 119, 83, 47, 41, 35, 29]

QUOTES = [
    "Kirby: (っˆڡˆς) Poyo! Your focus is sparkling!",
    "Iroh: Protection and power are overrated. Choose focus.",
    "MJ: If you want to make the world better, start with this task.",
    "Lana: Dream hard, work harder, stay pink.",
    "Waddle Dee: ( •⌄• ) I'm charting your progress, Pilot!"
]

class CosmicKirbyTerminal:
    def __init__(self):
        self.user_name = 'Cosmic Kirbs'
        self.history_file = Path('/workspaces/timetodime2/session_history.json')
        self.goal_mins = 25
        self.elapsed = 0
        self.paused = True
        self.stars = []
        self.frame = 0
        self.state = "FLIGHT"
        self.history = []
        self.load_history()

    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f: self.history = json.load(f)
            except: self.history = []

    def save_log(self):
        log = {"pilot": self.user_name, "date": str(datetime.datetime.now())[:16], "mins": self.elapsed // 60}
        self.history.append(log)
        with open(self.history_file, 'w') as f: json.dump(self.history, f, indent=4)

    def draw_bubble_menu(self, title, lines):
        os.system('clear')
        width = 60
        print(f"\n{COLORS['pink']}  ╭{'─'*(width-2)}╮")
        print(f"  │ {COLORS['gold']}{title.center(width-4)}{COLORS['pink']} │")
        print(f"  ├{'─'*(width-2)}┤")
        for l in lines:
            print(f"  │ {COLORS['white']}{l.ljust(width-4)}{COLORS['pink']} │")
        print(f"  ╰{'─'*(width-2)}╯{COLORS['reset']}")

    def comms_menu(self):
        self.draw_bubble_menu("📡 COMMS RELAY", ["", random.choice(QUOTES), "", "[Any key to return]"])
        self.wait_for_key()
        self.state = "FLIGHT"

    def history_menu(self):
        lines = ["Last 5 Missions:"]
        for entry in self.history[-5:]:
            lines.append(f"• {entry['date']} | {entry['mins']}m")
        lines.append("")
        lines.append("[Any key to return]")
        self.draw_bubble_menu("📊 FLIGHT ARCHIVES", lines)
        self.wait_for_key()
        self.state = "FLIGHT"

    def settings_menu(self):
        self.draw_bubble_menu("⚙️ SHIP SETTINGS", [f"1. Name: {self.user_name}", f"2. Timer: {self.goal_mins}m", "", "[1/2] Change | [B] Back"])
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            c = sys.stdin.read(1).lower()
            if c == '1': 
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
                self.user_name = input("\n New Pilot Name: ")
            elif c == '2': self.goal_mins = 50 if self.goal_mins == 25 else 90 if self.goal_mins == 50 else 25
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
        self.state = "FLIGHT"

    def wait_for_key(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            sys.stdin.read(1)
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def draw_flight(self):
        cols, rows = os.get_terminal_size()
        if not self.stars: self.stars = [{'x': random.uniform(-1, 1), 'y': random.uniform(-1, 1), 'z': random.uniform(0.1, 1.5), 'speed': 0.025} for _ in range(55)]
        
        buf = ["\033[H"]
        screen = [[' ' for _ in range(cols)] for _ in range(rows)]
        cx, cy = cols // 2, rows // 2

        # Star Logic
        for s in self.stars:
            s['z'] -= s['speed']
            if s['z'] <= 0: s['z'] = 1.5; s['x'], s['y'] = random.uniform(-1, 1), random.uniform(-1, 1)
            sx, sy = int(cx + (s['x'] / s['z']) * cx), int(cy + (s['y'] / s['z']) * cy)
            if 0 <= sx < cols and 0 <= sy < rows:
                color = COLORS['void'] if s['z'] > 1.0 else COLORS['sky'] if s['z'] > 0.5 else COLORS['white']
                screen[sy][sx] = f"{color}·{COLORS['reset']}"

        # Kirby Logic
        kx = int(cx - 5 + math.sin(self.frame * 0.1) * 15)
        ky = int(rows // 2 + math.cos(self.frame * 0.1) * 2)
        eye = "^" if (self.frame // 10) % 3 == 0 else "◕"
        face = f"{COLORS['pink']}⎛{COLORS['blush']}·{COLORS['pink']}{eye}v{eye}{COLORS['blush']}·{COLORS['pink']}⎞"
        
        # Progress Logic
        mins, secs = divmod(self.elapsed, 60)
        prog = min(self.elapsed / (self.goal_mins * 60), 1.0)
        bar_w = cols - 24
        filled = int(bar_w * prog)
        bar = f"{COLORS['gold']}★{'━'*filled}{COLORS['lavender']}{'┈'*(bar_w-filled)}☇{COLORS['reset']}"

        # Render Header
        buf.append(f"{COLORS['pink']}❤ {self.user_name} ❤{COLORS['reset']}".center(cols + 10) + "\n\n")
        for r in range(rows - 10): buf.append("".join(screen[r+2]) + "\n")
        buf.append(f"\033[{ky};{kx}H{face}\n")
        buf.append(f"\n {bar}\n")
        buf.append(f" {COLORS['mint']}{mins:02d}:{secs:02d} / {self.goal_mins}:00{COLORS['reset']}".center(cols+10) + "\n")
        buf.append(f"{COLORS['sky']}[Space] Nap | [C] Comms | [H] Log | [S] Set | [Q] Land{COLORS['reset']}".center(cols+10))

        sys.stdout.write("".join(buf))
        sys.stdout.flush()

    def run(self):
        print(COLORS['hide'])
        self.paused = False
        def listen():
            fd = sys.stdin.fileno()
            while True:
                old = termios.tcgetattr(fd)
                try:
                    tty.setcbreak(fd)
                    k = sys.stdin.read(1).lower()
                    if k == ' ': self.paused = not self.paused
                    elif k == 'c': self.state = "COMMS"
                    elif k == 'h': self.state = "STATS"
                    elif k == 's': self.state = "SETTINGS"
                    elif k == 'q':
                        self.save_log()
                        with open('music_signal.txt', 'w') as f: f.write('toggle')
                        print(COLORS['show'])
                        os._exit(0)
                finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)

        threading.Thread(target=listen, daemon=True).start()
        while True:
            if self.state == "FLIGHT":
                if not self.paused: self.elapsed += 1
                self.frame += 1
                self.draw_flight()
            elif self.state == "COMMS": self.comms_menu()
            elif self.state == "STATS": self.history_menu()
            elif self.state == "SETTINGS": self.settings_menu()
            time.sleep(0.05)

if __name__ == "__main__":
    app = CosmicKirbyTerminal()
    app.run()
