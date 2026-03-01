"""
Floating mic level indicator window.
Shows at the bottom-center of the screen (just above Dock).
Displays an animated waveform bar and current state text.
"""
import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QUrl
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt6.QtMultimedia import QSoundEffect


class _Signals(QObject):
    update_level = pyqtSignal(float)
    set_state = pyqtSignal(str)
    play_beep = pyqtSignal()
    set_prefix = pyqtSignal(str)
    set_label_suffix = pyqtSignal(str)
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    flash = pyqtSignal()


class MicIndicatorWindow(QWidget):
    STATE_COLORS = {
        "recording": QColor(255, 80, 80),      # red
        "processing": QColor(255, 200, 50),    # yellow
        "done": QColor(80, 200, 120),          # green
        "loading": QColor(0, 122, 255),       # blue
    }

    def __init__(self):
        super().__init__()
        self._level = 0.0
        self._state = "recording"
        self._prefix = ""  # 例如 "AI", "譯:日文"
        self._label_suffix = ""  # 例如 "(翻譯中: 英文)"
        self._bars = [0.0] * 20  # rolling bar history
        self._flash_active = False
        self._setup_window()
        
        # 音效器
        self._beep = QSoundEffect(self)
        from pathlib import Path
        beep_path = Path(__file__).parent.parent / "assets" / "beep.wav"
        from PyQt6.QtCore import QUrl
        self._beep.setSource(QUrl.fromLocalFile(str(beep_path.absolute())))
        self._beep.setVolume(0.5)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)  # 20fps

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.ToolTip
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(180, 26)
        self._reposition()

    def _reposition(self):
        screen_obj = QApplication.primaryScreen()
        if not screen_obj:
            return
        available = screen_obj.availableGeometry()
        x = available.x() + (available.width() - self.width()) // 2
        y = available.y() + available.height() - self.height() - 10
        self.move(x, y)

    def _tick(self):
        self._bars = self._bars[1:] + [self._level]
        self.update()

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))

    def set_state(self, state: str):
        self._state = state
        self.update()

    def set_label_suffix(self, suffix: str):
        """設定額外的標籤文字，例如 '(翻譯中)'"""
        self._label_suffix = suffix
        self.update()

    def set_prefix(self, text: str):
        """設定左側顯示的前綴文字，例如 'AI' 或 '譯:日'"""
        self._prefix = text
        self.update()

    def trigger_flash(self):
        """閃爍一下背景以此作為回饋。"""
        self._flash_active = True
        self.update()
        QTimer.singleShot(500, self._stop_flash)
        
        # macOS/Windows 音效回饋
        import platform
        if platform.system() == "Darwin":
            import subprocess
            try:
                subprocess.Popen(["afplay", "/System/Library/Sounds/Glass.aiff"])
            except:
                pass
        elif platform.system() == "Windows":
            try:
                import winsound
                winsound.Beep(1000, 100)
            except:
                pass

    def _stop_flash(self):
        self._flash_active = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background pill
        # 如果正在閃爍，使用亮藍色作為背景
        bg_color = QColor(0, 122, 255, 230) if self._flash_active else QColor(30, 30, 30, 210)
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

        # 內容配色
        text_base_color = QColor(255, 255, 255, 240) if self._flash_active else QColor(255, 255, 255, 200)
        prefix_color = QColor(255, 255, 255, 240) if self._flash_active else QColor(0, 122, 255, 220)
        wave_color = QColor(255, 255, 255, 240) if self._flash_active else self.STATE_COLORS.get(self._state, QColor(255, 80, 80))

        # ── 寬度計算與置中 ──
        import platform
        font_family = "PingFang TC" if platform.system() == "Darwin" else "Microsoft JhengHei"
        f_prefix = QFont(font_family, 7)
        f_prefix.setBold(True)
        f_label = QFont(font_family, 7)
        fm_prefix = QFontMetrics(f_prefix)
        fm_label = QFontMetrics(f_label)

        prefix_w = fm_prefix.horizontalAdvance(self._prefix) if self._prefix else 0
        prefix_gap = 8 if prefix_w > 0 else 0
        bar_w, gap = 3, 2
        total_bars = len(self._bars)
        bars_w = total_bars * (bar_w + gap) - gap
        label_map = {"recording": "錄音中...", "processing": "辨識中...", "done": "完成", "loading": "載入中..."}
        label_text = label_map.get(self._state, "")
        if self._state not in ["done", "loading"] and self._label_suffix:
            label_text += f" {self._label_suffix}"
        label_w = fm_label.horizontalAdvance(label_text)
        label_gap = 8 if label_w > 0 else 0
        total_content_w = prefix_w + prefix_gap + bars_w + label_gap + label_w
        start_x = (self.width() - total_content_w) // 2

        # ── 繪製內容 ──
        if self._prefix:
            painter.setPen(prefix_color)
            painter.setFont(f_prefix)
            painter.drawText(start_x, 0, prefix_w, self.height(),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._prefix)
            start_x += prefix_w + prefix_gap

        center_y = self.height() // 2
        max_bar_h = 14
        for i, val in enumerate(self._bars):
            h = max(2, int(val * max_bar_h))
            x = start_x + i * (bar_w + gap)
            y = center_y - h // 2
            painter.setBrush(wave_color)
            painter.drawRoundedRect(x, y, bar_w, h, 1, 1)
        start_x += bars_w + label_gap

        painter.setPen(text_base_color)
        painter.setFont(f_label)
        painter.drawText(start_x, 0, label_w + 10, self.height(),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label_text)


class MicIndicator:
    """Thread-safe wrapper around MicIndicatorWindow."""

    def __init__(self):
        self._app: QApplication | None = None
        self._window: MicIndicatorWindow | None = None
        self._signals = _Signals()
        self._ready = threading.Event()

    def start_app(self):
        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()
        self._window = MicIndicatorWindow()
        def on_show():
            self._window.show()
        self._signals.update_level.connect(self._window.set_level)
        self._signals.set_state.connect(self._window.set_state)
        self._signals.set_prefix.connect(self._window.set_prefix)
        self._signals.set_label_suffix.connect(self._window.set_label_suffix)
        self._signals.show_window.connect(on_show)
        self._signals.hide_window.connect(self._window.hide)
        self._signals.flash.connect(self._window.trigger_flash)
        self._signals.play_beep.connect(self._window._beep.play)
        self._ready.set()

    def show(self):
        self._ready.wait()
        self._signals.show_window.emit()

    def hide(self):
        self._ready.wait()
        self._signals.hide_window.emit()

    def flash(self):
        self._ready.wait()
        self._signals.flash.emit()

    def set_level(self, level: float):
        self._ready.wait()
        self._signals.update_level.emit(level)

    def set_state(self, state: str):
        self._ready.wait()
        self._signals.set_state.emit(state)

    def set_label_suffix(self, suffix: str):
        self._ready.wait()
        self._signals.set_label_suffix.emit(suffix)

    def set_prefix(self, text: str):
        self._ready.wait()
        self._signals.set_prefix.emit(text)

    def play_beep(self):
        self._ready.wait()
        self._signals.play_beep.emit()
