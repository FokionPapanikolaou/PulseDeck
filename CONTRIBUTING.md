# Contributing to PulseDeck

Thanks for thinking about helping! β¤οΈ PulseDeck is a one-person project and
all kinds of contributions are welcome β€” from bug reports to translations to
code.

## π› Reporting bugs

[Open an issue](https://github.com/FokionPapanikolaou/PulseDeck/issues/new/choose)
using the **Bug report** template. The more detail you can give about your
Windows version, install type and steps to reproduce, the faster I can help.

## β¨ Suggesting features

Use the **Feature request** template β€” even half-baked ideas are great. Or
start a thread in
[Discussions](https://github.com/FokionPapanikolaou/PulseDeck/discussions)
if you want to chat about it first.

## π Translations

PulseDeck supports 8 languages today. To add a new one or improve an existing
translation:

1. Open `taskbar_widget.py` and search for the `T = { ... }`, `TIP = { ... }`,
   `LANG_NAMES`, `WDAYS`, `*_LABEL` and `HINTS` dictionaries near the top.
2. Add a new language entry to **each** dictionary, keeping the keys
   identical.
3. Add the language code to the `LANGS` list (if it's new).
4. Test by setting `"language": "xx"` in your `config.json` and restarting.

PRs with translations are especially welcome.

## π› οΈ Code changes

```powershell
# 1) deps
pip install psutil Pillow pystray pyinstaller

# 2) run from source
python taskbar_widget.py

# 3) build the portable .exe (optional)
pyinstaller --noconfirm --onefile --windowed --name PulseDeck `
  --icon app.ico --add-data "icons;icons" --add-data "app.ico;." `
  --hidden-import pystray._win32 taskbar_widget.py
```

A few house rules:
- **No new external dependencies** unless it's a really good reason β€” we want
  the install size and surface area small.
- **No telemetry, analytics or tracking.** Network calls are listed in
  `PRIVACY.md`; anything new there needs an obvious user-facing toggle.
- **Settings live in `config.json`.** Add new keys to the `DEFAULTS` dict and
  read them with `self.cfg.get(...)`.
- **Strings get translated** β€” if you add user-facing text, add it to every
  language table.
- **Keep the widget click-through-friendly.** Don't add modal dialogs or
  anything that traps focus on the bar itself.

## π“ License

PulseDeck is licensed under the terms in `LICENSE.txt` (proprietary EULA, but
source is publicly readable on GitHub for transparency and contributions).
By contributing, you agree that your changes can be incorporated under the
same license.

## π™ Thanks

If you ship a contribution, you'll get credited in the release notes.
