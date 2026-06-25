# Changelog

All notable changes to **PulseDeck** (formerly **PulseBar**) are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.8.1] — 2026-06-25 — *Fixes: weather location, tab-switch*

### Fixed
- **Weather location/unit setting was missing.** When the tray menu was
  slimmed to "Customize…", the weather city/unit submenu was left behind and
  never moved into the window — so there was no way to set your city. It now
  lives under **Customize → Alerts → 🌤 Weather** (°C/°F + city, empty = auto
  by IP), with a live refresh on change.
- **Switching tabs while the System scan was loading broke the layout.** The
  background hardware scan could paint its widgets into whichever tab you had
  switched to (e.g. Tools); it now discards the result if you've moved on.
- Customize window is a little taller (and still resizable) so every Appearance
  / Alerts row fits.

## [2.8.0] — 2026-06-24 — *Bottleneck · Tools · DNS Boost · new 3D icons* 🧰

A big toolkit release: a live performance analyzer, a full Tools tab, a DNS
benchmark, fresh 3D icons, and a bar that can show text instead of glyphs.

### Added
- **Live bottleneck analysis** (System tab) — a "Performance (live)" section
  that names the current limiting factor (CPU / GPU / RAM / VRAM / Disk) with
  severity colouring, refreshed every second with ~4 s smoothing. A per-core
  check catches single-thread loads that hide behind a low average.
- **Live uptime & boot time** in the System tab.
- **Tools tab** — 24 safe shortcuts to built-in Windows tools across 5
  categories (Cleanup, Diagnostics, Performance, Network, System), with a
  **search box**, a **List / Tiles** layout toggle (responsive grid), and a
  one-line **hover description** for every tool. Three confirmed safe actions:
  clear Temp, empty Recycle Bin, flush DNS.
- **DNS Boost** (inside Tools → Network) — benchmarks 15 popular resolvers over
  IPv4 + IPv6, ranks them by latency, and pins your machine's **current DNS**
  at the top for comparison. Each result has Copy buttons; applying is done via
  Windows' own network settings (Store-safe, no system changes).
- **Bar marker: Icons or Text** — show CPU/GPU/RAM/NET/DISK/BAT labels on the
  bar instead of glyphs (Appearance tab).
- **Resizable Customize window** (bottom-right grip).

### Changed
- **New 3D glossy icon set** for the bar metrics and weather.
- Removed the vertical separators between bar metrics and tightened spacing to
  reclaim taskbar width.
- VRAM total now read from the `\GPU Adapter Memory\Dedicated Limit` PDH
  counter (correct on AMD RX 6000-series 8 GB cards).

### Fixed
- **No more pale/white fringe** around bar icons — icons use a binary-alpha
  threshold with a 1 px erode so the chroma-key edges stay clean.
- **Language & theme dropdowns** no longer close the instant they open (the
  overrideredirect window never held focus; now dismissed by click-outside).
- **ASUS monitors** no longer show as "AUS" (added the `AUS` EDID code).

## [2.7.1] — 2026-06-24 — *Bug fixes: dropdown, VRAM, monitor name*

### Fixed
- **Language & theme dropdowns close instantly** — clicking a language or theme
  option in the Customize window dismissed the menu before the selection
  registered. The `FocusOut` handler now waits 150 ms so the click lands first.
- **GPU VRAM total reports half the real capacity on AMD RX 6000 series** —
  the Windows registry (`HardwareInformation.qwMemorySize`) can return 4 GB
  for 8 GB cards due to an AMD driver quirk. The VRAM total is now read from
  the PDH counter `\GPU Adapter Memory(*)\Dedicated Limit`, the same source
  Task Manager uses, giving the correct value.
- **ASUS monitors shown as "AUS"** in the System tab — the EDID manufacturer
  code `AUS` (used by ASUS gaming monitors such as the VG279QR and ProArt
  series) was missing from the lookup table. Added alongside the existing
  `ACI` entry.

## [2.7.0] — 2026-06-12 — *PulseDeck rebrand · Customize window · System tab* ✨

The biggest release yet: a full **Customize** window replacing the tray
submenus, a detailed **System** tab, **earthquake alerts**, **power draw**,
and the new **PulseDeck** name.

### Added
- **Customize window** — a proper 6-tab settings dialog (General, Metrics,
  Appearance, Alerts, System, About) replacing the old nested tray menus.
  Live preview, **drag-to-reorder** metrics (☰ handle), custom-drawn radio
  pills and dropdowns themed to match the app.
- **System tab** — full read-only hardware snapshot: CPU, RAM (with per-module
  speed/vendor), GPU, **motherboard + BIOS**, **monitors** (via EDID),
  **audio devices**, **optical drives**, storage and network — each with a
  **brand wordmark** (AMD, Intel, NVIDIA, ASUS, MSI, Samsung, LG, AOC, …).
  *Copy all* button for support tickets.
- **Earthquake alerts** (EMSC + USGS) — felt-intensity (MMI) model based on
  magnitude and hypocentral distance, configurable **alert radius** (default
  100 km) and **duration** (default 20 min). A 🚨 dot pulses on the bar; click
  it (or a history row) to dismiss. Recent-events history popup.
- **Power draw** cell — estimated CPU + GPU watts (NVIDIA via `nvidia-smi`
  when present; modelled from TDP + utilization otherwise).
- **Single-row detail mode** — when two-row mode is off, choose whether the
  single row shows the **percentage** or the **detail** (GHz / GB / VRAM).
- **In-window donations** — PayPal & Revolut buttons live in the About tab.

### Changed
- **Rebrand to PulseDeck.** All user-visible surfaces (window title, About,
  tray tooltip, notifications, installer) now read **PulseDeck**. The internal
  package identity, config location and Store listing identity remain
  unchanged so existing installs upgrade cleanly.
- Smaller, sharper **Small** font scale; localized **Small / Normal / Large**
  size labels.
- Translations extended across all 8 languages for every new string.

### Fixed
- **Black fringes around bar icons** on light taskbars — icons are now hard
  alpha-thresholded and the chroma key adapts to the sampled taskbar colour.
- **Customize window freezes** while reordering metrics — replaced in-flight
  repacking with a ghost-target drag that reorders once on release.
- Throttled power, disk-usage and process sampling to keep the UI responsive.

## [2.5.1] — 2026-06-10 — *Auto-start fix for the Store build*

### Fixed
- **Auto-start under MSIX / Microsoft Store.** Inside the MSIX container,
  the legacy `HKCU\…\Run` registry key is virtualised and ignored by the
  shell at logon, so the previous Start-with-Windows toggle had no effect
  for users who installed PulseBar from the Store. PulseBar now detects
  it is running in the container via `GetCurrentPackageFullName` and uses
  the canonical path instead.

### Changed
- `desktop:StartupTask` in the AppxManifest now defaults to `Enabled="true"`,
  so first-time Store users get the standard Windows startup prompt and
  the app correctly auto-starts at logon.
- The tray menu in MSIX mode shows **Startup…** which opens
  Windows Settings → Apps → Startup (the Microsoft-recommended UX for
  Store apps). The Run-key toggle remains unchanged for the portable /
  installer builds.

### Added
- `_is_msix()` runtime helper for switching between MSIX and Win32 backends.

## [2.5.0] — 2026-06-09 — *Microsoft Store edition* 🎉

This is the version submitted to the **Microsoft Store**.

### Added
- **Auto-update check** — on launch, PulseBar quietly checks GitHub for a newer
  release (throttled to once every 12 hours). A subtle "Update available"
  entry appears in the tray menu. Toggle via *Check for updates*.
- **Rich weather** — the weather tooltip now shows **feels-like**, **humidity**,
  **wind speed** and a **3-day forecast** with localized weekday names.
- **Translated tooltips** — every hover panel string is now translated across
  all 8 supported languages.

### Changed
- Bumped to v2.5 for the Store release.
- `README.md` overhauled with a centred header, emblem, badges and a clearer
  feature list.

### Fixed
- Minor polish across the hover-tooltip layout.

## [2.4.0] — 2026-06-09 — *Hover details + per-drive*

### Added
- **Hover details** for every metric: top processes (CPU & RAM), per-core load
  bars, **VRAM used / total**, network session totals, **per-physical-disk
  I/O** rates.
- **Per-drive disk space** cells on the bar (e.g. `C 62%`, `D 35%`) — pick
  drives from the new *Disks (space)* tray submenu.
- **Used / total** displayed on the bar for **GPU** (e.g. `4.0 / 16`) and
  **RAM** (e.g. `14 / 32`).
- New *Hover details* toggle (so users who don't want popups can disable them).
- New *Reset position* tray action.

### Changed
- Removed the **Position** (left / center / right) menu — the widget is now
  drag-only, with the position locked once chosen.

### Fixed
- Disk-space cells now correctly add **and remove** when toggled from the
  tray menu (previously the addition worked but removal didn't refresh).

## [2.3.0] — 2026-06-09 — *PulseBar branding & on-taskbar mode*

### Added
- **New name & branding:** the project is now called **PulseBar**, with a new
  shield emblem (cyan/blue gradient, pulse + ascending bars) used across the
  app icon, tray icon and promotional materials.
- **On the taskbar** mode — the widget sits **inside** the taskbar band, in
  the empty space next to your app icons, using an aggressive keep-on-top
  loop to out-race the Win11 taskbar repaints.
- **Above the taskbar** mode — alternative thin strip just above the bar,
  rock-solid against any Win11 quirks. Toggle via the *On the taskbar*
  switch.
- **Self-healing auto-start** — if the portable `.exe` is moved or renamed,
  the Run-key entry is silently rewritten on next launch.
- **Multi-resolution `app.ico`** (16 → 256 px).

### Changed
- Numbers now include a space before their unit (e.g. `234 b`, `1.5 Mb`)
  for better legibility.
- The widget's window can no longer be dragged into the Win11 taskbar
  "dead zone", where XAML would paint over it.
- Default *Background* mode is fully **transparent** (chroma-key) — the
  widget overlays with no visible panel by default.

### Fixed
- Eliminated the "goes behind when clicking the taskbar" issue: stale
  `pos_y` values that fell inside the taskbar band are now clamped to the
  work-area bottom and the NOTOPMOST→TOPMOST flip reliably re-raises the
  widget if anything covers it.

## [2.2.0] and earlier — pre-Store history

Earlier iterations focused on the core feature set:

- Live **CPU**, **RAM**, **Network** and **GPU** metrics on a transparent
  overlay sitting at the bottom of the screen.
- **GPU usage + dedicated VRAM** via the PDH API (`\GPU Engine(*)\Utilization`
  and `\GPU Process Memory(*)\Dedicated Usage`).
- **Live CPU clock speed** via PDH `% Processor Performance` × base MHz from
  the registry.
- **Weather** widget via Open-Meteo + ipapi.co (free, no API key).
- **10 themes** including 5 gaming styles (Neon, Cyber, Inferno, Plasma,
  animated RGB) and **8 languages** with Windows auto-detect.
- **Free dragging** anywhere on screen with persistent position; lock toggle
  to avoid accidental moves.
- **System-tray icon** hosting all settings (so the widget itself remains a
  clean, click-through overlay).
- **Hide in fullscreen** behaviour, single-instance lock, portable & signed
  installer distribution.

---

## Links

- Microsoft Store: <https://apps.microsoft.com/detail/9P128R4SVXLC>
- Releases: <https://github.com/FokionPapanikolaou/PulseBar/releases>
- Issues: <https://github.com/FokionPapanikolaou/PulseBar/issues>
