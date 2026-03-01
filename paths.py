import os
from pathlib import Path

# Get user home directory and create standard app support directory
HOME = Path.home()
import platform
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    # Windows: %APPDATA%/VoiceType4TW
    APP_DATA_DIR = Path(os.environ.get("APPDATA", str(HOME / "AppData" / "Roaming"))) / "VoiceType4TW"
else:
    # macOS: ~/Library/Application Support/VoiceType4TW
    APP_DATA_DIR = HOME / "Library" / "Application Support" / "VoiceType4TW"

# Ensure the directory exists
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APP_DATA_DIR / "config.json"

# v2.5 新版三層式靈魂目錄
SOUL_DIR = APP_DATA_DIR / "soul"
SOUL_BASE_PATH = SOUL_DIR / "base.md"
SOUL_SCENARIO_DIR = SOUL_DIR / "scenario"
SOUL_FORMAT_DIR = SOUL_DIR / "format"
SOUL_TEMPLATE_DIR = SOUL_DIR / "templates"

# 舊版路徑 (用於遷移)
OLD_SOUL_PATH = APP_DATA_DIR / "soul.md"

import shutil
import sys

def get_data_dir(subfolder: str) -> Path:
    d = APP_DATA_DIR / subfolder
    d.mkdir(parents=True, exist_ok=True)
    return d

# Initial data migration
def _initialize_data():
    res_path = os.environ.get("RESOURCEPATH")
    base_dir = Path(res_path) if res_path else Path(__file__).parent
    
    # 建立目錄
    SOUL_DIR.mkdir(parents=True, exist_ok=True)
    SOUL_SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    SOUL_FORMAT_DIR.mkdir(parents=True, exist_ok=True)
    SOUL_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 舊版單一 soul.md 遷移至 soul/base.md
    if OLD_SOUL_PATH.exists() and not SOUL_BASE_PATH.exists():
        try:
            shutil.move(str(OLD_SOUL_PATH), str(SOUL_BASE_PATH))
        except Exception:
            pass

    # 2. 複製內建模板 (情境與格式)
    def sync_defaults(sub_path, dest_dir):
        src_dir = base_dir / sub_path
        if src_dir.exists():
            for f in src_dir.glob("*.md"):
                dest_file = dest_dir / f.name
                # 如果目標不存在，則從 bundle 複製預設值
                # 這樣使用者修改後就不會被覆蓋，但新用戶能拿到最讚的預設集
                if not dest_file.exists():
                    try:
                        shutil.copy2(f, dest_file)
                    except Exception:
                        pass

    sync_defaults("soul/scenario", SOUL_SCENARIO_DIR)
    sync_defaults("soul/format", SOUL_FORMAT_DIR)

    # 3. 如果沒檔案，從 bundle 複製預設值
    for filename in ["config.json"]:
        bundled_file = base_dir / filename
        user_file = APP_DATA_DIR / filename
        if bundled_file.exists() and not user_file.exists():
            try:
                shutil.copy2(bundled_file, user_file)
            except Exception:
                pass
    
    # 複製內建模板 (如果有在 bundle 裡的話)
    # 這裡暫時依賴 main.py 啟動時自動檢查
                
_initialize_data()
