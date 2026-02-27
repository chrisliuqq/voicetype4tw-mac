"""
獨立啟動設定視窗（子程序用）。
由 menu_bar.py 的 subprocess.Popen 呼叫，
避免 rumps run loop 與 Tkinter mainloop 衝突。
"""
import subprocess
import sys
import os
from pathlib import Path


def open_settings_window():
    script = Path(__file__).parent / "ui" / "settings_window.py"
    python = sys.executable
    env = os.environ.copy()

    project_root = str(Path(__file__).parent)
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{project_root}:{existing_path}" if existing_path else project_root

    # 打開視窗
    subprocess.Popen([python, str(script)], env=env, cwd=project_root)


if __name__ == "__main__":
    open_settings_window()
