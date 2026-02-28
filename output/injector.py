import subprocess
import pyperclip
import time


class TextInjector:
    """
    Injects text into the currently focused input field
    by writing to clipboard and simulating Cmd+V.
    """

    def inject(self, text: str) -> None:
        if not text:
            return
        pyperclip.copy(text)
        time.sleep(0.05)  # small delay to ensure clipboard is ready
        self._paste()

    def select_back(self, char_count: int) -> None:
        """往回選取 char_count 個字元（用於背景 LLM 替換）"""
        if char_count <= 0:
            return
        script = f"""
        tell application "System Events"
            repeat {char_count} times
                key code 123 using shift down
            end repeat
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    def _paste(self) -> None:
        script = """
        tell application "System Events"
            keystroke "v" using command down
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)
