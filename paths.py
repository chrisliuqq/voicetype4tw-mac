import os
from pathlib import Path

# Get user home directory and create standard app support directory
HOME = Path.home()
import platform
if platform.system() == "Windows":
    APP_DATA_DIR = Path(os.environ.get("APPDATA", HOME)) / "VoiceType4TW"
else:
    APP_DATA_DIR = HOME / "Library" / "Application Support" / "VoiceType4TW"

# Ensure the directory exists
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APP_DATA_DIR / "config.json"
SOUL_PATH = APP_DATA_DIR / "soul.md"

import shutil
import sys

def get_data_dir(subfolder: str) -> Path:
    d = APP_DATA_DIR / subfolder
    d.mkdir(parents=True, exist_ok=True)
    return d

# Initial data migration: if the user files don't exist yet, copy them from the app bundle/installation dir
def _initialize_data():
    # In py2app, resources are in os.environ['RESOURCEPATH']
    res_path = os.environ.get("RESOURCEPATH")
    base_dir = Path(res_path) if res_path else Path(__file__).parent
    
    # Defaults
    for filename in ["config.json", "soul.md"]:
        bundled_file = base_dir / filename
        user_file = APP_DATA_DIR / filename
        if bundled_file.exists() and not user_file.exists():
            try:
                shutil.copy2(bundled_file, user_file)
            except Exception:
                pass
                
_initialize_data()
