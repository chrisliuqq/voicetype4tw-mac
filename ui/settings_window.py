"""
Modern VoiceType Settings Window using PyQt6.
Features tabs for General, STT/LLM, Vocab/Memory, and Stats.
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, 
    QTextEdit, QListWidget, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_config, save_config

SOUL_PATH = Path(__file__).parent.parent / "soul.md"
STT_ENGINES = ["local_whisper", "groq", "gemini", "openrouter"]
LLM_ENGINES = ["ollama", "openai", "claude", "openrouter", "gemini", "deepseek", "qwen"]
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]
TRIGGER_MODES = ["push_to_talk", "toggle"]
HOTKEYS = ["right_option", "left_option", "right_ctrl", "f13", "f14", "f15"]
LLM_MODES = ["replace", "fast"]

from hotkey.listener import key_to_str, str_to_key


class HotkeyRecorderButton(QPushButton):
    """A button that captures the next key press to set a hotkey."""
    key_changed = pyqtSignal(str)

    def __init__(self, current_key_str, is_dark=False):
        super().__init__()
        self._key_str = current_key_str
        self._recording = False
        self._is_dark = is_dark
        self._update_text()
        self.clicked.connect(self._start_recording)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _update_text(self):
        if self._recording:
            self.setText("錄製中... 請按鍵")
            self.setStyleSheet("background: #ff9500; color: white; font-weight: bold;")
        else:
            self.setText(self._key_str if self._key_str else "未設定")
            bg = "#3a3a3a" if self._is_dark else "#e9e9eb"
            fg = "#e0e0e0" if self._is_dark else "#333"
            self.setStyleSheet(f"background: {bg}; color: {fg}; font-family: 'PingFang TC'; text-align: left; padding-left: 10px;")

    def _start_recording(self):
        self._recording = True
        self._update_text()
        self.setFocus()

    def keyPressEvent(self, event):
        if self._recording:
            # We use pynput's key_to_str logic conceptually, 
            # but here we need to map QKeyEvent to pynput-compatible strings.
            key = event.key()
            
            # Map common Qt keys to pynput names
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
            
            p_key = qt_to_pynput.get(key)
            if not p_key:
                # Try character
                p_key = event.text()
            
            if p_key:
                self._key_str = p_key
                self._recording = False
                self._update_text()
                self.key_changed.emit(self._key_str)
                self.clearFocus()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        if self._recording:
            self._recording = False
            self._update_text()
        super().focusOutEvent(event)

    @property
    def key_str(self):
        return self._key_str

    @key_str.setter
    def key_str(self, val):
        self._key_str = val
        self._update_text()


class SettingsWindow(QMainWindow):
    def __init__(self, on_save=None):
        super().__init__()
        self.config = load_config()
        self.on_save = on_save
        self._is_dark = self._is_dark_mode()
        self._setup_ui()
        self._load_data()

    def _is_dark_mode(self):
        """Detect if macOS is in dark mode."""
        try:
            import subprocess
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            return "Dark" in result.stdout
        except:
            return False

    def _setup_ui(self):
        self.setWindowTitle("VoiceType4TW-Mac 設定")
        self.setMinimumSize(750, 650)
        
        # Adaptive Palette
        bg_color = "#1e1e1e" if self._is_dark else "#f8f9fa"
        widget_bg = "#2d2d2d" if self._is_dark else "white"
        text_color = "#e0e0e0" if self._is_dark else "#333"
        border_color = "#444" if self._is_dark else "#dee2e6"
        input_border = "#555" if self._is_dark else "#ccc"
        tab_bg = "#252525" if self._is_dark else "#f0f0f0"
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg_color}; }}
            QTabWidget::pane {{ border: 1px solid {border_color}; border-radius: 4px; background: {widget_bg}; }}
            QTabBar::tab {{ padding: 10px 20px; font-size: 13px; font-family: 'PingFang TC'; background: {tab_bg}; color: {text_color}; }}
            QTabBar::tab:selected {{ background: {widget_bg}; border-bottom: 2px solid #007aff; color: #007aff; }}
            QLabel {{ font-family: 'PingFang TC'; font-size: 13px; color: {text_color}; }}
            QLineEdit, QComboBox, QTextEdit, QListWidget, QTreeWidget {{ 
                padding: 6px; border: 1px solid {input_border}; border-radius: 4px; 
                background: {widget_bg}; color: {text_color};
            }}
            QHeaderView::section {{
                background-color: {tab_bg}; padding: 4px; border: 1px solid {border_color}; color: {text_color};
            }}
            QCheckBox {{ color: {text_color}; spacing: 8px; }}
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{ border: none; background: transparent; width: 10px; }}
            QScrollBar::handle:vertical {{ background: #888; border-radius: 5px; min-height: 20px; }}
            QPushButton {{ 
                padding: 8px 16px; border-radius: 4px; background: #007aff; color: white; 
                font-weight: bold; border: none;
            }}
            QPushButton:hover {{ background: #0066cc; }}
            QPushButton#secondary {{ background: #6c757d; }}
            QPushButton#danger {{ background: #dc3545; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tabs
        self.tabs.addTab(self._create_stt_llm_tab(), "🎙 語音 & AI")
        self.tabs.addTab(self._create_vocab_mem_tab(), "📚 詞彙 & 記憶")
        self.tabs.addTab(self._create_stats_tab(), "📊 統計")
        self.tabs.addTab(self._create_general_tab(), "⚙️ 一般")

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("儲存設定")
        self.btn_save.clicked.connect(self._save_action)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setObjectName("secondary")
        self.btn_cancel.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def _create_stt_llm_tab(self):
        widget = QScrollArea()
        widget.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        # STT Section
        layout.addWidget(self._section_header("🎙 語音辨識 (STT)"))
        self.stt_engine = self._add_row(layout, "引擎", QComboBox())
        self.stt_engine.addItems(STT_ENGINES)
        self.stt_engine.setCurrentText(self.config.get("stt_engine", "local_whisper"))

        self.whisper_model = self._add_row(layout, "Whisper 模型", QComboBox())
        self.whisper_model.addItems(WHISPER_MODELS)
        self.whisper_model.setCurrentText(self.config.get("whisper_model", "medium"))

        self.groq_key = self._add_row(layout, "Groq API Key", QLineEdit())
        self.groq_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_key.setText(self.config.get("groq_api_key", ""))

        self.language = self._add_row(layout, "語言代碼", QLineEdit())
        self.language.setText(self.config.get("language", "zh"))

        layout.addWidget(self._divider())

        # LLM Section
        layout.addWidget(self._section_header("🤖 AI 潤飾 (LLM)"))
        self.llm_enabled = QCheckBox("啟用 LLM 潤飾")
        self.llm_enabled.setChecked(self.config.get("llm_enabled", False))
        layout.addWidget(self.llm_enabled)

        self.llm_engine = self._add_row(layout, "LLM 引擎", QComboBox())
        self.llm_engine.addItems(LLM_ENGINES)
        self.llm_engine.setCurrentText(self.config.get("llm_engine", "ollama"))

        self.llm_mode = self._add_row(layout, "注入模式", QComboBox())
        self.llm_mode.addItems(LLM_MODES)
        self.llm_mode.setCurrentText(self.config.get("llm_mode", "replace"))

        # LLM Keys & Models (Specific providers)
        self.openai_key = self._add_row(layout, "OpenAI Key", QLineEdit())
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key.setText(self.config.get("openai_api_key", ""))

        self.openrouter_key = self._add_row(layout, "OpenRouter Key", QLineEdit())
        self.openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.openrouter_key.setText(self.config.get("openrouter_api_key", ""))

        layout.addWidget(self._section_header("✨ 靈魂 Prompt (soul.md)"))
        self.soul_prompt = QTextEdit()
        self.soul_prompt.setMinimumHeight(150)
        layout.addWidget(self.soul_prompt)

        layout.addStretch()
        widget.setWidget(container)
        return widget

    def _create_vocab_mem_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Vocabulary
        vocab_widget = QWidget()
        vocab_layout = QVBoxLayout(vocab_widget)
        vocab_layout.addWidget(QLabel("✏️ 自訂詞彙 (專有名詞、品牌名等)"))
        self.vocab_list = QListWidget()
        vocab_layout.addWidget(self.vocab_list)
        
        v_h_layout = QHBoxLayout()
        self.vocab_input = QLineEdit()
        self.vocab_input.setPlaceholderText("輸入新詞彙...")
        self.btn_add_vocab = QPushButton("新增")
        self.btn_add_vocab.clicked.connect(self._add_vocab)
        self.btn_del_vocab = QPushButton("刪除選取")
        self.btn_del_vocab.setObjectName("danger")
        self.btn_del_vocab.clicked.connect(self._del_vocab)
        v_h_layout.addWidget(self.vocab_input)
        v_h_layout.addWidget(self.btn_add_vocab)
        v_h_layout.addWidget(self.btn_del_vocab)
        vocab_layout.addLayout(v_h_layout)

        # Memory
        mem_widget = QWidget()
        mem_layout = QVBoxLayout(mem_widget)
        mem_layout.addWidget(QLabel("🧠 對話記憶"))
        self.mem_tree = QTreeWidget()
        self.mem_tree.setHeaderLabels(["時間", "內容"])
        self.mem_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.mem_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        mem_layout.addWidget(self.mem_tree)

        m_h_layout = QHBoxLayout()
        self.btn_del_mem = QPushButton("刪除選取")
        self.btn_del_mem.setObjectName("danger")
        self.btn_del_mem.clicked.connect(self._del_memory)
        self.btn_clear_mem = QPushButton("清空全部")
        self.btn_clear_mem.setObjectName("danger")
        self.btn_clear_mem.clicked.connect(self._clear_memory)
        self.btn_open_folder = QPushButton("開啟資料夾")
        self.btn_open_folder.setObjectName("secondary")
        self.btn_open_folder.clicked.connect(self._open_data_folder)
        m_h_layout.addWidget(self.btn_del_mem)
        m_h_layout.addWidget(self.btn_clear_mem)
        m_h_layout.addStretch()
        m_h_layout.addWidget(self.btn_open_folder)
        mem_layout.addLayout(m_h_layout)

        splitter.addWidget(vocab_widget)
        
        # New: Auto Learned Vocab
        learned_widget = QWidget()
        learned_layout = QVBoxLayout(learned_widget)
        learned_layout.addWidget(QLabel("💡 自動學習詞彙 (出現多次後會幫助辨識)"))
        self.learned_list = QListWidget()
        learned_layout.addWidget(self.learned_list)
        
        l_h_layout = QHBoxLayout()
        self.btn_promote = QPushButton("升格為自訂")
        self.btn_promote.clicked.connect(self._promote_vocab)
        self.btn_refresh_learned = QPushButton("重新整理")
        self.btn_refresh_learned.setObjectName("secondary")
        self.btn_refresh_learned.clicked.connect(self._refresh_learned_vocab)
        l_h_layout.addWidget(self.btn_promote)
        l_h_layout.addWidget(self.btn_refresh_learned)
        l_h_layout.addStretch()
        learned_layout.addLayout(l_h_layout)
        
        splitter.addWidget(learned_widget)
        splitter.addWidget(mem_widget)
        return widget

    def _create_stats_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self._section_header("📊 使用統計"))
        
        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["時間範圍", "錄音次數", "總時長", "字數"])
        layout.addWidget(self.stats_tree)

        self.btn_refresh_stats = QPushButton("重新整理統計")
        self.btn_refresh_stats.clicked.connect(self._refresh_stats)
        layout.addWidget(self.btn_refresh_stats)
        
        layout.addStretch()

        # 版權聲明
        credit_label = QLabel("主要開發者：吉米丘 | 協助開發者：Gemini + Nebula")
        credit_label.setStyleSheet("color: #888; font-size: 11px; margin-top: 20px;")
        credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credit_label)
        
        return widget

    def _create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        layout.addWidget(self._section_header("⌨️ 快速鍵設定 (點擊後直接按鍵錄製)"))
        
        self.btn_ptt = HotkeyRecorderButton(self.config.get("hotkey_ptt", "alt_r"), self._is_dark)
        self._add_row(layout, "🎙 點按錄音 (Hold)", self.btn_ptt)
        
        self.btn_toggle = HotkeyRecorderButton(self.config.get("hotkey_toggle", "f13"), self._is_dark)
        self._add_row(layout, "🔄 切換錄音 (Toggle)", self.btn_toggle)
        
        self.btn_llm = HotkeyRecorderButton(self.config.get("hotkey_llm", "f14"), self._is_dark)
        self._add_row(layout, "✨ AI 強制處理 (Hold)", self.btn_llm)

        layout.addWidget(self._divider())

        layout.addWidget(self._section_header("🐛 其他"))
        self.debug_mode = QCheckBox("在終端機顯示偵錯資訊 (耗時、內容等)")
        self.debug_mode.setChecked(self.config.get("debug_mode", False))
        layout.addWidget(self.debug_mode)

        self.auto_paste = QCheckBox("自動貼上文字")
        self.auto_paste.setChecked(self.config.get("auto_paste", True))
        layout.addWidget(self.auto_paste)

        layout.addStretch()
        return widget

    # --- Helpers ---
    def _section_header(self, text):
        label = QLabel(text)
        color = "#58a6ff" if self._is_dark else "#007aff"
        label.setStyleSheet(f"font-weight: bold; font-size: 15px; margin-top: 10px; color: {color};")
        return label

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        color = "#444" if self._is_dark else "#eee"
        line.setStyleSheet(f"color: {color};")
        return line

    def _add_row(self, layout, label_text, widget):
        row = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        row.addWidget(label)
        row.addWidget(widget)
        layout.addLayout(row)
        return widget

    # --- Data Loading ---
    def _load_data(self):
        # Load Soul Prompt
        if SOUL_PATH.exists():
            self.soul_prompt.setPlainText(SOUL_PATH.read_text(encoding="utf-8"))
        
        # Load Vocab
        self._refresh_vocab()
        self._refresh_learned_vocab()
        
        # Load Memory
        self._refresh_memory()

        # Load Stats
        self._refresh_stats()

    def _refresh_vocab(self):
        self.vocab_list.clear()
        try:
            from vocab.manager import load_custom_vocab
            for word in load_custom_vocab():
                self.vocab_list.addItem(word)
        except Exception as e:
            print(f"Error loading vocab: {e}")

    def _refresh_learned_vocab(self):
        self.learned_list.clear()
        try:
            from vocab.manager import load_all_learned_words, load_auto_memory
            memory = load_auto_memory()
            for word in load_all_learned_words():
                count = memory.get(word, 0)
                self.learned_list.addItem(f"{word} ({count}次)")
        except Exception as e:
            print(f"Error loading learned vocab: {e}")

    def _promote_vocab(self):
        item = self.learned_list.currentItem()
        if not item: return
        # Extract word from "word (N次)"
        raw_text = item.text()
        word = raw_text.split(" (")[0]
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
                text = (entry.get("llm") or entry.get("stt", ""))[:60]
                item = QTreeWidgetItem([ts, text])
                self.mem_tree.addTopLevelItem(item)
        except Exception as e:
            print(f"Error loading memory: {e}")

    def _refresh_stats(self):
        self.stats_tree.clear()
        try:
            from stats.tracker import get_summary
            s = get_summary()
            rows = [
                ("今日", str(s["today"]["sessions"]), f"{s['today']['duration']}s", str(s["today"]["chars"])),
                ("本週", str(s["week"]["sessions"]), f"{s['week']['duration']}s", str(s["week"]["chars"])),
                ("累積", str(s["total"]["sessions"]), f"{s['total']['duration']}s", str(s["total"]["chars"])),
            ]
            for r in rows:
                self.stats_tree.addTopLevelItem(QTreeWidgetItem(r))
        except Exception as e:
            print(f"Error loading stats: {e}")

    # --- Actions ---
    def _add_vocab(self):
        word = self.vocab_input.text().strip()
        if not word: return
        try:
            from vocab.manager import add_custom_word
            add_custom_word(word)
            self.vocab_input.clear()
            self._refresh_vocab()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    def _del_vocab(self):
        items = self.vocab_list.selectedItems()
        if not items: return
        try:
            from vocab.manager import remove_custom_word
            for item in items:
                remove_custom_word(item.text())
            self._refresh_vocab()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    def _del_memory(self):
        items = self.mem_tree.selectedItems()
        if not items: return
        try:
            from memory.manager import load_memory, save_memory
            memory = load_memory()
            entries = memory.get("entries", [])
            del_ts = {item.text(0) for item in items}
            memory["entries"] = [e for e in entries if e.get("ts", "")[:16] not in del_ts]
            save_memory(memory)
            self._refresh_memory()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    def _clear_memory(self):
        if QMessageBox.question(self, "確認", "確定要清空所有對話記憶嗎？") == QMessageBox.StandardButton.Yes:
            try:
                from memory.manager import clear_memory
                clear_memory()
                self._refresh_memory()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", str(e))

    def _open_data_folder(self):
        import subprocess
        folder = Path(__file__).parent.parent / "memory"
        folder.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(folder)])

    def _save_action(self):
        # Update config object
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
        self.config["hotkey_toggle"] = self.btn_toggle.key_str
        self.config["hotkey_llm"] = self.btn_llm.key_str
        self.config["debug_mode"] = self.debug_mode.isChecked()
        self.config["auto_paste"] = self.auto_paste.isChecked()

        # Save soul.md
        try:
            SOUL_PATH.write_text(self.soul_prompt.toPlainText().strip(), encoding="utf-8")
        except Exception as e:
            print(f"Error saving soul.md: {e}")

        save_config(self.config)
        QMessageBox.information(self, "已儲存", "設定已儲存！部分設定需重啟後生效。")
        
        if self.on_save:
            self.on_save(self.config)
        self.close()

    def run(self):
        self.show()


def has_api_key(config: dict) -> bool:
    """Check if at least one API key is configured (or using local whisper + ollama)."""
    keys_to_check = [
        "groq_api_key", "openai_api_key", "anthropic_api_key",
        "openrouter_api_key", "gemini_api_key", "deepseek_api_key", "qwen_api_key",
    ]
    stt = config.get("stt_engine", "local_whisper")
    llm = config.get("llm_engine", "ollama")

    # Local whisper + ollama don't need external API keys
    if stt == "local_whisper" and (not config.get("llm_enabled") or llm == "ollama"):
        return True

    for k in keys_to_check:
        v = config.get(k, "")
        if v and v not in ("", "YOUR_OPENROUTER_API_KEY", "YOUR_API_KEY"):
            return True
    return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec())
