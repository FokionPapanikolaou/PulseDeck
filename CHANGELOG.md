# Changelog

All notable changes to **PulseDeck** are documented here.

---

## [2.8.2] — 2026-06-25

### Added
- **Diagnostic self-test** — new 🩺 button in the System tab runs 18 read-only hardware probes (CPU, RAM, GPU, disk, battery, network, PDH counters, weather) and shows a pass / warn / fail report with a **Copy** button for sharing.
- **10 new Tools** (34 total):
  - ⚡ Reset GPU driver — recovers a frozen GPU via `Win+Ctrl+Shift+B`, no reboot needed
  - 🔄 Restart Explorer — unfreezes a stuck taskbar or desktop
  - 🛌 Hibernate — immediate hibernate
  - 🔐 Proxy settings · 🛡 VPN — open Windows Settings
  - 🔒 Lock screen — instant lock (Win+L)
  - 🔊 Sound devices — Sound Control Panel
  - 🎤 Microphone privacy · 📷 Camera privacy · 📋 Clipboard history
  - All actions are Store-safe (no admin) and translated across all 8 languages

### Fixed
- App now launches on unusual hardware — every startup hardware read (taskbar height, network counters, battery, VRAM, CPU frequency, CPU/GPU name) is individually guarded with a safe fallback
- Polling loop can no longer be silenced by a crash in a single tick
- Weather background loop now recovers cleanly from any exception
- Sound devices tool now opens correctly as a Control Panel applet

---

## [2.8.1] — 2026-06-25

### Fixed
- **Weather city/unit setting was missing** — after the tray menu was simplified, the weather submenu was never moved into the Customize window. It now lives under **Customize → Alerts → Weather** (°C/°F + city; leave empty for automatic location by IP)
- **Tab-switch crash** — switching from System to Tools before the hardware scan finished would paint System widgets into the Tools tab. The scan now discards its result if you've moved on
- Customize window is slightly taller so all rows fit without scrolling

---

## [2.8.0] — 2026-06-24

### Added
- **Live bottleneck analysis** — System tab shows the current limiting factor (CPU / GPU / RAM / VRAM / Disk) with severity colour, updated every second. Per-core check catches single-thread loads that hide behind a low average
- **Live uptime & boot time** in the System tab
- **Tools tab** — 24 shortcuts to built-in Windows tools across 5 categories, with a search box, List / Tiles layout toggle, and hover descriptions for every tool
- **DNS Boost** (Tools → Network) — benchmarks 15 resolvers over IPv4 + IPv6, ranks by latency, and shows your current DNS at the top for comparison. Applying is done through Windows' own network settings (Store-safe)
- **Icons or Text** — bar markers can show text labels (CPU / GPU / RAM …) instead of glyphs (Customize → Appearance)
- **Resizable Customize window**

### Changed
- New 3D glossy icon set for bar metrics and weather
- Removed vertical separators between metrics; tightened spacing
- VRAM total now read from the `GPU Adapter Memory\Dedicated Limit` PDH counter — correct on AMD RX 6000-series cards

### Fixed
- No more pale/white fringe around bar icons — binary-alpha threshold + 1 px erode keeps chroma-key edges clean
- Language and theme dropdowns no longer close the instant they open
- ASUS monitors no longer appear as "AUS"

---

## [2.7.1] — 2026-06-24

### Fixed
- Language and theme dropdowns dismissed themselves before the selection registered — `FocusOut` now waits 150 ms so the click lands first
- GPU VRAM reported half capacity on AMD RX 6000 series — now read from the PDH counter `GPU Adapter Memory(*)\Dedicated Limit` (same source as Task Manager)
- ASUS monitors with EDID code `AUS` (e.g. VG279QR, ProArt series) now show the correct brand name

---

## [2.7.0] — 2026-06-12

### Added
- **Customize window** — 6-tab settings dialog (General, Metrics, Appearance, Alerts, System, About) with live preview and drag-to-reorder metrics
- **System tab** — full hardware snapshot: CPU, RAM (per-module speed/vendor), GPU, motherboard + BIOS, monitors (EDID), audio, storage, network — each with a brand wordmark. Copy-all button for support tickets
- **Earthquake alerts** — EMSC + USGS feeds, felt-intensity model, configurable radius (default 100 km) and duration (default 20 min). Pulsing 🚨 dot on the bar with history popup
- **Power draw** — estimated CPU + GPU watts (NVIDIA via `nvidia-smi`; modelled from TDP otherwise)
- **Single-row detail mode** — choose between percentage or detail (GHz / GB / VRAM) on the single row
- **In-window donations** — PayPal & Revolut buttons in the About tab

### Changed
- **Rebrand to PulseDeck** — all user-visible surfaces updated; internal package identity unchanged so existing installs upgrade cleanly
- Localized Small / Normal / Large size labels; sharper Small font scale
- All new strings translated across 8 languages

### Fixed
- Black fringes around bar icons on light taskbars — icons are hard alpha-thresholded; chroma key adapts to the sampled taskbar colour
- Customize window no longer freezes while reordering metrics
- Throttled power, disk, and process sampling to keep the UI responsive

---

## [2.5.1] — 2026-06-10

### Fixed
- **Auto-start broken in Store builds** — inside the MSIX container the legacy `HKCU\…\Run` key is virtualised and ignored at logon. The app now detects MSIX via `GetCurrentPackageFullName` and registers via the startup task instead

### Changed
- `desktop:StartupTask` now defaults to `Enabled="true"` so first-time Store users get the standard Windows startup prompt
- Tray menu in MSIX mode shows **Startup…** → Windows Settings → Apps → Startup

---

## [2.5.0] — 2026-06-09

### Added
- **Auto-update check** — checks GitHub on launch (throttled to once every 12 hours); subtle "Update available" tray entry
- **Rich weather tooltip** — feels-like, humidity, wind speed, 3-day forecast with localized weekday names
- **Translated tooltips** — all hover panel strings translated across 8 languages

---

## [2.4.0] — 2026-06-09

### Added
- **Hover detail panels** — top processes (CPU & RAM), per-core load bars, VRAM used/total, network session totals, per-physical-disk I/O
- **Per-drive disk space** cells on the bar (C 62%, D 35%) — pick drives from the tray menu
- Used/total on the bar for GPU and RAM (e.g. `4.0 / 16`, `14 / 32`)

### Fixed
- Drive cells now correctly appear and disappear when toggled

---

## [2.3.0] — 2026-06-09

### Added
- **PulseBar branding** — new shield emblem across app icon, tray icon, and promo materials
- **On the taskbar** mode — widget sits inside the taskbar band next to app icons
- **Above the taskbar** mode — alternative strip just above the bar
- Self-healing auto-start — Run key is silently rewritten if the .exe is moved

### Fixed
- Widget no longer goes behind the taskbar when you click it

---

## [2.2.0] and earlier

Core feature set: live CPU, RAM, GPU, Network metrics on a transparent overlay; GPU VRAM via PDH; live CPU clock speed; weather via Open-Meteo; 10 themes; 8 languages; free dragging; system-tray settings; hide-in-fullscreen; single-instance lock.

---

**Microsoft Store:** <https://apps.microsoft.com/detail/9P128R4SVXLC>  
**Releases:** <https://github.com/FokionPapanikolaou/PulseDeck/releases>  
**Issues:** <https://github.com/FokionPapanikolaou/PulseDeck/issues>
