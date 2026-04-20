# Quick Start Guide - World Clock Widget

## Installation (One-Time Setup)

1. **Check Python Version**
   ```bash
   python --version
   ```
   You need Python 3.9 or higher

2. **Install Dependencies**
   ```bash
   cd "C:\Code\study\world clock"
   pip install -r requirements.txt
   ```

## Running the Widget

### Option 1: Double-Click (Easiest)
Simply double-click `run_clock.bat`

### Option 2: Command Line
```bash
cd "C:\Code\study\world clock"
python main.py
```

## First Time Usage

When you first run the widget:
1. It will appear at the top-center of your screen
2. You'll see 4 cities: New York, London, Tokyo, Sydney
3. The widget stays in the background - it won't interrupt your work

## Basic Operations

### Change a City
1. Click on any city name
2. A dialog will open with searchable list of 138 cities
3. Type to search or scroll to find your city
4. Click OK to confirm

### Move the Widget
1. Click and drag anywhere on the widget
2. Release to place it
3. Position is automatically saved

### Access Controls
1. Hover your mouse over the widget
2. Two buttons will appear at the bottom:
   - ⚙ Settings (blue button)
   - ✕ Close (red button)
3. Buttons disappear when you move mouse away

### Close the Widget
1. Hover over the widget
2. Click the red ✕ button

## Design Features

### Apple Watch Liquid Drop Design
- Pill-shaped with dramatic rounded edges (no pointy corners!)
- Multi-layered depth with shadow and highlight effects
- Frosted glass appearance with 92% transparency
- Soft bluish color palette

### Non-Intrusive Behavior
- Widget stays in background - won't pop over your browser or apps
- Only comes to front when YOU click to change settings
- Hidden controls keep the design clean

## Testing

Run the test suite to verify everything works:
```bash
python test_widget.py
```

You should see:
```
[SUCCESS] All tests passed! Widget is ready to use.
```

## Customization

Edit `config.json` to customize:
- `cities`: Your 4 selected cities
- `window_position`: Where widget appears (x, y coordinates)
- `opacity`: Transparency level (0.92 = 92%)
- `always_on_top`: Keep as false to avoid interruptions

## Available Cities

138 cities worldwide including:
- **Americas**: New York, Los Angeles, Chicago, Toronto, Mexico City, São Paulo, Buenos Aires
- **Europe**: London, Paris, Berlin, Rome, Madrid, Moscow, Amsterdam, Stockholm
- **Asia**: Tokyo, Beijing, Singapore, Mumbai, Dubai, Bangkok, Hong Kong, Seoul
- **Oceania**: Sydney, Melbourne, Auckland, Perth
- **Africa**: Cairo, Johannesburg, Lagos, Nairobi, Casablanca

Use the search function in the city selector to find any city instantly.

## Troubleshooting

**Widget doesn't appear**
- Check if it's off-screen - delete `config.json` to reset position

**Times are wrong**
- Ensure `tzdata` is installed: `pip install tzdata`
- Check your system clock

**Widget interrupts my work**
- Check `config.json`: `always_on_top` should be `false`
- If it's `true`, change it to `false` and restart

**Can't drag widget**
- Click and hold on the main widget area (not on city names or buttons)
- Try clicking on empty space between clocks

## Tips

1. **Position**: Top-center or bottom-left corners work well for most users
2. **Visibility**: The widget is semi-transparent so it won't block important content
3. **Quick Check**: Glance at multiple timezones without switching apps
4. **Hover Controls**: Buttons only when needed keeps the design beautiful

## Support

For issues or suggestions:
- Check `README.md` for detailed documentation
- Review `DESIGN.md` for design philosophy
- Check `CHANGELOG.md` for recent updates

Enjoy your beautiful new world clock!
