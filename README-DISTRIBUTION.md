# Audiobook Creator TTS - Distribution Guide

Complete guide for building and distributing the Audiobook Creator TTS macOS app.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building the App](#building-the-app)
3. [Distribution Options](#distribution-options)
4. [User Installation](#user-installation)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Development Environment

**Required:**
- macOS 10.13 or later
- Python 3.11
- PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Verify installation
pyinstaller --version
```

**Optional (for code signing):**
- Apple Developer Account ($99/year)
- Xcode Command Line Tools

---

## Building the App

### Step 1: Prepare the Environment

```bash
# Navigate to project directory
cd /path/to/Audiobook-Creator-TTS

# Ensure dependencies are installed
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Create App Icon (Optional)

Follow instructions in `icon_instructions.md` to create `icon.icns`.

If you create an icon, update `Audiobook Creator TTS.spec` icon parameter:
```python
icon='icon.icns',  # Change from icon=None
```

### Step 3: Build the App

```bash
# Clean previous builds
rm -rf build dist

# Build the app
pyinstaller "Audiobook Creator TTS.spec"

# Result: dist/Audiobook Creator TTS.app
```

**Build time:** 2-5 minutes depending on system

**Output size:** ~450-550 MB (includes Python + all dependencies)

### Step 4: Test the App

```bash
# Run the app
open "dist/Audiobook Creator TTS.app"

# Or from terminal to see debug output
"dist/Audiobook Creator TTS.app/Contents/MacOS/Audiobook Creator TTS"
```

**First-run behavior:**
- Checks for Playwright browser
- Auto-downloads Chromium (~200MB) if not present
- Downloads to: `~/.cache/ms-playwright/chromium-*/`

---

## Distribution Options

### Option 1: Direct Distribution (Unsigned)

**Pros:**
- Free
- Simple
- Works for personal use

**Cons:**
- Gatekeeper warning on first launch
- Users must right-click → Open

**Steps:**

1. Compress the app:
```bash
cd dist
zip -r "Audiobook-Creator-TTS-v1.0.0.zip" "Audiobook Creator TTS.app"
```

2. Distribute the ZIP file via:
   - Google Drive / Dropbox
   - GitHub Releases
   - Direct download link

3. Provide installation instructions (see User Installation section)

### Option 2: Code Signing (Recommended for Public Distribution)

**Pros:**
- No Gatekeeper warning
- Professional appearance
- Users can double-click to run

**Cons:**
- Requires Apple Developer account ($99/year)
- More complex setup

**Steps:**

1. Get Apple Developer account and Developer ID certificate

2. Sign the app:
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  "dist/Audiobook Creator TTS.app"
```

3. Verify signature:
```bash
codesign --verify --deep --strict --verbose=2 "dist/Audiobook Creator TTS.app"
spctl -a -t exec -vv "dist/Audiobook Creator TTS.app"
```

4. Notarize with Apple (optional but recommended):
```bash
# Create ZIP for notarization
ditto -c -k --keepParent "dist/Audiobook Creator TTS.app" "audiobook-creator-tts.zip"

# Submit for notarization
xcrun notarytool submit audiobook-creator-tts.zip \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"

# Wait for approval (usually 5-15 minutes)

# Staple the notarization ticket
xcrun stapler staple "dist/Audiobook Creator TTS.app"
```

5. Create final ZIP:
```bash
cd dist
zip -r "Audiobook-Creator-TTS-v1.0.0-signed.zip" "Audiobook Creator TTS.app"
```

### Option 3: DMG Installer (Professional)

Create a drag-and-drop DMG installer:

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Audiobook Creator TTS" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Audiobook Creator TTS.app" 175 120 \
  --hide-extension "Audiobook Creator TTS.app" \
  --app-drop-link 425 120 \
  "Audiobook-Creator-TTS-v1.0.0.dmg" \
  "dist/"
```

---

## User Installation

### For End Users (Unsigned App)

**Download and Install:**

1. Download `Audiobook-Creator-TTS-v1.0.0.zip`
2. Double-click to extract `Audiobook Creator TTS.app`
3. Drag `Audiobook Creator TTS.app` to `/Applications` folder

**First Launch (Gatekeeper Bypass):**

When you first open the app, macOS will show: *"Audiobook Creator TTS.app can't be opened because it is from an unidentified developer."*

**To open:**
1. **Right-click** (or Control-click) on `Audiobook Creator TTS.app`
2. Click **"Open"**
3. Click **"Open"** again in the dialog
4. The app will launch (you only need to do this once)

**Alternative method:**
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine "/Applications/Audiobook Creator TTS.app"

# Now you can double-click to open
```

### For End Users (Signed App)

1. Download and extract
2. Drag to Applications folder
3. Double-click to run (no warnings)

### System Requirements

- **macOS:** 10.13 (High Sierra) or later
- **Disk Space:** 1 GB free (app + browser + audio output)
- **Internet:** Required for first-run browser download and API access
- **Optional:** ffmpeg (for M4B audiobook creation)

**To install ffmpeg:**
```bash
# Using Homebrew
brew install ffmpeg
```

---

## File Structure

### Inside the .app Bundle

```
Audiobook Creator TTS.app/
├── Contents/
│   ├── Info.plist                   # App metadata
│   ├── MacOS/
│   │   └── Audiobook Creator TTS    # Executable
│   ├── Resources/
│   │   ├── voices.json              # Voice library
│   │   ├── main.py                  # Core modules
│   │   └── ...
│   └── Frameworks/                  # Python + dependencies
```

### User Data Locations

- **Playwright Browser:** `~/.cache/ms-playwright/chromium-*/`
- **Audio Output:** `~/Documents/Audiobook-Creator-TTS/audio/` (or CWD/audio/)
- **No user config files** (all self-contained)

---

## Troubleshooting

### Build Issues

**"ModuleNotFoundError" during build:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Rebuild
rm -rf build dist
pyinstaller "Audiobook Creator TTS.spec"
```

**"ImportError: No module named 'X'" when running app:**

Add to `Audiobook Creator TTS.spec` hiddenimports:
```python
hiddenimports = [
    'X',  # Add missing module
    # ... existing imports
]
```

**Build fails with "Permission denied":**
```bash
# Remove old build artifacts
sudo rm -rf build dist

# Rebuild
pyinstaller "Audiobook Creator TTS.spec"
```

### Runtime Issues

**App won't launch (crashes immediately):**

Run from terminal to see error:
```bash
"/Applications/Audiobook Creator TTS.app/Contents/MacOS/Audiobook Creator TTS"
```

Common fixes:
- Ensure Python 3.11 was used for build
- Check all dependencies are bundled
- Verify no system-specific paths in code

**"Playwright browser not found":**

The app should auto-download on first run. If it fails:
```bash
# Manual install
/Applications/Audiobook\ Creator\ TTS.app/Contents/MacOS/Audiobook\ Creator\ TTS

# When it fails, open terminal and run:
playwright install chromium
```

**Gatekeeper keeps blocking the app:**
```bash
# Remove quarantine
xattr -d com.apple.quarantine "/Applications/Audiobook Creator TTS.app"

# Or allow in System Preferences
# System Preferences > Security & Privacy > General > "Open Anyway"
```

### Distribution Issues

**File size too large (>1GB):**

Reduce size by excluding unused libraries in `Audiobook Creator TTS.spec`:
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'pytest',
]
```

**macOS warns "damaged and can't be opened":**

This happens when downloading from non-HTTPS sources. Solutions:
1. Use HTTPS for distribution
2. Code sign the app
3. Users can remove quarantine: `xattr -d com.apple.quarantine`

---

## Version Updates

### Creating a New Release

1. Update version in `Audiobook Creator TTS.spec`:
```python
'CFBundleShortVersionString': '1.1.0',
'CFBundleVersion': '1.1.0',
```

2. Tag the release:
```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

3. Rebuild:
```bash
rm -rf build dist
pyinstaller "Audiobook Creator TTS.spec"
```

4. Create distribution package:
```bash
cd dist
zip -r "Audiobook-Creator-TTS-v1.1.0.zip" "Audiobook Creator TTS.app"
```

5. Upload to GitHub Releases or distribution platform

---

## Best Practices

### Before Distribution

- [ ] Test on clean macOS system (no development tools)
- [ ] Verify first-run browser download works
- [ ] Test with various document formats (PDF, EPUB, TXT)
- [ ] Check audio output quality
- [ ] Verify all voice options work
- [ ] Test M4B audiobook creation (with ffmpeg)
- [ ] Check app size is reasonable (<600MB)

### Security

- **Don't bundle secrets** - No API keys in the bundle
- **Use HTTPS** - Only distribute via secure channels
- **Code sign** - For public distribution
- **Keep dependencies updated** - Regularly update PyInstaller and dependencies

### Performance

- **Test on older Macs** - Ensure compatibility with macOS 10.13+
- **Monitor resource usage** - App should use <500MB RAM
- **Optimize startup time** - Should launch in <5 seconds

---

## Support

### For Developers

- Review `main_document_mode.py` for core logic
- Check `Audiobook Creator TTS.spec` for build configuration
- Update `requirements.txt` when adding dependencies
- Run tests with `pytest` before building

### For Users

- Check [README.md](README.md) for usage instructions
- Report issues on GitHub
- Include system info when reporting bugs:
  - macOS version
  - App version
  - Error messages from Terminal

---

## License

See LICENSE file for distribution rights.

## Credits

Built with PyInstaller, Playwright, and Python 3.11.

---

**Last Updated:** 2025-01-15
**Version:** 1.0.0
