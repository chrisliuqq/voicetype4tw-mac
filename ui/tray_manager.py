import platform
import threading
from typing import Callable, List, Dict, Optional

IS_WINDOWS = platform.system() == "Windows"

class TrayManager:
    """
    Unified system tray manager for macOS (rumps) and Windows (pystray).
    """
    def __init__(self, title: str, icon_path: str, menu_items: List[Dict]):
        self.title = title
        self.icon_path = icon_path
        self.menu_items = menu_items
        self._tray = None
        self._loop_thread = None

    def start(self):
        if IS_WINDOWS:
            self._start_windows()
        else:
            self._start_macos()

    def stop(self):
        if IS_WINDOWS:
            if self._tray:
                self._tray.stop()
        else:
            import rumps
            rumps.quit_application()

    def update_menu(self, menu_items: List[Dict]):
        self.menu_items = menu_items
        if IS_WINDOWS:
            self._update_windows_menu()
        else:
            self._update_macos_menu()

    def _start_windows(self):
        try:
            from pystray import Icon, Menu, MenuItem
            from PIL import Image
            
            image = Image.open(self.icon_path)
            
            def create_menu():
                items = []
                for item in self.menu_items:
                    items.append(MenuItem(item['label'], item['callback'], checked=item.get('checked', None)))
                return Menu(*items)

            self._tray = Icon(self.title, image, self.title, menu=create_menu())
            self._tray.run()
        except ImportError:
            print("[tray] Error: pystray or Pillow not found. System tray will not be available.")

    def _start_macos(self):
        try:
            import rumps
            class App(rumps.App):
                def __init__(self, title, icon, items):
                    super().__init__(title, icon=icon, quit_button=None)
                    self.items = items
                    self._rebuild_menu()

                def _rebuild_menu(self):
                    self.menu.clear()
                    for item in self.items:
                        name = item['label']
                        callback = item['callback']
                        checked = item.get('checked', False)
                        btn = rumps.MenuItem(name, callback=callback)
                        btn.state = 1 if checked else 0
                        self.menu.add(btn)
                    self.menu.add(rumps.MenuItem("結束", callback=lambda _: rumps.quit_application()))

            self._tray = App(self.title, self.icon_path, self.menu_items)
            self._tray.run()
        except ImportError:
            print("[tray] Error: rumps not found.")

    def _update_windows_menu(self):
        if self._tray:
            from pystray import Menu, MenuItem
            items = []
            for item in self.menu_items:
                items.append(MenuItem(item['label'], item['callback'], checked=item.get('checked', None)))
            self._tray.menu = Menu(*items)

    def _update_macos_menu(self):
        if self._tray:
            self._tray.items = self.menu_items
            self._tray._rebuild_menu()

    def set_icon(self, status: str):
        """status: '🎙' (idle), '🔴' (recording), '⏳' (processing)"""
        # On macOS, rumps uses 'title' for the icon emoji string
        # On Windows, pystray would need actual image files, but for now we might stick to console or simple tray update
        if not IS_WINDOWS:
            if self._tray:
                self._tray.title = status
        else:
            # TODO: Implementation for Windows pystray icon update (requires .ico files)
            pass

    def flash(self):
        # Placeholder for visual feedback
        pass
