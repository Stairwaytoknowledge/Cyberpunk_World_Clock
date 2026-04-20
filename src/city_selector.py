import tkinter as tk
from tkinter import ttk
import json
import os

class CitySelector:
    def __init__(self, parent, cities_file="assets/cities.json"):
        self.parent = parent
        self.selected_city = None
        self.selected_timezone = None
        self.cities_file = cities_file

        # Load cities from JSON
        self.cities_data = self.load_cities()

    def load_cities(self):
        """Load cities from JSON file."""
        try:
            with open(self.cities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cities: {e}")
            return {}

    def show_dialog(self):
        """Show the city selector dialog and return selected city."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select City")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)

        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (400 // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (500 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Search frame
        search_frame = tk.Frame(self.dialog, bg="#F0F0F0")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(search_frame, text="Search:", bg="#F0F0F0", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_cities)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.focus()

        # Listbox frame with scrollbar
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.city_listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            activestyle='dotbox',
            selectmode=tk.SINGLE
        )
        self.city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.city_listbox.yview)

        # Populate listbox
        self.populate_listbox()

        # Bind double-click to select
        self.city_listbox.bind('<Double-Button-1>', lambda e: self.select_city())

        # Buttons frame
        button_frame = tk.Frame(self.dialog, bg="#F0F0F0")
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=self.select_city,
            font=("Segoe UI", 10),
            width=10,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        ok_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            font=("Segoe UI", 10),
            width=10,
            cursor="hand2"
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # Wait for dialog to close
        self.parent.wait_window(self.dialog)

        return self.selected_city, self.selected_timezone

    def populate_listbox(self, filter_text=""):
        """Populate the listbox with cities, optionally filtered."""
        self.city_listbox.delete(0, tk.END)

        # Sort cities alphabetically
        sorted_cities = sorted(self.cities_data.items())

        for city, timezone in sorted_cities:
            if filter_text.lower() in city.lower():
                display_text = f"{city} ({timezone})"
                self.city_listbox.insert(tk.END, display_text)

    def filter_cities(self, *args):
        """Filter cities based on search input."""
        filter_text = self.search_var.get()
        self.populate_listbox(filter_text)

    def select_city(self):
        """Handle city selection."""
        selection = self.city_listbox.curselection()
        if selection:
            selected_text = self.city_listbox.get(selection[0])
            # Extract city name (before the parenthesis)
            city_name = selected_text.split(" (")[0]
            self.selected_city = city_name
            self.selected_timezone = self.cities_data[city_name]
            self.dialog.destroy()

    def cancel(self):
        """Cancel the dialog."""
        self.selected_city = None
        self.selected_timezone = None
        self.dialog.destroy()
