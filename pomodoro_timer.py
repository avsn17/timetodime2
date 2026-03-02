#!/usr/bin/env python3
"""
Pomodoro Timer - Terminal App
A cosmic productivity timer with philosophical wisdom
"""

import time
import sys
import os
import threading
import random
import json
from datetime import datetime
from pathlib import Path
# # from tkinter.tix import Meter

# Configuration
DATA_FILE = Path.home() / '.pomodoro_stats.json'
METERS_PER_MINUTE = 10

# Philosophical Quotes

QUOTES = {
    'wisdom': [
        'The journey is the reward.', 'Be like water, my friend.', 'Focus on the step, not the mountain.',
        'Silence is a source of great strength.', 'He who has a why to live can bear almost any how.'
    ],
    'heroic': [
        'Success is not final, failure is not fatal.', 'Fortune favors the brave.', 'I can do this all day.',
        'With great power comes great responsibility.', 'Hard times create strong men.'
    ],
    'iro': [
        'While it is always best to believe in oneself, a little help can be a blessing.',
        'Sharing tea with a fascinating stranger is one of lifes true delights.',
        'Hope is something you give yourself. That is the meaning of inner strength.'
    ],
    'bronte': [
        'I am no bird; and no net ensnares me.', 'I would always rather be happy than dignified.',
        'The soul that sees beauty may sometimes walk alone.'
    ],
    'kant': [
        'Two things fill the mind with wonder: the starry heavens and the moral law.',
        'Seek not the favor of the multitude; it is seldom got by honest means.'
    ],
    'lyrics': [
        'MJ: If you want to make the world a better place, take a look at yourself and make a change.',
        'MJ: Speed demon, minding my own business. Speedin on the highway of life.',
        'Lana: Will you still love me when I am no longer young and beautiful?',
        'Lana: Heaven is a place on earth with you.',
        'Lana: Summertime sadness, I just wanted you to know that baby you are the best.',
        'Bee Gees: Whether you are a brother or whether you are a mother, you are stayin alive.',
        'Bee Gees: Night fever, night fever! We know how to do it.',
        'CAS: I am a dreamer, and you are the dream.',
        'CAS: K. - I am always thinking of you.',
        'Billie: I am the bad guy, duh.',
        'Billie: Ocean eyes - I have never fallen from quite this high.',
        'Billie: You should see me in a crown.',
        'Bowie: Ground Control to Major Tom, commencing countdown.'
    ],
    'kirby': [
        '<( " )> Poyo! You are doing amazing, Cosmic Kirbs!',
        '<( o_o )> Focus mode: MAXIMUM PINK POWER.',
        '(> ^_^ )> <3 Sending positive vibes to the cockpit!'
    ],
    'vibe': [
        'Main Character Energy detected. 📈', 'No cap, your productivity is skyrocketing.',
        'Vibe check: ABSOLUTE LEGEND.', 'Big brain moves only.'
    ],
    'back': ['Returning to the cockpit...', 'Ready for ignition.', 'Focus mode: Reactivated.']
}

BREAK_ADVICES = [
    "Take a 5-minute walk to refresh your mind.",
    "Stretch your body and relax your shoulders.",
    "Look away from the screen - give your eyes a rest.",
    "Drink some water and stay hydrated.",
    "Take deep breaths and practice mindfulness.",
    "Step outside for fresh air if possible.",
    "Do a quick exercise - jumping jacks or push-ups!",
    "Listen to your favorite song.",
    "Message a friend or loved one.",
    "Enjoy a healthy snack.",
]

COLORS = {
    'stars': '\033[97m',      # Bright white
    'deep_space': '\033[94m', # Blue
    'nebula': '\033[95m',     # Magenta
    'cosmic': '\033[96m',     # Cyan
    'solar': '\033[93m',      # Yellow
    'void': '\033[90m',       # Dark gray
    'reset': '\033[0m',
    'green': '\033[92m',
    'red': '\033[91m',
}

class PomodoroTimer:

    def send_desktop_notification(self, title, message):
        import subprocess, sys
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['osascript', '-e', f'display notification "{message}" with title "{title}"'])
        else:  # Linux / Codespaces
            subprocess.run(['notify-send', '-t', '5000', title, message])

    def trigger_wellness_check(self):
        msg = '💧 Drink water + 🧘 Stretch and Bend! Poyo!'
        self.send_desktop_notification('KIRBY WELLNESS ALERT', msg)

    
    def update_widget(self):
        import os
        mins, secs = divmod(int(self.elapsed), 60)
        status = 'PAUSED' if self.paused else 'FOCUS'
        widget_data = f' <( " )> {status} | {mins:02d}:{secs:02d} | Goal: {self.distance_goal}m '
        try:
            with open('/tmp/pomodoro_widget.txt', 'w') as f:
                f.write(widget_data)
        except:
            pass



    def run(self):
        """Main application loop"""
        self.clear_screen()
        print(f"{COLORS['solar']}🌟 Welcome to Cosmic Pomodoro Timer 🌟{COLORS['reset']}\n")
        
        if not self.user_name:
            self.user_name = "Cosmic Kirbs"
            if not self.user_name:
                self.user_name = "Cosmic Kirbs"
        
        print(f"\n{COLORS['cosmic']}Welcome, {self.user_name}!{COLORS['reset']}")
        print(f"\n✨ {random.choice(QUOTES['iro'])}\n")
        
        while True:
            try:
                distance = int(input(f"\n{COLORS['green']}Enter distance goal in meters (10m = 1min): {COLORS['reset']}"))
                self.distance_goal = distance
                self.time_goal = (distance / METERS_PER_MINUTE) * 60
                self.elapsed = 0
                break
            except ValueError:
                print(f"{COLORS['red']}Please enter a valid number{COLORS['reset']}")
        
        self.start_timer_thread()
        
        import select
        import termios
        import tty
        
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            tty.setcbreak(sys.stdin.fileno())
            
            while self.running or self.paused:
                self.draw_ui()
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    
                    
                    
                    
                    
                    
                    if key == ' ':
                        self.paused = not self.paused
                    elif key.lower() == 'a':
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                        self.open_settings()
                        tty.setcbreak(sys.stdin.fileno())
                    elif key.lower() == 'c':
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                        self.chat()
                        tty.setcbreak(sys.stdin.fileno())
                    elif key.lower() == 's':
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                        self.show_stats()
                        tty.setcbreak(sys.stdin.fileno())
                    elif key.lower() == 'n':



                        distance_covered = (self.elapsed / 60) * 10
                        self.add_session(self.user_name, distance_covered, int(self.elapsed), completed=False)
                        self.running = False
                        return

                
                time.sleep(0.1)
        
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print(COLORS['reset'])
        
        if not self.running and self.elapsed >= self.time_goal:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            input()
            
            choice = input(f"\n{COLORS['green']}Start new timer? (y/n): {COLORS['reset']}").strip().lower()
            if choice == 'y':
                self.run()

if __name__ == "__main__":
    try:
        app = PomodoroTimer()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{COLORS['cosmic']}👋 Goodbye! May your path be guided by wisdom.{COLORS['reset']}");
        print(f'\n🎶 Music: {state}') # type: ignore # This is the "Unterminated String" causing the crash