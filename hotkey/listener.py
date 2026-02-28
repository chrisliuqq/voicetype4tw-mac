import threading
from typing import Callable, Optional, Dict
from pynput import keyboard


def key_to_str(key) -> str:
    """Convert a pynput key object to a string for storage."""
    if isinstance(key, keyboard.Key):
        return key.name
    if hasattr(key, 'char') and key.char:
        return key.char
    if hasattr(key, 'vk'):
        return f"vk_{key.vk}"
    return str(key)


def str_to_key(key_str: str):
    """Convert a stored string back to a pynput key object."""
    if not key_str:
        return None
    # Try keyboard.Key names (e.g., 'alt_r', 'f13')
    if hasattr(keyboard.Key, key_str):
        return getattr(keyboard.Key, key_str)
    # Try virtual key codes
    if key_str.startswith("vk_"):
        try:
            return keyboard.KeyCode.from_vk(int(key_str[3:]))
        except:
            pass
    # Default to single character
    return keyboard.KeyCode.from_char(key_str)


class HotkeyListener:
    """
    Listens for multiple global hotkeys and fires mode-specific callbacks.
    - hotkey_ptt: Hold to record
    - hotkey_toggle: Click to start, click to stop
    - hotkey_llm: Hold to record + Force LLM
    """

    def __init__(
        self,
        hotkey_configs: Dict[str, str],  # {"ptt": "alt_r", "toggle": "f13", "llm": "f14"}
        on_start: Callable[[str], None],  # mode -> action
        on_stop: Callable[[str], None],
    ):
        self.configs = hotkey_configs
        self.on_start = on_start
        self.on_stop = on_stop
        
        self._active_mode: Optional[str] = None
        self._listener: Optional[keyboard.Listener] = None

    def _refresh_key_map(self):
        self.key_map = {}
        for mode, key_str in self.configs.items():
            key_obj = str_to_key(key_str)
            if key_obj:
                self.key_map[key_obj] = mode

    def start(self) -> None:
        """Start the global keyboard listener in a background thread."""
        self._refresh_key_map()
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key) -> None:
        mode = self.key_map.get(key)
        if not mode:
            return

        if mode == "toggle":
            if self._active_mode is None:
                self._active_mode = "toggle"
                threading.Thread(target=self.on_start, args=("toggle",), daemon=True).start()
            elif self._active_mode == "toggle":
                self._active_mode = None
                threading.Thread(target=self.on_stop, args=("toggle",), daemon=True).start()
        else:
            # ptt or llm (holding modes)
            if self._active_mode is None:
                self._active_mode = mode
                threading.Thread(target=self.on_start, args=(mode,), daemon=True).start()

    def _on_release(self, key) -> None:
        mode = self.key_map.get(key)
        if not mode or mode == "toggle":
            return

        if self._active_mode == mode:
            self._active_mode = None
            threading.Thread(target=self.on_stop, args=(mode,), daemon=True).start()
