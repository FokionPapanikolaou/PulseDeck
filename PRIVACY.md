# PulseDeck β€” Privacy Policy

**Effective date:** 9 June 2026
**Publisher:** Fokion Papanikolaou

PulseDeck ("the app") is a desktop system-monitor for Windows 10/11. This
policy explains, in plain language, exactly what data the app sends, where it
goes, and what we do with it.

> **TL;DR β€” we don't collect anything.** No accounts, no analytics, no
> advertising, no telemetry. Your settings stay on your PC. The only network
> calls are the optional weather widget hitting third-party weather APIs.

---

## 1. What we collect
**Nothing.** PulseDeck does not have any servers, accounts, sign-in, telemetry,
crash reporting, advertising or analytics. We never see how you use the app.

## 2. What the app stores on your PC
PulseDeck saves a single configuration file (`config.json`) with your
preferences (chosen metrics, theme, language, position, etc.). It is stored
locally in your user profile (the package's `LocalState` folder or, for the
portable build, next to the executable). It is **never uploaded anywhere**.

## 3. What goes over the network (weather only)
The weather widget is **optional** and can be turned off from the tray menu
(*Metrics β†’ Weather*). If turned on, the app makes HTTPS requests to:

- **ipapi.co** β€” to obtain an approximate location based on your **public IP
  address** (city / latitude / longitude). This is only used when you have not
  entered a city manually.
  β†’ Their privacy policy: https://ipapi.co/privacy/

- **open-meteo.com** β€” to fetch the current weather and a short forecast for
  the resolved coordinates. Open-Meteo does **not** require an API key and
  does **not** track users.
  β†’ Their privacy policy: https://open-meteo.com/en/terms

If you set a city manually (*Weather β†’ Set cityβ€¦*), the IP-lookup call is
skipped. If you disable the weather widget entirely, no network calls are
made.

## 4. Update check (optional, on by default)
On launch, PulseDeck may contact the public **GitHub Releases API**
(`api.github.com`) to check whether a newer version is available. Only the
latest release tag is read β€” no personal information is sent and the request
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
stored settings at any time by uninstalling the app (Settings β†’ Apps β†’
PulseDeck β†’ Uninstall), which also removes the configuration file.

## 8. Changes to this policy
If this policy changes, the new version will be published in the project
repository at `github.com/FokionPapanikolaou/PulseDeck`. The "Effective date"
above will be updated accordingly.

## 9. Contact
Questions about this policy: open an issue at
**https://github.com/FokionPapanikolaou/PulseDeck/issues**
