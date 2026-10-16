#!/usr/bin/env bash
# ==============================================================================
# KeepClip Installer
# Windows-style Clipboard History with Direct-Paste for GNOME on Wayland
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DATA="$HOME/.local/share/clipboard-history"
TARGET_BIN="$HOME/.local/bin"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo -e "\033[1;34m==>\033[0m Installing \033[1;36mKeepClip\033[0m..."

# 1. Dependency checks
MISSING=()
command -v python3 >/dev/null 2>&1 || MISSING+=("python3")
command -v wl-paste >/dev/null 2>&1 || MISSING+=("wl-clipboard")
command -v nc >/dev/null 2>&1 || MISSING+=("nmap-ncat (or netcat)")

if [ ${#MISSING[@]} -ne 0 ]; then
    echo -e "\033[1;31mError:\033[0m Missing dependencies: ${MISSING[*]}"
    echo "Install them using your package manager:"
    echo "  Fedora: sudo dnf install python3 wl-clipboard nmap-ncat python3-gobject libadwaita"
    echo "  Ubuntu/Debian: sudo apt install python3 wl-clipboard netcat-openbsd python3-gi gir1.2-adw-1"
    echo "  Arch: sudo pacman -S python wl-clipboard openbsd-netcat python-gobject libadwaita"
    exit 1
fi

python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1'); gi.require_version('Pango', '1.0')" >/dev/null 2>&1 || {
    echo -e "\033[1;31mError:\033[0m GTK4 / Libadwaita Python bindings are missing."
    echo "Install them via: sudo dnf install python3-gobject libadwaita  (or apt: python3-gi gir1.2-adw-1)"
    exit 1
}

# 2. Check /dev/uinput permissions (required for direct auto-pasting)
if [ ! -w /dev/uinput ]; then
    echo -e "\033[1;33mNotice:\033[0m Your user currently does not have write access to /dev/uinput."
    echo "Direct auto-pasting might need uinput permissions. To enable without root:"
    echo '  echo "KERNEL==\"uinput\", MODE=\"0660\", GROUP=\"input\", TAG+=\"uaccess\"" | sudo tee /etc/udev/rules.d/99-uinput.rules'
    echo '  sudo udevadm trigger /dev/uinput'
fi

# 3. Setup directories
mkdir -p "$TARGET_DATA" "$TARGET_BIN" "$SYSTEMD_USER_DIR"

# 4. Copy backend files
echo -e "\033[1;32m==>\033[0m Installing application files to $TARGET_DATA..."
cp "$SCRIPT_DIR/service.py" "$TARGET_DATA/"
cp "$SCRIPT_DIR/store.py" "$TARGET_DATA/"
cp "$SCRIPT_DIR/uinput_paste.py" "$TARGET_DATA/"

# 5. Copy CLI launchers
echo -e "\033[1;32m==>\033[0m Installing executables to $TARGET_BIN..."
cp "$SCRIPT_DIR/clip-popup" "$TARGET_BIN/"
cp "$SCRIPT_DIR/clip" "$TARGET_BIN/"
chmod +x "$TARGET_BIN/clip-popup" "$TARGET_BIN/clip"

# 6. Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$TARGET_BIN:"* ]]; then
    export PATH="$TARGET_BIN:$PATH"
fi

# 7. Setup & Start Systemd Service
echo -e "\033[1;32m==>\033[0m Starting KeepClip background service..."
cp "$SCRIPT_DIR/clipboard-history.service" "$SYSTEMD_USER_DIR/"
systemctl --user daemon-reload
systemctl --user enable --now clipboard-history.service

# 8. Configure GNOME Win + V (Super + V) keybinding
echo -e "\033[1;32m==>\033[0m Binding Win + V (Super + V) shortcut in GNOME..."
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ name 'KeepClip'
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ command "$TARGET_BIN/clip-popup"
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/ binding '<Super>v'

echo ""
echo -e "\033[1;32m✔ KeepClip is successfully installed and ready to use immediately!\033[0m"
echo -e "• Press \033[1;36mWin + V\033[0m anywhere to open the clipboard popup."
echo -e "• Press \033[1;36mEsc\033[0m to dismiss."
echo -e "• Type \033[1;36mclip\033[0m in your terminal to view history or copy snippets by number."
