import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "app": {
        "name": "AI File Organizer",
        "version": "1.0.0",
        "theme": "light"
    },
    "paths": {
        "default_source": str(Path.home() / "Downloads"),
        "default_dest": str(Path.home() / "OrganizedFiles")
    },
    "ai": {
        "enable_suggestions": True,
        "categorization_model": "default",
        "api_key": ""
    },
    "behavior": {
        "keep_originals": False  # New: Default to move files (not keep copies)
    },
    "file_types": {
        "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "audio": [".mp3", ".wav", ".ogg", ".flac"],
        "videos": [".mp4", ".avi", ".mov", ".mkv"],
        "archives": [".zip", ".rar", ".7z", ".tar"],
        "code": [".py", ".js", ".html", ".css", ".java", ".cpp"]
    }
}

def load_config():
    """
    Load configuration from file or return defaults
    Returns merged configuration (user settings + defaults)
    """
    config_path = Path.home() / ".aifileorganizer" / "config.json"
    
    if not config_path.exists():
        os.makedirs(config_path.parent, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    
    with open(config_path, 'r') as f:
        try:
            user_config = json.load(f)
            # Deep merge with defaults
            config = _deep_merge(DEFAULT_CONFIG, user_config)
            return config
        except json.JSONDecodeError:
            return DEFAULT_CONFIG

def save_config(config):
    """
    Save configuration to file
    """
    config_path = Path.home() / ".aifileorganizer" / "config.json"
    os.makedirs(config_path.parent, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def _deep_merge(default, user):
    """
    Recursively merge dictionaries, preserving nested structures
    """
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def reset_to_defaults():
    """
    Reset configuration to default values
    Returns the default configuration
    """
    config_path = Path.home() / ".aifileorganizer" / "config.json"
    if config_path.exists():
        os.remove(config_path)
    return load_config()