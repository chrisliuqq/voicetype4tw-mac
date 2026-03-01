import threading
import time
import platform
from typing import Callable, Optional, Dict

IS_WINDOWS = platform.system() == "Windows"

def key_to_str(key) -> str:
    return str(key).lower().replace("key.", "")

def str_to_key(key_str: str):
    return key_str

# Mapping common key names to macOS virtual key codes
KEY_NAME_TO_CODE = {
    "alt": 58, "alt_r": 61,
    "cmd": 55, "cmd_r": 54,
    "ctrl": 59, "ctrl_r": 62,
    "shift": 56, "shift_r": 60,
    "f1": 122, "f2": 120, "f3": 99, "f4": 118, "f5": 96, "f6": 97,
    "f7": 98, "f8": 100, "f9": 101, "f10": 109, "f11": 103, "f12": 111,
    "f13": 105, "f14": 107, "f15": 113, "f16": 106,
    "space": 49, "enter": 36, "tab": 48, "esc": 53,
}

class HotkeyListener:
    def __init__(
        self,
        hotkey_configs: Dict[str, str],
        on_start: Callable[[str], None],
        on_stop: Callable[[str], None],
    ):
        self.configs = hotkey_configs
        self.on_start = on_start
        self.on_stop = on_stop
        
        self._active_mode: Optional[str] = None
        self._loop_thread: Optional[threading.Thread] = None
        
        # macOS specific
        self._run_loop = None
        self._tap = None
        self._key_states: Dict[int, bool] = {}
        
        # Windows specific
        self._win_listener = None

        self.key_map: Dict[int, str] = {}
        if not IS_WINDOWS:
            self._refresh_key_map_macos()

    def _refresh_key_map_macos(self):
        self.key_map = {}
        for mode, name in self.configs.items():
            name = name.lower()
            if name in KEY_NAME_TO_CODE:
                self.key_map[KEY_NAME_TO_CODE[name]] = mode

    def start(self) -> None:
        if IS_WINDOWS:
            self._start_windows()
        else:
            self._start_macos()

    def stop(self) -> None:
        if IS_WINDOWS:
            if self._win_listener:
                self._win_listener.stop()
        else:
            if self._run_loop:
                from Foundation import CFRunLoopStop
                CFRunLoopStop(self._run_loop)
            if self._loop_thread:
                self._loop_thread.join(timeout=0.5)
        self._loop_thread = None

    def _start_windows(self):
        try:
            from pynput import keyboard
            
            def on_press(key):
                k_str = key_to_str(key)
                for mode, cfg_key in self.configs.items():
                    if cfg_key.lower() == k_str:
                        self._handle_press(mode)

            def on_release(key):
                k_str = key_to_str(key)
                for mode, cfg_key in self.configs.items():
                    if cfg_key.lower() == k_str:
                        self._handle_release(mode)

            self._win_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self._win_listener.start()
            print("[hotkey] Windows listener started.")
        except ImportError:
            print("[hotkey] Error: pynput not found on Windows.")

    def _start_macos(self):
        if self._loop_thread and self._loop_thread.is_alive():
            return
        self._loop_thread = threading.Thread(target=self._run_macos, daemon=True)
        self._loop_thread.start()

    def _run_macos(self):
        import Quartz
        from Foundation import CFRunLoopGetCurrent, kCFRunLoopDefaultMode, CFRunLoopRunInMode
        self._run_loop = CFRunLoopGetCurrent()
        event_mask = (1 << Quartz.kCGEventKeyDown) | (1 << Quartz.kCGEventKeyUp) | (1 << Quartz.kCGEventFlagsChanged)
        self._tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionListenOnly, event_mask, self._macos_callback, None
        )
        if not self._tap:
            print("[hotkey] ERR: Failed to create macOS event tap.")
            return
        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self._tap, 0)
        Quartz.CFRunLoopAddSource(self._run_loop, run_loop_source, kCFRunLoopDefaultMode)
        Quartz.CGEventTapEnable(self._tap, True)
        CFRunLoopRunInMode(kCFRunLoopDefaultMode, 10e10, False)

    def _macos_callback(self, proxy, type, event, refcon):
        import Quartz
        keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
        mode = self.key_map.get(keycode)
        if not mode: return event

        if type == Quartz.kCGEventKeyDown:
            if not self._key_states.get(keycode, False):
                self._key_states[keycode] = True
                self._handle_press(mode)
        elif type == Quartz.kCGEventKeyUp:
            if self._key_states.get(keycode, False):
                self._key_states[keycode] = False
                self._handle_release(mode)
        elif type == Quartz.kCGEventFlagsChanged:
            flags = Quartz.CGEventGetFlags(event)
            is_pressed = False
            if keycode in [58, 61]: is_pressed = bool(flags & Quartz.kCGEventFlagMaskAlternate)
            elif keycode in [56, 60]: is_pressed = bool(flags & Quartz.kCGEventFlagMaskShift)
            elif keycode in [59, 62]: is_pressed = bool(flags & Quartz.kCGEventFlagMaskControl)
            elif keycode in [55, 54]: is_pressed = bool(flags & Quartz.kCGEventFlagMaskCommand)
            
            was_pressed = self._key_states.get(keycode, False)
            if is_pressed and not was_pressed:
                self._key_states[keycode] = True
                self._handle_press(mode)
            elif not is_pressed and was_pressed:
                self._key_states[keycode] = False
                self._handle_release(mode)
        return event

    def _handle_press(self, mode: str):
        if mode == "toggle":
            if self._active_mode is None:
                self._active_mode = "toggle"
                threading.Thread(target=self.on_start, args=("toggle",), daemon=True).start()
            elif self._active_mode == "toggle":
                self._active_mode = None
                threading.Thread(target=self.on_stop, args=("toggle",), daemon=True).start()
        elif self._active_mode is None:
            self._active_mode = mode
            threading.Thread(target=self.on_start, args=(mode,), daemon=True).start()

    def _handle_release(self, mode: str):
        if mode == "toggle": return
        if self._active_mode == mode:
            self._active_mode = None
            threading.Thread(target=self.on_stop, args=(mode,), daemon=True).start()

