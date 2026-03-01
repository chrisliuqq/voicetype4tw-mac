import webbrowser
import time
from datetime import datetime
import httpx

def get_weather():
    """使用 wttr.in 獲取當地天氣文字描述。"""
    try:
        # wttr.in/?format=3 回傳簡短的一行天氣
        response = httpx.get("https://wttr.in/?format=3", timeout=5.0)
        if response.status_code == 200:
            return f"當前天氣：{response.text.strip()}"
    except Exception as e:
        return f"無法獲取天氣資訊：{e}"
    return "天氣伺服器暫時沒有回應。"

def get_current_time():
    now = datetime.now()
    return f"現在時間是：{now.strftime('%Y-%m-%d %H:%M:%S')}"

def open_google_search(query: str):
    if not query: return "請提供搜尋關鍵字。"
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"已在瀏覽器開啟 Google 搜尋：{query}"

def open_website(url: str):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"已開啟網頁：{url}"

def run_calculator(expr: str):
    # 簡單的計算機邏輯，使用安全的計算方式或交給 LLM
    # 這裡先做基礎字串清理與 eval (注意安全性)
    clean_expr = expr.replace("x", "*").replace("÷", "/").replace("加", "+").replace("減", "-").replace("乘", "*").replace("除以", "/")
    # 移除所有非數字與運算符
    import re
    clean_expr = re.sub(r'[^\d\+\-\*\/\.\(\) ]', '', clean_expr)
    try:
        result = eval(clean_expr)
        return f"計算結果：{expr} = {result}"
    except Exception:
        return f"抱歉，我算不出來：{expr}"
