# VoiceType4TW - Mac

主要開發者：吉米丘
協助開發者：Gemini、Nebula

macOS 本地語音輸入工具。按下快捷鍵說話,自動辨識並輸入到任何應用程式。

## 功能
- 全域快捷鍵觸發(可自訂)
- Push-to-talk 或 Toggle 兩種模式
- 本地 Whisper 語音辨識(faster-whisper,支援 Apple Silicon 加速)
- 可選 Groq API 雲端辨識
- 可選 AI 文字潤飾(Ollama / OpenAI / Claude)
- macOS Menu Bar 控制
- 浮動錄音狀態視窗(底部中央)
- **Instant Translation (魔術語模式)**：無需進設定，直接用說的即可切換翻譯語言。
- **UI 強化**：沉浸式置底狀態列、藍色模式前綴、自動置中佈局。
- **智慧詞彙學習**：自動學習您的常用詞，提升辨識精準度。
- **不搶焦點設計**：深度優化 macOS 視窗屬性，錄音時不影響原本應用程式的輸入焦點。

## 魔術語指令 (Magic Commands)

您可以透過語音直接啟動翻譯模式，程式會發出閃光與音效回饋：

- **啟動翻譯**：「把下面這段話翻譯成英文」、「以下內容翻譯成日文」、「把內容翻譯成德文」。
- **恢復正常**：「恢復正常」、「取消翻譯」、「回到正常模式」。

## 安裝

```bash
# 建議使用 Python 3.11+
pip install -r requirements.txt
```

## 設定

編輯 `config.json`:

| 欄位 | 說明 | 預設值 |
|------|------|--------|
| `hotkey` | 快捷鍵(right_option / right_shift / right_ctrl / f13-f15) | `right_option` |
| `trigger_mode` | 觸發模式(push_to_talk / toggle) | `push_to_talk` |
| `stt_engine` | 語音引擎(local_whisper / groq) | `local_whisper` |
| `whisper_model` | Whisper 模型大小(tiny/base/small/medium/large) | `medium` |
| `groq_api_key` | Groq API Key(使用 groq 引擎時填入) | `""` |
| `llm_enabled` | 是否啟用 AI 文字潤飾 | `false` |
| `llm_engine` | LLM 引擎(ollama / openai / claude) | `ollama` |
| `language` | 辨識語言 | `zh` |

## 執行

```bash
python main.py
```

首次執行需在「系統設定 > 隱私權與安全性 > 輔助使用」將終端機加入允許清單。

## 系統需求
- macOS 12+
- Python 3.11+
- Apple Silicon 或 Intel Mac
