"""
Floating mic level indicator window.
Shows at the bottom-center of the screen (just above Dock).
Displays an animated waveform bar and current state text.
"""
import sys
import threading
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QColor, QPen, QFont


class _Signals(QObject):
    update_level = pyqtSignal(float)
    set_state = pyqtSignal(str)
    show_window = pyqtSignal()
    hide_window = pyqtSignal()


class MicIndicatorWindow(QWidget):
    STATE_COLORS = {
        "recording": QColor(255, 80, 80),      # red
        "processing": QColor(255, 200, 50),    # yellow
        "done": QColor(80, 200, 120),          # green
    }

    def __init__(self):
        super().__init__()
        self._level = 0.0
        self._state = "recording"
        self._bars = [0.0] * 20  # rolling bar history
        self._setup_window()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)  # 20fps

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(140, 26)
        self._reposition()

    def _reposition(self):
        screen_obj = QApplication.primaryScreen()
        if not screen_obj:
            return
        # availableGeometry() excludes Dock and Menu Bar
        available = screen_obj.availableGeometry()
        
        # Center horizontally in the available area
        x = available.x() + (available.width() - self.width()) // 2
        # Position 10px above the bottom of the available area (above the Dock)
        y = available.y() + available.height() - self.height() - 10
        
        self.move(x, y)

    def _tick(self):
        # Shift bars left and append current level
        self._bars = self._bars[1:] + [self._level]
        self.update()

    def set_level(self, level: float):
        self._level = max(0.0, min(1.0, level))

    def set_state(self, state: str):
        self._state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background pill
        bg = QColor(30, 30, 30, 210)
        painter.setBrush(bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)

        color = self.STATE_COLORS.get(self._state, QColor(255, 80, 80))

        # Draw waveform bars
        bar_w = 3
        gap = 2
        total_bars = len(self._bars)
        start_x = 10
        max_bar_h = 14
        center_y = self.height() // 2

        for i, val in enumerate(self._bars):
            h = max(2, int(val * max_bar_h))
            x = start_x + i * (bar_w + gap)
            y = center_y - h // 2
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, bar_w, h, 1, 1)

        # State label
        label_map = {"recording": "錄音中...", "processing": "辨識中...", "done": "完成"}
        label = label_map.get(self._state, "")
        painter.setPen(QColor(255, 255, 255, 200))
        font = QFont("PingFang TC", 7)
        painter.setFont(font)
        text_x = start_x + total_bars * (bar_w + gap) + 6
        # Add 10px margin on the right by subtracting from width
        painter.drawText(text_x, 0, self.width() - text_x - 10, self.height(),
                         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)


class MicIndicator:
    """Thread-safe wrapper around MicIndicatorWindow."""

    def __init__(self):
        self._app: QApplication | None = None
        self._window: MicIndicatorWindow | None = None
        self._signals = _Signals()
        self._ready = threading.Event()

    def start_app(self):
        """Run the Qt event loop — call this in the main thread."""
        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = QApplication.instance()

        self._window = MicIndicatorWindow()
        
        def on_show():
            self._window.show()
            self._window.raise_()
            self._window.activateWindow()

        self._signals.update_level.connect(self._window.set_level)
        self._signals.set_state.connect(self._window.set_state)
        self._signals.show_window.connect(on_show)
        self._signals.hide_window.connect(self._window.hide)
        
        self._ready.set()

    def show(self):
        self._ready.wait()
        self._signals.show_window.emit()

    def hide(self):
        self._ready.wait()
        self._signals.hide_window.emit()

    def set_level(self, level: float):
        self._ready.wait()
        self._signals.update_level.emit(level)

    def set_state(self, state: str):
        self._ready.wait()
        self._signals.set_state.emit(state)
