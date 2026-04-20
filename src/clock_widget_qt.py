import os
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,
                              QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, QRect
from PyQt6.QtGui import (QPainter, QColor, QPen, QPainterPath, QLinearGradient,
                          QRadialGradient, QPalette, QRegion, QBrush,
                          QFontDatabase, QPixmap)
from src.clock_manager import ClockManager
from src.config_manager import ConfigManager
from src.city_selector_qt import CitySelectorQt


MIN_CITIES = 4
MAX_CITIES = 6

# Primary display font. Orbitron is a free cyberpunk-flavoured geometric
# sans shipped under the SIL OFL 1.1 in assets/fonts/. We load it at
# runtime so the widget looks identical on every machine even though
# Orbitron is not a default Windows font.
CYBERPUNK_FONT = "Orbitron"
FALLBACK_STACK = "'Orbitron', 'Rajdhani', 'Chakra Petch', 'Cascadia Code', 'Consolas', monospace"

_FONT_LOADED = False


def _load_bundled_font():
    """Register the bundled Orbitron font with Qt the first time a widget
    is constructed. Silently falls back to the system font stack if the
    file is missing (e.g. running from a stripped clone without running
    generate_icons.py)."""
    global _FONT_LOADED
    if _FONT_LOADED:
        return
    # Resolve asset path whether running from the project root (dev mode)
    # or from the release bundle (install folder).
    candidates = [
        os.path.join("assets", "fonts", "Orbitron-VariableFont_wght.ttf"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "assets", "fonts", "Orbitron-VariableFont_wght.ttf"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            fid = QFontDatabase.addApplicationFont(path)
            if fid >= 0:
                _FONT_LOADED = True
                return
    # Not found - the CSS fallback stack kicks in. Not fatal.
    _FONT_LOADED = True  # don't retry every construction


class ClockWidgetQt(QWidget):
    """Production-ready Apple Watch Liquid Drop clock widget"""

    def __init__(self):
        super().__init__()

        _load_bundled_font()

        # Initialize managers
        self.config_manager = ConfigManager()
        self.clock_manager = ClockManager()

        # Load configuration
        self.config = self.config_manager.load_config()
        self.cities = self.config["cities"]
        # Clamp persisted city count to supported range (handles configs
        # that were edited by hand or copied from an older/newer version).
        if len(self.cities) < MIN_CITIES:
            defaults = self.config_manager.get_default_cities()
            while len(self.cities) < MIN_CITIES:
                self.cities.append(defaults[len(self.cities) % len(defaults)])
        if len(self.cities) > MAX_CITIES:
            self.cities = self.cities[:MAX_CITIES]
        self.config["cities"] = self.cities

        # State
        self.drag_position = None
        self.controls_visible = False

        # Setup
        self.setup_window()
        self.create_ui()

        # Start clock
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clocks)
        self.timer.start(1000)
        self.update_clocks()

    def setup_window(self):
        """Configure window for production"""
        # CRITICAL FIX: Proper window flags to stay in background
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint  # Extra hint for staying behind
        )

        # Transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Size - same width as before, reduced height so the empty lower
        # band is gone. Vertical padding above the city label and below
        # the date label is now symmetric (~22 px each).
        self.setFixedSize(920, 110)

        # Position
        x = self.config["window_position"]["x"]
        y = self.config["window_position"]["y"]

        if x is None or y is None:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 920) // 2
            y = 50

        self.move(x, y)

    def create_ui(self):
        """Create UI elements"""
        # Main layout - a single content band, no bottom stretch anymore.
        # The control buttons are floated on top of the right curve as
        # children of `self` (see create_control_buttons), so they don't
        # claim any layout space.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_widget = QWidget()
        content_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        content_layout = QVBoxLayout(content_widget)
        # Symmetric vertical padding: same `y` above the city labels as
        # below the date labels. Right margin reserves room for the
        # floating 2x2 button cluster so clocks are never clipped, even
        # when the cluster is visible on hover.
        content_layout.setContentsMargins(40, 18, 90, 18)
        content_layout.setSpacing(4)

        # Clocks row - rebuilt whenever the city count changes
        self.clocks_layout = QHBoxLayout()
        self.clock_labels = []
        self._rebuild_clock_row()
        content_layout.addLayout(self.clocks_layout)

        main_layout.addWidget(content_widget)

        # Floating right-cluster controls (hidden until hover)
        self.create_control_buttons()
        self.hide_controls()

    def _rebuild_clock_row(self):
        """Tear down and re-create clock displays for the current city count.
        Called on init and whenever the user adds/removes a city."""
        # Remove existing widgets
        while self.clocks_layout.count():
            item = self.clocks_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.clock_labels = []

        # Orbitron glyphs are ~30% wider than Segoe UI, so the digit sizes
        # that worked before would clip at 5/6 cities. These numbers keep
        # "HH:MM:SS" inside each column with a little slack on every count.
        n = len(self.cities)
        spacing = {4: 28, 5: 18, 6: 10}.get(n, 28)
        time_pt = {4: 20, 5: 17, 6: 14}.get(n, 20)
        self.clocks_layout.setSpacing(spacing)

        for i in range(n):
            clock = self.create_clock_display(i, time_pt=time_pt)
            self.clocks_layout.addWidget(clock)
            self.clock_labels.append(clock)

    def create_clock_display(self, index, time_pt=24):
        """Create single clock"""
        container = QWidget()
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout(container)
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # City - muted electric cyan, uppercase for cyber feel
        city_label = QLabel("LOADING")
        city_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(120, 210, 235, 210);
                font-family: {FALLBACK_STACK};
                font-size: 9pt;
                font-weight: 600;
                letter-spacing: 2px;
                background: transparent;
            }}
            QLabel:hover {{
                color: rgba(0, 245, 255, 255);
            }}
        """)
        city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        city_label.setCursor(Qt.CursorShape.PointingHandCursor)
        city_label.mousePressEvent = lambda e, idx=index: self.change_city(idx)
        layout.addWidget(city_label)

        # Time - bright electric cyan with soft neon glow (see below)
        time_label = QLabel("00:00:00")
        time_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(225, 250, 255, 255);
                font-family: {FALLBACK_STACK};
                font-size: {time_pt}pt;
                font-weight: 800;
                background: transparent;
            }}
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Neon glow: zero-offset cyan drop shadow with large blur radius
        glow = QGraphicsDropShadowEffect(time_label)
        glow.setBlurRadius(22)
        glow.setOffset(0, 0)
        glow.setColor(QColor(0, 229, 255, 220))
        time_label.setGraphicsEffect(glow)
        layout.addWidget(time_label)

        # Date - dim cyan
        date_label = QLabel("00-00")
        date_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(140, 195, 220, 180);
                font-family: {FALLBACK_STACK};
                font-size: 9pt;
                font-weight: 500;
                letter-spacing: 1px;
                background: transparent;
            }}
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(date_label)

        # DST alert - neon magenta, hidden until within 7 days of fall-back
        dst_label = QLabel("")
        dst_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 90, 190, 240);
                font-family: {FALLBACK_STACK};
                font-size: 8pt;
                font-weight: 700;
                letter-spacing: 1.5px;
                background: transparent;
            }}
        """)
        dst_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dst_label.hide()
        # The magenta glow is deliberately NOT attached here - the DST
        # label is empty for ~357 days of the year, so keeping a live
        # QGraphicsDropShadowEffect (plus its backing offscreen buffer)
        # would waste memory for no visible benefit. The effect is
        # attached on demand in update_clocks() the first time the
        # label is shown.
        layout.addWidget(dst_label)

        container.city_label = city_label
        container.time_label = time_label
        container.date_label = date_label
        container.dst_label = dst_label

        return container

    # Dimensions of the right-side button cluster. Two rows of two 24x24
    # square buttons with 4 px gaps. Kept small so the cluster nests
    # inside the right-curve semicircle without swallowing digits.
    BTN_SIZE = 24
    BTN_GAP  = 4

    def create_control_buttons(self):
        """Create the 4 control buttons as direct children of `self` so
        they can be floated over the right curve instead of occupying
        their own layout row. Positioned by _position_control_buttons()."""
        # Shared cyberpunk button style - translucent dark fill, cyan
        # border that brightens on hover.
        cyber_btn_css = """
            QPushButton {
                background: rgba(20, 32, 52, 180);
                color: rgba(190, 240, 255, 240);
                border: 1px solid rgba(0, 229, 255, 140);
                border-radius: 6px;
                font-family: %s;
                font-size: 10pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(0, 60, 90, 220);
                color: rgba(230, 250, 255, 255);
                border: 1px solid rgba(0, 245, 255, 230);
            }
            QPushButton:pressed { background: rgba(0, 100, 140, 230); }
            QPushButton:disabled {
                color: rgba(120, 170, 200, 80);
                border: 1px solid rgba(0, 229, 255, 50);
            }
        """ % FALLBACK_STACK

        close_css = f"""
            QPushButton {{
                background: rgba(40, 12, 20, 200);
                color: rgba(255, 190, 200, 245);
                border: 1px solid rgba(255, 80, 110, 200);
                border-radius: 6px;
                font-family: {FALLBACK_STACK};
                font-size: 10pt;
                font-weight: 800;
            }}
            QPushButton:hover {{
                background: rgba(120, 20, 40, 230);
                color: rgba(255, 230, 240, 255);
                border: 1px solid rgba(255, 100, 140, 255);
            }}
            QPushButton:pressed {{ background: rgba(180, 30, 50, 255); }}
        """

        def _mk(text, css, slot, tooltip):
            b = QPushButton(text, self)
            b.setFixedSize(self.BTN_SIZE, self.BTN_SIZE)
            b.setStyleSheet(css)
            b.clicked.connect(slot)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if tooltip:
                b.setToolTip(tooltip)
            return b

        self.minus_btn    = _mk("\u2212", cyber_btn_css, self.remove_city,   "Remove last city")
        self.plus_btn     = _mk("+",      cyber_btn_css, self.add_city,      "Add a city (max 6)")
        self.settings_btn = _mk("\u2699", cyber_btn_css, self.show_settings, "Settings")
        self.close_btn    = _mk("\u2715", close_css,     self.close_app,     "Close")

        self._refresh_count_buttons()
        self._position_control_buttons()

    def _position_control_buttons(self):
        """Place the 2x2 cluster against the right-side curve, vertically
        centered. Called on init and on every resize."""
        if not hasattr(self, "minus_btn"):
            return
        s, g = self.BTN_SIZE, self.BTN_GAP
        cluster_w = 2 * s + g
        cluster_h = 2 * s + g
        # Inset from the right edge. For a 110-tall pill the right
        # semicircle has radius 55; keep the cluster clear of the curve.
        right_inset = 32
        x0 = self.width() - cluster_w - right_inset
        y0 = (self.height() - cluster_h) // 2
        # Layout:
        #   -  +
        #   |@|  X
        self.minus_btn.move(x0,              y0)
        self.plus_btn.move (x0 + s + g,      y0)
        self.settings_btn.move(x0,           y0 + s + g)
        self.close_btn.move(x0 + s + g,      y0 + s + g)
        for b in (self.minus_btn, self.plus_btn, self.settings_btn, self.close_btn):
            b.raise_()

    def _render_background_to_pixmap(self, size):
        """Build the pill's static background into a transparent QPixmap
        so paintEvent can just blit it on every tick."""
        pm = QPixmap(size)
        pm.fill(QColor(0, 0, 0, 0))  # fully transparent - the pill shape clips it
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()
        radius = self.height() // 2
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(rect), radius, radius)
        painter.setClipPath(clip)

        # Layer 1: outer cyan glow halo - 5 rings is visually
        # indistinguishable from the old 10 but allocates half the paths
        for i in (9, 7, 5, 3, 1):
            halo = QColor(0, 229, 255, max(0, int(12 - i * 1.1)))
            r = rect.adjusted(i, i, -i, -i)
            p = QPainterPath()
            p.addRoundedRect(QRectF(r), radius - i, radius - i)
            painter.fillPath(p, halo)

        # Layer 2: main body - dark slate gradient, ~55% translucent
        main_rect = rect.adjusted(8, 8, -8, -8)
        gradient = QLinearGradient(
            QPointF(main_rect.center().x(), main_rect.top()),
            QPointF(main_rect.center().x(), main_rect.bottom()),
        )
        gradient.setColorAt(0.0, QColor(14, 22, 36, 135))
        gradient.setColorAt(0.5, QColor(20, 32, 52, 150))
        gradient.setColorAt(1.0, QColor(10, 16, 28, 140))
        main_path = QPainterPath()
        main_path.addRoundedRect(QRectF(main_rect), radius - 8, radius - 8)
        painter.fillPath(main_path, gradient)

        # Layer 3: cyan neon rim
        painter.setPen(QPen(QColor(0, 229, 255, 150), 1.4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(main_path)

        # Layer 4: inner soft cyan halo
        painter.setPen(QPen(QColor(0, 229, 255, 55), 2.5))
        inner_path = QPainterPath()
        inner_rect = main_rect.adjusted(3, 3, -3, -3)
        inner_path.addRoundedRect(QRectF(inner_rect), radius - 11, radius - 11)
        painter.drawPath(inner_path)

        # Layer 5: top scanline highlight
        scan_rect = QRectF(main_rect.x() + 12, main_rect.y() + 10,
                           main_rect.width() - 24, 32)
        scan = QLinearGradient(
            QPointF(scan_rect.center().x(), scan_rect.top()),
            QPointF(scan_rect.center().x(), scan_rect.bottom()),
        )
        scan.setColorAt(0.0, QColor(120, 240, 255, 70))
        scan.setColorAt(1.0, QColor(120, 240, 255, 0))
        scan_path = QPainterPath()
        scan_path.addRoundedRect(scan_rect, radius - 20, radius - 20)
        painter.fillPath(scan_path, scan)
        painter.end()
        return pm

    def paintEvent(self, event):
        """Blit the pre-rendered static pill background.  On first paint
        (or any resize - the widget is fixed-size, so this happens once
        per instance) we build the pixmap once; every subsequent frame
        is a single fast drawPixmap call with no QPainterPath or
        QGradient allocations.  The cache is per-instance so closing
        one widget doesn't invalidate another's pixmap."""
        key = (self.width(), self.height())
        if getattr(self, "_bg_cache_key", None) != key:
            self._bg_cache_pm  = self._render_background_to_pixmap(self.size())
            self._bg_cache_key = key
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._bg_cache_pm)

    def resizeEvent(self, event):
        """Apply mask on resize to clip to pill shape, and reposition the
        floating right-side button cluster."""
        super().resizeEvent(event)
        radius = self.height() // 2
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        self._position_control_buttons()

    def update_clocks(self):
        """Update clocks"""
        clock_data = self.clock_manager.get_all_clock_data(self.cities)
        for i, data in enumerate(clock_data):
            if i < len(self.clock_labels):
                slot = self.clock_labels[i]
                slot.city_label.setText(data["city"].upper())
                slot.time_label.setText(data["time"])
                slot.date_label.setText(data["date"])
                alert = data.get("dst_alert", "")
                if alert:
                    # Swap the date out for the alert so we stay in the
                    # same vertical footprint - adding a 5th line would
                    # spill below the pill's rounded bottom.
                    slot.date_label.hide()
                    slot.dst_label.setText(alert)
                    # Lazily attach the magenta glow the first time this
                    # label becomes visible; keeps the effect (and its
                    # offscreen buffer) out of memory for the 50 weeks
                    # a year no alert is active.
                    if slot.dst_label.graphicsEffect() is None:
                        glow = QGraphicsDropShadowEffect(slot.dst_label)
                        glow.setBlurRadius(14)
                        glow.setOffset(0, 0)
                        glow.setColor(QColor(255, 90, 190, 180))
                        slot.dst_label.setGraphicsEffect(glow)
                    slot.dst_label.show()
                else:
                    slot.dst_label.hide()
                    slot.date_label.show()

    def _refresh_count_buttons(self):
        """Enable/disable +/- buttons at the supported limits."""
        n = len(self.cities)
        if hasattr(self, "minus_btn"):
            self.minus_btn.setEnabled(n > MIN_CITIES)
        if hasattr(self, "plus_btn"):
            self.plus_btn.setEnabled(n < MAX_CITIES)

    def add_city(self):
        """Append a new city slot (max MAX_CITIES). Opens the picker
        immediately so the user doesn't end up with a duplicate clock."""
        if len(self.cities) >= MAX_CITIES:
            return
        # Seed with a sensible default (UTC) so the slot has SOMETHING
        # if the user dismisses the picker.
        self.cities.append({"name": "UTC", "timezone": "UTC"})
        self.config["cities"] = self.cities
        self.config_manager.save_config(self.config)
        self._rebuild_clock_row()
        self._refresh_count_buttons()
        self.update_clocks()
        # Prompt the user to pick a real city for the new slot
        self.change_city(len(self.cities) - 1)

    def remove_city(self):
        """Remove the last city slot (min MIN_CITIES)."""
        if len(self.cities) <= MIN_CITIES:
            return
        self.cities.pop()
        self.config["cities"] = self.cities
        self.config_manager.save_config(self.config)
        self._rebuild_clock_row()
        self._refresh_count_buttons()
        self.update_clocks()

    def change_city(self, index):
        """Change city"""
        # Temporarily to front
        self.setWindowFlag(Qt.WindowType.WindowStaysOnBottomHint, False)
        self.show()

        selector = CitySelectorQt(self)
        city, timezone = selector.show_dialog()

        # Back to background
        self.setWindowFlag(Qt.WindowType.WindowStaysOnBottomHint, True)
        self.show()

        if city and timezone:
            self.cities[index] = {"name": city, "timezone": timezone}
            self.config["cities"] = self.cities
            self.config_manager.save_config(self.config)
            self.update_clocks()

    def show_settings(self):
        """Settings"""
        pass  # TODO: Add settings dialog

    def show_controls(self):
        """Show buttons"""
        if not self.controls_visible:
            self.minus_btn.show()
            self.plus_btn.show()
            self.settings_btn.show()
            self.close_btn.show()
            self.controls_visible = True

    def hide_controls(self):
        """Hide buttons"""
        if hasattr(self, "minus_btn"):
            self.minus_btn.hide()
            self.plus_btn.hide()
        self.settings_btn.hide()
        self.close_btn.hide()
        self.controls_visible = False

    def enterEvent(self, event):
        """Mouse enter"""
        self.show_controls()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave"""
        self.hide_controls()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """Mouse move"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        """Mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self.config["window_position"]["x"] = self.x()
            self.config["window_position"]["y"] = self.y()
            self.config_manager.save_config(self.config)

    def close_app(self):
        """Close"""
        self.config["window_position"]["x"] = self.x()
        self.config["window_position"]["y"] = self.y()
        self.config_manager.save_config(self.config)
        QApplication.quit()


def run_qt_widget():
    """Run widget"""
    app = QApplication(sys.argv)
    # Ensure app stays in background
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus)
    widget = ClockWidgetQt()
    widget.show()
    # Force to background after show
    widget.lower()
    sys.exit(app.exec())
