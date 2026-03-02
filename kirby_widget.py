#!/usr/bin/env python3
import time
import os
import sys
import signal

class PomodoroMonitor:
    def __init__(self, watch_path='/tmp/pomodoro_widget.txt'):
        self.path = watch_path
        self.active = True
        # Setup signal handling for clean exit
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, signum, frame):
        self.active = False
        # Restore cursor and clear line on exit
        sys.stdout.write("\033[?25h\033[K\n[Status Monitor Terminated]\n")
        sys.stdout.flush()
        sys.exit(0)

    def draw(self):
        # Hide cursor for a professional CLI look
        sys.stdout.write("\033[?25l")
        
        while self.active:
            try:
                # Check for file existence and read
                if os.path.exists(self.path):
                    with open(self.path, 'r') as f:
                        # Professional tools often use a status prefix
                        content = f.read().strip()
                    
                    status_line = content if content else "SYSTEM IDLE"
                else:
                    status_line = "INITIALIZING COSMIC LINK..."

                # Format the output: 
                # \r = Return to start of line
                # \033[K = Clear from cursor to end of line (prevents ghosting)
                timestamp = time.strftime("%H:%M:%S")
                sys.stdout.write(f"\r\033[K[{timestamp}] {status_line}")
                sys.stdout.flush()

            except Exception as e:
                sys.stdout.write(f"\r\033[K[Error] Accessing {self.path}...")
                sys.stdout.flush()

            time.sleep(1)

if __name__ == "__main__":
    monitor = PomodoroMonitor()
    monitor.draw()
