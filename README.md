# Win-V Linux

> **Native Windows-style Clipboard History (`Win + V`) with Direct-Paste for GNOME on Wayland.**

[![Linux](https://img.shields.io/badge/OS-Linux%20%7C%20Fedora%20%7C%20Ubuntu-orange.svg)](https://kernel.org)
[![Desktop](https://img.shields.io/badge/Desktop-GNOME%20(Wayland)-blue.svg)](https://gnome.org)
[![Toolkit](https://img.shields.io/badge/UI-Libadwaita%20%2F%20GTK4-purple.svg)](https://gnome.pages.gitlab.gnome.org/libadwaita/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

On Windows, pressing **`Win + V`** opens your clipboard history, and clicking any previous item immediately pastes it into your active document. 

On Linux Wayland desktops, native clipboard managers either require extensions that demand full desktop restarts, don't auto-paste, or destroy your active `Ctrl + V` clipboard buffer.

**Win-V Linux** brings the exact Windows `Win + V` workflow to GNOME on Wayland, with zero external dependencies and unique advantages:

- **Lightning Fast (<50ms):** Uses a pre-warmed resident daemon with Unix Domain Socket IPC for instantaneous popups.
- **Direct Paste into Any Application:** Uses Linux kernel `/dev/uinput` to inject the paste directly into the focused window.
- **Preserves Your Active `Ctrl + V`:** Pasting an old snippet does **not** destroy your clipboard; the system automatically restores your latest copied text immediately after pasting!
- **Pure Native Libadwaita / GTK4:** Beautiful GNOME styling matching your desktop theme.
- **Pinning & Search:** Real-time search filter and pinned snippets that stay permanently at the top.
- **Terminal CLI Included:** Use `clip` in your shell for terminal-based number shortcuts and management.

---

## Architecture

```
                    [ Win + V ] Keypress
                             │
                             ▼
                    ┌─────────────────┐
                    │   clip-popup    │ (Shell IPC trigger)
                    └────────┬────────┘
                             │ (Unix Domain Socket in ~2ms)
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

---

## Installation

### Prerequisites
- GNOME Desktop on Wayland (Fedora, Ubuntu, Debian, Arch)
- `python3`, `wl-clipboard`
- `python3-gobject` and `libadwaita` (pre-installed on standard GNOME desktops)

### Quick Install

```bash
git clone https://github.com/KiranK0304/win-v-linux.git
cd win-v-linux
./install.sh
```

The installer will:
1. Copy backend files to `~/.local/share/clipboard-history/`.
2. Install `clip` and `clip-popup` to `~/.local/bin/`.
3. Enable and start the systemd user service `clipboard-history.service`.
4. Automatically bind `<Super>v` in GNOME settings.

---

## Usage

### Graphical Popup
- Press **`Win + V` (`Super + V`)** anywhere on your desktop.
- **Search:** Start typing immediately to filter your clips.
- **Paste:** Click any snippet or navigate with `↑`/`↓` and hit `Enter` to paste it into your active window.
- **Pin / Delete:** Click the star icon to pin favorites to the top, or the trash icon to delete.
- **Dismiss:** Hit `Esc` or click `×` to close without changing your clipboard.

### Terminal Companion (`clip`)

```bash
clip            # Display interactive clipboard history dashboard
clip 2          # Copy snippet #2 to clipboard
clip searchterm # Filter history from terminal
clip clear      # Clear all non-pinned history
```

---

## Uninstallation

To remove completely and restore GNOME defaults:

```bash
cd win-v-linux
./uninstall.sh
```

---

## License

MIT © [Kiran Kuruvila](https://github.com/KiranK0304)
