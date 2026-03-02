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
    def __init__(self):
        self.distance_goal = 0  # Meter;
        self.time_goal = 0  # min;
        self.elapsed = 0
        self.running = False
        self.paused = False
        self.chat_messages = []
        self.user_name = "Cosmic Kirbs"
        self.stats = self.load_stats()
        self.star_offset = 0
        self.bg_color = 'deep_space'
        self.timer_thread = None
        
    def load_stats(self):
        """Load statistics from file"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_stats(self):
        """Save statistics to file immediately"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def add_session(self, username, distance, duration, completed=True):
        """Add a session to stats and save immediately"""
        if username not in self.stats:
            self.stats[username] = {
                'sessions': [],
                'total_distance': 0,
                'total_time': 0,
                'completed_sessions': 0
            }
        
        session = {
            'date': datetime.now().isoformat(),
            'distance': distance,
            'duration': duration,
            'completed': completed
        }
        
        self.stats[username]['sessions'].append(session)
        self.stats[username]['total_distance'] += distance
        self.stats[username]['total_time'] += duration
        if completed:
            self.stats[username]['completed_sessions'] += 1
        
        self.save_stats()
    
    def get_bot_response(self, user_message):
        """Get a philosophical quote based on user message"""
        msg_lower = user_message.lower()
        
        # Keyword detection for quote categories
        if any(word in msg_lower for word in ['iro', 'tea', 'wisdom', 'uncle']):
            category = 'iro'
        elif any(word in msg_lower for word in ['bronte', 'emily', 'love', 'soul']):
            category = 'bronte'
        elif any(word in msg_lower for word in ['kant', 'moral', 'reason', 'science']):
            category = 'kant'
        elif any(word in msg_lower for word in ['song', 'music', 'sing', 'lyric']):
            category = 'lyrics'
        elif any(word in msg_lower for word in ['hero', 'courage', 'brave', 'strong']):
            category = 'heroic'
        else:
            # Random category
            category = random.choice(list(QUOTES.keys()))
        
        return random.choice(QUOTES.get(category, QUOTES.get('wisdom', ['Stay focused.'])))
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def draw_stars(self, width, height):
        """Draw moving star field"""
        stars = []
        star_chars = ['·', '∙', '•', '*', '✦', '✧']
        num_stars = (width * height) // 40
        
        for _ in range(num_stars):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            char = random.choice(star_chars)
            stars.append((x, y, char))
        
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        for x, y, char in stars:
            new_x = (x + self.star_offset) % width
            if 0 <= new_x < width and 0 <= y < height:
                grid[y][new_x] = char
        
        return grid
    
    def draw_ui(self):
        """Draw the main UI"""
        self.clear_screen()
        
        try:
            cols, rows = os.get_terminal_size()
        except:
            cols, rows = 80, 24
        
        # Apply background color
        print(COLORS[self.bg_color], end='')
        
        star_grid = self.draw_stars(cols, rows - 1)
        
        progress = min(self.elapsed / self.time_goal if self.time_goal > 0 else 0, 1.0)
        progress_bar_width = max(cols - 30, 20)
        filled = int(progress_bar_width * progress)
        
        distance_covered = (self.elapsed / 60) * METERS_PER_MINUTE
        
        header = f"🎯 Goal: {self.distance_goal}m ({self.time_goal // 60}min) | User: {self.user_name}"
        
        mins, secs = divmod(int(self.elapsed), 60)
        timer_display = f"⏱️  {mins:02d}:{secs:02d}"
        
        bar_color = COLORS['green'] if progress < 1.0 else COLORS['solar']
        bar = f"{bar_color}[{'🟩' * filled}{'░' * (progress_bar_width - filled)}]{COLORS[self.bg_color]} {distance_covered:.0f}m"
        
        if self.running and not self.paused:
            status = f"{COLORS['green']}▶ RUNNING{COLORS[self.bg_color]}"
        elif self.paused:
            status = f"{COLORS['solar']}⏸ PAUSED{COLORS[self.bg_color]}"
        else:
            status = f"{COLORS['red']}⏹ STOPPED{COLORS[self.bg_color]}"
        
        for row_idx in range(rows - 1):
            line = star_grid[row_idx]
            
            if row_idx == 1:
                for i, char in enumerate(header[:len(line)]):
                    if i < len(line):
                        line[i] = char
            
            elif row_idx == 3:
                start_pos = 2
                for i, char in enumerate(timer_display):
                    if start_pos + i < len(line):
                        line[start_pos + i] = char
            
            elif row_idx == 5:
                start_pos = 2
                bar_plain = f"[{'█' * filled}{'░' * (progress_bar_width - filled)}] {distance_covered:.0f}m"
                for i, char in enumerate(bar_plain):
                    if start_pos + i < len(line):
                        line[start_pos + i] = char
            
            elif row_idx == 7:
                start_pos = 2
                status_plain = status.replace(COLORS['green'], '').replace(COLORS['solar'], '').replace(COLORS['red'], '').replace(COLORS[self.bg_color], '')
                for i, char in enumerate(status_plain):
                    if start_pos + i < len(line):
                        line[start_pos + i] = char
            
            elif row_idx >= 10 and row_idx < rows - 8:
                chat_start = cols - 48
                if chat_start > 50:
                    if row_idx == 10:
                        chat_header = "💬 CHAT WITH WISDOM BOT"
                        for i, char in enumerate(chat_header):
                            if chat_start + i < len(line):
                                line[chat_start + i] = char
                    else:
                        msg_idx = row_idx - 11
                        if msg_idx < len(self.chat_messages):
                            msg = self.chat_messages[-(msg_idx + 1)]
                            display_msg = msg[:45]
                            for i, char in enumerate(display_msg):
                                if chat_start + i < len(line):
                                    line[chat_start + i] = char
            
            print(''.join(line))
        
        controls = "SPACE=pause | B=back | Q=quit | C=chat | S=stats | O=color | N=new"
        print(controls[:cols] + COLORS['reset'])
        
        sys.stdout.flush()
    
    def timer_loop(self):
        """Background thread for timer"""
        while self.running:
            if not self.paused:
                time.sleep(0.1)
                self.elapsed += 0.1
                self.star_offset = (self.star_offset + 1) % 100
                
                # Auto-save progress every 30 seconds
                if int(self.elapsed) % 30 == 0 and self.elapsed > 0:
                    distance_covered = (self.elapsed / 60) * METERS_PER_MINUTE
                    self.add_session(self.user_name, distance_covered, int(self.elapsed), completed=False)
                
                if self.elapsed >= self.time_goal:
                    self.timer_complete()
                    break
            else:
                time.sleep(0.1)
    
    def timer_complete(self):
        """Handle timer completion"""
        self.running = False
        distance_covered = (self.elapsed / 60) * METERS_PER_MINUTE
        
        self.add_session(self.user_name, distance_covered, int(self.elapsed), completed=True)
        
        advice = random.choice(BREAK_ADVICES)
        
        print(f"\n\n{COLORS['solar']}🎉 Congratulations! Goal Reached! 🎉{COLORS['reset']}")
        print(f"{COLORS['green']}Distance covered: {distance_covered:.0f}m{COLORS['reset']}")
        print(f"\n💡 Break Advice: {advice}")
        print("💧 Remember to drink water!")
        
        wisdom = random.choice(QUOTES[random.choice(list(QUOTES.keys()))])
        print(f"\n✨ Wisdom: {wisdom}")
        
        print("\nPress [N] for New Timer, [S] for Stats, [Q] to Quit")
        
        print("🚀 Mission Status Updated!")
    
    def show_stats(self):
        """Display statistics comparison"""
        self.clear_screen()
        print(f"\n{COLORS['solar']}📊 STATISTICS LEADERBOARD{COLORS['reset']}\n")
        print("=" * 80)
        
        if not self.stats:
            print("No statistics yet. Complete a session to see stats!")
        else:
            sorted_users = sorted(
                self.stats.items(),
                key=lambda x: x[1]['total_distance'],
                reverse=True
            )
            
            print(f"{'Rank':<6} {'Name':<20} {'Distance':<15} {'Time':<15} {'Sessions':<12} {'Completed':<10}")
            print("-" * 80)
            
            for rank, (name, data) in enumerate(sorted_users, 1):
                hours = data['total_time'] // 3600
                minutes = (data['total_time'] % 3600) // 60
                time_str = f"{hours}h {minutes}m"
                completed = data.get('completed_sessions', 0)
                
                color = COLORS['solar'] if rank == 1 else COLORS['green'] if rank <= 3 else ''
                print(f"{color}{rank:<6} {name:<20} {data['total_distance']:.0f}m{'':<10} {time_str:<15} {len(data['sessions']):<12} {completed:<10}{COLORS['reset']}")
        
        print("\nPress ENTER to go back...")
        input()
    
    def chat(self):
        """Interactive chat with bot"""
        print(f"\n{COLORS['cosmic']}💬 Chat with Wisdom Bot{COLORS['reset']}")
        print("Categories: iro, heroic, bronte, kant, lyrics")
        print("Type 'back' to return to timer\n")
        
        while True:
            user_input = input(f"{COLORS['green']}You: {COLORS['reset']}").strip()
            if user_input.lower() == 'back':
                break
            if user_input:
                response = self.get_bot_response(user_input)
                self.chat_messages.append(f"You: {user_input[:40]}")
                self.chat_messages.append(f"Bot: {response[:40]}")
                print(f"\n{COLORS['cosmic']}Bot: {response}{COLORS['reset']}\n")
    
    def choose_color(self):
        """Let user choose background color"""
        self.clear_screen()
        print(f"\n{COLORS['solar']}🎨 Choose Background Color{COLORS['reset']}\n")
        
        color_options = {
            '1': ('stars', 'Bright Stars'),
            '2': ('deep_space', 'Deep Space Blue'),
            '3': ('nebula', 'Nebula Magenta'),
            '4': ('cosmic', 'Cosmic Cyan'),
            '5': ('solar', 'Solar Yellow'),
            '6': ('void', 'Dark Void'),
        }
        
        for key, (_, name) in color_options.items():
            print(f"{key}. {name}")
        
        choice = input("\nEnter choice (1-6): ").strip()
        if choice in color_options:
            self.bg_color = color_options[choice][0]
            print(f"{COLORS['green']}Color changed!{COLORS['reset']}")
        
        time.sleep(1)
    
    def start_timer_thread(self):
        """Start the timer in background"""
        if self.timer_thread and self.timer_thread.is_alive():
            return
        
        self.running = True
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
    
    
    
    
    
    def open_settings(self):
        import termios, sys
        # Save current state to restore later
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            # Switch to 'cooked' mode so input() works
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            print('\n' + '★' * 15)
            print('🛠️ KIRBY CONFIG [A]')
            print('★' * 15)
            curr_mood = getattr(self, 'mood', 'Hype')
            curr_int = getattr(self, 'remind_interval', '10')
            print(f'[1] Hydration Interval (Current: {curr_int}m)')
            print(f'[2] Kirby Mood: {curr_mood}')
            print(f'[3] Reset Session Count')
            print(f'[4] Exit Settings')
            
            choice = input('\nSelect: ')
            if choice == '1':
                self.remind_interval = input('Enter minutes: ')
                print(f'<( " )> Interval updated to {self.remind_interval}m!')
            elif choice == '2':
                self.mood = 'Calm' if curr_mood == 'Hype' else 'Hype'
                print(f'<( ^.^ )> Mood switched to {self.mood}!')
            elif choice == '3':
                self.session_count = 0
                print('🔄 Session count reset.')
        finally:
            # Caller handles resetting back to cbreak
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