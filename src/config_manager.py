import json
import os

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.default_config = {
            "cities": [
                {"name": "New York", "timezone": "America/New_York"},
                {"name": "London", "timezone": "Europe/London"},
                {"name": "Tokyo", "timezone": "Asia/Tokyo"},
                {"name": "Sydney", "timezone": "Australia/Sydney"}
            ],
            "window_position": {"x": None, "y": None},
            "opacity": 0.92,  # Higher transparency for liquid drop effect
            "always_on_top": False  # Stay in background, don't interrupt other apps
        }

    def load_config(self):
        """Load configuration from file, or return defaults if file doesn't exist."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.default_config, **config}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        return self.default_config.copy()

    def save_config(self, config):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get_default_cities(self):
        """Return the default list of cities."""
        return self.default_config["cities"].copy()
