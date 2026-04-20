import tkinter as tk
from tkinter import font
from src.clock_manager import ClockManager
from src.config_manager import ConfigManager
from src.city_selector import CitySelector

class ClockWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("World Clock")

        # Initialize managers
        self.config_manager = ConfigManager()
        self.clock_manager = ClockManager()

        # Load configuration
        self.config = self.config_manager.load_config()
        self.cities = self.config["cities"]

        # Hover state for showing controls
        self.controls_visible = False

        # Window setup
        self.setup_window()

        # Create UI elements
        self.create_ui()

        # Dragging support
        self.drag_data = {"x": 0, "y": 0, "dragging": False}

        # Start clock update
        self.update_clocks()

    def setup_window(self):
        """Configure the main window properties."""
        # Remove window decorations
        self.root.overrideredirect(True)

        # Set window size - Horizontal layout with extra padding for shadow effect
        window_width = 920
        window_height = 180
        self.window_width = window_width
        self.window_height = window_height
        self.root.geometry(f"{window_width}x{window_height}")

        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position window
        x = self.config["window_position"]["x"]
        y = self.config["window_position"]["y"]

        if x is None or y is None:
            # Default position: top-center of screen
            x = (screen_width - window_width) // 2
            y = 50

        self.root.geometry(f"+{x}+{y}")

        # IMPORTANT: Remove always-on-top to fix the bug
        # Widget should stay in background, not interrupt other apps
        self.root.attributes('-alpha', 0.92)  # Higher transparency for liquid drop effect
        self.root.attributes('-topmost', False)  # Stay in background

        # Apple Watch Liquid Drop colors - softer, more dynamic
        self.bg_color = "#EBF5FB"  # Very light blue background
        self.glass_color = "#F7FBFF"  # Almost white with hint of blue
        self.shadow_color = "#D4E6F1"  # Subtle shadow color
        self.border_color = "#A8D5E2"  # Soft blue border
        self.root.configure(bg=self.bg_color)

    def create_ui(self):
        """Create all UI elements with Apple Watch Liquid Drop design."""
        # Create canvas for custom drawing
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_width,
            height=self.window_height,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Apple Watch Liquid Drop - very rounded, pill-shaped
        padding = 10  # Padding for shadow effect
        corner_radius = 80  # MUCH larger radius for dramatic liquid drop effect

        # Layer 1: Outer shadow (for depth)
        self.shadow_rect = self.create_rounded_rectangle(
            padding + 3, padding + 3,
            self.window_width - padding + 3,
            self.window_height - padding + 3,
            corner_radius,
            fill=self.shadow_color,
            outline="",
            width=0
        )

        # Layer 2: Main liquid drop shape with subtle gradient border
        self.outer_rect = self.create_rounded_rectangle(
            padding + 1, padding + 1,
            self.window_width - padding + 1,
            self.window_height - padding + 1,
            corner_radius,
            fill=self.border_color,
            outline="",
            width=0
        )

        # Layer 3: Inner glass surface
        self.main_rect = self.create_rounded_rectangle(
            padding + 2, padding + 2,
            self.window_width - padding - 2,
            self.window_height - padding - 2,
            corner_radius - 2,
            fill=self.glass_color,
            outline="",
            width=0
        )

        # Layer 4: Highlight effect (top of bubble)
        self.highlight_rect = self.create_rounded_rectangle(
            padding + 4, padding + 4,
            self.window_width - padding - 4,
            padding + 40,
            corner_radius - 4,
            fill="#FFFFFF",
            outline="",
            width=0,
            stipple="gray25"  # Creates semi-transparent effect
        )

        # Main container frame on top of canvas
        self.main_frame = tk.Frame(self.canvas, bg=self.glass_color)
        self.canvas.create_window(
            self.window_width // 2,
            self.window_height // 2,
            window=self.main_frame
        )

        # Bind hover events to show/hide controls
        self.root.bind('<Enter>', self.show_controls)
        self.root.bind('<Leave>', self.hide_controls)
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drag)

        # Clock displays frame - HORIZONTAL layout
        self.clocks_frame = tk.Frame(self.main_frame, bg=self.glass_color)
        self.clocks_frame.pack(padx=25, pady=18)

        # Create 4 clock displays in HORIZONTAL arrangement
        self.clock_labels = []
        for i in range(4):
            clock_display = self.create_clock_display(i)
            self.clock_labels.append(clock_display)

        # Control buttons frame (hidden by default)
        self.create_control_buttons()

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle on canvas."""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def create_clock_display(self, index):
        """Create a single clock display in horizontal layout."""
        # Container for one clock - pack SIDE by SIDE
        clock_container = tk.Frame(self.clocks_frame, bg=self.glass_color)
        clock_container.pack(side=tk.LEFT, padx=15, pady=5)

        # Inner frame for vertical stacking
        inner_frame = tk.Frame(clock_container, bg=self.glass_color)
        inner_frame.pack()

        # City name (clickable) - on TOP
        city_label = tk.Label(
            inner_frame,
            text="Loading...",
            font=("Segoe UI", 9),
            bg=self.glass_color,
            fg="#5B7C8D",
            cursor="hand2",
            anchor="center"
        )
        city_label.pack(side=tk.TOP, pady=(0, 2))

        # Bind click event to change city
        city_label.bind('<Button-1>', lambda e, idx=index: self.change_city(idx))
        city_label.bind('<Enter>', lambda e: city_label.config(fg="#007AFF"))  # Apple blue
        city_label.bind('<Leave>', lambda e: city_label.config(fg="#5B7C8D"))

        # Time label - MIDDLE (larger)
        time_label = tk.Label(
            inner_frame,
            text="00:00:00",
            font=("SF Pro Display", 22, "bold") if self.has_sf_font() else ("Segoe UI", 22, "bold"),
            bg=self.glass_color,
            fg="#1D1D1F",
            anchor="center"
        )
        time_label.pack(side=tk.TOP, pady=2)

        # Date label - BOTTOM
        date_label = tk.Label(
            inner_frame,
            text="00-00",
            font=("SF Pro Display", 9) if self.has_sf_font() else ("Segoe UI", 9),
            bg=self.glass_color,
            fg="#5B7C8D",
            anchor="center"
        )
        date_label.pack(side=tk.TOP, pady=(2, 0))

        return {
            "city": city_label,
            "time": time_label,
            "date": date_label,
            "container": clock_container
        }

    def has_sf_font(self):
        """Check if SF Pro Display font is available."""
        try:
            test_font = font.Font(family="SF Pro Display", size=10)
            return True
        except:
            return False

    def create_control_buttons(self):
        """Create control buttons (Settings, Close) - hidden by default."""
        self.button_frame = tk.Frame(self.main_frame, bg=self.glass_color)
        # Don't pack yet - will show on hover

        # Apple-style minimalist buttons
        # Close button
        self.close_btn = tk.Button(
            self.button_frame,
            text="✕",
            command=self.close_app,
            font=("Segoe UI", 11, "bold"),
            bg="#FF3B30",  # Apple red
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            width=3,
            height=1,
            borderwidth=0,
            highlightthickness=0
        )
        self.close_btn.pack(side=tk.RIGHT, padx=3)

        # Settings button
        self.settings_btn = tk.Button(
            self.button_frame,
            text="⚙",
            command=self.show_settings,
            font=("Segoe UI", 11),
            bg="#007AFF",  # Apple blue
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            width=3,
            height=1,
            borderwidth=0,
            highlightthickness=0
        )
        self.settings_btn.pack(side=tk.RIGHT, padx=3)

    def show_controls(self, event=None):
        """Show control buttons on hover."""
        if not self.controls_visible:
            self.button_frame.pack(side=tk.BOTTOM, pady=(5, 5))
            self.controls_visible = True

    def hide_controls(self, event=None):
        """Hide control buttons when not hovering."""
        if self.controls_visible:
            self.button_frame.pack_forget()
            self.controls_visible = False

    def update_clocks(self):
        """Update all clock displays."""
        clock_data = self.clock_manager.get_all_clock_data(self.cities)

        for i, data in enumerate(clock_data):
            if i < len(self.clock_labels):
                self.clock_labels[i]["city"].config(text=data["city"])
                self.clock_labels[i]["time"].config(text=data["time"])
                self.clock_labels[i]["date"].config(text=data["date"])

        # Schedule next update in 1 second
        self.root.after(1000, self.update_clocks)

    def change_city(self, index):
        """Open dialog to change city at given index."""
        # Temporarily bring window to front for dialog
        self.root.attributes('-topmost', True)
        selector = CitySelector(self.root)
        city, timezone = selector.show_dialog()
        # Return to background
        self.root.attributes('-topmost', False)

        if city and timezone:
            self.cities[index] = {"name": city, "timezone": timezone}
            self.config["cities"] = self.cities
            self.config_manager.save_config(self.config)
            # Update immediately
            self.update_clocks()

    def show_settings(self):
        """Show settings dialog."""
        # Temporarily bring window to front for dialog
        self.root.attributes('-topmost', True)

        # Simple dialog to inform user
        info_window = tk.Toplevel(self.root)
        info_window.title("Settings")
        info_window.geometry("320x170")
        info_window.resizable(False, False)
        info_window.transient(self.root)
        info_window.grab_set()
        info_window.configure(bg="#F5F5F7")

        # Center the dialog
        info_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (320 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (170 // 2)
        info_window.geometry(f"+{x}+{y}")

        tk.Label(
            info_window,
            text="World Clock Settings",
            font=("Segoe UI", 13, "bold"),
            bg="#F5F5F7",
            fg="#1D1D1F",
            pady=20
        ).pack()

        tk.Label(
            info_window,
            text="Click on any city name to change it.\n\nThe widget stays in the background\nso it won't interrupt your work.",
            font=("Segoe UI", 10),
            bg="#F5F5F7",
            fg="#5B7C8D",
            justify=tk.CENTER
        ).pack()

        tk.Button(
            info_window,
            text="OK",
            command=lambda: [info_window.destroy(), self.root.attributes('-topmost', False)],
            font=("Segoe UI", 10),
            width=12,
            bg="#007AFF",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            borderwidth=0
        ).pack(pady=20)

    def start_drag(self, event):
        """Start dragging the window."""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["dragging"] = True

    def on_drag(self, event):
        """Handle window dragging."""
        if self.drag_data["dragging"]:
            # Calculate delta
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            # Move window
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        """Stop dragging and save position."""
        self.drag_data["dragging"] = False

        # Save window position
        self.config["window_position"]["x"] = self.root.winfo_x()
        self.config["window_position"]["y"] = self.root.winfo_y()
        self.config_manager.save_config(self.config)

    def close_app(self):
        """Close the application."""
        # Save final position
        self.config["window_position"]["x"] = self.root.winfo_x()
        self.config["window_position"]["y"] = self.root.winfo_y()
        self.config_manager.save_config(self.config)

        # Destroy window
        self.root.destroy()

    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
