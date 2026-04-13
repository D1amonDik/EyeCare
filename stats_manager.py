"""stats_manager.py — Eye Care v3"""

import json, logging, os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)
STATS_FILE = Path(__file__).parent / "stats.json"


class StatsManager:
    def __init__(self, lang: str = "en"):
        self._data: Dict[str, int] = {}
        self.lang = lang
        self._load()

    def _load(self):
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception as e:
            logger.warning(f"stats load: {e}")

    def _save(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
                f.flush(); os.fsync(f.fileno())
        except Exception as e:
            logger.error(f"stats save: {e}")

    def record_break(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self._data[today] = self._data.get(today, 0) + 1
        self._save()

    def get_today_breaks(self) -> int:
        return self._data.get(datetime.now().strftime("%Y-%m-%d"), 0)

    def get_weekly_summary(self) -> List[Tuple[str, int]]:
        # Дни недели на разных языках
        if self.lang == "ru":
            labels = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
            today_label = "Сег"
            yesterday_label = "Вчр"
        elif self.lang == "ua":
            labels = ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"]
            today_label = "Сьг"
            yesterday_label = "Вчр"
        else:  # en
            labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
            today_label = "Tod"
            yesterday_label = "Yes"
        
        result = []
        for i in range(6, -1, -1):
            d = datetime.now() - timedelta(days=i)
            key = d.strftime("%Y-%m-%d")
            lbl = today_label if i == 0 else (yesterday_label if i == 1 else labels[d.weekday()])
            result.append((lbl, self._data.get(key, 0)))
        return result

    def get_total_breaks(self) -> int:
        return sum(self._data.values())

    def reset(self):
        self._data = {}
        self._save()
