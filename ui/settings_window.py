"""
Modern VoiceType Settings Window using PyQt6.
Features tabs for General, STT/LLM, Vocab/Memory, and Stats.
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, 
    QTextEdit, QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect, QUrl, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QLinearGradient, QBrush, QPixmap, QDesktopServices

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config, save_config
from paths import SOUL_PATH
STT_ENGINES = ["local_whisper", "groq", "gemini", "openrouter"]
LLM_ENGINES = ["ollama", "openai", "claude", "openrouter", "gemini", "deepseek", "qwen"]
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]
TRIGGER_MODES = ["push_to_talk", "toggle"]
HOTKEYS = ["right_option", "left_option", "right_ctrl", "f13", "f14", "f15"]
LLM_MODES = ["replace", "fast"]

from hotkey.listener import key_to_str, str_to_key


class GlassCard(QFrame):
    """A premium looking card with subtle border and background."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            GlassCard {
                background-color: rgba(45, 45, 55, 180);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
            }
        """)

class SidebarButton(QPushButton):
    def __init__(self, icon_text, label, index, on_click, parent=None):
        super().__init__(parent)
        self.index = index
        self.setCheckable(True)
        self.setText(f"{icon_text}  {label}")
        self.setFont(QFont("Taipei Sans TC Beta", 16, QFont.Weight.Medium))
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: on_click(self.index))
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8a8d91;
                text-align: left;
                padding-left: 20px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 10);
            }
            QPushButton:checked {
                background-color: #252a33;
                color: #7c4dff;
                font-weight: bold;
            }
        """)

class SNSButton(QPushButton):
    def __init__(self, icon_path, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(24, 24))
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; } QPushButton:hover { background: rgba(255,255,255,20); border-radius: 4px; }")
        self.clicked.connect(self._open_url)

    def _open_url(self):
        QDesktopServices.openUrl(QUrl(self.url))


class HotkeyRecorderButton(QPushButton):
    """A button that captures the next key press to set a hotkey."""
    key_changed = pyqtSignal(str)

    def __init__(self, current_key_str, is_dark=True):
        super().__init__()
        self._key_str = current_key_str
        self._recording = False
        self._is_dark = is_dark
        self._update_text()
        self.clicked.connect(self._start_recording)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(32)

    def _update_text(self):
        if self._recording:
            self.setText("錄製中...")
            self.setStyleSheet("background: palette(highlight); color: white; border-radius: 6px;")
        else:
            self.setText(self._key_str if self._key_str else "未設定")
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 10);
                    border: 1px solid rgba(255, 255, 255, 20);
                    color: #ddd;
                    border-radius: 6px;
                    padding-left: 10px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 15);
                }
            """)

    def _start_recording(self):
        self._recording = True
        self._update_text()
        self.setFocus()

    def keyPressEvent(self, event):
        if self._recording:
            key = event.key()
            qt_to_pynput = {
                Qt.Key.Key_Alt: "alt_r",
                Qt.Key.Key_Control: "ctrl_r",
                Qt.Key.Key_Shift: "shift_r",
                Qt.Key.Key_Meta: "cmd_r",
                Qt.Key.Key_F13: "f13",
                Qt.Key.Key_F14: "f14",
                Qt.Key.Key_F15: "f15",
                Qt.Key.Key_Return: "enter",
                Qt.Key.Key_Space: "space",
            }
            p_key = qt_to_pynput.get(key) or event.text()
            if p_key:
                self._key_str = p_key
                self._recording = False
                self._update_text()
                self.key_changed.emit(self._key_str)
                self.clearFocus()
        else:
            super().keyPressEvent(event)

    @property
    def key_str(self): return self._key_str
    @key_str.setter
    def key_str(self, val):
        self._key_str = val
        self._update_text()


class PermissionLight(QWidget):
    def __init__(self, label_text, preference_url):
        super().__init__()
        self.url = preference_url
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        self.dot = QFrame()
        self.dot.setFixedSize(12, 12)
        self.dot.setStyleSheet("background-color: #555; border-radius: 6px;")
        layout.addWidget(self.dot)

        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: #e2e4e7; font-size: 14px;")
        layout.addWidget(self.label)

        layout.addStretch()

        self.fix_btn = QPushButton("設定")
        self.fix_btn.setFixedWidth(60)
        self.fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d333d;
                color: #8a8d91;
                font-size: 11px;
                padding: 2px 5px;
            }
            QPushButton:hover { background-color: #3d4452; color: #fff; }
        """)
        self.fix_btn.clicked.connect(self._open_preference)
        layout.addWidget(self.fix_btn)

    def _open_preference(self):
        import subprocess
        subprocess.run(["open", self.url])

    def set_status(self, authorized: bool):
        color = "#00e676" if authorized else "#ff5252"
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        status_text = " (已授權)" if authorized else " (未授權)"
        # Note: We keep the original label text and just update the color dot
        self.fix_btn.setVisible(not authorized)


class SettingsWindow(QMainWindow):
    def __init__(self, on_save=None, start_page=0):
        super().__init__()
        self.config = load_config()
        self.on_save = on_save
        self._is_dark = True # Pro mode is dark by default
        self._setup_ui()
        self._load_data()
        
        # 根據語言動態設定視窗標題
        lang = self.config.get("language", "zh")
        if "zh" in lang:
            self.setWindowTitle("嘴砲輸入法 2.2.2 Pro")
        else:
            self.setWindowTitle("VoiceType4TW Mac 2.2.2 Pro")
        
        # 設定啟動頁面
        if 0 <= start_page < len(self.sidebar_buttons):
            # 延遲一點點執行，避免在 UI 還沒完全掛載時觸發 visibility 切換
            QTimer.singleShot(10, lambda: self._on_sidebar_changed(start_page))
        
        # 定期檢查權限狀態
        self.perm_timer = QTimer(self)
        self.perm_timer.timeout.connect(self._check_all_permissions)
        self.perm_timer.start(2000) # 每 2 秒檢查一次

    def _setup_ui(self):
        self.setWindowTitle("VoiceType4TW Mac 2.2.2 Pro")
        self.setMinimumSize(900, 680)
        
        # Premium CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f1115;
            }
            QWidget#sidebar_container {
                background-color: #16191f;
                border-right: 1px solid #252a33;
            }
            QListWidget#sidebar {
                background: transparent;
                border: none;
                outline: none;
                padding: 15px;
            }
            QListWidget#sidebar::item {
                padding: 20px;
                color: #8a8d91;
                border-radius: 12px;
                margin-bottom: 10px;
            }
            QListWidget#sidebar::item:selected {
                background-color: #252a33;
                color: #7c4dff;
                font-weight: bold;
            }
            QLabel {
                color: #e2e4e7;
                font-family: 'PingFang TC';
            }
            QLineEdit, QComboBox, QTextEdit, QListWidget, QTreeWidget {
                background-color: #1c1f26;
                border: 1px solid #2d333d;
                border-radius: 8px;
                color: #e2e4e7;
                padding: 8px;
                selection-background-color: #3d4452;
            }
            QTreeWidget::item { padding: 4px; }
            QHeaderView::section {
                background-color: #1c1f26;
                color: #8a8d91;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                background-color: #7c4dff;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #9575cd; }
            QPushButton#secondary {
                background-color: #2d333d;
                color: #e2e4e7;
            }
            QPushButton#danger {
                background-color: transparent;
                border: 1px solid #ff5252;
                color: #ff5252;
            }
            QPushButton#danger:hover {
                background-color: #ff5252;
                color: white;
            }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3d3d4d;
                border-radius: 3px;
                min-height: 20px;
            }
            QCheckBox { color: #e2e4e7; spacing: 10px; }
            QCheckBox::indicator { width: 18px; height: 18px; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebar_container")
        sidebar_container.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_container = QWidget()
        logo_vbox = QVBoxLayout(logo_container)
        logo_vbox.setContentsMargins(0, 50, 0, 0) # Apply 50px Margin Top
        logo_vbox.setSpacing(0)
        
        lbl_en = QLabel("VoiceType4TW")
        lbl_en.setStyleSheet("font-family: 'Myriad Pro'; font-weight: bold; font-size: 28px; color: white;")
        lbl_en.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_mac = QLabel("Mac version")
        lbl_mac.setStyleSheet("font-family: 'Myriad Pro'; font-style: italic; font-size: 14px; color: #8a8d91;")
        lbl_mac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_vbox.addWidget(lbl_en)
        logo_vbox.addWidget(lbl_mac)
        sidebar_layout.addWidget(logo_container)

        # Menu List - Use Layout instead of QListWidget for perfect visibility
        self.menu_group = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_group)
        self.menu_layout.setContentsMargins(10, 20, 10, 0)
        self.menu_layout.setSpacing(5)
        
        self.sidebar_buttons = []
        menus = [
            ("🏠", "Dashboard"),
            ("🎙", "辨識 & AI"),
            ("✨", "靈魂設定"),
            ("📚", "詞彙 & 記憶"),
            ("📊", "數據統計"),
            ("⚙️", "系統設定")
        ]
        
        for i, (icon, label) in enumerate(menus):
            btn = SidebarButton(icon, label, i, self._on_sidebar_changed)
            self.menu_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
        
        self.sidebar_buttons[0].setChecked(True) # Default
        sidebar_layout.addWidget(self.menu_group)
        
        sidebar_layout.addStretch()
        
        # Credits and SNS at Bottom
        credit_box = QLabel("v2.2.2 Pro\n主要開發者：吉米丘\n協助開發者：Gemini, Nebula")
        credit_box.setStyleSheet("color: #555; font-size: 10px; margin-left: 25px; line-height: 1.2;")
        sidebar_layout.addWidget(credit_box)
        
        sns_container = QWidget()
        sns_layout = QHBoxLayout(sns_container)
        sns_layout.setContentsMargins(25, 5, 25, 20) # Left align with credit box
        sns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        sns_layout.setSpacing(10)
        
        sns_links = [
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-youtube.png", "https://youtube.com/@Jimmy4TW"),
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-facebook.png", "https://www.facebook.com/acykjcms"),
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-instagram.png", "https://www.instagram.com/jimmy4tw/"),
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-tiktok.png", "https://www.tiktok.com/@jimmy4tw"),
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-threads.png", "https://www.threads.net/@jimmy4tw"),
            ("/Users/acyk/scripts/voicetype-mac/assets/sns-4tw.png", "https://Jimmy4.TW/")
        ]
        
        for icon_path, url in sns_links:
            btn = SNSButton(icon_path, url)
            sns_layout.addWidget(btn)
        
        sidebar_layout.addWidget(sns_container)
        
        main_layout.addWidget(sidebar_container)

        # Content Area
        content_container = QWidget()
        self.content_layout = QVBoxLayout(content_container)
        self.content_layout.setContentsMargins(40, 50, 40, 40) # 50px Top Margin
        
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)

        # Pages
        self.stack.addWidget(self._create_dashboard_page())
        self.stack.addWidget(self._create_stt_llm_page())
        self.stack.addWidget(self._create_soul_page())
        self.stack.addWidget(self._create_vocab_mem_page())
        self.stack.addWidget(self._create_stats_page())
        self.stack.addWidget(self._create_general_page())

        # Footer Actions (Grouped for visibility control)
        self.footer_widget = QWidget()
        footer = QHBoxLayout(self.footer_widget)
        footer.setContentsMargins(0, 20, 0, 0)
        self.btn_save = QPushButton("儲存並套用變更")
        self.btn_save.clicked.connect(self._save_action)
        self.btn_cancel = QPushButton("捨棄變更")
        self.btn_cancel.setObjectName("secondary")
        self.btn_cancel.clicked.connect(self.close)
        
        footer.addStretch()
        footer.addWidget(self.btn_cancel)
        footer.addWidget(self.btn_save)
        self.content_layout.addWidget(self.footer_widget)
        
        # Initial footer visibility
        self._on_sidebar_changed(0)

        main_layout.addWidget(content_container)

    def _on_sidebar_changed(self, idx):
        # Update button states
        for i, btn in enumerate(self.sidebar_buttons):
            btn.setChecked(i == idx)
        
        self.stack.setCurrentIndex(idx)
        # Dashboard (0) and Stats (4) hide save buttons
        self.footer_widget.setVisible(idx not in [0, 4])

    def _create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        # Shift everything UP: significantly reduce top margin
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        dash_header = QHBoxLayout()
        header = QLabel("Dashboard")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff;")
        dash_header.addWidget(header)
        
        dash_header.addStretch()
        
        title_cn = QLabel("嘴砲輸入法")
        title_cn.setStyleSheet("font-family: 'Taipei Sans TC Beta'; font-size: 32px; font-weight: bold; color: #ffffff;")
        dash_header.addWidget(title_cn)
        
        # Add side margins to content but not to the header text alignment if needed
        dash_header_container = QWidget()
        dash_header_v = QVBoxLayout(dash_header_container)
        dash_header_v.setContentsMargins(0, 0, 0, 0) # Tight
        dash_header_v.addLayout(dash_header)
        layout.addWidget(dash_header_container)

        # Top Cards: Row 1
        cards_row1 = QHBoxLayout()
        
        # 1. Permission Card
        perm_card = GlassCard()
        p_layout = QVBoxLayout(perm_card)
        p_layout.setContentsMargins(20, 20, 20, 20)
        p_layout.addWidget(QLabel("權限驗證 (macOS 隱私)"))
        
        self.light_acc = PermissionLight("輔助功能 (Accessibility)", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
        p_layout.addWidget(self.light_acc)
        
        self.light_input = PermissionLight("輸入監聽 (Input Monitoring)", "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent")
        p_layout.addWidget(self.light_input)
        
        self.light_mic = PermissionLight("麥克風 (Microphone)", "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone")
        p_layout.addWidget(self.light_mic)
        cards_row1.addWidget(perm_card)

        # 2. Status Card
        status_card = GlassCard()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.addWidget(QLabel("系統狀態"))
        
        self.lbl_status_ai = QLabel("AI 潤飾: 已開啟")
        self.lbl_status_ai.setStyleSheet("color: #7c4dff; font-weight: bold; font-size: 16px;")
        status_layout.addWidget(self.lbl_status_ai)
        
        self.lbl_status_stt = QLabel("引擎: Local Whisper (Medium)")
        self.lbl_status_stt.setStyleSheet("color: #888; font-size: 13px;")
        status_layout.addWidget(self.lbl_status_stt)
        cards_row1.addWidget(status_card)

        layout.addLayout(cards_row1)

        # Bottom Cards: Row 2
        cards_row2 = QHBoxLayout()

        # 3. Quick Stats Card
        stats_card = GlassCard()
        sq_layout = QVBoxLayout(stats_card)
        sq_layout.setContentsMargins(20, 20, 20, 20)
        sq_layout.addWidget(QLabel("今日語效"))
        self.lbl_today_count = QLabel("0 次錄音")
        self.lbl_today_count.setStyleSheet("color: #00e5ff; font-weight: bold; font-size: 16px;")
        sq_layout.addWidget(self.lbl_today_count)
        self.lbl_today_chars = QLabel("錄製約 0 字")
        sq_layout.addWidget(self.lbl_today_chars)
        cards_row2.addWidget(stats_card)

        # 4. Time Saved Card
        time_card = GlassCard()
        t_layout = QVBoxLayout(time_card)
        t_layout.setContentsMargins(20, 20, 20, 20)
        t_layout.addWidget(QLabel("累計省下時間"))
        self.lbl_time_saved = QLabel("0 分鐘")
        self.lbl_time_saved.setStyleSheet("color: #ffab40; font-weight: bold; font-size: 16px;")
        t_layout.addWidget(self.lbl_time_saved)
        self.lbl_total_chars_desc = QLabel("共辨識 0 字")
        self.lbl_total_chars_desc.setStyleSheet("color: #888; font-size: 13px;")
        t_layout.addWidget(self.lbl_total_chars_desc)
        cards_row2.addWidget(time_card)
        
        layout.addLayout(cards_row2)

        # Recent Activity Card
        recent_card = GlassCard()
        rc_layout = QVBoxLayout(recent_card)
        rc_layout.setContentsMargins(20, 20, 20, 20)
        rc_layout.addWidget(QLabel("💡 最近學到的詞彙"))
        self.dashboard_vocab = QListWidget()
        self.dashboard_vocab.setStyleSheet("background: transparent; border: none; font-size: 13px;")
        self.dashboard_vocab.setFixedHeight(120)
        rc_layout.addWidget(self.dashboard_vocab)
        layout.addWidget(recent_card)

        layout.addStretch()
        return page

    def _create_stt_llm_page(self):
        page = QScrollArea()
        page.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(25)

        layout.addWidget(self._page_section_header("🎙 語音辨識配置"))
        self.stt_engine = self._add_grid_row(layout, "核心引擎", QComboBox())
        self.stt_engine.addItems(STT_ENGINES)
        
        self.whisper_model = self._add_grid_row(layout, "Whisper 規格", QComboBox())
        self.whisper_model.addItems(WHISPER_MODELS)

        self.groq_key = self._add_grid_row(layout, "Groq API Key (選填)", QLineEdit())
        self.groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.language = self._add_grid_row(layout, "優先辨識語言", QLineEdit())

        layout.addWidget(self._page_section_header("🤖 大語言模型潤飾 (LLM) 配置"))
        self.llm_enabled = QCheckBox("啟用高階智慧潤飾與翻譯")
        layout.addWidget(self.llm_enabled)

        self.llm_engine = self._add_grid_row(layout, "模型提供者", QComboBox())
        self.llm_engine.addItems(LLM_ENGINES)

        self.llm_mode = self._add_grid_row(layout, "內容注入模式", QComboBox())
        self.llm_mode.addItems(LLM_MODES)

        # API Keys
        self.openai_key = self._add_grid_row(layout, "OpenAI / Claude Key", QLineEdit())
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.openrouter_key = self._add_grid_row(layout, "OpenRouter / DeepSeek Key", QLineEdit())
        self.openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)

        container.setLayout(layout)
        page.setWidget(container)
        return page

    def _create_soul_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        layout.addWidget(self._page_section_header("✨ AI 靈魂設定 (人格與提示詞)"))
        lbl_info = QLabel("在這裡定義 AI 的個性、對話風格以及特殊的翻譯/潤飾指令。")
        lbl_info.setStyleSheet("color: #8a8d91; font-size: 13px;")
        layout.addWidget(lbl_info)

        self.soul_prompt = QTextEdit()
        self.soul_prompt.setFont(QFont("Monaco", 12))
        self.soul_prompt.setPlaceholderText("輸入 AI 的靈魂提示詞...")
        self.soul_prompt.setMinimumHeight(400) # 原本預設沒有或是200，現在加上明確的高度讓它變為兩倍
        layout.addWidget(self.soul_prompt)

        layout.addStretch()
        return page

    def _create_vocab_mem_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: Vocab
        v_box = QWidget()
        v_layout = QVBoxLayout(v_box)
        v_layout.addWidget(QLabel("✏️ 私人詞庫"))
        self.vocab_list = QListWidget()
        v_layout.addWidget(self.vocab_list)
        
        vh = QHBoxLayout()
        self.vocab_input = QLineEdit()
        self.vocab_input.setPlaceholderText("新增...")
        self.btn_add_vocab = QPushButton("+")
        self.btn_add_vocab.setFixedWidth(50)
        self.btn_add_vocab.clicked.connect(self._add_vocab)
        vh.addWidget(self.vocab_input)
        vh.addWidget(self.btn_add_vocab)
        v_layout.addLayout(vh)
        
        self.btn_del_vocab = QPushButton("刪除已選")
        self.btn_del_vocab.setObjectName("danger")
        self.btn_del_vocab.clicked.connect(self._del_vocab)
        v_layout.addWidget(self.btn_del_vocab)

        # Right: Learned & Memory
        right_box = QWidget()
        rl = QVBoxLayout(right_box)
        
        rl.addWidget(QLabel("💡 AI 學習清單"))
        self.learned_list = QListWidget()
        rl.addWidget(self.learned_list)
        lh = QHBoxLayout()
        self.btn_promote = QPushButton("升格自訂")
        self.btn_promote.clicked.connect(self._promote_vocab)
        lh.addWidget(self.btn_promote)
        rl.addLayout(lh)

        rl.addWidget(QLabel("🧠 長期記憶"))
        self.mem_tree = QTreeWidget()
        self.mem_tree.setHeaderLabels(["時間", "快照"])
        rl.addWidget(self.mem_tree)

        splitter.addWidget(v_box)
        splitter.addWidget(right_box)
        return page

    def _create_stats_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._page_section_header("詳細分析數據"))
        
        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["範圍", "對話數", "語音長度", "轉錄字數"])
        layout.addWidget(self.stats_tree)
        
        self.btn_refresh_stats = QPushButton("重新整理數據")
        self.btn_refresh_stats.setObjectName("secondary")
        self.btn_refresh_stats.clicked.connect(self._refresh_stats)
        layout.addWidget(self.btn_refresh_stats)
        
        layout.addStretch()
        return page

    def _create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        layout.addWidget(self._page_section_header("⌨️ 控制熱鍵錄製"))
        
        hotkey_grid = QFrame()
        grid_layout = QVBoxLayout(hotkey_grid)
        
        self.btn_ptt = HotkeyRecorderButton(self.config.get("hotkey_ptt", "alt_r"))
        self._add_grid_row(grid_layout, "錄音按住 (PTT)", self.btn_ptt)
        
        layout.addWidget(hotkey_grid)
        
        layout.addWidget(self._page_section_header("⚙️ 偏好偏好"))
        self.auto_paste = QCheckBox("結果自動貼上 (Paste automatically)")
        self.auto_paste.setChecked(self.config.get("auto_paste", True))
        layout.addWidget(self.auto_paste)
        
        self.debug_mode = QCheckBox("啟用詳細日誌輸出 (Debug logging)")
        self.debug_mode.setChecked(self.config.get("debug_mode", False))
        layout.addWidget(self.debug_mode)

        layout.addStretch()
        return page

    def _page_section_header(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-weight: bold; font-size: 16px; color: #7c4dff; margin-top: 10px; margin-bottom: 5px;")
        return l

    def _add_grid_row(self, layout, label_text, widget):
        row = QHBoxLayout()
        l = QLabel(label_text)
        l.setFixedWidth(160)
        row.addWidget(l)
        row.addWidget(widget)
        layout.addLayout(row)
        return widget

    # --- Data and Logic ---
    def _load_data(self):
        if SOUL_PATH.exists():
            self.soul_prompt.setPlainText(SOUL_PATH.read_text(encoding="utf-8"))
        
        # Load from config
        self.stt_engine.setCurrentText(self.config.get("stt_engine", "local_whisper"))
        self.whisper_model.setCurrentText(self.config.get("whisper_model", "medium"))
        self.groq_key.setText(self.config.get("groq_api_key", ""))
        self.language.setText(self.config.get("language", "zh"))
        self.llm_enabled.setChecked(self.config.get("llm_enabled", False))
        self.llm_engine.setCurrentText(self.config.get("llm_engine", "ollama"))
        self.llm_mode.setCurrentText(self.config.get("llm_mode", "replace"))
        self.openai_key.setText(self.config.get("openai_api_key", ""))
        self.openrouter_key.setText(self.config.get("openrouter_api_key", ""))

        self._refresh_vocab()
        self._refresh_learned_vocab()
        self._refresh_memory()
        self._refresh_stats()
        self._update_dashboard_status()

    def _update_dashboard_status(self):
        ai = "已開啟" if self.config.get("llm_enabled") else "已關閉"
        self.lbl_status_ai.setText(f"AI 潤飾: {ai}")
        self.lbl_status_ai.setStyleSheet(f"color: {'#7c4dff' if ai == '已開啟' else '#666'}; font-weight: bold; font-size: 16px;")
        
        eng = self.config.get("stt_engine", "local_whisper")
        self.lbl_status_stt.setText(f"引擎: {eng.upper()}")
        
        # 啟動時試探性要求麥克風權限，確保出現在系統清單中
        QTimer.singleShot(1000, self._request_mic_permission)
        self._check_all_permissions()

    def _request_mic_permission(self):
        """主動試探麥克風，誘發 macOS 彈出權限請求視窗"""
        try:
            import objc
            ns = {}
            objc.loadBundle('AVFoundation',
                            bundle_path='/System/Library/Frameworks/AVFoundation.framework',
                            module_globals=ns)
            AVCaptureDevice = ns['AVCaptureDevice']
            if AVCaptureDevice.authorizationStatusForMediaType_('soun') == 0:
                AVCaptureDevice.requestAccessForMediaType_completionHandler_('soun', lambda granted: None)
        except Exception:
            pass

    def _check_all_permissions(self):
        # 1. Accessibility — AXIsProcessTrusted 是 C 函數，必須用 ctypes
        trusted = False
        try:
            import ctypes
            lib = ctypes.cdll.LoadLibrary(
                '/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices')
            lib.AXIsProcessTrusted.restype = ctypes.c_bool
            trusted = lib.AXIsProcessTrusted()
        except Exception:
            trusted = False
        self.light_acc.set_status(trusted)

        # 2. Input Monitoring（通常與輔助功能同步）
        self.light_input.set_status(trusted)

        # 3. Microphone — AVCaptureDevice 是 ObjC 類別，用 objc.loadBundle
        mic_ok = False
        try:
            import objc
            ns = {}
            objc.loadBundle('AVFoundation',
                            bundle_path='/System/Library/Frameworks/AVFoundation.framework',
                            module_globals=ns)
            AVCaptureDevice = ns['AVCaptureDevice']
            # 0=NotDetermined, 1=Restricted, 2=Denied, 3=Authorized
            status = AVCaptureDevice.authorizationStatusForMediaType_('soun')
            mic_ok = (status == 3)
        except Exception:
            mic_ok = False
        self.light_mic.set_status(mic_ok)

    def _refresh_vocab(self):
        self.vocab_list.clear()
        try:
            from vocab.manager import load_custom_vocab
            for word in load_custom_vocab():
                self.vocab_list.addItem(word)
        except: pass

    def _refresh_learned_vocab(self):
        self.learned_list.clear()
        self.dashboard_vocab.clear()
        try:
            from vocab.manager import load_all_learned_words, load_auto_memory
            memory = load_auto_memory()
            words = load_all_learned_words()
            for word in words:
                count = memory.get(word, 0)
                self.learned_list.addItem(f"{word} ({count})")
            # Dashboard only show top 5
            for word in words[:5]:
                self.dashboard_vocab.addItem(word)
        except: pass

    def _promote_vocab(self):
        item = self.learned_list.currentItem()
        if not item: return
        word = item.text().split(" (")[0]
        try:
            from vocab.manager import promote_learned_word
            promote_learned_word(word)
            self._refresh_vocab()
            self._refresh_learned_vocab()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    def _refresh_memory(self):
        self.mem_tree.clear()
        try:
            from memory.manager import load_memory
            memory = load_memory()
            for entry in reversed(memory.get("entries", [])):
                ts = entry.get("ts", "")[:16]
                text = (entry.get("llm") or entry.get("stt", ""))[:40]
                self.mem_tree.addTopLevelItem(QTreeWidgetItem([ts, text + "..."]))
        except: pass

    def _refresh_stats(self):
        self.stats_tree.clear()
        try:
            from stats.tracker import get_summary
            s = get_summary()
            self.lbl_today_count.setText(f"{s['today']['sessions']} 次錄音")
            self.lbl_today_chars.setText(f"錄製約 {s['today']['chars']} 字")
            
            # 計算省下時間 (以一般人打字速度 40字/分 計算)
            total_chars = s['total']['chars']
            saved_mins = total_chars / 40.0
            if saved_mins < 60:
                self.lbl_time_saved.setText(f"{saved_mins:.1f} 分鐘")
            else:
                self.lbl_time_saved.setText(f"{saved_mins/60.0:.1f} 小時")
            self.lbl_total_chars_desc.setText(f"累計辨識 {total_chars} 字")
            
            self.stats_tree.addTopLevelItem(QTreeWidgetItem(["今日", str(s["today"]["sessions"]), f"{s['today']['duration']}s", str(s["today"]["chars"])]))
            self.stats_tree.addTopLevelItem(QTreeWidgetItem(["本週", str(s["week"]["sessions"]), f"{s['week']['duration']}s", str(s["week"]["chars"])]))
            self.stats_tree.addTopLevelItem(QTreeWidgetItem(["累積", str(s["total"]["sessions"]), f"{s['total']['duration']}s", str(s["total"]["chars"])]))
        except: pass

    def _add_vocab(self):
        word = self.vocab_input.text().strip()
        if not word: return
        from vocab.manager import add_custom_word
        add_custom_word(word)
        self.vocab_input.clear()
        self._refresh_vocab()

    def _del_vocab(self):
        item = self.vocab_list.currentItem()
        if not item: return
        from vocab.manager import remove_custom_word
        remove_custom_word(item.text())
        self._refresh_vocab()

    def _save_action(self):
        self.config["stt_engine"] = self.stt_engine.currentText()
        self.config["whisper_model"] = self.whisper_model.currentText()
        self.config["groq_api_key"] = self.groq_key.text().strip()
        self.config["language"] = self.language.text().strip()
        self.config["llm_enabled"] = self.llm_enabled.isChecked()
        self.config["llm_engine"] = self.llm_engine.currentText()
        self.config["llm_mode"] = self.llm_mode.currentText()
        self.config["openai_api_key"] = self.openai_key.text().strip()
        self.config["openrouter_api_key"] = self.openrouter_key.text().strip()
        self.config["hotkey_ptt"] = self.btn_ptt.key_str
        self.config["auto_paste"] = self.auto_paste.isChecked()
        self.config["debug_mode"] = self.debug_mode.isChecked()

        try:
            SOUL_PATH.write_text(self.soul_prompt.toPlainText().strip(), encoding="utf-8")
        except: pass

        save_config(self.config)
        QMessageBox.information(self, "嘴砲輸入法", "設定已儲存並生效。")
        if self.on_save: self.on_save(self.config)
        self.close()

    def run(self):
        self.show()

def has_api_key(config: dict) -> bool:
    stt = config.get("stt_engine", "local_whisper")
    if stt == "local_whisper" and (not config.get("llm_enabled") or config.get("llm_engine") == "ollama"):
        return True
    for k in ["groq_api_key", "openai_api_key", "openrouter_api_key"]:
        if config.get(k): return True
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())
