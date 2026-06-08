<p align="center">
  <img src="assets/pulsebar_emblem.png" width="120" alt="PulseBar">
</p>

<h1 align="center">PulseBar</h1>

<p align="center">
  <b>Your PC's pulse — right on the taskbar.</b><br>
  A lightweight system monitor that sits <b>on</b> your Windows 10/11 taskbar
  (or floats just above it) — always visible, never in the way. <b>Free.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/version-2.4-3fb950" alt="v2.4">
  <img src="https://img.shields.io/badge/price-Free-brightgreen" alt="Free">
</p>

![PulseBar](assets/promo_banner.png)

> **⬇️ Download** — grab the latest **`PulseBar-Setup.exe`** (installer) or
> **`PulseBar.exe`** (portable) from the [**Releases**](../../releases) page.

---

## ✨ Features

### Live metrics
- **CPU** — usage % (+ clock speed in GHz)
- **RAM** — usage % and **used / total GB**
- **GPU** — usage % + **VRAM used / total GB** *(via Windows performance counters — no extra tools)*
- **Network** — real-time upload ▲ / download ▼ (MB/s **or** Mbps)
- **Disk** — read **R** / write **W** speed, **+ per-drive space %** (C:, D: …)
- **Battery** — % with ⚡ charging indicator (laptops only)

### 🆕 Hover details (v2.4)
Point at any metric for a popup panel:
- **CPU** → top processes + per-core bars · **RAM** → top processes (GB)
- **GPU** → VRAM used / total · **Network** → session ↑↓ totals
- **Disk** → read/write **per physical disk** · **Drives** → used / free / total
- Toggle it on/off from the menu (**Hover details**)

### Layout
- **Horizontal** (on the taskbar) or **Vertical** (stacked panel above the taskbar)
- **Two-row mode** — each metric shows its detail on top (e.g. `3.3 GHz`) and % below
- **Drag anywhere** (free positioning, lockable), adjustable **size**, **transparency**, **refresh rate**

### Smart display
- **Color warnings** — values go white → orange → red as load climbs
- **Mini graphs (sparklines)** — optional history line for CPU & RAM
- **10 color themes** including **gaming** styles:
  - Classic: Default · Ocean · Matrix · Amber · Mono
  - 🎮 Gaming: **Neon** · **Cyber** · **Inferno** · **Plasma** · **RGB** (animated rainbow wave!)
- **8 languages** — English · Ελληνικά · Español · Deutsch · Français · Italiano · Português · Русский (auto-detected)

### Behaves like part of the taskbar
- **On the taskbar** — sits *inside* the taskbar band, in the empty space next to
  your icons, and stays put even when you click the taskbar
- **Above the taskbar** — or float as a thin strip just above it (rock-solid)
- One toggle in the menu switches between the two
- Transparent, always on top, blends with the taskbar
- **Hides in fullscreen** — disappears with the taskbar during games/videos, reappears on Alt-Tab (like the clock)

### Convenience
- **Start with Windows** — one-click auto-start toggle
- **Single instance** — never opens twice
- **Portable** — settings travel next to the .exe (USB-friendly)
- **Digitally signed** by *Fokion Papanikolaou*

---

## 🚀 Installation

### Option A — Installer (recommended)
1. Run **`PulseBar-Setup.exe`**
2. Follow the wizard (optionally enable "Start with Windows")
3. The widget appears on your taskbar

### Option B — Portable
1. Copy **`PulseBar.exe`** anywhere (folder, USB stick…)
2. Double-click to run — settings are saved as `config.json` right next to it

> **First launch:** Windows SmartScreen may show a warning for new apps.
> Click **More info → Run anyway**. The app is digitally signed.

---

## 🖱️ Usage

All settings live in the **system-tray icon** (notification area, bottom-right —
you may need to expand the hidden-icons ▲ arrow):

| Action | Result |
|---|---|
| **Right-click the tray icon** | Open the full settings menu |
| Left-click + drag the widget | Move it (when not in transparent mode) |

The widget itself is a clean, **fully transparent** overlay by default — only the
icons and numbers show, with no background box. On first launch a banner points you
to the tray icon.

### Settings menu
- **Metrics** — show/hide CPU, RAM, GPU, Network, Disk, Battery
- **Details** — CPU speed (GHz), RAM in GB
- **Layout** — Horizontal / Vertical + Two-row (stacked) toggle
- **Position** — left / center / right
- **On the taskbar** — sit *inside* the taskbar band, or float just above it
- **Size** — small / normal / large
- **Opacity** — 50% – 100%
- **Refresh** — 0.5s – 5s
- **Network unit** — MB/s (bytes) or Mbps (bits)
- **Theme** — 10 color schemes (incl. gaming + RGB)
- **Language** — 8 languages
- **Mini graphs** — toggle sparklines
- **Hide in fullscreen** — taskbar-like behavior
- **Start with Windows** — auto-start toggle
- **💜 Donate** — support development

---

## 🎮 Gaming themes

Tray icon → **Theme** and pick a gaming style:
- **Neon** — bright neon-green readouts
- **Cyber** — cyberpunk cyan + magenta
- **Inferno** — fiery orange/red
- **Plasma** — purple plasma glow
- **RGB** — animated rainbow wave that flows across all metrics 🌈

---

## 💜 Support / Donate

This widget is **free**. If you enjoy it, consider a small donation —
tray icon → **Donate**:
- **PayPal:** https://www.paypal.com/donate/?hosted_button_id=PHZG592VLQAFA
- **Revolut:** https://revolut.me/fokionpap

Thank you! 🙏

---

## 💻 Requirements
- Windows 10 / 11 (64-bit)
- No other dependencies

---

## ❓ FAQ

**Does it slow down my PC?**
No — tiny CPU usage and ~15 MB RAM.

**Where does the GPU usage come from?**
Windows performance counters (the same source as Task Manager). No external tools
needed, and it works regardless of your Windows display language.

**Why is the network speed lower than my plan?**
The widget shows **MB/s** (megabytes) by default; ISPs advertise **Mbps** (megabits).
1 MB/s = 8 Mbps. Switch to *Mbps* in the menu to match speed-test numbers.

**The numbers turned red?**
That's the load warning — red means the resource is heavily used.

**Where are my settings stored?**
Portable: `config.json` next to the .exe. Installed: `%APPDATA%\PulseBar\`.

**How do I remove it?**
Right-click → Close to quit. Use the installer's uninstaller, or just delete the
portable .exe and its `config.json`.

---

## 🛠️ Build from source

Requires **Python 3.11+** on **Windows**.

```powershell
# 1) dependencies
pip install psutil Pillow pystray pyinstaller

# 2) (optional) regenerate icons & banner
python make_icons.py
python make_menu_icons.py
python make_app_icon.py
python make_promo.py

# 3) build the portable exe
pyinstaller --noconfirm --onefile --windowed --name PulseBar `
  --icon app.ico --add-data "icons;icons" --add-data "app.ico;." `
  --hidden-import pystray._win32 taskbar_widget.py

# 4) (optional) build the installer — needs Inno Setup 6
ISCC installer.iss
```

The portable `dist\PulseBar.exe` runs with no install; settings are saved as
`config.json` next to it.

---

## 📜 License
See [LICENSE.txt](LICENSE.txt). Third-party notices in [THIRD_PARTY.txt](THIRD_PARTY.txt).

© 2026 Fokion Papanikolaou. All rights reserved.
