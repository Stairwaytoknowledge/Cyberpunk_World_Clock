"""
Generates all icon assets needed for:
  - The PyQt window / taskbar (icon.ico, icon.png)
  - The PyInstaller-built .exe (icon.ico)
  - Microsoft Store tile assets (assets/store/*.png at all required sizes)

Run once per release (or whenever you change the design):
    pip install -r requirements-build.txt
    python build/generate_icons.py

Replace the draw_clock() body to use your own artwork.
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
STORE = ASSETS / "store"

# Microsoft Store / Windows tile sizes (Square + Wide + Splash + Store logo)
STORE_SIZES = {
    "Square44x44Logo.png": (44, 44),
    "Square71x71Logo.png": (71, 71),
    "Square150x150Logo.png": (150, 150),
    "Square310x310Logo.png": (310, 310),
    "Wide310x150Logo.png": (310, 150),
    "StoreLogo.png": (50, 50),
    "SplashScreen.png": (620, 300),
    # Scaled assets recommended by Store certification:
    "Square44x44Logo.targetsize-24_altform-unplated.png": (24, 24),
    "Square44x44Logo.targetsize-256.png": (256, 256),
}

# .ico embeds multiple sizes for crisp rendering everywhere Windows shows it
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def draw_clock(size: int, *, transparent_bg: bool = True) -> Image.Image:
    """Draw a simple flat clock face. Replace with custom artwork later."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = max(1, size // 16)
    box = (pad, pad, size - pad, size - pad)

    # Background pill — Apple-watch-ish soft blue gradient via simple radial fill
    # (Pillow has no native gradient; approximate with concentric circles)
    cx, cy = size / 2, size / 2
    radius = (size - 2 * pad) / 2
    steps = max(20, size // 4)
    for i in range(steps, 0, -1):
        t = i / steps
        # blend from #ffffff (center) to #d9eaf7 (edge)
        r = int(255 * (1 - t) + 217 * t)
        g = int(255 * (1 - t) + 234 * t)
        b = int(255 * (1 - t) + 247 * t)
        rr = radius * t
        d.ellipse(
            (cx - rr, cy - rr, cx + rr, cy + rr),
            fill=(r, g, b, 255),
        )

    # Outer ring
    ring_w = max(1, size // 32)
    d.ellipse(box, outline=(91, 124, 141, 255), width=ring_w)

    # Hour ticks
    import math
    tick_outer = radius - max(2, size // 24)
    tick_inner = tick_outer - max(2, size // 18)
    tick_w = max(1, size // 64)
    for hour in range(12):
        ang = math.radians(hour * 30 - 90)
        x1 = cx + tick_inner * math.cos(ang)
        y1 = cy + tick_inner * math.sin(ang)
        x2 = cx + tick_outer * math.cos(ang)
        y2 = cy + tick_outer * math.sin(ang)
        d.line((x1, y1, x2, y2), fill=(29, 29, 31, 230), width=tick_w)

    # Hands — fixed at "10:10" for icon convention (looks balanced)
    hand_w = max(2, size // 22)
    # Hour hand to "10"
    ang_h = math.radians(10 * 30 - 90)
    hx = cx + (radius * 0.45) * math.cos(ang_h)
    hy = cy + (radius * 0.45) * math.sin(ang_h)
    d.line((cx, cy, hx, hy), fill=(29, 29, 31, 255), width=hand_w)
    # Minute hand to "2"
    ang_m = math.radians(2 * 30 - 90)
    mx = cx + (radius * 0.65) * math.cos(ang_m)
    my = cy + (radius * 0.65) * math.sin(ang_m)
    d.line((cx, cy, mx, my), fill=(29, 29, 31, 255), width=hand_w)

    # Center pin
    pin = max(2, size // 22)
    d.ellipse((cx - pin, cy - pin, cx + pin, cy + pin), fill=(0, 122, 255, 255))

    if not transparent_bg:
        # Composite onto white for tiles where transparency is undesirable
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.alpha_composite(img)
        return bg
    return img


def generate_ico(out_path: Path):
    """Generate a multi-resolution .ico file."""
    # Pillow needs the highest-resolution image and a `sizes=` argument
    base = draw_clock(256)
    base.save(out_path, format="ICO", sizes=ICO_SIZES)
    print(f"  wrote {out_path.relative_to(ROOT)}")


def generate_png(out_path: Path, w: int, h: int):
    """Generate a single PNG (square or wide)."""
    if w == h:
        img = draw_clock(w)
    else:
        # Wide: draw a square clock centered on transparent canvas
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        clock = draw_clock(min(w, h))
        offset = ((w - clock.width) // 2, (h - clock.height) // 2)
        img.paste(clock, offset, clock)
    img.save(out_path, format="PNG")
    print(f"  wrote {out_path.relative_to(ROOT)}")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    STORE.mkdir(parents=True, exist_ok=True)

    print("Generating app icons...")
    generate_ico(ASSETS / "icon.ico")
    generate_png(ASSETS / "icon.png", 256, 256)

    print("Generating Microsoft Store tile assets...")
    for filename, (w, h) in STORE_SIZES.items():
        generate_png(STORE / filename, w, h)

    print("\nDone. Icons in assets/, Store tiles in assets/store/.")
    print("Replace draw_clock() in this script (or overwrite the PNGs / ICO directly) to ship your own artwork.")


if __name__ == "__main__":
    main()
