#!/bin/bash

# Audiobook Creator TTS - Complete Installation Script
# Installs all Python packages and system dependencies

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Audiobook Creator TTS - Installation Script                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect platform
PLATFORM="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
    echo -e "${GREEN}✓${NC} Platform detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
    echo -e "${GREEN}✓${NC} Platform detected: Linux"
else
    echo -e "${RED}✗${NC} Unsupported platform: $OSTYPE"
    exit 1
fi

echo ""
echo -e "${YELLOW}Installing system packages...${NC}"
echo ""

# Install system packages based on platform
if [[ "$PLATFORM" == "macos" ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}✗${NC} Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

    echo -e "${BLUE}Installing Homebrew packages...${NC}"

    # Install python-tk@3.11 (for file browser)
    if brew list python-tk@3.11 &> /dev/null; then
        echo -e "${GREEN}✓${NC} python-tk@3.11 already installed"
    else
        echo -e "${YELLOW}→${NC} Installing python-tk@3.11..."
        brew install python-tk@3.11
        echo -e "${GREEN}✓${NC} python-tk@3.11 installed"
    fi

    # Install ffmpeg (for M4B creation)
    if brew list ffmpeg &> /dev/null; then
        echo -e "${GREEN}✓${NC} ffmpeg already installed"
    else
        echo -e "${YELLOW}→${NC} Installing ffmpeg..."
        brew install ffmpeg
        echo -e "${GREEN}✓${NC} ffmpeg installed"
    fi

    # Install atomicparsley (for cover art)
    if brew list atomicparsley &> /dev/null; then
        echo -e "${GREEN}✓${NC} atomicparsley already installed"
    else
        echo -e "${YELLOW}→${NC} Installing atomicparsley..."
        brew install atomicparsley
        echo -e "${GREEN}✓${NC} atomicparsley installed"
    fi

elif [[ "$PLATFORM" == "linux" ]]; then
    echo -e "${BLUE}Installing Linux packages (requires sudo)...${NC}"

    # Update package list
    sudo apt-get update -qq

    # Install packages
    echo -e "${YELLOW}→${NC} Installing python3-tk, ffmpeg, atomicparsley..."
    sudo apt-get install -y python3-tk ffmpeg atomicparsley
    echo -e "${GREEN}✓${NC} System packages installed"
fi

echo ""
echo -e "${YELLOW}Installing Python packages...${NC}"
echo ""

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo -e "${RED}✗${NC} pip not found. Please install pip first."
    exit 1
fi

# Install Python packages from requirements.txt
echo -e "${BLUE}Installing packages from requirements.txt...${NC}"
pip install -r requirements.txt

echo ""
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
echo ""

# Install Playwright browsers (required for browser automation)
echo -e "${BLUE}Installing Chromium browser for Playwright...${NC}"
playwright install chromium

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Installation Verification                                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify installations
VERIFICATION_FAILED=0

# Check Python packages
echo -e "${BLUE}Python packages:${NC}"
if python3 -c "import requests" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} requests"
else
    echo -e "  ${RED}✗${NC} requests"
    VERIFICATION_FAILED=1
fi

if python3 -c "import playwright" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} playwright"
else
    echo -e "  ${RED}✗${NC} playwright"
    VERIFICATION_FAILED=1
fi

if python3 -c "import pypdf" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} pypdf"
else
    echo -e "  ${RED}✗${NC} pypdf"
    VERIFICATION_FAILED=1
fi

if python3 -c "import ebooklib" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} ebooklib"
else
    echo -e "  ${RED}✗${NC} ebooklib"
    VERIFICATION_FAILED=1
fi

echo ""
echo -e "${BLUE}System packages:${NC}"

# Check tkinter
if python3 -c "import tkinter" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} tkinter (file browser available)"
else
    echo -e "  ${YELLOW}⚠${NC} tkinter (file browser unavailable - use manual input)"
fi

# Check ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} ffmpeg (M4B creation available)"
else
    echo -e "  ${YELLOW}⚠${NC} ffmpeg (M4B creation unavailable)"
fi

# Check AtomicParsley
if command -v AtomicParsley &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} AtomicParsley (cover art embedding available)"
else
    echo -e "  ${YELLOW}⚠${NC} AtomicParsley (cover art embedding unavailable)"
fi

echo ""

if [[ $VERIFICATION_FAILED -eq 0 ]]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Installation Complete!                                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}You can now run:${NC}"
    echo -e "  ${YELLOW}python3 main_document_mode.py${NC}  - Convert documents to audiobooks"
    echo -e "  ${YELLOW}python3 main.py${NC}                - Convert text to audio"
    echo ""
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  Installation completed with errors                              ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Please check the errors above and retry installation.${NC}"
    exit 1
fi
