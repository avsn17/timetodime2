import time
import os
import sys
import threading
import json
import termios
import tty
import subprocess

COLORS = {
    "cosmic": "\033[38;5;141m",
    "solar": "\033[38;5;220m",
    "pink": "\033[38;5;213m",
    "reset": "\033[0m"
}

class PomodoroTimer:
    def __init__(self):
        # IDENTITY & HISTORY
        self.user_name = 'Cosmic Kirbs'
        self.history_file = 'session_history.json'
        
        # MISSION GOALS
        self.time_goal = 25 * 60
        self.distance_goal = 100
        self.elapsed = 0
        self.paused = True
        
        # KIRBY CONFIG
        self.mood = 'Hype'
        self.remind_interval = 10
        self.sessions = 0
        self.star_offset = 0
        self.timer_thread = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def send_desktop_notification(self, title, message):
        if sys.platform == 'darwin':
            subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])
        else:
            subprocess.run(['notify-send', '-t', '5000', title, message])

    def update_widget(self):
        try:
            progress = min(1.0, self.elapsed / self.time_goal) if self.time_goal > 0 else 0
            width = 15
            pos = int(width * progress)
            kirby = '<( ^.^ )>✨' if progress >= 1.0 else ('<( -.- )>' if self.paused else '<( o.o )>')
            path_str = '·' * pos + kirby + '·' * (width - pos) + '🌟'
            mood_icon = '💖' if self.mood == 'Hype' else '🍵'
            mins, secs = divmod(int(self.elapsed), 60)
            widget_data = f' {mood_icon} {mins:02d}:{secs:02d} | {path_str} | {int(self.distance_goal)}m '
            with open('/tmp/pomodoro_widget.txt', 'w') as f:
                f.write(widget_data)
        except: pass

    def run(self):
        # Check Identity
        if not self.user_name:
            self.user_name = input("Enter Pilot Name: ")
        
        self.clear_screen()
        print(f"🌟 Welcome back, {self.user_name}! 🌟")
        time.sleep(1)
        
        self.paused = False
        try:
            while True:
                if not self.paused:
                    self.elapsed += 1
                    # Wellness Check
                    if self.elapsed % (self.remind_interval * 60) == 0:
                        self.send_desktop_notification("KIRBY ALERT", "💧 Hydrate + 🧘 Stretch!")
                
                self.update_widget()
                self.draw_ui()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nMission Paused.")

    def draw_ui(self):
        self.clear_screen()
        mins, secs = divmod(int(self.elapsed), 60)
        print(f"{COLORS['cosmic']}🚀 MISSION: COSMIC POMODORO{COLORS['reset']}")
        print(f"{COLORS['pink']}Pilot: {self.user_name}{COLORS['reset']}")
        print(f"{COLORS['solar']}Time: {mins:02d}:{secs:02d} / Goal: {int(self.distance_goal)}m{COLORS['reset']}")
        print("\n" + " " * (self.elapsed % 20) + "<( \" )> *poyo*")
        print("-" * 40)
        print("[Q] Quit | [Space] Pause | [S] Stats")

if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
