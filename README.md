# VoiceType4TW 嘴砲輸入法 (v2.5.0 Pro)

主要開發者：吉米丘  
協助開發者：Gemini、Nebula (Google AI)

全方位本地語音輸入工具，按下快捷鍵即刻開講，AI 自動幫你潤飾、翻譯並精準輸入到任何視窗。

---

## 為什麼做這套工具

![Dashboard](assets/screenshot-01.png)

靈感來自TypeLess這類語音輸入工具，但因為授權限制與雲端依賴，我就想：能不能做一套「完全可以在本地端自己掌握」的語音輸入工具  
於是就結合Apple Silicon的本地Whisper能力，再加上Gemini、Nebula等AI夥伴，一起打造出這套專為Mac打造的VoiceType4TW，也就是嘴砲輸入法

---

![辨識AI](assets/screenshot-02.png)

## 功能特色

- **跨平台支援**：全新重構，原生支援 macOS (Universal) 與 Windows 10/11。
- **全域快捷鍵**：按住說話 (PTT) 或 切換開關 (Toggle)，反應迅速不卡頓。
- **神經級辨識**：搭載本地 Faster-Whisper，支援各平台硬體加速。
- **✨ 三層式靈魂系統**：結合「基底靈魂 + 情境模板 + 格式決定」，打造個人化 AI 風格。
- **⚡️ 旗艦預設情境**：隨附商務英文、專業回應、社群貼文、情商大師等優質人格。
- **Instant Translation 魔術語**：用語音即時切換翻譯模式，無需動手操作設定。
- **不搶焦點設計**：深度優化視窗屬性，確保文字直接精準注入當前編輯位置。
- **智慧詞彙學習**：自動記憶專有名詞與常用關鍵字。

---

## 浮動錄音狀態視窗

![浮動錄音狀態視窗](assets/screenshot-miclevel.jpg)

這裡有多種模式呈現

- 左側沒有AI的字樣，直接辨識、輸出
- 左側有AI的部分，透過LLM做修飾完成之後再輸出
- 黃色模式，當我們的語音講完之後，它就開始做辨識
- 翻譯成英文，當你直接講中文，它就會翻譯成英文
- 翻譯成日文，當你直接講中文，它就會翻譯成日文


---

## ✨ 靈魂治理：三層疊加系統

這套系統最核心的特色在於您可以自由調配 AI 的「靈魂組成」：

1.  **🏠 基底靈魂 (Base)**：定義 AI 的核心價值觀，例如：不廢話、修正錯字、繁體中文輸出。
2.  **🎭 情境模板 (Scenario)**：定義特定場合的對話風格，如：`💼 商務回應`、`🌐 商務英文`、`📱 社群貼文`。
3.  **📝 輸出格式 (Format)**：決定最後呈現的樣子，例如：電子郵件格式、條列式筆記、Markdown 表格。

透過 Menu Bar 可以隨時組合不同靈魂，讓輸入法真正成為您的私人助理。

---

## 詞彙記憶

![詞彙記憶](assets/screenshot-04.png)
因為吉米常常需要輸入一些專有名詞，或者是客戶的品牌名稱，所以我在這個地方設計了一個詞彙新增的功能，可以手動輸入我們想要辨識的專有名詞

甚至我這邊是設定了，當一個詞彙出現三次以上，他會自動把它記錄起來

因為有了「養龍蝦」觀念的經驗之後，我也希望它能夠擁有一個長期記錄

每一週，它會去把當週所有的記憶做一個濃縮之後再另存起來，讓它持續保有我們之前所有的記憶

我的想法是這樣子啦


---

![翻譯功能](assets/screenshot-menubar.jpg)

## 魔術語指令 Magic Commands

你可以直接用語音啟動或關閉翻譯模式，螢幕會有閃光與音效提示目前狀態，或是在系統列上快速切換

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

## 數據統計

![數據統計](assets/screenshot-05.png)

這套系統會記錄你輸入了多少語音，語音總長度是多少，然後再除以一般人平均每分鐘的打字字數，總結出幫你省下多少時間的統計。

希望讓大家長久使用下來，能夠看到一個漂亮的數據！

---

## 系統設定

![系統設定](assets/screenshot-06.png)

設定成要按哪個按鈕來觸發語音輸入法的設定頁面。在這個地方可以按住錄音的呈現，錄音切換這個部分，我現在還在調整當中。強制AI處理這部分，其實我沒有MenuBar的選單就可以了。這部分我來修改一下好了。

結果自動貼上，這玩意兒就是會把我們輸入之後的文字，自動貼上我們所在Focus的視窗輸入頁面上面，同時也會存在剪貼簿裡面。

如果說它沒有出現的話，你只要直接按Ctrl-V貼上就可以了。

然後，如果你是喜歡看這個輸出結果的話，你可以啟用詳細一日制輸出，這個只有在Terminal的視窗上面會出現，這是我們在Debug的時候使用的。


---

## 工作流程

1. 按下你設定好的快捷鍵開始講話  
2. 系統透過本地Whisper或Groq雲端進行語音辨識  
3. 可選擇直接輸出文字，或先丟給LLM做潤飾、整理口氣、調整風格  
4. 輸出結果自動送回目前有輸入焦點的應用程式  
5. 若使用魔術語，則會在流程中自動進行翻譯後再輸出  

---

---

## 💻 各平台快速安裝

### macOS (Apple Silicon / Intel)
打開終端機，貼上這行指令：
```bash
curl -fsSL https://raw.githubusercontent.com/jfamily4tw/voicetype4tw-mac/main/install.sh | bash
```

### Windows (PC 版)
1. 下載本專案並進入目錄。
2. 執行 `pip install -r requirements-win.txt`。
3. 執行 `python main.py` 即可在系統列看到🎙圖示。

---

## 手動安裝

如果你想自己來，也可以手動操作：

```bash
# 1. Clone 專案
git clone https://github.com/jfamily4tw/voicetype4tw-mac.git
cd voicetype4tw-mac

# 2. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動
python main.py
```

> ⚠️ 首次執行時，macOS 會詢問你是否允許「終端機」使用麥克風與輔助使用權限，請務必允許。  
> 路徑：系統設定 → 隱私權與安全性 → 麥克風 / 輔助使用

---

## 設定

編輯 `config.json`：

| 欄位            | 說明                                                | 預設值          |
|-----------------|-----------------------------------------------------|-----------------| 
| `hotkey`        | 快捷鍵(right_option / right_shift / right_ctrl / f13-f15) | `right_option` |
| `trigger_mode`  | 觸發模式(push_to_talk / toggle)                    | `push_to_talk`  |
| `stt_engine`    | 語音引擎(local_whisper / mlx_whisper / groq)       | `local_whisper` |
| `whisper_model` | Whisper模型大小(tiny/base/small/medium/large)      | `medium`        |
| `groq_api_key`  | Groq API Key(使用groq引擎時填入)                  | `""`            |
| `llm_enabled`   | 是否啟用AI文字潤飾                                 | `false`         |
| `llm_engine`    | LLM引擎(ollama / openai / claude)                  | `ollama`        |
| `language`      | 辨識語言                                           | `zh`            |

---

## 系統需求

- macOS 12+  
- Python 3.10+  
- Apple Silicon（推薦，可用 MLX 加速）或 Intel Mac  

---

## 支援與回饋

<img src="assets/donate-linepay.jpg" alt="歡迎抖內" width="200" />

如果你覺得嘴砲輸入法對你有幫助，歡迎：

- 在GitHub按顆星支持  
- 分享給身邊常需要打字、開會做紀錄、寫文件的朋友  
- 請吉米喝杯咖啡、小額贊助，支持持續開發  

有任何功能建議、Bug回報、或想一起共創的點子，都可以：

- 直接在GitHub開Issue  
- 透過吉米的SNS管道來找我聊聊  
