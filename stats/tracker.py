"""
使用統計追蹤器。
記錄每次錄音的時長與輸出字數，支援今日 / 本週 / 總計查詢。
資料存放：~/voicetype_data/stats.json
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "memory"
STATS_PATH = DATA_DIR / "stats.json"


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_stats() -> dict:
    _ensure_dir()
    if STATS_PATH.exists():
        try:
            with open(STATS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": []}


def save_stats(stats: dict):
    _ensure_dir()
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_session(duration_sec: float, char_count: int):
    """錄音結束後呼叫，記錄這次 session。"""
    stats = load_stats()
    stats["sessions"].append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "duration": round(duration_sec, 2),
        "chars": char_count,
    })
    save_stats(stats)


def get_summary() -> dict:
    """
    回傳統計摘要：
    {
        "today":   {"duration": x, "chars": x, "sessions": x},
        "week":    {"duration": x, "chars": x, "sessions": x},
        "total":   {"duration": x, "chars": x, "sessions": x},
    }
    """
    stats = load_stats()
    sessions = stats.get("sessions", [])
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())

    result = {
        "today": {"duration": 0.0, "chars": 0, "sessions": 0},
        "week":  {"duration": 0.0, "chars": 0, "sessions": 0},
        "total": {"duration": 0.0, "chars": 0, "sessions": 0},
    }

    for s in sessions:
        try:
            ts = datetime.fromisoformat(s["ts"])
        except Exception:
            continue
        dur = s.get("duration", 0)
        chars = s.get("chars", 0)

        result["total"]["duration"] += dur
        result["total"]["chars"] += chars
        result["total"]["sessions"] += 1

        if ts >= week_start:
            result["week"]["duration"] += dur
            result["week"]["chars"] += chars
            result["week"]["sessions"] += 1

        if ts >= today_start:
            result["today"]["duration"] += dur
            result["today"]["chars"] += chars
            result["today"]["sessions"] += 1

    # 格式化秒數
    for k in result:
        result[k]["duration"] = round(result[k]["duration"], 1)

    return result
