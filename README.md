# KeepClip 📎

> **Native Windows-style Clipboard History (`Win + V`) with Direct-Paste for GNOME on Wayland.**  
> *Instant popup, direct auto-paste into active windows, and your active `Ctrl + V` is never overwritten.*

[![Linux](https://img.shields.io/badge/OS-Linux%20%7C%20Fedora%20%7C%20Ubuntu%20%7C%20Arch-orange.svg)](https://kernel.org)
[![Desktop](https://img.shields.io/badge/Desktop-GNOME%20(Wayland)-blue.svg)](https://gnome.org)
[![Toolkit](https://img.shields.io/badge/UI-Libadwaita%20%2F%20GTK4-purple.svg)](https://gnome.pages.gitlab.gnome.org/libadwaita/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Why KeepClip?

On Windows, pressing **`Win + V`** opens clipboard history, and clicking an older item immediately pastes it into your document.

On Linux Wayland desktops, existing tools either:
- Demand a full desktop restart/logout to install (GNOME extensions on GNOME 45–50).
- Only copy text without actually pasting it into your focused window.
- Overwrite your active `Ctrl + V` buffer with the old item you just pasted.

**KeepClip solves all three:**
1. **Direct Auto-Paste:** Clicking any past snippet pastes it directly into your active window at the cursor position.
2. **Preserves Active `Ctrl + V`:** Pasting an older snippet **never** destroys your clipboard. KeepClip automatically restores your last copied text immediately after pasting.
3. **Instant Startup (<50ms):** Uses a pre-warmed background resident daemon with Unix Domain Socket IPC for instant popup speed.
4. **100% Directly Usable After Install:** **No reboot or session logout required.** It starts working the exact second `./install.sh` finishes.
5. **Native Libadwaita / GTK4 Design:** Matches modern GNOME styling with dark mode, smooth scrolling, search filtering, and pinning.

---

## 🚀 Quick Start (Installation)

### 1. Clone the repository
```bash
git clone https://github.com/KiranK0304/KeepClip.git
cd KeepClip
```

### 2. Run the installer
```bash
./install.sh
```

### 3. That's it!
**KeepClip is immediately active.** Press **`Win + V`** anywhere on your desktop right now!

---

## 📦 Prerequisites (By Distribution)

KeepClip uses tools already present on modern GNOME installations. If you are on a minimal install, ensure you have:

#### Fedora / RHEL
```bash
sudo dnf install python3 wl-clipboard nmap-ncat python3-gobject libadwaita
```

#### Ubuntu / Debian / Pop!_OS
```bash
sudo apt update
sudo apt install python3 wl-clipboard netcat-openbsd python3-gi gir1.2-adw-1
```

#### Arch Linux
```bash
sudo pacman -S python wl-clipboard openbsd-netcat python-gobject libadwaita
```

---

## 🎮 How to Use

### 🖥️ Graphical Popup (`Win + V`)

- **Open:** Press **`Win + V`** (`Super + V`) anywhere on your desktop.
- **Search:** Start typing immediately to filter your clipboard history in real time.
- **Paste:** Click any snippet (or use `↑` / `↓` and press `Enter`) to paste it directly into your active window.
- **Pin Items:** Click the star icon to pin important snippets permanently to the top.
- **Delete / Clear:** Click the trash icon to remove an individual item, or click "Clear" in the header to wipe history.
- **Dismiss:** Press `Esc` or click `×` to close the popup without changing your clipboard.

### 💻 Terminal Companion (`clip`)

KeepClip also comes with a companion CLI tool for your shell:

```bash
clip            # Display interactive clipboard history table
clip 2          # Copy snippet #2 directly to clipboard
clip searchterm # Filter history from terminal
clip clear      # Clear all non-pinned history
```

---

## 🛠️ Architecture

```
                    [ Win + V ] Keypress
                             │
                             ▼
                    ┌─────────────────┐
                    │   clip-popup    │ (Fast socket trigger in ~2ms)
                    └────────┬────────┘
                             │ (Unix Domain Socket)
                             ▼
┌────────────────────────────────────────────────────────┐
│               clipboard-history.service                │
│                                                        │
│  ┌──────────────────┐          ┌────────────────────┐  │
│  │ Wayland Poller   │          │ Libadwaita Window  │  │
│  │ (wl-paste 400ms) │          │ (Pre-warmed in RAM)│  │
│  └────────┬─────────┘          └─────────┬──────────┘  │
│           │                              │             │
│           ▼                              ▼             │
│  ┌──────────────────┐          ┌────────────────────┐  │
│  │ history.json     │          │ uinput Virtual Kb  │  │
│  │ (Deduplicated)   │          │ (Auto-paste driver)│  │
│  └──────────────────┘          └────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

- **Memory Usage:** ~25 MB RAM.
- **CPU Usage:** < 0.01% idle load.
- **IPC Protocol:** Unix Domain Socket (`~/.local/share/clipboard-history/popup.sock`).

---

## ⚙️ Troubleshooting

### Direct auto-paste not typing into the window?
KeepClip uses the Linux kernel `/dev/uinput` subsystem to simulate the paste keystroke into the active window. Most modern desktop distributions (like Fedora) grant user ACL permissions to `/dev/uinput` automatically.

If your distribution restricts `/dev/uinput` to root, grant non-root access by creating a udev rule:

```bash
echo 'KERNEL=="uinput", MODE="0660", GROUP="input", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo udevadm trigger /dev/uinput
```

---

## 🗑️ Uninstallation

To cleanly remove KeepClip and restore your GNOME settings:

```bash
cd KeepClip
./uninstall.sh
```

---

## 📄 License

MIT © [Kiran Kuruvila](https://github.com/KiranK0304)
