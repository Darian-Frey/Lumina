# Packaging Lumina

This document covers how to build distributable binaries for each platform.

---

## Linux — AppImage

### Step 1: Build the PyInstaller executable

```bash
./build.sh
```

This produces `dist/Lumina`, a single-file executable with all dependencies bundled.

### Step 2: Test the binary

```bash
./dist/Lumina
```

The launcher should open exactly as it does with `python3 -m lumina`.

### Step 3: Wrap in an AppImage

Download `appimagetool` if you don't have it:

```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

Create an AppDir structure:

```bash
mkdir -p Lumina.AppDir/usr/bin
cp dist/Lumina Lumina.AppDir/usr/bin/lumina
```

Create `Lumina.AppDir/lumina.desktop`:

```ini
[Desktop Entry]
Name=Lumina
Exec=lumina
Icon=lumina
Type=Application
Categories=Education;Science;Physics;
Comment=Interactive simulation suite for physics and mathematics
```

Create `Lumina.AppDir/AppRun` (the entry point):

```bash
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/lumina" "$@"
```

Make it executable and build the AppImage:

```bash
chmod +x Lumina.AppDir/AppRun
./appimagetool-x86_64.AppImage Lumina.AppDir Lumina-x86_64.AppImage
```

### Step 4: Distribute

The resulting `Lumina-x86_64.AppImage` runs on most Linux distributions without installation. Users just download, `chmod +x`, and run.

---

## Windows — .exe

On a Windows machine with Python 3.11+ installed:

```powershell
pip install -r requirements.txt -r requirements-dev.txt
python -m PyInstaller lumina.spec --clean --noconfirm
```

The result is `dist/Lumina.exe`. For a nicer installer, use Inno Setup or NSIS.

---

## macOS — .dmg

On a Mac with Python 3.11+:

```bash
python3 -m PyInstaller lumina.spec --clean --noconfirm
```

The result is `dist/Lumina.app`. To create a `.dmg`:

```bash
hdiutil create -volname Lumina -srcfolder dist/Lumina.app -ov -format UDZO Lumina.dmg
```

Code signing requires an Apple Developer ID and is documented separately.

---

## Known issues

- **Qt xcb plugin**: on some Linux distros you may need `libxcb-cursor0`:
  ```bash
  sudo apt install libxcb-cursor0
  ```
- **Wayland**: if xcb fails, try `QT_QPA_PLATFORM=wayland ./Lumina`.
- **Binary size**: the PyInstaller bundle will be ~200-300 MB because it includes Qt, NumPy, SciPy, and pyqtgraph. This is unavoidable without more aggressive dependency trimming.
- **First launch is slow**: PyInstaller extracts the bundled files to a temp directory on first run. Subsequent launches are faster.
