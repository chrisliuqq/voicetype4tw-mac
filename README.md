# VoiceType Mac

macOS 本地語音輸入工具。按下快捷鍵說話,自動辨識並輸入到任何應用程式。

## 功能
- 全域快捷鍵觸發(可自訂)
- Push-to-talk 或 Toggle 兩種模式
- 本地 Whisper 語音辨識(faster-whisper,支援 Apple Silicon 加速)
- 可選 Groq API 雲端辨識
- 可選 AI 文字潤飾(Ollama / OpenAI / Claude)
- macOS Menu Bar 控制
- 浮動錄音狀態視窗(底部中央)

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
