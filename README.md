# VoiceType4TW - Mac 嘴炮輸入法

主要開發者：吉米丘  
協助開發者：Gemini、Nebula  

macOS本地語音輸入工具，按下快捷鍵開始講話，系統自動幫你辨識並輸入到任何應用程式裡面

---

## 為什麼做這套工具

靈感來自TypeLess這類語音輸入工具，但因為授權限制與雲端依賴，我就想：能不能做一套「完全可以在本地端自己掌握」的語音輸入工具  
於是就結合Apple Silicon的本地Whisper能力，再加上Gemini、Nebula等AI夥伴，一起打造出這套專為Mac打造的VoiceType4TW，也就是嘴炮輸入法

---

## 功能特色

- 全域快捷鍵觸發(可自訂)  
- Push-to-talk或Toggle兩種啟動模式  
- 本地Whisper語音辨識(faster-whisper，支援Apple Silicon加速)  
- 可選Groq API雲端辨識  
- 可選AI文字潤飾(Ollama / OpenAI / Claude)  
- macOS Menu Bar控制  
- 浮動錄音狀態視窗(底部中央顯示目前狀態)  
- **Instant Translation 魔術語模式**：不用先進設定，只要用講的就能切換翻譯語言  
- **UI強化**：沉浸式置底狀態列、藍色模式前綴、自動置中佈局  
- **智慧詞彙學習**：自動學習你常講的專有名詞與關鍵字，提升辨識精準度  
- **不搶焦點設計**：深度調整macOS視窗屬性，錄音與輸出時，不會把游標焦點搶走  

---

## 魔術語指令 Magic Commands

你可以直接用語音啟動或關閉翻譯模式，螢幕會有閃光與音效提示目前狀態

### 啟動翻譯

說出以下類型指令，即會切換為翻譯模式，並將後續內容翻譯成指定語言：

- 「把下面這段話翻譯成英文」  
- 「以下內容翻譯成日文」  
- 「把內容翻譯成德文」  

### 恢復正常模式

想回到一般語音輸入模式時，可以說：

- 「恢復正常」  
- 「取消翻譯」  
- 「回到正常模式」  

---

## 工作流程

1. 按下你設定好的快捷鍵開始講話  
2. 系統透過本地Whisper或Groq雲端進行語音辨識  
3. 可選擇直接輸出文字，或先丟給LLM做潤飾、整理口氣、調整風格  
4. 輸出結果自動送回目前有輸入焦點的應用程式  
5. 若使用魔術語，則會在流程中自動進行翻譯後再輸出  

---

## 安裝

```bash
# 建議使用 Python 3.11+
pip install -r requirements.txt
```

---

## 設定

編輯 `config.json`：

| 欄位            | 說明                                                | 預設值          |
|-----------------|-----------------------------------------------------|-----------------|
| `hotkey`        | 快捷鍵(right_option / right_shift / right_ctrl / f13-f15) | `right_option` |
| `trigger_mode`  | 觸發模式(push_to_talk / toggle)                    | `push_to_talk`  |
| `stt_engine`    | 語音引擎(local_whisper / groq)                     | `local_whisper` |
| `whisper_model` | Whisper模型大小(tiny/base/small/medium/large)      | `medium`        |
| `groq_api_key`  | Groq API Key(使用groq引擎時填入)                  | `""`            |
| `llm_enabled`   | 是否啟用AI文字潤飾                                 | `false`         |
| `llm_engine`    | LLM引擎(ollama / openai / claude)                  | `ollama`        |
| `language`      | 辨識語言                                           | `zh`            |

---

## 執行

```bash
python main.py
```

首次執行需在：

> 系統設定 > 隱私權與安全性 > 輔助使用  

將終端機(或你使用的執行工具)加入允許清單，讓程式可以模擬鍵盤輸入

---

## 系統需求

- macOS 12+  
- Python 3.11+  
- Apple Silicon 或 Intel Mac  

---

## 支援與回饋

如果你覺得嘴炮輸入法對你有幫助，歡迎：

- 在GitHub按顆星支持  
- 分享給身邊常需要打字、開會做紀錄、寫文件的朋友  
- 請吉米喝杯咖啡、小額贊助，支持持續開發  

有任何功能建議、Bug回報、或想一起共創的點子，都可以：

- 直接在GitHub開Issue  
- 透過吉米的SNS管道來找我聊聊  
