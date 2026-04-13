"""
config_manager.py — Eye Care v3
Конфиг хранится рядом со скриптом в config.json
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

BASE_DIR  = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "work_minutes":        20,
    "rest_seconds":        20,
    "color_scheme":        "Neon",
    "custom_hex_color":    "#00FF88",
    "opacity":             0.92,
    "autostart":           False,
    "smart_pause":         True,
    "smart_pause_minutes": 5,
    "strict_mode":         False,
    "fullscreen_mode":     False,
    "sound_enabled":       True,
    "sound_type":          "alert",  # "alert", "beep", "custom", "none"
    "sound_file":          None,      # путь к кастомному звуку
    "monitor_target":      "all",
    "smart_detect":        True,
    "language":            "en",      # "en", "ru", "ua"
    "first_run":           True,      # Флаг первого запуска
    # Позиция и размер overlay окна
    "overlay_width":       560,
    "overlay_height":      400,
    "overlay_x":           None,  # None = центр экрана
    "overlay_y":           None,
    # Размер и позиция окна настроек
    "settings_width":      800,
    "settings_height":     650,
    "settings_x":          None,
    "settings_y":          None,
}

COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
    "Neon": {
        "bg":         "#0a0a0f",
        "accent":     "#00FF88",
        "text":       "#d0fce8",
        "secondary":  "#1a3a28",
        "timer":      "#00FF88",
        "button_bg":  "#00FF88",
        "button_fg":  "#050a07",
        "entry_bg":   "#0d1a12",
        "sep":        "#1a6640",
    },
    "Dark": {
        "bg":         "#16161e",
        "accent":     "#e94560",
        "text":       "#e8e8e8",
        "secondary":  "#2a1a22",
        "timer":      "#e94560",
        "button_bg":  "#e94560",
        "button_fg":  "#ffffff",
        "entry_bg":   "#201820",
        "sep":        "#5a2035",
    },
    "Light": {
        "bg":         "#f4f7fb",
        "accent":     "#2563eb",
        "text":       "#1e293b",
        "secondary":  "#dbeafe",
        "timer":      "#2563eb",
        "button_bg":  "#2563eb",
        "button_fg":  "#ffffff",
        "entry_bg":   "#ffffff",
        "sep":        "#93c5fd",
    },
    "Ocean": {
        "bg":         "#0a1628",
        "accent":     "#00c6fb",
        "text":       "#cce8f4",
        "secondary":  "#0a2a3d",
        "timer":      "#00c6fb",
        "button_bg":  "#00c6fb",
        "button_fg":  "#041020",
        "entry_bg":   "#0d1f30",
        "sep":        "#0a4a6a",
    },
}


class ConfigManager:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._config = {**DEFAULT_CONFIG, **loaded}
            else:
                self._config = DEFAULT_CONFIG.copy()
                self.save()
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Конфиг не загружен: {e}")
            self._config = DEFAULT_CONFIG.copy()

    def save(self) -> None:
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
        except OSError as e:
            logger.error(f"Конфиг не сохранён: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
        self.save()

    def update_bulk(self, updates: Dict[str, Any]) -> None:
        self._config.update(updates)
        self.save()

    def get_color_scheme(self, override_name: str = None) -> Dict[str, str]:
        """
        Возвращает словарь цветов.
        override_name — временная схема (без сохранения), напр. при превью.
        """
        name    = override_name or self._config.get("color_scheme", "Neon")
        custom  = self._config.get("custom_hex_color", "#00FF88")

        if name == "Custom":
            # Строим схему на основе кастомного цвета
            bg = "#0a0a0f"
            return {
                "bg":        bg,
                "accent":    custom,
                "text":      "#ffffff",
                "secondary": "#1a1a1a",
                "timer":     custom,
                "button_bg": custom,
                "button_fg": _contrast_fg(custom),
                "entry_bg":  "#111111",
                "sep":       _darken(custom, 0.5),
            }
        return COLOR_SCHEMES.get(name, COLOR_SCHEMES["Neon"])

    @property
    def all(self) -> Dict[str, Any]:
        return self._config.copy()


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _darken(hex_color: str, factor: float) -> str:
    try:
        r, g, b = _hex_to_rgb(hex_color)
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#333333"


def _contrast_fg(hex_color: str) -> str:
    """Возвращает белый или чёрный в зависимости от яркости фона."""
    try:
        r, g, b = _hex_to_rgb(hex_color)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#000000" if luminance > 0.5 else "#ffffff"
    except Exception:
        return "#000000"
