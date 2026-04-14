import tkinter as tk
import threading, time, logging, random
from typing import Callable, Dict, List, Optional, Tuple
from localization import get_text

logger = logging.getLogger(__name__)

def get_exercises(lang: str = "en") -> List[Dict[str, str]]:
    return [
        {"title": get_text("exercise_rotation", lang),
         "desc": get_text("exercise_rotation_desc", lang)},
        {"title": get_text("exercise_distance", lang),
         "desc": get_text("exercise_distance_desc", lang)},
        {"title": get_text("exercise_blinking", lang),
         "desc": get_text("exercise_blinking_desc", lang)},
        {"title": get_text("exercise_horizontal", lang),
         "desc": get_text("exercise_horizontal_desc", lang)},
        {"title": get_text("exercise_vertical", lang),
         "desc": get_text("exercise_vertical_desc", lang)},
        {"title": get_text("exercise_eight", lang),
         "desc": get_text("exercise_eight_desc", lang)},
        {"title": get_text("exercise_palming", lang),
         "desc": get_text("exercise_palming_desc", lang)},
        {"title": get_text("exercise_near_far", lang),
         "desc": get_text("exercise_near_far_desc", lang)},
    ]


def _get_dpi(root: tk.Tk) -> float:
    try:
        return max(1.0, root.winfo_fpixels("1i") / 96.0)
    except Exception:
        return 1.0


def sc(v: int, scale: float) -> int:
    return max(1, int(v * scale))


class EyeCareOverlay:

    def __init__(
        self,
        rest_seconds:     int,
        colors:           Dict[str, str],
        opacity:          float = 0.92,
        strict_mode:      bool  = False,
        fullscreen:       bool  = False,
        monitor_geometry: Optional[Tuple[int,int,int,int]] = None,
        on_close_callback: Optional[Callable] = None,
        is_preview:       bool  = False,
        config:           Optional = None,
    ):
        self.rest_seconds     = rest_seconds
        self.colors           = colors
        self.opacity          = max(0.1, min(1.0, opacity))
        self.strict_mode      = strict_mode
        self.fullscreen       = fullscreen
        self.monitor_geometry = monitor_geometry
        self.on_close_cb      = on_close_callback
        self.is_preview       = is_preview
        self.config           = config

        self._remaining   = rest_seconds
        self._running     = False
        self._dpi         = 1.0
        
        self.lang = self.config.get("language", "en") if self.config else "en"
        self._exercise    = random.choice(get_exercises(self.lang))

        self._rs_active   = False
        self._rs_edge     = ""
        self._rs_sx       = 0
        self._rs_sy       = 0
        self._rs_ox       = 0
        self._rs_oy       = 0
        self._rs_ow       = 0
        self._rs_oh       = 0

        self._drag_sx     = 0
        self._drag_sy     = 0
        self._drag_ox     = 0
        self._drag_oy     = 0

        self.root:             Optional[tk.Tk]    = None
        self._canvas:          Optional[tk.Canvas] = None
        self._timer_id:        Optional[int]       = None
        self._pb_id:           Optional[int]       = None
        self._pb_bg_id:        Optional[int]       = None
        self._close_id:        Optional[int]       = None
        self._pulse_colors:    List[str]           = []
        self._pulse_idx:       int                 = 0

    def show(self) -> None:
        logger.info(f"[OVERLAY] Открытие overlay (preview={self.is_preview})")
        self.root = tk.Tk()
        self._dpi = _get_dpi(self.root)
        self._configure_window()
        self._build()
        self._start_timer()
        if not self.fullscreen and not self.is_preview:
            self._pulse_step()
        logger.info(f"[OVERLAY] Запуск mainloop (preview={self.is_preview})")
        self.root.mainloop()
        logger.info(f"[OVERLAY] Mainloop finished (preview={self.is_preview})")

    def _configure_window(self) -> None:
        r = self.root
        d = self._dpi
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        r.attributes("-alpha",   self.opacity)
        r.configure(bg=self.colors["bg"])
        
        r.update_idletasks()

        if self.fullscreen:
            sw = r.winfo_screenwidth()
            sh = r.winfo_screenheight()
            r.geometry(f"{sw}x{sh}+0+0")
            logger.info(f"[OVERLAY] Полноэкранный режим: {sw}x{sh}")
        else:
            w = self.config.get("overlay_width", sc(560, d)) if self.config else sc(560, d)
            h = self.config.get("overlay_height", sc(400, d)) if self.config else sc(400, d)
            saved_x = self.config.get("overlay_x") if self.config else None
            saved_y = self.config.get("overlay_y") if self.config else None
            
            r.update_idletasks()
            sw = r.winfo_screenwidth()
            sh = r.winfo_screenheight()
            
            if saved_x is not None and saved_y is not None:
                x, y = saved_x, saved_y
                logger.info(f"[OVERLAY] Используем сохраненную позицию: x={x}, y={y}")
            else:
                x = (sw - w) // 2
                y = (sh - h) // 2
                logger.info(f"[OVERLAY] Центрирование на экране: x={x}, y={y}, sw={sw}, sh={sh}")
            
            logger.info(f"[OVERLAY] Позиционирование: w={w}, h={h}, x={x}, y={y}")
            r.geometry(f"{w}x{h}+{x}+{y}")
            
            if self.is_preview:
                r.resizable(True, True)
                r.minsize(sc(380, d), sc(280, d))
            else:
                r.resizable(False, False)

        r.bind("<Configure>", self._on_configure)
        if not self.fullscreen:
            if self.is_preview:
                r.bind("<ButtonPress-1>",   self._on_press)
                r.bind("<B1-Motion>",       self._on_motion)
                r.bind("<ButtonRelease-1>", self._on_release)
                r.bind("<Motion>",          self._on_hover)
            else:
                r.bind("<ButtonPress-1>",   self._on_press_drag)
                r.bind("<B1-Motion>",       self._on_motion_drag)
                r.bind("<ButtonRelease-1>", self._on_release_drag)

    def _build(self) -> None:
        if self._canvas:
            self._canvas.destroy()
        c = self.colors
        self._canvas = tk.Canvas(
            self.root,
            bg=c["bg"], highlightthickness=0,
        )
        self._canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()
        self._draw_all()

    def _draw_all(self) -> None:
        canvas = self._canvas
        canvas.delete("all")
        
        c = self.colors
        
        self.root.update_idletasks()
        cw = self.root.winfo_width()
        ch = self.root.winfo_height()
        
        if cw < 10: cw = 560
        if ch < 10: ch = 400
        cx = cw // 2

        title_fs = -max(14, int(ch * 0.05))
        timer_fs = -max(40, int(ch * 0.18))
        sub_fs   = -max(12, int(ch * 0.035))
        ex_fs    = -max(16, int(ch * 0.05))
        desc_fs  = -max(12, int(ch * 0.035))
        pb_h     = max(4,  int(ch * 0.02))

        y_title    = int(ch * 0.10)
        y_timer    = int(ch * 0.35)
        y_sub      = int(ch * 0.52)
        y_pb       = int(ch * 0.62)
        y_exercise = int(ch * 0.75)
        y_desc     = int(ch * 0.88)

        canvas.create_rectangle(0, ch-5, cw, ch, fill=c["accent"], outline="")

        canvas.create_text(cx, y_title, anchor="center",
            text=get_text("eye_rest_time", self.lang),
            font=("Segoe UI", title_fs, "bold"), fill=c["text"])

        self._timer_id = canvas.create_text(cx, y_timer, anchor="center",
            text=self._fmt(self._remaining),
            font=("Segoe UI", timer_fs, "bold"), fill=c["timer"])

        canvas.create_text(cx, y_sub, anchor="center",
            text=get_text("seconds_remaining", self.lang),
            font=("Segoe UI", sub_fs), fill=c["sep"])

        pb_w = int(cw * 0.7)
        x0, x1 = cx - pb_w//2, cx + pb_w//2
        self._pb_bg_id = canvas.create_rectangle(x0, y_pb, x1, y_pb + pb_h,
                                               fill=c["secondary"], outline="")
        self._pb_id = canvas.create_rectangle(x0, y_pb, x1, y_pb + pb_h,
                                            fill=c["accent"], outline="")
        self._pb_x0, self._pb_x1, self._pb_y0, self._pb_y1 = x0, x1, y_pb, y_pb + pb_h

        canvas.create_text(cx, y_exercise, anchor="center",
            text=self._exercise["title"],
            font=("Segoe UI", ex_fs, "bold"), fill=c["accent"])

        canvas.create_text(cx, y_desc, anchor="center",
            text=self._exercise["desc"],
            font=("Segoe UI", desc_fs), fill=c["text"],
            width=int(cw * 0.85), justify="center")

        if not self.strict_mode:
            close_size = -max(20, int(ch * 0.06))
            self._close_id = canvas.create_text(cw-30, 30, anchor="center", text="✕",
                font=("Segoe UI", close_size, "bold"), fill=c["sep"], tags="close_btn")
            canvas.tag_bind("close_btn", "<Button-1>", lambda e: self._close())
            
            skip_size = -max(14, int(ch * 0.04))
            canvas.create_text(cx, ch-40, text=get_text("skip", self.lang),
                font=("Segoe UI", skip_size), fill=c["sep"], tags="skip_btn", anchor="center")
            canvas.tag_bind("skip_btn", "<Button-1>", lambda e: self._close())

        self._pulse_colors = [c["timer"], c["accent"], c["sep"]]

    def _on_configure(self, event: tk.Event) -> None:
        if self._canvas and event.widget == self.root:
            self._canvas.config(width=event.width, height=event.height)
            self._draw_all()
            self._update_pb()

    def _start_timer(self) -> None:
        if self.is_preview:
            return
            
        self._running = True
        def loop():
            while self._remaining > 0 and self._running:
                time.sleep(1)
                self._remaining -= 1
                if self.root:
                    try:
                        self.root.after(0, self._tick_ui)
                    except Exception:
                        break
            if self._remaining <= 0 and self._running:
                if self.root:
                    try:
                        self.root.after(0, self._close)
                    except Exception:
                        pass
        threading.Thread(target=loop, daemon=True, name="OverlayTimer").start()

    def _tick_ui(self) -> None:
        if not self._canvas:
            return
        if self._timer_id is not None:
            self._canvas.itemconfig(self._timer_id,
                                    text=self._fmt(self._remaining))
        self._update_pb()

    def _update_pb(self) -> None:
        if self._pb_id is None or not self._canvas:
            return
        pct   = max(0.0, self._remaining / self.rest_seconds)
        fill_x = self._pb_x0 + int((self._pb_x1 - self._pb_x0) * pct)
        self._canvas.coords(self._pb_id,
                            self._pb_x0, self._pb_y0,
                            fill_x,      self._pb_y1)

    def _pulse_step(self) -> None:
        if not self.root or not self._canvas or self._timer_id is None:
            return
        self._pulse_idx = (self._pulse_idx + 1) % len(self._pulse_colors)
        try:
            self._canvas.itemconfig(self._timer_id,
                                    fill=self._pulse_colors[self._pulse_idx])
        except Exception:
            return
        self.root.after(1000, self._pulse_step)

    _BORDER = 10  # пикселей

    def _edge_at(self, x: int, y: int) -> str:
        b = self._BORDER
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        e = ""
        if y <= b:       e += "n"
        elif y >= h - b: e += "s"
        if x <= b:       e += "w"
        elif x >= w - b: e += "e"
        return e

    def _on_press(self, ev: tk.Event) -> None:
        self.root.update_idletasks()
        edge = self._edge_at(ev.x, ev.y)
        if edge:
            self._rs_active = True
            self._rs_edge   = edge
            self._rs_sx     = ev.x_root
            self._rs_sy     = ev.y_root
            self._rs_ox     = self.root.winfo_x()
            self._rs_oy     = self.root.winfo_y()
            self._rs_ow     = self.root.winfo_width()
            self._rs_oh     = self.root.winfo_height()
        else:
            self._rs_active = False
            self._drag_sx   = ev.x_root
            self._drag_sy   = ev.y_root
            self._drag_ox   = self.root.winfo_x()
            self._drag_oy   = self.root.winfo_y()

    def _on_motion(self, ev: tk.Event) -> None:
        if self._rs_active:
            self._do_resize(ev.x_root, ev.y_root)
        else:
            dx = ev.x_root - self._drag_sx
            dy = ev.y_root - self._drag_sy
            nx = self._drag_ox + dx
            ny = self._drag_oy + dy
            self.root.geometry(f"+{nx}+{ny}")

    def _on_release(self, ev: tk.Event) -> None:
        self._rs_active = False

    def _do_resize(self, mx: int, my: int) -> None:
        d   = self._dpi
        MIN_W = sc(380, d)
        MIN_H = sc(280, d)

        dx = mx - self._rs_sx
        dy = my - self._rs_sy

        ox, oy, ow, oh = self._rs_ox, self._rs_oy, self._rs_ow, self._rs_oh
        nx, ny, nw, nh = ox, oy, ow, oh

        edge = self._rs_edge
        if "e" in edge:
            nw = max(MIN_W, ow + dx)
        if "s" in edge:
            nh = max(MIN_H, oh + dy)
        if "w" in edge:
            nw = max(MIN_W, ow - dx)
            nx = ox + ow - nw
        if "n" in edge:
            nh = max(MIN_H, oh - dy)
            ny = oy + oh - nh

        self.root.geometry(f"{nw}x{nh}+{nx}+{ny}")

    def _on_hover(self, ev: tk.Event) -> None:
        edge = self._edge_at(ev.x, ev.y)
        cur = {
            "n":  "top_side",    "s":  "bottom_side",
            "e":  "right_side",  "w":  "left_side",
            "ne": "top_right_corner",  "nw": "top_left_corner",
            "se": "bottom_right_corner","sw": "bottom_left_corner",
        }.get(edge, "")
        self.root.config(cursor=cur)

    def _on_press_drag(self, ev: tk.Event) -> None:
        self._drag_sx = ev.x_root
        self._drag_sy = ev.y_root
        self._drag_ox = self.root.winfo_x()
        self._drag_oy = self.root.winfo_y()

    def _on_motion_drag(self, ev: tk.Event) -> None:
        dx = ev.x_root - self._drag_sx
        dy = ev.y_root - self._drag_sy
        nx = self._drag_ox + dx
        ny = self._drag_oy + dy
        self.root.geometry(f"+{nx}+{ny}")

    def _on_release_drag(self, ev: tk.Event) -> None:
        pass

    def _close(self) -> None:
        logger.info(f"[OVERLAY] Starting close (preview={self.is_preview}, running={self._running})")
        self._running = False
        
        if self.is_preview and self.root and self.config:
            try:
                self.root.update_idletasks()
                w = self.root.winfo_width()
                h = self.root.winfo_height()
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                
                logger.info(f"[OVERLAY] Сохранение позиции preview: w={w}, h={h}, x={x}, y={y}")
                
                self.config.update_bulk({
                    "overlay_width": w,
                    "overlay_height": h,
                    "overlay_x": x,
                    "overlay_y": y
                })
                
                logger.info(f"[OVERLAY] Позиция preview сохранена успешно")
            except Exception as e:
                logger.error(f"[OVERLAY] Error saving position: {e}", exc_info=True)
        
        if self.on_close_cb and not self.is_preview:
            try:
                logger.info("[OVERLAY] Вызов callback...")
                self.on_close_cb()
                logger.info("[OVERLAY] Callback выполнен")
            except Exception as e:
                logger.error(f"[OVERLAY] Error in callback: {e}", exc_info=True)
        
        if self.root:
            try:
                logger.info("[OVERLAY] Отвязка событий...")
                self.root.unbind("<Configure>")
                if not self.fullscreen:
                    if self.is_preview:
                        self.root.unbind("<ButtonPress-1>")
                        self.root.unbind("<B1-Motion>")
                        self.root.unbind("<ButtonRelease-1>")
                        self.root.unbind("<Motion>")
                    else:
                        self.root.unbind("<ButtonPress-1>")
                        self.root.unbind("<B1-Motion>")
                        self.root.unbind("<ButtonRelease-1>")
                
                logger.info("[OVERLAY] Вызов destroy()...")
                self.root.destroy()
                
                logger.info("[OVERLAY] Окно уничтожено")
            except Exception as e:
                logger.error(f"[OVERLAY] Error during close: {e}", exc_info=True)
        
        self._running = False
        logger.info(f"[OVERLAY] Close finished (preview={self.is_preview})")

    @staticmethod
    def _fmt(sec: int) -> str:
        m, s = divmod(max(0, sec), 60)
        return f"{m:02d}:{s:02d}" if m > 0 else str(s)
