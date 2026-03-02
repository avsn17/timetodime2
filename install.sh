#!/usr/bin/env bash

echo "🛰️ Installing Cosmic Kirbs System..."

PROJECT="/workspaces/timetodime2"

# Detect shell config
if [ -f ~/.bashrc ]; then
    RCFILE=~/.bashrc
else
    RCFILE=~/.zshrc
fi

# Add alias if missing
grep -q "alias poyo=" $RCFILE || \
echo "alias poyo='cd $PROJECT && python3 cosmic_boot.py'" >> $RCFILE

echo "✅ Alias installed (poyo)"
echo "Run: source $RCFILE"
