#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║     🌟 COSMIC POMODORO TIMER                     ║
║         Pilot: Cosmic Kirbs | avsn17             ║
╚══════════════════════════════════════════════════╝
"""

import time, sys, os, threading, random, json, select
import termios, tty
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DATA_FILE         = Path.home() / '.pomodoro_stats.json'
SIGNAL_FILE       = Path('music_signal.txt')
METERS_PER_MINUTE = 10
USER_ID           = "Cosmic Kirbs"

# ─── COLORS ───────────────────────────────────────────────────────────────────
COLORS = {
    'stars':      '\033[97m',
    'deep_space': '\033[94m',
    'nebula':     '\033[95m',
    'cosmic':     '\033[96m',
    'solar':      '\033[93m',
    'void':       '\033[90m',
    'green':      '\033[92m',
    'red':        '\033[91m',
    'pink':       '\033[38;5;218m',
    'bold':       '\033[1m',
    'reset':      '\033[0m',
}

# ─── QUOTES ───────────────────────────────────────────────────────────────────
QUOTES = {
    'wisdom': [
        'The journey is the reward.', 'Be like water, my friend.',
        'Focus on the step, not the mountain.',
        'Silence is a source of great strength.',
        'He who has a why to live can bear almost any how.'
    ],
    'heroic': [
        'Success is not final, failure is not fatal.', 'Fortune favors the brave.',
        'I can do this all day.', 'With great power comes great responsibility.',
        'Hard times create strong men.', 'Marcus Aurelius: The impediment to action advances action.',
    ],
    'iro': [
        'While it is always best to believe in oneself, a little help can be a blessing.',
        'Sharing tea with a fascinating stranger is one of lifes true delights.',
        'Hope is something you give yourself. That is the meaning of inner strength.'
    ],
    'bronte': [
        'I am no bird; and no net ensnares me.',
        'I would always rather be happy than dignified.',
        'The soul that sees beauty may sometimes walk alone.'
    ],
    'kant': [
        'Two things fill the mind with wonder: the starry heavens and the moral law.',
        'Seek not the favor of the multitude; it is seldom got by honest means.',
        'Act only according to that maxim whereby you can at the same time will it to be universal.',
    ],
    'lyrics': [
        'MJ: If you want to make the world a better place, take a look at yourself.',
        'MJ: Speed demon, minding my own business. Speedin on the highway of life.',
        'Lana: Will you still love me when I am no longer young and beautiful?',
        'Lana: Heaven is a place on earth with you.',
        'Lana: Summertime sadness, I just wanted you to know that baby you are the best.',
        'Bee Gees: Whether you are a brother or whether you are a mother, you are stayin alive.',
        'Billie: I am the bad guy, duh.', 'Billie: You should see me in a crown.',
        'Bowie: Ground Control to Major Tom, commencing countdown.',
        'CAS: I am a dreamer, and you are the dream.',
    ],
    'kirby': [
        '<( " )> Poyo! You are doing amazing, Cosmic Kirbs!',
        '<( o_o )> Focus mode: MAXIMUM PINK POWER.',
        '(> ^_^ )> <3 Sending positive vibes to the cockpit!',
        '<( ^.^ )> You are a LEGEND. Keep going!',
    ],
    'vibe': [
        'Main Character Energy detected. 📈', 'No cap, your productivity is skyrocketing.',
        'Vibe check: ABSOLUTE LEGEND.', 'Big brain moves only.',
    ],
}

BREAK_ADVICES = [
    "Take a 5-minute walk to refresh your mind.",
    "Stretch your body and relax your shoulders.",
    "Look away from the screen — give your eyes a rest.",
    "Drink some water and stay hydrated. 💧",
    "Take deep breaths and practice mindfulness.",
    "Step outside for fresh air if possible.",
    "Do a quick exercise — jumping jacks or push-ups!",
    "Listen to your favorite song.",
    "Message a friend or loved one.",
    "Enjoy a healthy snack.",
]

RANK_TIERS = [
    (0,    "🛸 Space Cadet"),
    (100,  "🌙 Moon Walker"),
    (500,  "☄️  Comet Rider"),
    (1000, "🚀 Orbit Master"),
    (2500, "⭐ Star Pilot"),
    (5000, "🌌 Galactic Overlord"),
]

KIRBY_FRAMES = ['<( " )>', '<( ´ )>', '<( ^ )>', '<( o )>']

MILESTONE_MSGS = {25: "Quarter way!", 50: "Halfway!!", 75: "Almost there!", 100: "POYO COMPLETE!"}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_rank(total_m: float) -> str:
    rank = RANK_TIERS[0][1]
    for threshold, label in RANK_TIERS:
        if total_m >= threshold:
            rank = label
    return rank

def clear():
    sys.stdout.write("\033[H\033[2J")
    sys.stdout.flush()

def signal_music(state: str = "PLAY_NEXT"):
    try:
        SIGNAL_FILE.write_text(state)
    except Exception:
        pass

# ─── NOTIFICATIONS (optional — works if kirby_notify.py is present) ───────────
def _try_notify(fn_name: str, *args):
    try:
        import kirby_notify
        getattr(kirby_notify, fn_name)(*args)
    except Exception:
        pass

# ─── MAIN CLASS ───────────────────────────────────────────────────────────────
class PomodoroTimer:
    def __init__(self):
        self.user_name       = USER_ID
        self.distance_goal   = 0
        self.time_goal       = 0.0
        self.elapsed         = 0.0
        self.running         = False
        self.paused          = False
        self.in_subscreen    = False
        self.chat_messages   = []
        self.stats           = self._load_stats()
        self.star_offset     = 0
        self.bg_color        = 'deep_space'
        self.timer_thread    = None
        self.mood            = "Hype"
        self.remind_interval = "10"
        self.session_count   = 0
        self.music_enabled   = True
        self._status_banner  = ("", 0.0)
        self._old_termios    = None
        self._last_percent   = -1

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _load_stats(self) -> dict:
        if DATA_FILE.exists():
            try:
                return json.loads(DATA_FILE.read_text())
            except Exception:
                pass
        return {}

    def _save_stats(self):
        DATA_FILE.write_text(json.dumps(self.stats, indent=2))

    def _add_session(self, distance: float, duration: float, completed: bool = True):
        u = self.user_name
        if u not in self.stats:
            self.stats[u] = {'sessions': [], 'total_distance': 0.0,
                              'total_time': 0.0, 'completed_sessions': 0}
        self.stats[u]['sessions'].append({
            'date': datetime.now().isoformat(),
            'distance': round(distance, 2),
            'duration': round(duration, 1),
            'completed': completed,
        })
        self.stats[u]['total_distance'] += distance
        self.stats[u]['total_time']     += duration
        if completed:
            self.stats[u]['completed_sessions'] += 1
            self.session_count += 1
        self._save_stats()

    def _total_distance(self) -> float:
        return self.stats.get(self.user_name, {}).get('total_distance', 0.0)

    # ── Banner ────────────────────────────────────────────────────────────────
    def _set_banner(self, text: str, duration: float = 2.5):
        self._status_banner = (text, time.time() + duration)

    def _get_banner(self) -> str:
        text, expiry = self._status_banner
        return text if time.time() < expiry else ""

    # ── Timer thread ──────────────────────────────────────────────────────────
    def _timer_loop(self):
        while self.running:
            if not self.paused and not self.in_subscreen:
                time.sleep(0.1)
                self.elapsed    += 0.1
                self.star_offset = (self.star_offset + 1) % 200
                if self.elapsed >= self.time_goal:
                    self._complete()
                    break
            else:
                time.sleep(0.05)

    def _start_timer(self):
        self.running      = True
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()

    def _complete(self):
        self.running = False
        dist = (self.elapsed / 60) * METERS_PER_MINUTE
        self._add_session(dist, self.elapsed, completed=True)
        _try_notify('notify_session_end', dist, get_rank(self._total_distance()))
        if self.music_enabled:
            signal_music("PLAY_NEXT")

    # ── UI ────────────────────────────────────────────────────────────────────
    def _draw_stars(self, cols, rows):
        chars = ['·', '∙', '•', '✦', '✧', '*']
        n     = (cols * rows) // 35
        grid  = [[' '] * cols for _ in range(rows)]
        for _ in range(n):
            x  = random.randint(0, cols - 1)
            y  = random.randint(0, rows - 1)
            nx = (x + self.star_offset) % cols
            grid[y][nx] = random.choice(chars)
        return grid

    def _draw_ui(self):
        clear()
        try:
            cols, rows = os.get_terminal_size()
        except Exception:
            cols, rows = 80, 24

        color = COLORS[self.bg_color]
        print(color, end='')

        grid      = self._draw_stars(cols, rows - 1)
        progress  = min(self.elapsed / self.time_goal, 1.0) if self.time_goal > 0 else 0.0
        bar_w     = max(cols - 32, 20)
        filled    = int(bar_w * progress)
        dist_done = (self.elapsed / 60) * METERS_PER_MINUTE
        mins, sec = divmod(int(self.elapsed), 60)
        total_d   = self._total_distance()
        percent   = int(progress * 100)

        header     = (f"🎯 Goal: {self.distance_goal}m  |  Pilot: {self.user_name}  |  "
                      f"Sessions: {self.session_count}  |  Rank: {get_rank(total_d)}")
        timer_d    = f"⏱  {mins:02d}:{sec:02d}"
        bar_str    = f"[{'█' * filled}{'░' * (bar_w - filled)}] {dist_done:.0f}/{self.distance_goal}m"
        music_ind  = '🎵 ON' if self.music_enabled else '🔇 OFF'

        if self.running and not self.paused:   status_str = f"▶ RUNNING  {music_ind}"
        elif self.paused:                       status_str = f"⏸ PAUSED   {music_ind}"
        else:                                   status_str = f"⏹ STOPPED  {music_ind}"

        banner    = self._get_banner()
        kirby_x   = int((dist_done / max(self.distance_goal, 1)) * max(cols - 10, 1))
        kf        = KIRBY_FRAMES[int(self.elapsed) % len(KIRBY_FRAMES)]
        chat_col  = cols - 50

        def _wr(r, text, start=0):
            for i, ch in enumerate(text):
                p = start + i
                if 0 <= p < len(grid[r]):
                    grid[r][p] = ch

        for r in range(rows - 1):
            if r == 1:  _wr(r, header[:cols])
            elif r == 3: _wr(r, timer_d, 2)
            elif r == 5: _wr(r, bar_str, 2)
            elif r == 7: _wr(r, status_str, 2)
            elif r == 9:
                if banner:
                    _wr(r, banner, max(0, (cols - len(banner)) // 2))
                elif self.distance_goal > 0:
                    _wr(r, kf, kirby_x)

            if chat_col > 40:
                if r == 11:
                    _wr(r, "💬 WISDOM SIDEBAR", chat_col)
                elif 12 <= r <= rows - 3:
                    idx     = r - 12
                    visible = self.chat_messages[-(rows - 15):]
                    if idx < len(visible):
                        _wr(r, visible[idx][:47], chat_col)

            print(''.join(grid[r]))

        controls = ("[Space] Pause  [N] New  [S] Stats  [A] Settings  "
                    "[C] Chat  [M] Music  [O] Color  [Q] Quit")
        print(controls[:cols] + COLORS['reset'])
        sys.stdout.flush()

    # ── Subscreen helpers ─────────────────────────────────────────────────────
    def _enter_sub(self):
        self.in_subscreen = True
        if self._old_termios:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_termios)

    def _exit_sub(self):
        self.in_subscreen = False
        tty.setcbreak(sys.stdin.fileno())

    # ── Chat ──────────────────────────────────────────────────────────────────
    def _chat(self):
        self._enter_sub()
        clear()
        print(f"{COLORS['cosmic']}{COLORS['bold']}💬 WISDOM CHAT{COLORS['reset']}")
        print(f"{COLORS['void']}Categories: iro · bronte · kant · lyrics · heroic · kirby · vibe · wisdom{COLORS['reset']}")
        print(f"{COLORS['void']}Type 'back' to return.\n{COLORS['reset']}")
        while True:
            try:
                raw = input(f"{COLORS['green']}You: {COLORS['reset']}").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if raw.lower() == 'back':
                break
            if raw:
                resp = self._bot_reply(raw)
                self.chat_messages.append(f"You: {raw[:43]}")
                self.chat_messages.append(f"Bot: {resp[:43]}")
                print(f"\n{COLORS['cosmic']}Bot: {resp}{COLORS['reset']}\n")
        self._exit_sub()

    def _bot_reply(self, msg: str) -> str:
        ml = msg.lower()
        if any(w in ml for w in ['iro', 'tea', 'uncle']):               cat = 'iro'
        elif any(w in ml for w in ['bronte', 'emily', 'love', 'soul']): cat = 'bronte'
        elif any(w in ml for w in ['kant', 'moral', 'reason']):         cat = 'kant'
        elif any(w in ml for w in ['song', 'music', 'lyric', 'sing']):  cat = 'lyrics'
        elif any(w in ml for w in ['hero', 'brave', 'courage']):        cat = 'heroic'
        elif any(w in ml for w in ['kirby', 'poyo', 'pink']):           cat = 'kirby'
        elif any(w in ml for w in ['vibe', 'cap', 'legend']):           cat = 'vibe'
        else:                                                             cat = random.choice(list(QUOTES))
        return random.choice(QUOTES[cat])

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _show_stats(self):
        self._enter_sub()
        clear()
        print(f"{COLORS['solar']}{COLORS['bold']}📊 COSMIC LEADERBOARD{COLORS['reset']}\n")
        print("═" * 82)
        if not self.stats:
            print("No data yet. Complete a session to appear on the board!")
        else:
            print(f"{'#':<5} {'Pilot':<22} {'Distance':<12} {'Time':<12} {'Sessions':<10} {'Rank'}")
            print("─" * 82)
            for i, (name, d) in enumerate(sorted(
                    self.stats.items(), key=lambda x: x[1].get('total_distance', 0), reverse=True), 1):
                total_d   = d.get('total_distance', 0)
                total_t   = d.get('total_time', 0)
                sessions  = len(d.get('sessions', []))
                completed = d.get('completed_sessions', 0)
                h, m      = divmod(int(total_t) // 60, 60)
                t_str     = f"{h}h {m:02d}m" if h else f"{m}m"
                col       = COLORS['solar'] if i == 1 else COLORS['green'] if i <= 3 else ''
                print(f"{col}{i:<5} {name:<22} {total_d:.0f}m{'':<6} {t_str:<12} {sessions}/{completed}{'':<4} {get_rank(total_d)}{COLORS['reset']}")
        print("\nPress ENTER to return...")
        input()
        self._exit_sub()

    # ── Settings ──────────────────────────────────────────────────────────────
    def _open_settings(self):
        self._enter_sub()
        clear()
        print(f"\n{COLORS['pink']}{COLORS['bold']}{'★' * 20}{COLORS['reset']}")
        print(f"{COLORS['pink']}🛠  KIRBY CONFIG  ★ avsn17{COLORS['reset']}")
        print(f"{COLORS['pink']}{'★' * 20}{COLORS['reset']}\n")
        print(f"  [1] Hydration Reminder  (Every: {self.remind_interval}m)")
        print(f"  [2] Kirby Mood          ({self.mood})")
        print(f"  [3] Reset Session Count ({self.session_count})")
        print(f"  [4] Toggle Music        ({'ON 🎵' if self.music_enabled else 'OFF 🔇'})")
        print(f"  [5] Change BG Color")
        print(f"  [6] Back\n")
        try:
            ch = input(f"{COLORS['cosmic']}Select: {COLORS['reset']}").strip()
            if ch == '1':
                v = input("  Interval (minutes): ").strip()
                if v.isdigit():
                    self.remind_interval = v
                    print(f"  <( \" )> Updated to {v}m!")
            elif ch == '2':
                self.mood = 'Calm' if self.mood == 'Hype' else 'Hype'
                print(f"  <( ^.^ )> Mood: {self.mood}!")
            elif ch == '3':
                self.session_count = 0
                print("  🔄 Session count reset.")
            elif ch == '4':
                self.music_enabled = not self.music_enabled
                if self.music_enabled:
                    signal_music("PLAY_NEXT")
                print(f"  Music: {'ON 🎵' if self.music_enabled else 'OFF 🔇'}")
            elif ch == '5':
                self._choose_color()
        except (EOFError, KeyboardInterrupt):
            pass
        time.sleep(0.6)
        self._exit_sub()

    def _choose_color(self):
        opts = {'1':'stars','2':'deep_space','3':'nebula','4':'cosmic','5':'solar','6':'void'}
        labels = {'stars':'Bright Stars ⭐','deep_space':'Deep Space 🌌','nebula':'Nebula 🟣',
                  'cosmic':'Cosmic Cyan 🔵','solar':'Solar Gold 🌟','void':'Dark Void 🖤'}
        print()
        for k, v in opts.items():
            print(f"  [{k}] {labels[v]}")
        ch = input("  Pick (1-6): ").strip()
        if ch in opts:
            self.bg_color = opts[ch]
            print(f"  Color set to {labels[opts[ch]]}!")

    # ── Splash ────────────────────────────────────────────────────────────────
    def _splash(self):
        clear()
        for line in [
            "",
            f"{COLORS['pink']}{COLORS['bold']}  ╔══════════════════════════════════════════╗{COLORS['reset']}",
            f"{COLORS['pink']}{COLORS['bold']}  ║   🌟 COSMIC POMODORO — PERFECT EDITION  ║{COLORS['reset']}",
            f"{COLORS['pink']}{COLORS['bold']}  ║          Pilot: Cosmic Kirbs ✦           ║{COLORS['reset']}",
            f"{COLORS['pink']}{COLORS['bold']}  ╚══════════════════════════════════════════╝{COLORS['reset']}",
            "",
            f"  {COLORS['cosmic']}>> PILOT IDENTIFIED: {self.user_name} <<{COLORS['reset']}",
            f"  {COLORS['solar']}Rank: {get_rank(self._total_distance())}{COLORS['reset']}",
            "",
            f"  {COLORS['void']}{random.choice(QUOTES['iro'])}{COLORS['reset']}",
            "",
        ]:
            print(line)

    # ── Finish ────────────────────────────────────────────────────────────────
    def _finish_screen(self):
        clear()
        dist = (self.elapsed / 60) * METERS_PER_MINUTE
        print(f"\n{COLORS['solar']}{COLORS['bold']}  🎉 MISSION COMPLETE! 🎉{COLORS['reset']}")
        print(f"  {COLORS['green']}Distance covered: {dist:.0f} m{COLORS['reset']}")
        print(f"  {COLORS['cosmic']}New rank: {get_rank(self._total_distance())}{COLORS['reset']}")
        print(f"\n  💡 Break tip: {random.choice(BREAK_ADVICES)}")
        print(f"\n  ✨ {random.choice(QUOTES['kirby'])}")
        _try_notify('notify_session_end', dist, get_rank(self._total_distance()))
        if self.music_enabled:
            signal_music("PLAY_NEXT")
            print(f"\n  🎵 Music autoplay triggered.")
        self._ask_restart()

    def _ask_restart(self):
        try:
            ch = input(f"\n  {COLORS['green']}Start a new mission? (y/n): {COLORS['reset']}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            ch = 'n'
        if ch == 'y':
            self.elapsed       = 0.0
            self.running       = False
            self.paused        = False
            self.chat_messages = []
            self._last_percent = -1
            self.run()
        else:
            print(f"\n  {COLORS['cosmic']}👋 Fly safe, {self.user_name}. The stars await. 🌌{COLORS['reset']}\n")

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        self._splash()

        while True:
            try:
                raw  = input(f"\n  {COLORS['green']}Enter distance goal in meters (10 m = 1 min): {COLORS['reset']}").strip()
                dist = int(raw)
                if dist <= 0:
                    raise ValueError
                self.distance_goal = dist
                self.time_goal     = (dist / METERS_PER_MINUTE) * 60
                self.elapsed       = 0.0
                break
            except ValueError:
                print(f"  {COLORS['red']}Please enter a positive integer.{COLORS['reset']}")

        self._start_timer()
        _try_notify('notify_session_start', self.distance_goal)

        self._old_termios = termios.tcgetattr(sys.stdin)

        try:
            tty.setcbreak(sys.stdin.fileno())

            while self.running or self.paused:
                if not self.in_subscreen:
                    # Milestone check
                    percent = int((self.elapsed / self.time_goal) * 100) if self.time_goal > 0 else 0
                    if percent != self._last_percent and percent in MILESTONE_MSGS:
                        self._set_banner(f"★ {percent}% — {MILESTONE_MSGS[percent]} ★", 2.5)
                        _try_notify('notify_milestone', percent)
                    self._last_percent = percent
                    self._draw_ui()

                if select.select([sys.stdin], [], [], 0.08)[0]:
                    key = sys.stdin.read(1).lower()

                    if key == ' ':
                        self.paused = not self.paused

                    elif key == 'q':
                        dist = (self.elapsed / 60) * METERS_PER_MINUTE
                        self._add_session(dist, self.elapsed, completed=False)
                        self.running = False
                        break

                    elif key == 'n':
                        dist = (self.elapsed / 60) * METERS_PER_MINUTE
                        self._add_session(dist, self.elapsed, completed=False)
                        self.running = False
                        break

                    elif key == 'c':
                        self._chat()

                    elif key == 's':
                        self._show_stats()

                    elif key == 'a':
                        self._open_settings()

                    elif key == 'm':
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            signal_music("PLAY_NEXT")
                            banner = "🎵 MUSIC ON  — signal sent!"
                        else:
                            signal_music("STOP")
                            banner = "🔇 MUSIC OFF — signal sent."
                        self._set_banner(banner, 2.5)
                        self.chat_messages.append(banner)

                    elif key == 'o':
                        self._enter_sub()
                        clear()
                        self._choose_color()
                        time.sleep(0.4)
                        self._exit_sub()

                time.sleep(0.05)

        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_termios)
            except Exception:
                pass
            print(COLORS['reset'])

        if self.elapsed >= self.time_goal > 0:
            self._finish_screen()
        else:
            self._ask_restart()


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        PomodoroTimer().run()
    except KeyboardInterrupt:
        print(f"\n\n{COLORS['cosmic']}👋 Mission aborted. Goodbye, Cosmic Kirbs.{COLORS['reset']}\n")