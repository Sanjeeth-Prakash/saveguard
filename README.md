<div align="center">

```
 ██████╗  █████╗ ██╗   ██╗███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗
██╔════╝ ██╔══██╗██║   ██║██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
╚╚█████╗ ███████║██║   ██║█████╗  ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
 ╚════██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
 ██████╔╝██║  ██║ ╚████╔╝ ███████╗╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
 ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
```

**Game Save Manager — Never lose your progress again.**

![Python](https://img.shields.io/badge/Python-3.8+-red?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-red?style=flat-square&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-darkred?style=flat-square)
![Made with love](https://img.shields.io/badge/made%20with-%E2%9D%A4-red?style=flat-square)

</div>

---

## What is SaveGuard?

Some games wipe your save file every time they update. SaveGuard fixes that.

Set your source once, set your backup folder once — then with one click you can back up your save before an update, and restore it after. Your paths are remembered forever so you never have to hunt them down again.

Also includes **Ticket Claim** — a one-click launcher for [Windows Update Blocker (WUB)](https://www.sordum.org/9470/) that opens it with admin privileges so you can pause Windows Update on demand.

---

## Features

- 💾 **Save File** — backs up your game save (Source → Destination)
- ⬆ **Transfer Save** — restores your backup after an update wipes it (Destination → Source)
- 🎟 **Ticket Claim** — launches Windows Update Blocker as admin with one click
- 📄 / 📁 **File or Folder** — works whether your game saves as a single file or a whole folder
- 🔁 **Remembered paths** — set source & destination once, they're saved forever
- ♻ **Auto-replace** — always overwrites silently, no confirmation dialogs slowing you down

---

## Getting Started

### Option A — Download the EXE *(easiest)*

1. Go to [Releases](../../releases) and download `SaveGuard.exe`
2. Run it — no install needed
3. Set your **Source** (game save location) and **Destination** (your backup folder)
4. Done

### Option B — Run from source

Requirements: **Python 3.8+**

```bash
git clone https://github.com/YOUR_USERNAME/saveguard.git
cd saveguard
python app.py
```

### Option C — Build the EXE yourself

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SaveGuard" app.py
# EXE will be in the dist/ folder
```

---

## How to Use

| Action | What it does |
|---|---|
| **Set SOURCE** | Point to your game's save file or save folder |
| **Set DESTINATION** | Pick any folder where you want backups stored |
| **💾 Save Now** | Copies save from Source → Destination (run this before every update) |
| **⬆ Restore Now** | Copies backup from Destination → Source (run this after an update breaks your save) |
| **⚙ Settings** | Set the path to `Wub.exe` (Windows Update Blocker) |
| **🎟 Ticket Claim** | Launches Wub.exe as admin — blocks Windows from auto-updating |

> **Tip:** Your Source and Destination are saved the first time you set them. You never need to set them again.

---

## Windows Update Blocker (Ticket Claim)

To use the Ticket Claim button you need [Windows Update Blocker](https://www.sordum.org/9470/) — a free tool by Sordum.

1. Download and extract it anywhere
2. Open SaveGuard → ⚙ Settings
3. Browse to `Wub.exe` and save
4. Now the 🎟 Ticket Claim button will launch it as admin instantly

---

## File Structure

```
saveguard/
├── app.py          # Main application
├── README.md       # This file
└── dist/           # Generated after build (contains SaveGuard.exe)
```

Config is stored at `%APPDATA%\SaveGuard\config.json` — your paths persist between sessions.

---

## License

MIT — free to use, share, and modify.

---

<div align="center">

created with 💗 by **sxnjxxth**

</div>
