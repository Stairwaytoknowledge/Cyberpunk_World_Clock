import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                              QListWidget, QPushButton, QLabel)
from PyQt6.QtCore import Qt

class CitySelectorQt(QDialog):
    """City selector dialog for PyQt6"""

    def __init__(self, parent=None, cities_file="assets/cities.json"):
        super().__init__(parent)
        self.selected_city = None
        self.selected_timezone = None
        self.cities_file = cities_file

        # Load cities
        self.cities_data = self.load_cities()

        # Setup dialog
        self.setup_ui()

    def load_cities(self):
        """Load cities from JSON file"""
        try:
            with open(self.cities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cities: {e}")
            return {}

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Select City")
        self.setFixedSize(400, 500)
        self.setModal(True)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Search box
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 10pt; color: #2C3E50;")
        layout.addWidget(search_label)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter cities...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #B0D4E3;
                border-radius: 5px;
                font-size: 10pt;
            }
        """)
        self.search_box.textChanged.connect(self.filter_cities)
        layout.addWidget(self.search_box)

        # City list
        self.city_list = QListWidget()
        self.city_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #B0D4E3;
                border-radius: 5px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #E8F4F8;
            }
        """)
        self.city_list.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.city_list)

        # Populate list
        self.populate_list()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #E0E0E0;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(100)
        ok_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        ok_btn.clicked.connect(self.accept_selection)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)

        # Focus search box
        self.search_box.setFocus()

    def populate_list(self, filter_text=""):
        """Populate the city list"""
        self.city_list.clear()

        # Sort cities
        sorted_cities = sorted(self.cities_data.items())

        for city, timezone in sorted_cities:
            if filter_text.lower() in city.lower():
                display_text = f"{city} ({timezone})"
                self.city_list.addItem(display_text)

    def filter_cities(self):
        """Filter cities based on search input"""
        filter_text = self.search_box.text()
        self.populate_list(filter_text)

    def accept_selection(self):
        """Accept the selected city"""
        current_item = self.city_list.currentItem()
        if current_item:
            selected_text = current_item.text()
            # Extract city name (before parenthesis)
            city_name = selected_text.split(" (")[0]
            self.selected_city = city_name
            self.selected_timezone = self.cities_data[city_name]
            self.accept()

    def show_dialog(self):
        """Show the dialog and return selected city"""
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            return self.selected_city, self.selected_timezone
        return None, None
