#!/bin/bash
# 1. Start the Kirby Widget in the background
python3 /workspaces/timetodime2/kirby_widget.py &
WIDGET_PID=$!

# 2. Start the Main Timer in the foreground
python3 /workspaces/timetodime2/pomodoro_timer.py

# 3. Cleanup: When you quit the timer, stop the widget too
kill $WIDGET_PID 2>/dev/null
