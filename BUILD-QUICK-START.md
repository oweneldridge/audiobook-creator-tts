# Quick Start: Build macOS App

**Goal:** Create `Audiobook Creator TTS.app` that non-technical users can double-click to run.

## 5-Minute Build

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Generate spec file (one-time)
pyinstaller --name "Audiobook Creator TTS" \
  --windowed \
  --icon icon.icns \
  --add-data "voices.json:." \
  --hidden-import=pypdf \
  --hidden-import=ebooklib \
  --hidden-import=playwright \
  main_document_mode.py

# 3. Build the app (use this for subsequent builds)
pyinstaller "Audiobook Creator TTS.spec"

# 4. Test it
open "dist/Audiobook Creator TTS.app"
```

**Result:** `dist/Audiobook Creator TTS.app` (~500MB)

**Note:** After the first build, you can just run step 3 to rebuild.

## Distribute to Users

### Simple Way (Unsigned)

```bash
# Create ZIP
cd dist
zip -r "Audiobook-Creator-TTS.zip" "Audiobook Creator TTS.app"

# Share the ZIP file
```

**User instructions:**
1. Download and unzip
2. Drag `Audiobook Creator TTS.app` to Applications folder
3. Right-click app → Open (first time only, bypasses Gatekeeper warning)
4. Click "Open" in dialog
5. App launches! First run will download browser (~200MB)

### Professional Way (Code Signed)

**Requirements:**
- Apple Developer account ($99/year)
- Developer ID certificate

```bash
# Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/Audiobook Creator TTS.app"

# Create ZIP
cd dist
zip -r "Audiobook-Creator-TTS-signed.zip" "Audiobook Creator TTS.app"
```

**User experience:**
- No Gatekeeper warning
- Just double-click to run
- Professional feel

## What Gets Bundled

✅ Python 3.11 interpreter
✅ All dependencies (pypdf, ebooklib, playwright, etc.)
✅ Voice library (voices.json)
✅ Core scripts
❌ Playwright browser (downloads on first run)
❌ ffmpeg (optional, user installs if needed)

## File Sizes

- **App bundle:** ~500MB
- **First-run browser download:** ~200MB (one-time)
- **Total disk space needed:** ~1GB (including output audio)

## Common Issues

**"ModuleNotFoundError" when building:**
```bash
pip install -r requirements.txt
pyinstaller "Audiobook Creator TTS.spec"
```

**App won't launch:**
```bash
# Run from terminal to see error
"dist/Audiobook Creator TTS.app/Contents/MacOS/Audiobook Creator TTS"
```

**Gatekeeper blocks app:**
```bash
# Remove quarantine
xattr -d com.apple.quarantine "dist/Audiobook Creator TTS.app"
```

## Full Details

See `README-DISTRIBUTION.md` for:
- Code signing process
- DMG creation
- Notarization
- Troubleshooting
- Version management

---

**That's it!** You now have a distributable macOS app that anyone can run.
