# MSIX (Microsoft Store) package

Build config for the Store submission. Tracked here so the Store build is
reproducible. The program files are **not committed** — they are copied into
a clean staging folder right before packing.

## Files
- `AppxManifest.xml` — package manifest. **Identity** (`PapanikolaouFokion.PulseBar`,
  Publisher `CN=4DDDFD1C-…`), Application Id `PulseBar` and StartupTask id
  `PulseBarStartup` must never change (the Store would treat it as another app);
  `Version` must be higher than the last submission. `DisplayName` is the
  user-visible name (PulseDeck).
- `Assets/` — Store tile / splash logos.

## Build
Since 2.15 the package carries the **one-folder** build (`PulseDeck.exe` plus
its `_internal\` folder). The single-file build unpacked itself to `%TEMP%` on
every start, and Storage Sense / temp cleaners deleted files out from under a
PulseDeck that had been running for days (missing icons, no tray menu).

```powershell
# 1. one-folder build (see the README's build section), sign PulseDeck.exe
# 2. stage: manifest + assets + the whole one-folder build
$stage = "$env:TEMP\pulsedeck-msix"
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory $stage | Out-Null
Copy-Item .\AppxManifest.xml, .\Assets $stage -Recurse
Copy-Item ..\dist\PulseDeck\* $stage -Recurse

# 3. bump Version in AppxManifest.xml (e.g. 2.15.0.0), then pack
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" `
    pack /d $stage /p ..\dist\PulseDeck-<version>.msix /o
```

Do **not** sign the .msix locally — the manifest Publisher is the Store-assigned
identity, which won't match the local cert. The Store re-signs on submission.
Upload the .msix manually via Partner Center.
