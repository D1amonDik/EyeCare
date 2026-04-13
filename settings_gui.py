"""
settings_gui.py — Eye Care v4
Простое компактное окно 660×520. Без прокрутки. Без фоновых потоков.
- tk.Var создаются ПОСЛЕ Tk() → нет RuntimeError
- Прозрачность: кнопка "Тест" открывает Toplevel, слайдер меняет alpha напрямую
- Custom цвет работает корректно
- Смена темы сохраняет активную вкладку
- Предпросмотр overlay в отдельном потоке (простой threading.Thread)
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import threading, logging, sys, os
from typing import Callable, Dict, Optional

from config_manager import ConfigManager, COLOR_SCHEMES
from localization import get_text

logger = logging.getLogger(__name__)


def _dpi(root) -> float:
    try:
        return max(1.0, root.winfo_fpixels("1i") / 96.0)
    except Exception:
        return 1.0


def sc(v: int, d: float) -> int:
    return max(1, int(v * d))


class SettingsWindow:
    def __init__(self, config: ConfigManager, on_saved: Optional[Callable] = None):
        self.config   = config
        self.on_saved = on_saved
        self.root:    Optional[tk.Tk] = None
        self._d       = 1.0
        self._saved_tab_idx   = 0
        self._opacity_preview: Optional[tk.Toplevel] = None
        
        # Получаем текущий язык
        self.lang = self.config.get("language", "en")
        
        # Все tk.Var — None до вызова show()
        self._var_work    = None
        self._var_rest    = None
        self._var_opacity = None
        self._var_smart   = None
        self._var_idle    = None
        self._var_scheme  = None
        self._var_hex     = None
        self._var_sound   = None
        self._var_full    = None
        self._var_strict  = None
        self._var_auto    = None
        self._var_detect  = None
        self._var_monitor = None
        self._var_sound_type = None
        self._var_sound_file = None
        self._var_language = None
    
    def t(self, key: str) -> str:
        """Shortcut для получения переведенного текста."""
        return get_text(key, self.lang)

    # ─────────────────────────────────────────────
    # Создание переменных (ПОСЛЕ Tk()!)
    # ─────────────────────────────────────────────

    def _init_vars(self) -> None:
        cfg = self.config
        self._var_work    = tk.IntVar(value=cfg.get("work_minutes",         20))
        self._var_rest    = tk.IntVar(value=cfg.get("rest_seconds",         20))
        self._var_opacity = tk.DoubleVar(value=cfg.get("opacity",          0.92))
        self._var_smart   = tk.BooleanVar(value=cfg.get("smart_pause",     True))
        self._var_idle    = tk.IntVar(value=cfg.get("smart_pause_minutes",    5))
        self._var_scheme  = tk.StringVar(value=cfg.get("color_scheme",   "Neon"))
        self._var_hex     = tk.StringVar(value=cfg.get("custom_hex_color","#00FF88"))
        self._var_sound   = tk.BooleanVar(value=cfg.get("sound_enabled",  True))
        self._var_full    = tk.BooleanVar(value=cfg.get("fullscreen_mode",False))
        self._var_strict  = tk.BooleanVar(value=cfg.get("strict_mode",   False))
        self._var_auto    = tk.BooleanVar(value=cfg.get("autostart",      False))
        self._var_detect  = tk.BooleanVar(value=cfg.get("smart_detect",   True))
        self._var_monitor = tk.StringVar(value=str(cfg.get("monitor_target","all")))
        self._var_sound_type = tk.StringVar(value=cfg.get("sound_type", "system"))
        self._var_sound_file = tk.StringVar(value=cfg.get("sound_file", ""))
        self._var_language = tk.StringVar(value=cfg.get("language", "en"))

    # ─────────────────────────────────────────────
    # Запуск
    # ─────────────────────────────────────────────

    def show(self) -> None:
        self.root = tk.Tk()
        self._d   = _dpi(self.root)
        d         = self._d

        self._init_vars()  # ← ПОСЛЕ tk.Tk()

        self.root.title(self.t("settings_title"))
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        
        # Привязываем обработчик resize для адаптивности текста
        self.root.bind("<Configure>", self._on_window_resize)

        # Получаем сохраненные размеры и позицию
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        saved_w = self.config.get("settings_width", 800)
        saved_h = self.config.get("settings_height", 650)
        saved_x = self.config.get("settings_x")
        saved_y = self.config.get("settings_y")
        
        # Размеры окна (БЕЗ масштабирования - используем сохраненные пиксели напрямую)
        win_w = max(480, min(saved_w, int(sw * 0.9)))
        win_h = max(400, min(saved_h, int(sh * 0.9)))
        
        # Позиция окна
        if saved_x is not None and saved_y is not None:
            # Используем сохраненную позицию
            win_x = saved_x
            win_y = saved_y
        else:
            # Центрируем
            win_x = (sw - win_w) // 2
            win_y = (sh - win_h) // 2
        
        self.root.geometry(f"{win_w}x{win_h}+{win_x}+{win_y}")
        self.root.minsize(sc(480, d), sc(400, d))

        c = self.config.get_color_scheme(self._var_scheme.get())
        self.root.configure(bg=c["bg"])
        self._build(c)
        self.root.mainloop()
    
    def _on_window_resize(self, event):
        """Обработчик изменения размера окна для адаптивности текста."""
        # Игнорируем события от дочерних виджетов
        if event.widget != self.root:
            return
        
        # Пересчитываем масштаб на основе размера окна
        try:
            # Базовые размеры окна
            base_w = 600
            base_h = 500
            
            # Текущие размеры
            current_w = event.width
            current_h = event.height
            
            # Вычисляем масштаб по обеим осям и берем среднее
            scale_w = current_w / base_w
            scale_h = current_h / base_h
            scale = (scale_w + scale_h) / 2
            
            # Ограничиваем масштаб разумными пределами
            new_d = max(0.7, min(2.0, scale))
            
            # Перестраиваем UI только если масштаб значительно изменился
            if abs(new_d - self._d) > 0.05:
                self._d = new_d
                c = self.config.get_color_scheme(self._var_scheme.get())
                self._build(c)
        except Exception:
            pass

    # ─────────────────────────────────────────────
    # Построение UI
    # ─────────────────────────────────────────────

    def _build(self, c: Dict) -> None:
        r = self.root
        d = self._d

        for w in r.winfo_children():
            w.destroy()
        r.configure(bg=c["bg"])

        # ── Заголовок ──────────────────────────────────────
        hdr = tk.Frame(r, bg=c["accent"], height=sc(46, d))
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"👁  {self.t('app_name')} — {self.t('settings_title').split('—')[1].strip()}",
                 font=("Segoe UI", sc(13, d), "bold"),
                 bg=c["accent"], fg=c["button_fg"]
                 ).pack(side="left", padx=sc(16, d))

        # ── Нижние кнопки (всегда видны) ───────────────────
        tk.Frame(r, bg=c["sep"], height=1).pack(side="bottom", fill="x")
        bot = tk.Frame(r, bg=c["bg"])
        bot.pack(side="bottom", fill="x", padx=sc(14, d), pady=sc(8, d))
        self._mkbtn(bot, f"  {self.t('save')}  ", c, self._save,    "right", True)
        self._mkbtn(bot, f"  {self.t('cancel')}  ",    c, self._close,   "right", False)
        self._mkbtn(bot, self.t('reset'),       c, self._reset_all_settings, "left", False)
        self._mkbtn(bot, self.t('preview'), c, self._preview, "left", False)

        # ── Notebook ───────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("S.TNotebook",
                        background=c["bg"], borderwidth=0)
        style.configure("S.TNotebook.Tab",
                        background=c["bg"], foreground=c["text"],
                        padding=[sc(12, d), sc(6, d)],
                        font=("Segoe UI", sc(11, d)))  # Увеличен с 10 до 11
        style.map("S.TNotebook.Tab",
                  background=[("selected", c["accent"])],
                  foreground=[("selected", c["button_fg"])])
        style.configure("S.TFrame", background=c["bg"])

        nb = ttk.Notebook(r, style="S.TNotebook")
        nb.pack(fill="both", expand=True)
        self._nb = nb

        for title, builder in [
            (self.t("tab_timer"),       self._tab_timer),
            (self.t("tab_appearance"), self._tab_appearance),
            (self.t("tab_behavior"),    self._tab_behavior),
            (self.t("tab_stats"),  self._tab_stats),
        ]:
            frm = ttk.Frame(nb, style="S.TFrame")
            nb.add(frm, text=title)
            inner = tk.Frame(frm, bg=c["bg"])
            inner.pack(fill="both", expand=True,
                       padx=sc(18, d), pady=sc(10, d))
            builder(inner, c)

        try:
            nb.select(self._saved_tab_idx)
        except Exception:
            pass

    # ─────────────────────────────────────────────
    # Вкладка: Таймер
    # ─────────────────────────────────────────────

    def _tab_timer(self, f: tk.Frame, c: Dict) -> None:
        d = self._d
        self._sec(f, self.t("work_time"), c)
        self._slider_entry(f, c, self._var_work, 1, 60, self.t("minutes"))

        self._sec(f, self.t("rest_time"), c)
        self._slider_entry(f, c, self._var_rest, 10, 300, self.t("seconds"))

        self._sec(f, self.t("smart_pause"), c)
        self._chk(f, self.t("smart_pause_desc"), self._var_smart, c)

        row = tk.Frame(f, bg=c["bg"])
        row.pack(anchor="w", pady=(sc(3, d), 0))
        tk.Label(row, text=self.t("threshold"),
                 font=("Segoe UI", sc(11, d)),
                 bg=c["bg"], fg=c["text"]).pack(side="left")
        tk.Spinbox(
            row, from_=1, to=60, textvariable=self._var_idle,
            width=4, font=("Segoe UI", sc(11, d)),
            bg=c["entry_bg"], fg=c["accent"],
            buttonbackground=c["sep"],
            highlightthickness=0,
        ).pack(side="left", padx=(sc(6, d), sc(4, d)))
        tk.Label(row, text=self.t("minutes"), font=("Segoe UI", sc(11, d)),
                 bg=c["bg"], fg=c["text"]).pack(side="left")

    # ─────────────────────────────────────────────
    # Вкладка: Внешний вид
    # ─────────────────────────────────────────────

    def _tab_appearance(self, f: tk.Frame, c: Dict) -> None:
        d = self._d

        # ── Схемы ──────────────────────────────────────────
        self._sec(f, self.t("color_scheme"), c)
        row = tk.Frame(f, bg=c["bg"])
        row.pack(anchor="w", pady=(sc(2, d), sc(8, d)))
        for name in list(COLOR_SCHEMES.keys()) + ["Custom"]:
            tk.Radiobutton(
                row, text=name,
                variable=self._var_scheme, value=name,
                font=("Segoe UI", sc(11, d)),
                bg=c["bg"], fg=c["text"],
                selectcolor=c["bg"],
                activebackground=c["bg"],
                activeforeground=c["accent"],
                command=self._apply_theme,
            ).pack(side="left", padx=(0, sc(10, d)))

        # ── Custom HEX ─────────────────────────────────────
        hex_row = tk.Frame(f, bg=c["bg"])
        hex_row.pack(anchor="w", pady=(0, sc(10, d)))
        tk.Label(hex_row, text=self.t("custom_hex"),
                 font=("Segoe UI", sc(11, d)),
                 bg=c["bg"], fg=c["text"]).pack(side="left")
        tk.Entry(
            hex_row, textvariable=self._var_hex, width=9,
            font=("Segoe UI", sc(11, d)),
            bg=c["entry_bg"], fg=c["accent"],
            insertbackground=c["accent"],
            highlightthickness=1,
            highlightcolor=c["accent"],
            highlightbackground=c["sep"],
        ).pack(side="left", padx=(sc(6, d), sc(6, d)))
        self._color_dot = tk.Label(
            hex_row, text="   ",
            bg=self._safe_hex(self._var_hex.get()),
        )
        self._color_dot.pack(side="left", padx=(0, sc(6, d)))
        pick = tk.Label(hex_row, text=f" {self.t('pick')} ",
                        font=("Segoe UI", sc(10, d)),
                        bg=c["sep"], fg=c["button_fg"],
                        cursor="hand2", padx=sc(4, d), pady=sc(2, d))
        pick.pack(side="left", padx=(sc(6, d), 0))
        pick.bind("<Button-1>", self._pick_color)
        self._var_hex.trace_add("write", self._hex_changed)

        # ── Прозрачность ───────────────────────────────────
        self._sec(f, self.t("opacity"), c)

        op_row = tk.Frame(f, bg=c["bg"])
        op_row.pack(anchor="w", pady=(sc(2, d), sc(2, d)))

        self._op_slider = tk.Scale(
            op_row, from_=0.1, to=1.0, resolution=0.05,
            orient="horizontal", variable=self._var_opacity,
            bg=c["bg"], fg=c["text"],
            troughcolor=c["secondary"], activebackground=c["accent"],
            highlightthickness=0,
            length=sc(310, d), sliderlength=sc(18, d),
            showvalue=False,
            command=self._opacity_moved,
        )
        self._op_slider.pack(side="left")

        self._op_val_lbl = tk.Label(
            op_row,
            text=f"{self._var_opacity.get():.2f}",
            font=("Segoe UI", sc(11, d), "bold"),
            bg=c["bg"], fg=c["accent"], width=5,
        )
        self._op_val_lbl.pack(side="left", padx=(sc(8, d), sc(6, d)))

        # Кнопка "Тест" — открывает/закрывает плавающее окошко
        test_btn = tk.Label(
            op_row, text=f" {self.t('test')} ",
            font=("Segoe UI", sc(9, d)),
            bg=c["sep"], fg=c["button_fg"],
            cursor="hand2", padx=sc(6, d), pady=sc(3, d),
        )
        test_btn.pack(side="left")
        test_btn.bind("<Button-1>", lambda e: self._toggle_opacity_preview())

        tk.Label(
            f,
            text=self.t("opacity_hint"),
            font=("Segoe UI", sc(9, d), "italic"),
            bg=c["bg"], fg=c["sep"],
        ).pack(anchor="w", pady=(sc(2, d), 0))

        # ── Звук ───────────────────────────────────────────
        self._sec(f, self.t("sound"), c)
        
        sound_options = [
            ("alert", self.t("sound_alert")),
            ("beep", self.t("sound_beep")),
            ("custom", self.t("sound_custom")),
            ("none", self.t("sound_none")),
        ]
        
        for val, label in sound_options:
            sound_row = tk.Frame(f, bg=c["bg"])
            sound_row.pack(anchor="w", pady=sc(1, d))
            
            rb = tk.Radiobutton(
                sound_row, text=label,
                variable=self._var_sound_type, value=val,
                font=("Segoe UI", sc(10, d)),
                bg=c["bg"], fg=c["text"],
                selectcolor=c["bg"],
                activebackground=c["bg"],
                activeforeground=c["accent"],
                command=lambda v=val: self._on_sound_select(v),
            )
            rb.pack(side="left")
        
        # Выбор файла (показывается только для custom)
        self._sound_file_frame = tk.Frame(f, bg=c["bg"])
        self._sound_file_frame.pack(anchor="w", pady=(sc(4, d), 0))
        
        tk.Label(self._sound_file_frame, text=self.t("sound_file"),
                 font=("Segoe UI", sc(10, d)),
                 bg=c["bg"], fg=c["text"]).pack(side="left")
        
        self._sound_file_entry = tk.Entry(
            self._sound_file_frame, textvariable=self._var_sound_file, width=30,
            font=("Segoe UI", sc(9, d)),
            bg=c["entry_bg"], fg=c["accent"],
            insertbackground=c["accent"],
            highlightthickness=1,
            highlightcolor=c["accent"],
            highlightbackground=c["sep"],
        )
        self._sound_file_entry.pack(side="left", padx=(sc(6, d), sc(6, d)))
        
        browse_btn = tk.Label(
            self._sound_file_frame, text=f" {self.t('browse')} ",
            font=("Segoe UI", sc(9, d)),
            bg=c["sep"], fg=c["button_fg"],
            cursor="hand2", padx=sc(6, d), pady=sc(2, d),
        )
        browse_btn.pack(side="left")
        browse_btn.bind("<Button-1>", lambda e: self._browse_sound())
        
        # Обновляем видимость UI
        self._update_sound_ui()

    def _on_sound_select(self, sound_type: str) -> None:
        """Вызывается при выборе звука - автоматически проигрывает его."""
        self._update_sound_ui()
        # Автоматически проигрываем выбранный звук
        if sound_type != "custom":
            self._test_sound()
    
    def _update_sound_ui(self, *_) -> None:
        """Показывает/скрывает UI выбора файла в зависимости от типа звука."""
        if self._var_sound_type.get() == "custom":
            self._sound_file_frame.pack(anchor="w", pady=(sc(4, self._d), 0))
        else:
            self._sound_file_frame.pack_forget()
    
    def _browse_sound(self) -> None:
        """Открывает диалог выбора звукового файла."""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            parent=self.root,
            title=self.t("sound_file") if self.lang == "ru" else "Select sound file",
            filetypes=[
                ("Аудио файлы", "*.mp3 *.wav *.ogg"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("OGG", "*.ogg"),
                ("Все файлы", "*.*")
            ]
        )
        if filename:
            self._var_sound_file.set(filename)
            # Автоматически проигрываем выбранный файл
            self._test_sound()
    
    def _test_sound(self) -> None:
        """Тестирует выбранный звук."""
        sound_type = self._var_sound_type.get()
        sound_file = self._var_sound_file.get()
        
        if sound_type == "none":
            return
        
        if sound_type == "custom":
            if not sound_file or not os.path.exists(sound_file):
                return
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
            except ImportError:
                messagebox.showerror(self.t("error"),
                                 f"{self.t('error')}:\n{e}",
                                 parent=self.root)
            except Exception as e:
                messagebox.showerror(self.t("error"), f"{self.t('sound_play_error')} {e}", parent=self.root)
        else:
            # Встроенные звуки
            if sys.platform == "win32":
                try:
                    import winsound
                    
                    if sound_type == "alert":
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                    elif sound_type == "beep":
                        winsound.Beep(800, 400)
                except Exception:
                    pass

    # ─────────────────────────────────────────────
    # Вкладка: Поведение
    # ─────────────────────────────────────────────

    def _tab_behavior(self, f: tk.Frame, c: Dict) -> None:
        d = self._d

        self._sec(f, self.t("overlay_mode"), c)
        self._chk(f, self.t("fullscreen_mode"), self._var_full, c)
        self._chk(f, self.t("strict_mode"), self._var_strict, c)

        self._sec(f, self.t("system"), c)
        self._chk(f, self.t("autostart"), self._var_auto, c)
        self._chk(f, self.t("smart_detect"), self._var_detect, c)

        self._sec(f, self.t("language"), c)
        lang_f = tk.Frame(f, bg=c["bg"])
        lang_f.pack(anchor="w")
        
        from localization import get_language_name
        for lang_code in ["en", "ru", "ua"]:
            tk.Radiobutton(
                lang_f, text=get_language_name(lang_code),
                variable=self._var_language, value=lang_code,
                font=("Segoe UI", sc(10, d)),
                bg=c["bg"], fg=c["text"],
                selectcolor=c["bg"],
                activebackground=c["bg"],
                activeforeground=c["accent"],
            ).pack(anchor="w", pady=sc(1, d))
        
        tk.Label(lang_f, text="(Restart required / Требуется перезапуск)",
                 font=("Segoe UI", sc(8, d), "italic"),
                 bg=c["bg"], fg=c["sep"]).pack(anchor="w", pady=(sc(4, d), 0))

        self._sec(f, self.t("monitor"), c)
        mon_f = tk.Frame(f, bg=c["bg"])
        mon_f.pack(anchor="w")
        monitors = self._get_monitors()
        for val, label in [(self.t("all_monitors") if val == "all" else f"#{i + 1}: {m}", val) 
                           for i, (val, m) in enumerate([("all", "")] + [(str(i), m) for i, m in enumerate(monitors)])]:
            if val == self.t("all_monitors"):
                label = self.t("all_monitors")
                val = "all"
            tk.Radiobutton(
                mon_f, text=label,
                variable=self._var_monitor, value=val,
                font=("Segoe UI", sc(10, d)),
                bg=c["bg"], fg=c["text"],
                selectcolor=c["bg"],
                activebackground=c["bg"],
                activeforeground=c["accent"],
            ).pack(anchor="w", pady=sc(1, d))

    # ─────────────────────────────────────────────
    # Вкладка: Статистика
    # ─────────────────────────────────────────────

    def _tab_stats(self, f: tk.Frame, c: Dict) -> None:
        d = self._d
        from stats_manager import StatsManager
        sm    = StatsManager(lang=self.lang)
        today = sm.get_today_breaks()
        total = sm.get_total_breaks()
        GOAL  = 8

        self._sec(f, self.t("today"), c)
        pct  = min(1.0, today / GOAL)
        pb_w = sc(400, d)
        pb_h = sc(22, d)
        cnv  = tk.Canvas(f, width=pb_w, height=pb_h,
                         bg=c["secondary"], highlightthickness=0)
        cnv.pack(anchor="w", pady=(sc(4, d), sc(4, d)))
        cnv.create_rectangle(0, 0, int(pb_w * pct), pb_h,
                             fill=c["accent"], outline="")
        cnv.create_text(
            pb_w // 2, pb_h // 2, anchor="center",
            text=f"{today}/{GOAL} {self.t('breaks')} ({int(pct * 100)}%)",
            fill=c["button_fg"],
            font=("Segoe UI", sc(9, d), "bold"),
        )
        tk.Label(f, text=f"{self.t('total_all_time')} {total}",
                 font=("Segoe UI", sc(10, d)),
                 bg=c["bg"], fg=c["text"]).pack(anchor="w")

        self._sec(f, self.t("last_7_days"), c)
        for lbl, cnt in sm.get_weekly_summary():
            row = tk.Frame(f, bg=c["bg"])
            row.pack(anchor="w", pady=sc(2, d))
            tk.Label(row, text=lbl, width=4,
                     font=("Segoe UI", sc(9, d)),
                     bg=c["bg"], fg=c["text"], anchor="w").pack(side="left")
            bw = sc(220, d)
            bh = sc(12, d)
            bc = tk.Canvas(row, width=bw, height=bh,
                           bg=c["secondary"], highlightthickness=0)
            bc.pack(side="left", padx=(sc(4, d), sc(4, d)))
            bc.create_rectangle(0, 0, int(bw * min(1.0, cnt / GOAL)), bh,
                                fill=c["accent"], outline="")
            tk.Label(row, text=str(cnt),
                     font=("Segoe UI", sc(9, d), "bold"),
                     bg=c["bg"], fg=c["accent"]).pack(side="left")

        rst = tk.Label(
            f, text=f" {self.t('reset_stats')} ",
            font=("Segoe UI", sc(9, d)),
            bg=c["sep"], fg=c["button_fg"],
            cursor="hand2", padx=sc(6, d), pady=sc(3, d),
        )
        rst.pack(anchor="w", pady=(sc(12, d), 0))
        rst.bind("<Button-1>", lambda e: self._reset_stats())

    # ─────────────────────────────────────────────
    # Слайдер + Entry (двусторонняя синхронизация)
    # ─────────────────────────────────────────────

    def _slider_entry(self, parent, c: Dict, var,
                      from_, to, unit,
                      is_float=False, res=1) -> None:
        d   = self._d
        fmt = (lambda v: f"{float(v):.2f}") if is_float else \
              (lambda v: str(int(float(v))))
        e_var = tk.StringVar(value=fmt(var.get()))

        row = tk.Frame(parent, bg=c["bg"])
        row.pack(anchor="w", pady=(0, sc(10, d)))

        tk.Scale(
            row, from_=from_, to=to, resolution=res,
            orient="horizontal", variable=var,
            bg=c["bg"], fg=c["text"],
            troughcolor=c["secondary"], activebackground=c["accent"],
            highlightthickness=0,
            length=sc(310, d), sliderlength=sc(18, d),
            showvalue=False,
        ).pack(side="left")

        tk.Entry(
            row, textvariable=e_var, width=6,
            font=("Segoe UI", sc(10, d)),
            bg=c["entry_bg"], fg=c["accent"],
            insertbackground=c["accent"],
            justify="center",
            highlightthickness=1,
            highlightcolor=c["accent"],
            highlightbackground=c["sep"],
        ).pack(side="left", padx=(sc(8, d), sc(4, d)))

        if unit:
            tk.Label(row, text=unit,
                     font=("Segoe UI", sc(10, d)),
                     bg=c["bg"], fg=c["text"]).pack(side="left")

        # slider → entry
        def _from_slider(*_):
            try:
                e_var.set(fmt(var.get()))
            except Exception:
                pass
        var.trace_add("write", _from_slider)

        # entry → slider
        def _from_entry(*_):
            try:
                v = float(e_var.get())
                clamped = max(from_, min(to, v))
                var.set(round(clamped, 2) if is_float else int(clamped))
            except Exception:
                pass
        e_var.trace_add("write", _from_entry)

    # ─────────────────────────────────────────────
    # Прозрачность: ползунок + тестовое окошко
    # ─────────────────────────────────────────────

    def _opacity_moved(self, value) -> None:
        """Вызывается при каждом движении ползунка прозрачности."""
        val = float(value)
        # Обновляем метку
        try:
            self._op_val_lbl.config(text=f"{val:.2f}")
        except Exception:
            pass
        # Если тестовое окошко открыто — меняем его alpha напрямую
        if self._opacity_preview and self._opacity_preview.winfo_exists():
            try:
                self._opacity_preview.attributes("-alpha", val)
            except Exception:
                pass
            # Обновляем текст внутри
            try:
                for w in self._opacity_preview.winfo_children():
                    if isinstance(w, tk.Label):
                        txt = w.cget("text")
                        if ":" in txt and any(c.isdigit() for c in txt):
                            w.config(text=f"{self.t('opacity')}: {val:.2f}")
                            break
            except Exception:
                pass

    def _toggle_opacity_preview(self) -> None:
        """Открывает или закрывает тестовое окошко прозрачности."""
        if self._opacity_preview and self._opacity_preview.winfo_exists():
            self._opacity_preview.destroy()
            self._opacity_preview = None
            return

        c   = self.config.get_color_scheme(self._var_scheme.get())
        d   = self._d
        val = float(self._var_opacity.get())

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", val)
        win.configure(bg=c["bg"])

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = sc(300, d)
        wh = sc(110, d)
        win.geometry(f"{ww}x{wh}+{(sw - ww) // 2}+{(sh - wh) // 2}")

        tk.Label(win, text=f"👁  {self.t('test')} {self.t('opacity')}",
                 font=("Segoe UI", sc(13, d), "bold"),
                 bg=c["bg"], fg=c["accent"]).pack(pady=(sc(14, d), sc(4, d)))
        tk.Label(win, text=f"{self.t('opacity')}: {val:.2f}",
                 font=("Segoe UI", sc(11, d)),
                 bg=c["bg"], fg=c["text"]).pack()
        hint_text = "Click 'Test' again to close" if self.lang == "en" else "(кликни «Тест» снова чтобы закрыть)" if self.lang == "ru" else "(клікни «Тест» знову щоб закрити)"
        tk.Label(win, text=hint_text,
                 font=("Segoe UI", sc(8, d)),
                 bg=c["bg"], fg=c["sep"]).pack(pady=(sc(4, d), 0))

        win.bind("<Button-1>", lambda e: self._toggle_opacity_preview())
        self._opacity_preview = win

    # ─────────────────────────────────────────────
    # Мгновенная смена темы (остаёмся на вкладке)
    # ─────────────────────────────────────────────

    def _apply_theme(self) -> None:
        try:
            self._saved_tab_idx = self._nb.index(self._nb.select())
        except Exception:
            self._saved_tab_idx = 0
        self.config._config["custom_hex_color"] = self._safe_hex(
            self._var_hex.get()
        )
        c = self.config.get_color_scheme(self._var_scheme.get())
        self._build(c)

    # ─────────────────────────────────────────────
    # Предпросмотр overlay
    # ─────────────────────────────────────────────

    def _preview(self) -> None:
        """Запускает overlay в отдельном процессе — без блокировки настроек."""
        import subprocess
        import sys
        
        self.config._config["custom_hex_color"] = self._safe_hex(
            self._var_hex.get()
        )
        
        # Создаем скрипт для запуска preview
        script = f'''
import sys
import os
import logging

# Настраиваем логирование для preview
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(r"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eye_care.log')}", encoding="utf-8"),
    ],
)
logger = logging.getLogger("PreviewProcess")
logger.info("[PREVIEW] Запуск preview процесса")

sys.path.insert(0, r"{os.path.dirname(os.path.abspath(__file__))}")

try:
    from overlay import EyeCareOverlay
    from config_manager import ConfigManager

    config = ConfigManager()
    config._config["custom_hex_color"] = "{self._safe_hex(self._var_hex.get())}"
    c = config.get_color_scheme("{self._var_scheme.get()}")
    
    logger.info("[PREVIEW] Создание overlay")

    EyeCareOverlay(
        rest_seconds      = {max(5, int(self._var_rest.get()))},
        colors            = c,
        opacity           = {float(self._var_opacity.get())},
        strict_mode       = False,
        fullscreen        = False,
        monitor_geometry  = None,
        on_close_callback = None,
        is_preview        = True,
        config            = config,  # Передаем config для сохранения позиции
    ).show()
    
    logger.info("[PREVIEW] Preview finished")
except Exception as e:
    logger.error(f"[PREVIEW] Error: {{e}}", exc_info=True)
'''
        
        try:
            # Запускаем в отдельном процессе
            logger.info("Запуск preview процесса")
            subprocess.Popen([sys.executable, "-c", script],
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        except Exception as e:
            logger.error(f"Preview error: {e}", exc_info=True)

    # ─────────────────────────────────────────────
    # Сохранение
    # ─────────────────────────────────────────────

    def _save(self) -> None:
        try:
            # ВАЖНО: Перезагружаем конфиг с диска, чтобы получить актуальные координаты overlay,
            # которые могли быть сохранены окном preview
            self.config.load()
            logger.info("[SAVE] Конфиг перезагружен с диска перед сохранением")
            
            # Формируем словарь обновлений ТОЛЬКО для полей, которые редактируются в настройках
            # Координаты overlay НЕ включаем - они уже в self.config._config после load()
            updates = {
                "work_minutes":        max(1,   min(60,  int(self._var_work.get()))),
                "rest_seconds":        max(10,  min(300, int(self._var_rest.get()))),
                "color_scheme":        self._var_scheme.get(),
                "custom_hex_color":    self._safe_hex(self._var_hex.get()),
                "opacity":             round(max(0.1, min(1.0,
                                           float(self._var_opacity.get()))), 2),
                "autostart":           bool(self._var_auto.get()),
                "smart_pause":         bool(self._var_smart.get()),
                "smart_pause_minutes": max(1, min(60, int(self._var_idle.get()))),
                "strict_mode":         bool(self._var_strict.get()),
                "fullscreen_mode":     bool(self._var_full.get()),
                "sound_enabled":       bool(self._var_sound.get()),
                "sound_type":          self._var_sound_type.get(),
                "sound_file":          self._var_sound_file.get() if self._var_sound_file.get() else None,
                "monitor_target":      self._var_monitor.get(),
                "smart_detect":        bool(self._var_detect.get()),
                "language":            self._var_language.get(),
            }
            
            logger.info(f"[SAVE] Сохранение настроек (координаты overlay сохраняются автоматически)")
                
        except Exception as e:
            messagebox.showerror(self.t("error"),
                                 f"{self.t('error')}:\n{e}",
                                 parent=self.root)
            return

        self.config.update_bulk(updates)

        if sys.platform == "win32":
            self._set_autostart(updates["autostart"])

        # Показываем красивое уведомление вместо messagebox
        self._show_save_notification()
        logger.info("Settings saved.")

    def _reset_all_settings(self) -> None:
        """Сбрасывает все настройки на значения по умолчанию (кроме размера окна настроек)."""
        if not messagebox.askyesno(self.t("reset_confirm"), 
                                    self.t("reset_message"),
                                    parent=self.root):
            return
        
        # Сохраняем текущий размер и позицию окна настроек
        settings_w = self.config.get("settings_width", 800)
        settings_h = self.config.get("settings_height", 650)
        settings_x = self.config.get("settings_x")
        settings_y = self.config.get("settings_y")
        
        # Загружаем дефолтные настройки
        from config_manager import DEFAULT_CONFIG
        self.config._config = DEFAULT_CONFIG.copy()
        
        # Восстанавливаем размер окна настроек
        self.config._config["settings_width"] = settings_w
        self.config._config["settings_height"] = settings_h
        self.config._config["settings_x"] = settings_x
        self.config._config["settings_y"] = settings_y
        
        # Сохраняем
        self.config.save()
        
        # Перезагружаем UI
        self._init_vars()
        c = self.config.get_color_scheme()
        self._build(c)
        
        self._show_save_notification()
        logger.info("Settings reset to defaults")

    def _show_save_notification(self) -> None:
        """Показывает красивое уведомление о сохранении в окне настроек."""
        if not self.root:
            return
            
        c = self.config.get_color_scheme(self._var_scheme.get())
        d = self._d
        
        # Создаем уведомление в верхней части окна
        notif = tk.Frame(self.root, bg=c["accent"], height=sc(50, d))
        notif.place(relx=0.5, rely=0, anchor="n", relwidth=1.0)
        
        tk.Label(notif, text=self.t("saved"),
                 font=("Segoe UI", sc(12, d), "bold"),
                 bg=c["accent"], fg=c["button_fg"]).pack(expand=True)
        
        # Автоматически скрываем через 2 секунды
        def hide():
            try:
                notif.destroy()
            except Exception:
                pass
        
        self.root.after(2000, hide)

    def _close(self) -> None:
        # Сохраняем размер и позицию окна настроек
        if self.root:
            try:
                self.root.update_idletasks()
                w = self.root.winfo_width()
                h = self.root.winfo_height()
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                
                # Сохраняем реальные пиксели (БЕЗ деления на DPI)
                self.config.update_bulk({
                    "settings_width": w,
                    "settings_height": h,
                    "settings_x": x,
                    "settings_y": y
                })
                logger.info(f"Settings window size and position saved: {w}x{h} at ({x}, {y})")
            except Exception as e:
                logger.warning(f"Failed to save window size: {e}")
        
        if self._opacity_preview:
            try:
                self._opacity_preview.destroy()
            except Exception:
                pass
        if self.root:
            self.root.destroy()
            self.root = None

    # ─────────────────────────────────────────────
    # Вспомогательные виджеты
    # ─────────────────────────────────────────────

    def _sec(self, parent, text: str, c: Dict) -> None:
        d = self._d
        tk.Label(parent, text=text,
                 font=("Segoe UI", sc(11, d), "bold"),
                 bg=c["bg"], fg=c["accent"],
                 ).pack(anchor="w", pady=(sc(10, d), sc(1, d)))
        tk.Frame(parent, bg=c["sep"], height=1).pack(
            fill="x", pady=(0, sc(4, d)))

    def _chk(self, parent, text: str, var, c: Dict) -> None:
        d = self._d
        tk.Checkbutton(
            parent, text=text, variable=var,
            font=("Segoe UI", sc(10, d)),
            bg=c["bg"], fg=c["text"],
            selectcolor=c["bg"],
            activebackground=c["bg"],
            activeforeground=c["accent"],
        ).pack(anchor="w", pady=sc(1, d))

    def _mkbtn(self, parent, text: str, c: Dict,
               cmd: Callable, side="left", primary=True) -> None:
        d  = self._d
        bg = c["button_bg"] if primary else c["sep"]
        fg = c["button_fg"]
        btn = tk.Label(parent, text=text,
                       font=("Segoe UI", sc(10, d),
                             "bold" if primary else "normal"),
                       bg=bg, fg=fg, cursor="hand2",
                       padx=sc(12, d), pady=sc(6, d))
        btn.pack(side=side, padx=(0 if side == "left" else sc(8, d), 0))
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.config(bg=c["accent"],
                                                    fg=c["button_fg"]))
        btn.bind("<Leave>",    lambda e: btn.config(bg=bg, fg=fg))

    def _pick_color(self, _=None) -> None:
        color = colorchooser.askcolor(
            color=self._safe_hex(self._var_hex.get()),
            title=self.t("pick") if self.lang == "en" else "Выберите цвет",
            parent=self.root,
        )
        if color and color[1]:
            self._var_hex.set(color[1])
            self._var_scheme.set("Custom")
            self._apply_theme()

    def _hex_changed(self, *_) -> None:
        try:
            hex_val = self._safe_hex(self._var_hex.get())
            self._color_dot.config(bg=hex_val)
            # Если выбран Custom, применяем изменения сразу
            if self._var_scheme.get() == "Custom":
                self.config._config["custom_hex_color"] = hex_val
                # Обновляем только цвета без перестройки всего UI
                c = self.config.get_color_scheme("Custom")
                if self.root:
                    self.root.configure(bg=c["bg"])
        except Exception:
            pass

    def _reset_stats(self) -> None:
        if messagebox.askyesno(self.t("reset_confirm"), self.t("reset_stats_confirm"),
                               parent=self.root):
            from stats_manager import StatsManager
            StatsManager().reset()
            messagebox.showinfo(self.t("saved"), self.t("stats_reset"),
                                parent=self.root)

    @staticmethod
    def _safe_hex(h: str) -> str:
        try:
            s = h.strip()
            if s.startswith("#") and len(s) in (4, 7):
                int(s[1:], 16)
                return s
        except Exception:
            pass
        return "#00FF88"

    @staticmethod
    def _get_monitors():
        try:
            import screeninfo
            return [f"{m.width}×{m.height}" for m in screeninfo.get_monitors()]
        except Exception:
            return ["основной"]

    def _set_autostart(self, enable: bool) -> None:
        try:
            import winreg
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            exe = f'"{sys.executable}" "{os.path.abspath("main.py")}"'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0,
                                winreg.KEY_SET_VALUE) as k:
                if enable:
                    winreg.SetValueEx(k, "EyeCare", 0, winreg.REG_SZ, exe)
                else:
                    try:
                        winreg.DeleteValue(k, "EyeCare")
                    except FileNotFoundError:
                        pass
        except Exception as e:
            logger.warning(f"Autostart: {e}")
