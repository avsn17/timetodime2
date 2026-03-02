from datetime import time

from pomodoro_timer import COLORS


def run(self):
        """Main application loop with Y2K Start - Licensed to Cosmic Kirbs"""
        # 1. Hardcoded identity (The New Era)
        self.user_name = "Cosmic Kirbs"
        
        # 2. Start the Glitch Aesthetic Welcome
        self.show_y2k_splash()
        
        # 3. Stats & History Check (Locked in)
        print(f"{COLORS['cosmic']}>> PILOT IDENTIFIED: {self.user_name} <<{COLORS['reset']}")
        print(f"{COLORS['nebula']}Current Rank: {self.get_rank()} | Let's get it. ✨{COLORS['reset']}\n")

        try:
            # 4. Mission Setup
            goal_input = input(f"{COLORS['solar']}Set orbit distance (e.g. 250m): {COLORS['reset']}")
            self.target_distance = float(goal_input)
            
            # Ignition
            self.start_timer()
            
        except ValueError:
            print(f"{COLORS['red']}Error: Enter a number, bestie. 🛑{COLORS['reset']}")
            time.sleep(1)
            self.run()