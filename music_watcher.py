#!/usr/bin/env python3
import os
import time
import subprocess

SIGNAL_FILE = 'music_signal.txt'
# Change this to your preferred player command (e.g., 'spotify', 'vlc', 'mpv')
# Example: ['vlc', '--random', '/path/to/your/music/folder']
MUSIC_COMMAND = ['mpv', '--shuffle', '~/Music/CosmicVibes/']

def listen():
    print("🛰️  Satellite Listener Online... Waiting for Cosmic Kirbs' signal.")
    
    # Ensure signal file exists so we don't error out
    if not os.path.exists(SIGNAL_FILE):
        open(SIGNAL_FILE, 'w').close()

    while True:
        if os.path.exists(SIGNAL_FILE):
            with open(SIGNAL_FILE, 'r+') as f:
                content = f.read().strip()
                if content == 'PLAY_NEXT':
                    print("🎵 Signal Received! Igniting Autoplay...")
                    
                    # Clear the signal so it doesn't loop
                    f.seek(0)
                    f.truncate()
                    
                    # Execute music command
                    try:
                        subprocess.Popen(MUSIC_COMMAND)
                    except Exception as e:
                        print(f"❌ Failed to start music: {e}")
                        
        time.sleep(2) # Check every 2 seconds to save CPU

if __name__ == "__main__":
    listen()