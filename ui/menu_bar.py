"""
Cross-platform Menu Bar / System Tray manager.
"""
from typing import Callable, List, Dict
import platform

class VoiceTypeMenuBar:
    """
    Unified Menu Bar logic. This class builds the menu structure 
    and handles state, delegating the actual rendering to TrayManager.
    """
    def __init__(self, config: dict, on_quit: Callable, on_toggle_llm: Callable,
                 on_set_translation: Callable, on_config_saved: Callable = None):
        self.config = config
        self.on_quit = on_quit
        self.on_toggle_llm = on_toggle_llm
        self.on_set_translation = on_set_translation
        self.on_config_saved = on_config_saved
        self.on_set_template = None
        
        self.tray = None # Set by main.py

    def get_menu_items(self) -> List[Dict]:
        """Builds the nested list structure for TrayManager."""
        llm_state = "ON" if self.config.get("llm_enabled") else "OFF"
        action_state = "ON" if self.config.get("action_mode") else "OFF"
        engine = self.config.get("stt_engine", "local_whisper")
        
        from paths import SOUL_SCENARIO_DIR, SOUL_FORMAT_DIR, SOUL_TEMPLATE_DIR
        scenarios = [f.stem for f in SOUL_SCENARIO_DIR.glob("*.md")] if SOUL_SCENARIO_DIR.exists() else []
        formats = [f.stem for f in SOUL_FORMAT_DIR.glob("*.md")] if SOUL_FORMAT_DIR.exists() else []
        templates = [f.stem for f in SOUL_TEMPLATE_DIR.glob("*.json")] if SOUL_TEMPLATE_DIR.exists() else []

        items = [
            {'label': "VoiceType4TW", 'callback': None},
            {'label': "關於", 'callback': lambda _: self._show_about()},
            {'label': "---", 'callback': None},
            {'label': f"STT: {engine}", 'callback': None},
            {'label': f"AI 助理模式 : {action_state}", 'callback': self._toggle_action_mode},
            {'label': "---", 'callback': None},
            {'label': f"AI 潤飾/翻譯 : {llm_state}", 'callback': self._toggle_llm},
            
            # Scenario Submenu
            {'label': "🎭 情境模式", 'callback': None, 'submenu': self._build_scenario_menu(scenarios)},
            {'label': "📝 輸出格式", 'callback': None, 'submenu': self._build_format_menu(formats)},
            {'label': "📌 我的模板", 'callback': None, 'submenu': self._build_template_menu(templates)},
            
            {'label': "快速翻譯", 'callback': None, 'submenu': [
                {'label': "翻譯成 英文", 'callback': lambda _: self._translate_en()},
                {'label': "翻譯成 日文", 'callback': lambda _: self._translate_jp()},
                {'label': "恢復正常模式", 'callback': lambda _: self._translate_none()},
            ]},
            
            {'label': "---", 'callback': None},
            {'label': "⚙️  偏好設定...", 'callback': lambda _: self._open_settings()},
            {'label': "---", 'callback': None},
            {'label': "結束", 'callback': lambda _: self._quit()},
        ]
        return items

    def _build_scenario_menu(self, scenarios):
        active = self.config.get("active_scenario", "default")
        items = [{'label': "🏠 基底靈魂", 'callback': self._set_scenario, 'checked': (active == "default")}]
        for s in sorted(scenarios):
            if s == "default": continue
            items.append({'label': s, 'callback': self._set_scenario, 'checked': (active == s)})
        return items

    def _build_format_menu(self, formats):
        active = self.config.get("active_format", "natural")
        items = [{'label': "📄 自然排版 (無格式支援)", 'callback': self._set_format, 'checked': (active == "natural")}]
        for f in sorted(formats):
            if f == "natural": continue
            items.append({'label': f, 'callback': self._set_format, 'checked': (active == f)})
        return items

    def _build_template_menu(self, templates):
        if not templates:
            return [{'label': "(尚無儲存模板)", 'callback': None}]
        return [{'label': t, 'callback': self._use_template} for t in sorted(templates)]

    def _toggle_action_mode(self, _):
        enabled = not self.config.get("action_mode", False)
        self.config["action_mode"] = enabled
        from config import save_config
        save_config(self.config)
        self.refresh_ui()

    def _set_scenario(self, sender):
        name = sender.text if hasattr(sender, 'text') else str(sender)
        internal_name = "default" if "基底靈魂" in name else name
        self.config["active_scenario"] = internal_name
        from config import save_config
        save_config(self.config)
        self.refresh_ui()

    def _set_format(self, sender):
        name = sender.text if hasattr(sender, 'text') else str(sender)
        internal_name = "natural" if "自然排版" in name else name
        self.config["active_format"] = internal_name
        from config import save_config
        save_config(self.config)
        self.refresh_ui()

    def _use_template(self, sender):
        name = sender.text if hasattr(sender, 'text') else str(sender)
        from paths import SOUL_TEMPLATE_DIR
        import json
        tpl_path = SOUL_TEMPLATE_DIR / f"{name}.json"
        if tpl_path.exists():
            with open(tpl_path, "r", encoding="utf-8") as f:
                output_text = json.load(f).get("output", "")
                if self.on_set_template:
                    self.on_set_template(output_text, name)

    def _toggle_llm(self, _):
        self.on_toggle_llm()
        self.refresh_ui()

    def _translate_en(self): self.on_set_translation("英文"); self.refresh_ui()
    def _translate_jp(self): self.on_set_translation("日文"); self.refresh_ui()
    def _translate_none(self): self.on_set_translation(None); self.refresh_ui()

    def _open_settings(self):
        import subprocess, sys, os
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        launcher = os.path.join(script_dir, "open_settings.py")
        subprocess.Popen([sys.executable, launcher], cwd=script_dir)

    def _show_about(self):
        # This still requires PyQt6
        from ui.about_window import AboutDialog
        dialog = AboutDialog(is_dark=self.config.get("dark_mode", True))
        dialog.exec()

    def _quit(self):
        self.on_quit()
        if self.tray: self.tray.stop()

    def refresh_ui(self):
        if self.tray:
            self.tray.update_menu(self.get_menu_items())

    def set_recording(self):
        if self.tray and hasattr(self.tray, 'set_icon'): 
            self.tray.set_icon("🔴")

    def set_processing(self):
        if self.tray and hasattr(self.tray, 'set_icon'):
            self.tray.set_icon("⏳")

    def set_idle(self):
        if self.tray and hasattr(self.tray, 'set_icon'):
            self.tray.set_icon("🎙")
