"""
VocabEditor - 詞彙庫 GUI 編輯器
使用原生 Tkinter，支援：
- 查看/新增/刪除 自定義詞彙
- 查看/刪除 自動記憶詞彙
- 直接開啟 JSON 檔案位置
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path
import sys
import os

# 動態加入 project root 到 path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vocab.manager import (
    load_custom_vocab, add_custom_word, remove_custom_word,
    load_auto_memory, _save_auto_memory,
    CUSTOM_VOCAB_PATH, AUTO_MEMORY_PATH, AUTO_LEARN_THRESHOLD
)


class VocabEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VoiceType 詞彙庫管理")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        # Notebook (分頁)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- 分頁1: 自定義詞彙 ---
        self.custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.custom_frame, text="✏️ 自定義詞彙")
        self._build_custom_tab()

        # --- 分頁2: 自動記憶 ---
        self.auto_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auto_frame, text="🧠 自動記憶")
        self._build_auto_tab()

        # --- 底部按鈕 ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="開啟檔案位置", command=self._open_folder).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="關閉", command=self.root.destroy).pack(side=tk.RIGHT)

    def _build_custom_tab(self):
        # 說明
        ttk.Label(self.custom_frame, text="手動新增的專有名詞、品牌名、術語，優先辨識這些詞彙。",
                  foreground="gray").pack(anchor=tk.W, padx=10, pady=(10, 0))

        # 列表
        list_frame = ttk.Frame(self.custom_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.custom_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                          font=("PingFang TC", 13), selectmode=tk.EXTENDED)
        self.custom_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.custom_listbox.yview)

        # 輸入區
        input_frame = ttk.Frame(self.custom_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.custom_entry = ttk.Entry(input_frame, font=("PingFang TC", 13))
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.custom_entry.bind("<Return>", lambda e: self._add_custom())

        ttk.Button(input_frame, text="新增", command=self._add_custom).pack(side=tk.LEFT)
        ttk.Button(input_frame, text="刪除選取", command=self._remove_custom).pack(side=tk.LEFT, padx=(5, 0))

    def _build_auto_tab(self):
        ttk.Label(self.auto_frame,
                  text=f"從歷史轉錄自動學習的詞彙（出現 {AUTO_LEARN_THRESHOLD} 次以上標示為常用）。",
                  foreground="gray").pack(anchor=tk.W, padx=10, pady=(10, 0))

        # 列表（顯示詞彙 + 出現次數）
        list_frame = ttk.Frame(self.auto_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("word", "count", "status")
        self.auto_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=15)
        self.auto_tree.heading("word", text="詞彙")
        self.auto_tree.heading("count", text="出現次數")
        self.auto_tree.heading("status", text="狀態")
        self.auto_tree.column("word", width=200)
        self.auto_tree.column("count", width=100, anchor=tk.CENTER)
        self.auto_tree.column("status", width=120, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, command=self.auto_tree.yview)
        self.auto_tree.configure(yscrollcommand=scrollbar.set)
        self.auto_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.auto_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="刪除選取", command=self._remove_auto).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="清除全部記憶", command=self._clear_auto).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(btn_frame, text="重新整理", command=self._refresh_all).pack(side=tk.RIGHT)

    def _refresh_all(self):
        # 刷新自定義列表
        self.custom_listbox.delete(0, tk.END)
        for word in load_custom_vocab():
            self.custom_listbox.insert(tk.END, word)

        # 刷新自動記憶
        for item in self.auto_tree.get_children():
            self.auto_tree.delete(item)
        memory = load_auto_memory()
        for word, count in sorted(memory.items(), key=lambda x: -x[1]):
            status = "✅ 常用" if count >= AUTO_LEARN_THRESHOLD else "學習中"
            self.auto_tree.insert("", tk.END, values=(word, count, status))

    def _add_custom(self):
        word = self.custom_entry.get().strip()
        if not word:
            return
        add_custom_word(word)
        self.custom_entry.delete(0, tk.END)
        self._refresh_all()

    def _remove_custom(self):
        selected = self.custom_listbox.curselection()
        if not selected:
            return
        words = [self.custom_listbox.get(i) for i in selected]
        for word in words:
            remove_custom_word(word)
        self._refresh_all()

    def _remove_auto(self):
        selected = self.auto_tree.selection()
        if not selected:
            return
        memory = load_auto_memory()
        for item in selected:
            word = self.auto_tree.item(item)["values"][0]
            memory.pop(str(word), None)
        _save_auto_memory(memory)
        self._refresh_all()

    def _clear_auto(self):
        if messagebox.askyesno("確認", "確定要清除所有自動記憶詞彙嗎？"):
            _save_auto_memory({})
            self._refresh_all()

    def _open_folder(self):
        folder = CUSTOM_VOCAB_PATH.parent
        subprocess.run(["open", str(folder)])

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    VocabEditor().run()
