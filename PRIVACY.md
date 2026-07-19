# PulseDeck — Privacy Policy

**Effective date:** 6 July 2026
**Publisher:** Fokion Papanikolaou

PulseDeck ("the app") is a desktop system-monitor for Windows 10/11. This
policy explains, in plain language, exactly what data the app sends, where it
goes, and what we do with it.

> **TL;DR — we don't collect anything.** No accounts, no analytics, no
> advertising, no telemetry. Your settings stay on your PC. The only network
> calls are the optional weather widget, an optional update check and, when
> you open the System tab, a lookup of your own public IP so it can be shown
> to you.

---

## 1. What we collect
**Nothing.** PulseDeck does not have any servers, accounts, sign-in, telemetry,
crash reporting, advertising or analytics. We never see how you use the app.

## 2. What the app stores on your PC
PulseDeck saves a single configuration file (`config.json`) with your
preferences (chosen metrics, theme, language, position, etc.). It is stored
locally in your user profile (the package's `LocalState` folder or, for the
portable build, next to the executable). It is **never uploaded anywhere**.

## 3. What goes over the network
- **Weather (optional widget).** If the weather cell is enabled, the app makes
  HTTPS requests to:
  - **ipapi.co** — to get an approximate location from your **public IP**
    (city / latitude / longitude), only when you have not set a city manually.
    → https://ipapi.co/privacy/
  - **open-meteo.com** (weather + geocoding) — to resolve a typed city name to
    coordinates and fetch the current conditions and short forecast. Open-Meteo
    requires no API key and does not track users.
    → https://open-meteo.com/en/terms

  If you set a city manually the IP-lookup call is skipped; if you turn the
  weather cell off, none of these calls are made.

- **Public IP display (System tab).** When you open *Settings → System*, the
  app asks **api.ipify.org** for your own public IP address so it can be shown
  in the Network section. The service simply echoes the address back; nothing
  else is sent, and the result is only displayed on your screen — never stored
  or transmitted elsewhere. The result is cached for 30 minutes.
  → Their privacy policy: https://www.ipify.org

No other feature makes network requests, apart from the update check below.
(The earthquake alerts that existed in older versions were removed in 2.8.5.)

## 4. Update check (optional, on by default)
On launch, PulseDeck may contact the public **GitHub Releases API**
(`api.github.com`) to check whether a newer version is available. Only the
latest release tag is read — no personal information is sent and the request
is throttled to once every 12 hours. You can disable this from the tray menu
(*Check for updates*).

## 5. What we do **not** do
- We do **not** create accounts or ask you to sign in.
- We do **not** read your files, browser history, keystrokes, screenshots or
  network traffic.
- We do **not** send crash reports or analytics.
- We do **not** show ads.
- We do **not** sell, share or transfer any data to third parties.

## 6. Children
PulseDeck is a general-purpose utility and is not directed at children. We do
not knowingly collect any data from anyone.

## 7. Your rights
Because we do not collect or store personal data on our side, there is nothing
for us to access, export or delete on your behalf. You can remove all locally
stored settings at any time by uninstalling the app (Settings → Apps →
PulseDeck → Uninstall), which also removes the configuration file.

## 8. Changes to this policy
If this policy changes, the new version will be published in the project
repository at `github.com/FokionPapanikolaou/PulseDeck`. The "Effective date"
above will be updated accordingly.

## 9. Contact
Questions about this policy: open an issue at
**https://github.com/FokionPapanikolaou/PulseDeck/issues**
