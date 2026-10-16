#!/usr/bin/env bash
# ==============================================================================
# Win-V Linux Installer
# Native Windows-style Clipboard History with Direct Paste for GNOME Wayland
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DATA="$HOME/.local/share/clipboard-history"
TARGET_BIN="$HOME/.local/bin"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo -e "\033[1;34m==>\033[0m Installing Win-V Linux..."

# 1. Check dependencies
command -v python3 >/dev/null 2>&1 || { echo -e "\033[1;31mError:\033[0m python3 is required." >&2; exit 1; }
command -v wl-paste >/dev/null 2>&1 || { echo -e "\033[1;31mError:\033[0m wl-clipboard (wl-paste, wl-copy) is required." >&2; exit 1; }

python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')" >/dev/null 2>&1 || {
    echo -e "\033[1;31mError:\033[0m GTK4 and Libadwaita Python bindings are required (python3-gobject, libadwaita)." >&2
    exit 1
}

# 2. Setup directories
mkdir -p "$TARGET_DATA" "$TARGET_BIN" "$SYSTEMD_USER_DIR"

# 3. Copy application files
echo -e "\033[1;32m==>\033[0m Copying service files to $TARGET_DATA..."
cp "$SCRIPT_DIR/service.py" "$TARGET_DATA/"
cp "$SCRIPT_DIR/store.py" "$TARGET_DATA/"
cp "$SCRIPT_DIR/uinput_paste.py" "$TARGET_DATA/"

# 4. Copy CLI launchers
echo -e "\033[1;32m==>\033[0m Installing executables to $TARGET_BIN..."
cp "$SCRIPT_DIR/clip-popup" "$TARGET_BIN/"
cp "$SCRIPT_DIR/clip" "$TARGET_BIN/"
chmod +x "$TARGET_BIN/clip-popup" "$TARGET_BIN/clip"

# 5. Setup Systemd Service
echo -e "\033[1;32m==>\033[0m Configuring systemd user service..."
cp "$SCRIPT_DIR/clipboard-history.service" "$SYSTEMD_USER_DIR/"
systemctl --user daemon-reload
systemctl --user enable --now clipboard-history.service

# 6. Configure GNOME Super+V shortcut
echo -e "\033[1;32m==>\033[0m Setting GNOME Super + V keybinding..."
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name 'Clipboard History'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command "$TARGET_BIN/clip-popup"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding '<Super>v'

echo ""
echo -e "\033[1;32m✔ Installation complete!\033[0m"
echo -e "Press \033[1;36mWin + V\033[0m anywhere to open your clipboard history."
echo -e "Use \033[1;36mclip\033[0m in your terminal to view or manage clipboard history."
