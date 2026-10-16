#!/usr/bin/env bash
# ==============================================================================
# KeepClip Uninstaller
# ==============================================================================
set -e

echo -e "\033[1;33m==>\033[0m Stopping and disabling KeepClip service..."
systemctl --user stop clipboard-history.service 2>/dev/null || true
systemctl --user disable clipboard-history.service 2>/dev/null || true

echo -e "\033[1;33m==>\033[0m Removing KeepClip files..."
rm -f "$HOME/.config/systemd/user/clipboard-history.service"
rm -f "$HOME/.local/bin/clip-popup"
rm -f "$HOME/.local/bin/clip"
rm -rf "$HOME/.local/share/clipboard-history"

systemctl --user daemon-reload

echo -e "\033[1;33m==>\033[0m Clearing GNOME Win + V shortcut..."
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "@as []" 2>/dev/null || true

echo -e "\033[1;32m✔ KeepClip has been completely uninstalled.\033[0m"
