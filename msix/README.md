# MSIX (Microsoft Store) package

Build config for the Store submission. Tracked here so the Store build is
reproducible. The **`PulseBar.exe` payload is intentionally not committed**
(it's gitignored as `*.exe`) — drop the freshly built + signed exe in here
right before packing.

## Files
- `AppxManifest.xml` — package manifest. **Identity** (`PapanikolaouFokion.PulseBar`,
  Publisher `CN=4DDDFD1C-…`) and the `Version` must match Partner Center.
  `DisplayName` is the user-visible name (PulseDeck).
- `Assets/` — Store tile / splash logos.

## Build
```powershell
# 1. build + sign the exe (from repo root), then copy it in:
copy ..\dist\PulseBar.exe .\PulseBar.exe

# 2. bump Version in AppxManifest.xml (e.g. 2.7.0.0)

# 3. pack
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" `
    pack /d . /p ..\dist\PulseDeck-<version>.msix /o
```

Do **not** sign the .msix locally — the manifest Publisher is the Store-assigned
identity, which won't match the local cert. The Store re-signs on submission.
Upload the .msix manually via Partner Center.
