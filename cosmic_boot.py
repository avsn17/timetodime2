#!/usr/bin/env python3
"""
COSMIC AUTO SYSTEM v2
Self-updating + rollback protected launcher
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
SYSTEM = ROOT / "cosmic/system"
VERSION_FILE = SYSTEM / "version.json"
TIMER = ROOT / "pomodoro_timer.py"
BACKUP = SYSTEM / "backup_timer.py"

print("🛰️ Cosmic Auto v2 starting...\n")

# ---------------------------------
# Load version info
# ---------------------------------
data = json.loads(VERSION_FILE.read_text())
print(f"✨ Version {data['version']}")

# ---------------------------------
# Detect environment
# ---------------------------------
env = "codespaces" if "/workspaces/" in str(ROOT) else "local"
print(f"🌎 Environment: {env}")

# ---------------------------------
# Auto Git Sync
# ---------------------------------
try:
    subprocess.run(["git", "pull"], cwd=ROOT)
    print("✅ Repo synced")
except:
    print("⚠️ Git sync skipped")

# ---------------------------------
# Ensure required files
# ---------------------------------
required = {
    "session_history.json": "[]",
    "music_signal.txt": ""
}

for f, default in required.items():
    p = ROOT / f
    if not p.exists():
        p.write_text(default)
        print(f"📦 Created {f}")

# ---------------------------------
# Backup before patch
# ---------------------------------
if TIMER.exists():
    shutil.copy(TIMER, BACKUP)

# ---------------------------------
## ---------------------------------
# Feature Repair Engine
# ---------------------------------
print("🔧 Verifying features...")

import re

text = TIMER.read_text()

def ensure(pattern, addition, label):
    global text
    if not re.search(pattern, text, re.DOTALL):
        text += "\n\n" + addition
        print(f"✅ Restored {label}")
    else:
        print(f"✔ {label} OK")


# ---- CHAT FEATURE ----
ensure(
    r"def chat\(",
"""
def chat(self):
    print("\\n💬 Cosmic Chat Online")
    input("Press ENTER to return...")
""",
"Chat system"
)

# ---- STATS FEATURE ----
ensure(
    r"def show_stats\(",
"""
def show_stats(self):
    print("\\n📊 Stats")
    try:
        import json
        with open("session_history.json") as f:
            data = json.load(f)
        print(f"Sessions:", len(data))
    except:
        print("No stats yet.")
    input("Press ENTER...")
""",
"Stats system"
)

# ---- SETTINGS FEATURE ----
ensure(
    r"def open_settings\(",
"""
def open_settings(self):
    print("\\n⚙ Kirby Config")
    input("Press ENTER...")
""",
"Settings system"
)

TIMER.write_text(text)
# ---------------------------------
try:
    text = TIMER.read_text()

    legend = '[Space] Pause | [N] New | [S] Stats | [A] Kirby Config | [C] Chat | [Q] Quit'

    import re
    text = re.sub(
        r'controls\s*=\s*".*?"',
        f'controls = "{legend}"',
        text
    )

    TIMER.write_text(text)
    print("🔧 Auto patch applied")

except Exception as e:
    print("❌ Patch failed — restoring backup")
    shutil.copy(BACKUP, TIMER)

# ---------------------------------
# Launch
# ---------------------------------
print("\n🚀 Launching Pomodoro\n")

subprocess.run(["python3", str(TIMER)])
