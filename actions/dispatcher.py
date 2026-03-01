import re
from actions.builtins import get_weather, get_current_time, open_google_search, open_website, run_calculator

class ActionDispatcher:
    def __init__(self, injector, indicator):
        self.injector = injector
        self.indicator = indicator

    def dispatch(self, text: str) -> bool:
        """
        解析語音文字，如果匹配到指令則執行動作並回傳 True，否則回傳 False。
        """
        text = text.strip("。，！？ ")
        
        # 1. 天氣
        if re.search(r"天氣(如何|怎麼樣|好不好)?$", text) or "查天氣" in text:
            result = get_weather()
            self._finish_action(result)
            return True
            
        # 2. 時間
        if re.search(r"(現在)?幾點(了)?$|現在時間", text):
            result = get_current_time()
            self._finish_action(result)
            return True
            
        # 3. 搜尋
        search_match = re.search(r"(幫我)?(搜尋|搜一下|查一下|查詢一下|查詢|查|找一下)(.+)", text)
        if search_match:
            query = search_match.group(3).strip()
            # 移除開頭或結尾的贅詞以提升搜尋精準度
            # 例如 "幫我查一下 [特斯拉的股價]" 中的 "一下" 可能被誤抓進 query
            query = re.sub(r"^(一下|看看|看看是|到底|一下關於)", "", query).strip()
            query = re.sub(r"(是多少|幾塊錢|是多少錢|的價格|是什麼|是什麼呢)$", "", query).strip()
            result = open_google_search(query)
            self._finish_action(result)
            return True
            
        # 4. 開網頁
        web_match = re.search(r"(打開|開啟)(?:網站)?(.+)", text)
        if web_match:
            site = web_match.group(2).strip()
            # 排除掉常見的情境名稱，避免誤觸
            if site not in ["客訴模式", "IG模式", "正常模式"]:
                result = open_website(site)
                self._finish_action(result)
                return True

        # 5. 計算機
        if re.search(r"\d+[\+\-\*\/x加減乘除]", text):
            result = run_calculator(text)
            self._finish_action(result)
            return True

        return False

    def _finish_action(self, msg: str):
        """執行完動作後的統一回饋。"""
        self.indicator.flash()
        self.indicator.set_state("done")
        # 語音指令的回應通常也直接注入到目前輸入框，或是僅在 Dashboard 顯示
        # 這裡設定直接注入，方便使用者直接得到答案
        self.injector.inject(f"「{msg}」")
