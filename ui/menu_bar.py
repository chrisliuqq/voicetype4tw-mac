"""
macOS Menu Bar icon using rumps.
Shows app status and provides quick actions.
"""
import rumps
from typing import Callable


class VoiceTypeMenuBar(rumps.App):
    def __init__(self, config: dict, on_quit: Callable, on_toggle_llm: Callable,
                 on_set_translation: Callable, on_config_saved: Callable = None):
        super().__init__("VoiceType4TW-Mac", quit_button=None)
        self.config = config
        self.on_quit = on_quit
        self.on_toggle_llm = on_toggle_llm
        self.on_set_translation = on_set_translation
        self.on_config_saved = on_config_saved  # 設定儲存後重載 app

        self._build_menu()
        self._set_idle_icon()

    def _build_menu(self):
        llm_state = "ON" if self.config.get("llm_enabled") else "OFF"
        engine = self.config.get("stt_engine", "local_whisper")
        mode = self.config.get("trigger_mode", "push_to_talk")
        hotkey = self.config.get("hotkey", "right_option")

        self.menu = [
            rumps.MenuItem("VoiceType4TW-Mac", callback=None),
            rumps.MenuItem("關於", callback=self._show_about),
            None,
            rumps.MenuItem(f"STT: {engine}"),
            rumps.MenuItem(f"模式: {mode}"),
            rumps.MenuItem(f"快捷鍵: {hotkey}"),
            None,
            rumps.MenuItem(f"AI 潤飾/翻譯 : {llm_state}", callback=self._toggle_llm),
            ("快速翻譯", [
                rumps.MenuItem("翻譯成 英文", callback=self._translate_en),
                rumps.MenuItem("翻譯成 日文", callback=self._translate_jp),
                rumps.MenuItem("恢復正常模式", callback=self._translate_none),
            ]),
            rumps.MenuItem("⚙️  偏好設定...", callback=self._open_settings),
            None,
            rumps.MenuItem("結束", callback=self._quit),
        ]

    def _toggle_llm(self, sender):
        self.on_toggle_llm()
        enabled = self.config.get("llm_enabled", False)
        sender.title = f"AI 潤飾/翻譯 : {'ON' if enabled else 'OFF'}"

    def _translate_en(self, _):
        self.on_set_translation("英文")

    def _translate_jp(self, _):
        self.on_set_translation("日文")

    def _translate_none(self, _):
        self.on_set_translation(None)

    def _open_settings(self, _):
        import subprocess
        import sys
        import os
        # 用獨立子程序開視窗，避免與 rumps run loop 衝突
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        launcher = os.path.join(script_dir, "open_settings.py")
        subprocess.Popen([sys.executable, launcher], cwd=script_dir)

    def _show_about(self, _):
        from ui.about_window import AboutDialog
        dialog = AboutDialog(is_dark=self.config.get("dark_mode", True)) # Default to dark for about
        dialog.exec()

    def _quit(self, _):
        self.on_quit()
        rumps.quit_application()

    def _set_idle_icon(self):
        self.title = "🎙"

    def set_recording(self):
        self.title = "🔴"

    def set_processing(self):
        self.title = "⏳"

    def set_idle(self):
        self.title = "🎙"
