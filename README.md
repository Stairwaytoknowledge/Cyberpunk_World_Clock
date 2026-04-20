# World Clock Widget for Windows 11

A stunning floating desktop widget inspired by Apple Watch's Liquid Drop design that displays the current time for 4 cities around the world.

## Two Versions Available

### 🌟 PyQt6 Version (RECOMMENDED - Authentic Blur Effects)
True Apple Watch aesthetic with:
- ✅ **Real frosted glass blur effects**
- ✅ **Authentic gradient shadows**
- ✅ **Smoother animations**
- ✅ **Better performance**
- ✅ **True to Apple's design language**

### Tkinter Version (Basic)
- ⚠️ Limited visual effects (no real blur)
- ⚠️ Simulated glass appearance
- ✅ Lightweight, no extra dependencies

**We strongly recommend the PyQt6 version for authentic Apple Watch Liquid Drop design.**

## Features

- **4 Simultaneous Time Zones**: Display time for any 4 cities from over 130+ cities worldwide
- **Automatic DST Support**: Automatically handles daylight saving time transitions
- **24-Hour Format**: All times displayed in 24-hour format (HH:MM:SS)
- **Date Display**: Shows date in DD-MM format below each time
- **Apple Watch Liquid Drop Design**: Breathtaking pill-shaped design with dramatic rounded edges, layered depth effects, and frosted glass appearance
- **Horizontal Layout**: Space-efficient horizontal design (920x180px)
- **Non-Intrusive**: Stays in background - won't interrupt your work or pop over active apps
- **Hidden Controls**: Settings and Close buttons appear only when hovering over the widget
- **Customizable Cities**: Click on any city name to change it
- **Draggable**: Drag the widget anywhere on your screen
- **Position Memory**: Remembers window position between sessions
- **Organic Aesthetics**: Smooth, bubble-like appearance with no pointy edges - just like a liquid drop

## Installation

### Easiest — Microsoft Store
*(coming soon)* — search **"World Clock"** in the Store and click Install. Auto-updates included.

### Two-click install from GitHub (no Python required)
1. Download **`WorldClock-vX.Y.Z.zip`** from the [Releases page](../../releases) and **right-click → Extract All**.
2. Double-click **`Install.bat`**.
3. Double-click **World Clock** on your Desktop.

That's it. The zip already contains a private Python runtime, so the installer doesn't need internet, doesn't touch your system Python, doesn't trigger SmartScreen, and finishes in under a second. The installer asks (Y/N) whether to launch now and whether to launch automatically at login.

To remove: run **`Uninstall.bat`** in the same folder, then delete the folder (~110 MB).

### Run from source (developers)
```bash
pip install -r requirements.txt
python main_qt.py
```

### Build the release bundle locally
```powershell
powershell -ExecutionPolicy Bypass -File build\build_bundle.ps1 -Version v1.0.0
# Output: dist\WorldClock-v1.0.0\  (zip the contents to ship)
```

### Microsoft Store packaging
See [STORE_SUBMISSION.md](STORE_SUBMISSION.md) for the Partner Center walkthrough and `build/build_msix.ps1` for the build script.

## Usage

### Changing Cities
- Click on any city name to open the city selector dialog
- Use the search box to filter cities
- Select a new city and click OK

### Moving the Widget
- Click and drag anywhere on the widget to move it around your screen
- The position is automatically saved

### Accessing Controls
- Hover your mouse over the widget to reveal the Settings (⚙) and Close (✕) buttons
- Controls disappear when you move your mouse away to keep the design clean

### Closing the Widget
- Hover over the widget and click the red "✕" button

## Configuration

The application stores its configuration in `config.json` including:
- Selected cities
- Window position
- Opacity settings

Default cities:
- New York (America/New_York)
- London (Europe/London)
- Tokyo (Asia/Tokyo)
- Sydney (Australia/Sydney)

## Available Cities

The widget includes 130+ cities from all continents, including major cities like:
- Americas: New York, Los Angeles, Toronto, Mexico City, São Paulo, Buenos Aires
- Europe: London, Paris, Berlin, Moscow, Rome, Madrid
- Asia: Tokyo, Beijing, Dubai, Singapore, Mumbai, Bangkok
- Oceania: Sydney, Melbourne, Auckland
- Africa: Cairo, Johannesburg, Lagos, Nairobi

## Technical Details

- **Framework**: Python + tkinter with advanced Canvas rendering
- **Design**: Apple Watch Liquid Drop inspired with dramatic rounded corners (80px radius)
- **Visual Effects**: Multi-layered depth with shadow, border, glass surface, and highlight layers
- **Timezone Library**: zoneinfo (Python 3.9+)
- **Update Frequency**: 1 second
- **Default Opacity**: 92% for authentic liquid drop effect
- **Layout**: Horizontal pill-shaped (920x180px)
- **Background Behavior**: Non-intrusive (stays behind active windows)
- **Edge Design**: Completely organic oval edges - no pointy corners

## System Requirements

- Windows 11 (also works on Windows 10)
- Python 3.9 or higher
- Display resolution: 1280x720 or higher recommended

## Troubleshooting

**Widget doesn't appear**:
- Check if it's positioned off-screen
- Delete `config.json` to reset to default position

**Times are incorrect**:
- Ensure `tzdata` package is installed: `pip install tzdata`
- Check your system time is correct

**Widget won't drag**:
- Click and drag from the title bar area only

## Future Enhancements

- Opacity adjustment slider
- More color themes
- System tray integration
- Start with Windows option
- Custom time/date formats
- Additional timezone information (UTC offset, timezone abbreviations)
