# World Clock Widget - Changelog

## Version 2.0 - Apple Watch Liquid Drop Design (2026-01-21)

### Major Visual Redesign
- **Apple Watch Liquid Drop Aesthetic**: Complete redesign inspired by Apple Watch's organic, liquid drop design language
- **Dramatic Rounded Corners**: Increased corner radius from 25px to 80px for authentic pill-shaped, bubble-like appearance
- **Multi-Layered Depth Effects**:
  - Layer 1: Outer shadow for floating effect
  - Layer 2: Border gradient for subtle depth
  - Layer 3: Main glass surface
  - Layer 4: Highlight effect on top edge (simulates light reflection on liquid)
- **Enhanced Transparency**: Increased opacity to 92% for more authentic frosted glass effect
- **Softer Color Palette**: Lighter, more dynamic bluish tones (#F7FBFF glass, #EBF5FB background)
- **Completely Organic Edges**: Zero pointy corners - fully smooth oval edges throughout

### Bug Fixes
- **Fixed**: Widget no longer pops in front of active applications
- **Fixed**: Changed `always_on_top` from `True` to `False` - widget now stays in background
- **Fixed**: Widget only comes to foreground temporarily when user clicks to change cities or settings

### UI/UX Improvements
- **Hidden Controls**: Settings and Close buttons now hidden by default, only appear on hover
- **Horizontal Layout**: Changed from vertical (400x380px) to horizontal (920x180px) pill-shaped layout
- **Space Efficient**: Consumes less vertical desktop space while maintaining readability
- **Minimalist Buttons**: Apple-style circular buttons with proper Apple blue (#007AFF) and red (#FF3B30) colors

### Technical Changes
- Window size: 920x180px (was 400x380px)
- Corner radius: 80px (was 25px)
- Default opacity: 0.92 (was 0.88)
- Always-on-top: False (was True)
- Added multi-layer canvas rendering for depth effects
- Improved shadow and border rendering

### Design Philosophy
This version embraces Apple Watch's philosophy of making technology feel organic and alive. The liquid drop design creates a sense of fluidity and depth, making the widget feel like a natural extension of your desktop rather than a rigid rectangular window.

---

## Version 1.0 - Initial Release

### Features
- 4 simultaneous timezone displays
- Automatic DST support
- 24-hour time format
- DD-MM date format
- 130+ cities worldwide
- Translucent bluish design
- Basic rounded corners
- Click to change cities
- Draggable widget
- Position persistence

### Known Issues
- Widget interrupted other applications (always-on-top behavior)
- Control buttons always visible
- Vertical layout consumed more screen space
- Rounded corners not dramatic enough
