# Changelog

All notable changes to **PulseDeck** are documented here.

---

## [2.9.5] — 2026-07-10

Identical to 2.9.4 — version bump for a clean Microsoft Store resubmission
(the 2.9.4 submission was entangled with a stale, invalid package upload).

---

## [2.9.4] — 2026-07-10

### Fixed
- Scrolling right after switching Settings tabs no longer throws silent
  errors against the previous tab's destroyed canvas.

### Changed
- **Classic right-click menu tool is hidden in the Store (MSIX) build.** The
  MSIX container virtualizes HKCU registry writes into a private hive Explorer
  never reads, and Microsoft denied the `unvirtualizedResources` capability
  that would lift this (Store policy 10.6.3) — so inside the Store build the
  toggle cannot take effect and is not shown. The portable and installer
  builds keep the feature. It is also hidden on Windows 10, where the menu is
  already classic.
- `reg.exe` / `taskkill` / `tasklist` are now invoked via their full System32
  paths (hardening).
- The System tab's public-IP lookup is cached for 30 minutes.
- Privacy policy refreshed: stale weather section removed, the System tab's
  public-IP lookup (api.ipify.org) documented.
- MSIX: MaxVersionTested raised to 10.0.26200.

---

## [2.9.3] — 2026-07-02

### Added
- **GPU detail:** vendor, GPU processor (chip), colour depth, plus **live GPU
  usage %** and **VRAM in use** from the widget's own counters.
- **Network detail:** default **gateway**, **DNS servers** in use, and **public IP**.
- **CPU:** L2 cache size.
- **Battery detail:** health/wear % (design vs full-charge capacity), capacity
  (Wh), voltage and charge-cycle count (where the laptop exposes them).

### Fixed
- **RAM speed/type sometimes missing:** the big combined WMI scan could return
  Win32_PhysicalMemory empty under load. RAM now falls back to a small
  dedicated query, so speed (MHz) and type (DDR4/5) show reliably.
- **Classic right-click menu didn't always apply:** the Explorer restart was
  too quick and raced Windows' own auto-restart. It now waits for the shell to
  fully close and only relaunches it if Windows hasn't already.

---

## [2.9.2] — 2026-07-02

### Added
- **RAM detail:** memory type (DDR3/DDR4/DDR5) and the actual running speed
  (ConfiguredClockSpeed) now shown in both views.
- **Disk health** status (SMART "OK" → ✓ Healthy) per physical drive.
- **Battery status** line (Fully charged / Charging / On battery + time left),
  and the Battery section moved to the bottom of the Advanced view.
- **TPM** now detected without admin via the PnP device (shows on machines that
  have a TPM even when the privileged WMI class is unavailable).

### Fixed
- **Motherboard / RAM speed / model occasionally vanished** — WMI can return
  some classes empty under load. Motherboard, BIOS and system model now fall
  back to the registry (always available), and the WMI scan retries once and
  merges results so RAM speed and other sections no longer randomly disappear.

---

## [2.9.1] — 2026-07-02

### Added
- **System tab now has two views** — a **Summary** ("at a glance", Speccy-style)
  card with the key specs, and an **Advanced** view with the full per-component
  detail. A toggle at the top switches between them instantly (the scan is
  cached, so no re-query).
- **More system detail:** RAM **slots used + max supported capacity**, CPU
  **virtualization** state, GPU **driver date**, Windows **activation** status,
  **firmware mode** (UEFI/Legacy) and **domain/workgroup**.

### Changed
- **Superuser** is now a **category inside the Tools tab** (God Mode, Developer
  Mode, msconfig, Registry Editor, Group Policy, Services, Startup folder,
  System32) instead of a separate tab.
- New strings translated into all supported languages (EN, EL, ES, DE, FR, IT,
  PT, RU).

---

## [2.9.0] — 2026-07-02

### Added
- **Superuser tab** — one place for power-user shortcuts: **God Mode** (the
  hidden "All Tasks" shell view), **Developer Mode**, **System Configuration
  (msconfig)**, **Registry Editor**, **Group Policy**, **Services**, the
  **Startup folder** and the **System32 folder**.
- **Tools → Classic right-click menu** — one click toggles the Windows 10 style
  context menu on Windows 11 (per-user registry tweak, no admin) and restarts
  Explorer so it applies immediately.
- **System tab — much more detail:** machine make/model, device name & signed-in
  user, **battery** (charge, state, chemistry), **physical drives** (model, size,
  SSD/HDD, bus), **Windows install date**, and a **Security** section
  (Secure Boot + TPM).
- **General → "Hide when an app goes fullscreen"** is now a visible toggle
  (previously tray-menu only).

### Fixed
- **System tab was empty / partial on some machines** — the per-class WMI calls
  each spawned their own PowerShell (~5-7 s cold on slower laptops, ~70 s total)
  and timed out at 6 s. All classes are now fetched in a **single** PowerShell
  process (~10-12 s) with a generous timeout, and CPU/OS fall back to the
  registry/`platform` if WMI is unavailable, so those sections always populate.
- **BIOS date showed garbage** (`/Date(15…`) — the CIM date is now formatted to
  `yyyy-MM-dd` in PowerShell before it reaches Python.
- **Long System values were clipped** — field values now wrap instead of being
  cut off, and re-wrap when the window is resized.
- **Bar stayed on top of fullscreen video** — fullscreen detection no longer
  bails out on `IsZoomed` (Chrome reports fullscreen video as "zoomed"). It now
  distinguishes true fullscreen (fills the monitor exactly) from a maximized
  window (overhangs by the resize border), and works on any monitor / DPI.

### Changed
- **Settings window** no longer stays always-on-top — it surfaces on open then
  releases topmost, so other windows can come in front of it. Added a
  **minimize** button (it drops to the taskbar and restores with the frameless
  look intact).
- All new UI strings are translated into every supported language
  (EN, EL, ES, DE, FR, IT, PT, RU).

---

## [2.8.6] — 2026-06-30

### Fixed
- **Black strip flashing on the bar when values grew** — cells that changed
  width each tick (Network rate, Power watts) made the layered window resize,
  and Windows left the newly exposed strip un-keyed, so a black band flashed.
  The Network and Power cells now have a locked width (padded to their max), and
  the transparent colour key is re-asserted whenever the bar width changes — so
  battery (⚡ on plug-in), GPU and any other dynamic cell stay clean too.

---

## [2.8.5] — 2026-06-26

### Removed
- **Weather** and **earthquake alerts** have been removed entirely — the bar
  cells, the Alerts tab, the tray entries and their background threads are all
  gone. Existing configs are scrubbed so the features don't linger after update.
- The Tools tab **search box** and the weather **city input** were removed (the
  full tool list is always shown; weather is no longer present at all).
- The now-redundant "Always last" toggle in the Metrics tab.

### Fixed
- **Widget vanished behind a maximized window** — a maximized app (e.g. a
  maximized browser) was mistaken for a fullscreen game/video, so the
  hide-in-fullscreen logic withdrew the whole widget. Maximized windows
  (`IsZoomed`) are now excluded; the widget only hides for true fullscreen.
- **Dark halo around the bar numbers** — the adaptive chroma key now uses the
  most-common taskbar colour, keeping the readouts clean.
- **Customize window opened hidden behind the focused app** — it's now marked
  top-most so it always appears in front.
- No stray `tk`/`python` window in the taskbar.

---

## [2.8.4] — 2026-06-26

### Changed
- **Zero-lag polling** — all slow hardware reads are now handled by a dedicated
  background thread (`_SlowPoller`) so the main UI thread never blocks:
  - `nvidia-smi` (GPU watts) — was blocking the main thread up to 500 ms every 2 s
  - `psutil.sensors_battery()` — was called every tick; now pre-fetched every 1 s
  - `psutil.disk_io_counters(perdisk=True)` — moved off the main thread
  - `psutil.cpu_freq()` fallback — moved off the main thread
- `_is_fullscreen_foreground()` result is now cached for 250 ms so the Win32 API
  calls don't fire on every single tick.

---

## [2.8.3] — 2026-06-26

### Fixed
- **Weather city field and Tools search box could not be typed in** — the
  `focus_force()` call on the parent window was stealing keyboard focus back
  from the Entry widget immediately after the click. Focus is now forced
  directly on the Entry itself, deferred 10 ms so the click event settles first.

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
- **New branding** — new shield emblem across app icon, tray icon, and promo materials
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
