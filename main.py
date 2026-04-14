import sys, os, time, threading, logging, ctypes
from pathlib import Path
from typing import List, Optional, Tuple
from ctypes import wintypes

LOG_FILE = Path(__file__).parent / "eye_care.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("EyeCare")

def _set_dpi():
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

_set_dpi()

import socket

LOCK_PORT = 48129
_lock_socket = None

def is_already_running():
    global _lock_socket
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _lock_socket.bind(('127.0.0.1', LOCK_PORT))
        _lock_socket.listen(1)
        return False
    except OSError as e:
        logger.info(f"Port {LOCK_PORT} is busy: {e}")
        _lock_socket = None
        return True

from config_manager import ConfigManager
from stats_manager  import StatsManager
from idle_detector  import IdleDetector
from overlay        import EyeCareOverlay
from localization   import get_text

try:
    import pystray
    from pystray import MenuItem as Item
    from PIL import Image, ImageDraw
    TRAY_OK = True
except ImportError:
    TRAY_OK = False
    logger.warning("pystray/Pillow не найдены — трей недоступен.")

try:
    import screeninfo
    SCREEN_OK = True
except ImportError:
    SCREEN_OK = False


class EyeCareApp:
    def __init__(self):
        self.config  = ConfigManager()
        self.stats   = StatsManager(lang=self.config.get("language", "en"))
        self.idle:   Optional[IdleDetector] = None
        self.tray    = None

        self._running      = False
        self._overlay_up   = False
        self._idle_paused  = False
        self._elapsed      = 0
        self._lock         = threading.Lock()
        self._quit_ev      = threading.Event()

        self._start_idle()
        
        if self.config.get("first_run", True):
            logger.info("First run detected - opening settings")
            self.config.set("first_run", False)
            threading.Thread(target=self._open_settings, daemon=True).start()

    def start(self):
        if self._running:
            return
        self._running = True
        self._elapsed = 0
        threading.Thread(target=self._loop, daemon=True, name="WorkTimer").start()
        logger.info("Timer started.")

    def _loop(self):
        while self._running and not self._quit_ev.is_set():
            time.sleep(1)
            with self._lock:
                if self._overlay_up or self._idle_paused:
                    continue
                self._elapsed += 1

            if self._elapsed >= self.config.get("work_minutes", 20) * 60:
                with self._lock:
                    self._elapsed = 0
                if self.config.get("smart_detect", True) and self._is_fullscreen():
                    logger.info("Fullscreen app detected - skipping break.")
                    continue
                self._break()

    def _break(self):
        import subprocess
        import sys
        
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "--overlay"]
        else:
            cmd = [sys.executable, sys.argv[0], "--overlay"]

        try:
            logger.info(f"[MAIN] Starting overlay: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            process.wait() 
        except Exception as e:
            logger.error(f"[MAIN] Error starting overlay: {e}")

    def _show_overlay(self, geom, record):
        logger.info(f"[MAIN] Starting overlay (record={record}, geom={geom})")
        c = self.config.get_color_scheme()
        def on_close():
            logger.info(f"[MAIN] Overlay close callback (record={record})")
            if record:
                logger.info("[MAIN] Recording break statistics")
                self.stats.record_break()
            logger.info("[MAIN] Callback finished")
        
        try:
            EyeCareOverlay(
                rest_seconds     = self.config.get("rest_seconds", 20),
                colors           = c,
                opacity          = self.config.get("opacity", 0.92),
                strict_mode      = self.config.get("strict_mode", False),
                fullscreen       = self.config.get("fullscreen_mode", False),
                monitor_geometry = geom,
                on_close_callback= on_close,
            ).show()
            logger.info(f"[MAIN] Overlay closed (record={record})")
        except Exception as e:
            logger.error(f"[MAIN] Error in overlay: {e}", exc_info=True)

    def reset_timer(self):
        with self._lock:
            self._elapsed     = 0
            self._idle_paused = False

    def _start_idle(self):
        if not self.config.get("smart_pause", True):
            return
        mins = self.config.get("smart_pause_minutes", 5)
        self.idle = IdleDetector(
            idle_threshold_seconds=mins * 60,
            on_idle  =self._on_idle,
            on_active=self._on_active,
        )
        self.idle.start()

    def _on_idle(self):
        with self._lock:
            self._idle_paused = True
        logger.info("Smart Idle: paused.")

    def _on_active(self):
        with self._lock:
            self._idle_paused = False
            self._elapsed = 0
        logger.info("Smart Idle: reset.")

    def setup_tray(self):
        if not TRAY_OK:
            return
        lang = self.config.get("language", "en")
        img  = self._tray_icon()
        menu = pystray.Menu(
            Item(f"👁  {get_text('app_name', lang)}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            Item(get_text("menu_settings", lang),      lambda *_: threading.Thread(
                target=self._open_settings, daemon=True).start()),
            Item(get_text("menu_break_now", lang), lambda *_: threading.Thread(
                target=self._break, daemon=True).start()),
            Item(get_text("menu_reset_timer", lang),lambda *_: self.reset_timer()),
            pystray.Menu.SEPARATOR,
            Item(get_text("menu_exit", lang),          lambda *_: self._quit()),
        )
        self.tray = pystray.Icon("EyeCare", img, "Eye Care", menu)

    def _open_settings(self):
        import subprocess
        import sys
        
        if getattr(sys, 'frozen', False):
            cmd = [sys.executable, "--settings"]
        else:
            cmd = [sys.executable, sys.argv[0], "--settings"]

        logger.info(f"[MAIN] Opening settings: {' '.join(cmd)}")
        try:
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
        except Exception as e:
            logger.error(f"Failed to open settings: {e}")

    def _tray_icon(self):
        img = Image.new("RGBA", (64, 64), (0,0,0,0))
        d   = ImageDraw.Draw(img)
        d.ellipse([2,2,62,62], fill=(10,20,15,230))
        d.ellipse([6,18,58,46], outline=(0,255,136), width=4)
        d.ellipse([24,24,40,40], fill=(0,255,136))
        d.ellipse([28,28,36,36], fill=(10,20,15,200))
        return img

    def _update_tray(self):
        if self.tray:
            lang = self.config.get("language", "en")
            n = self.stats.get_today_breaks()
            self.tray.title = f"Eye Care — {n} {get_text('tray_breaks_today', lang)}"

    def _quit(self):
        global _lock_socket
        
        logger.info("Starting shutdown sequence...")
        self._running = False
        self._quit_ev.set()
        if self.idle:
            try: 
                self.idle.stop()
            except: 
                pass

        try:
            import psutil
            parent = psutil.Process(os.getpid())
            for child in parent.children(recursive=True):
                child.kill()
        except:
            pass

        if self.tray:
            try:
                self.tray.visible = False
                self.tray.stop()
            except:
                pass

        if _lock_socket:
            try:
                _lock_socket.close()
                logger.info("Lock socket closed")
            except:
                pass

        logger.info("Final exit.")
        os._exit(0)
        
        os._exit(0)

    def _monitors(self) -> List[Tuple]:
        if SCREEN_OK:
            try:
                return [(m.x, m.y, m.width, m.height)
                        for m in screeninfo.get_monitors()]
            except Exception:
                pass
        try:
            import tkinter as tk
            r = tk.Tk(); r.withdraw()
            w, h = r.winfo_screenwidth(), r.winfo_screenheight()
            r.destroy()
            return [(0, 0, w, h)]
        except Exception:
            return [(0, 0, 1920, 1080)]

    def _is_fullscreen(self) -> bool:
        if sys.platform != "win32":
            return False
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return False
            import ctypes.wintypes
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            sw = ctypes.windll.user32.GetSystemMetrics(0)
            sh = ctypes.windll.user32.GetSystemMetrics(1)
            return (rect.right-rect.left) >= sw and (rect.bottom-rect.top) >= sh
        except Exception:
            return False

    def _play_sound(self):
        if not self.config.get("sound_enabled", True):
            return
        
        sound_type = self.config.get("sound_type", "alert")
        
        if sound_type == "none":
            return
        
        if sound_type == "custom":
            sound_file = self.config.get("sound_file")
            if sound_file and os.path.exists(sound_file):
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()
                    logger.info(f"Воспроизведение кастомного звука: {sound_file}")
                    return
                except ImportError:
                    logger.warning("pygame не установлен, используем встроенный звук")
                except Exception as e:
                    logger.error(f"Sound playback error: {e}")
        
        if sys.platform == "win32":
            try:
                import winsound
                
                if sound_type == "alert":
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                elif sound_type == "beep":
                    winsound.Beep(800, 400)
                else:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception as e:
                logger.error(f"Sound playback error: {e}")
        else:
            try: print("\a", end="", flush=True)
            except Exception: pass

    def run(self):
        logger.info("=" * 50)
        logger.info("Eye Care v3 started.")
        self.start()
        logger.info("Timer started.")
        self.setup_tray()
        self._update_tray()
        if self.tray:
            self.tray.run()
        else:
            logger.info("Tray unavailable - opening settings.")
            self._open_settings()
            try:
                self._quit_ev.wait()
            except KeyboardInterrupt:
                self._quit()

def main():
    import sys
    import ctypes

    args = sys.argv[1:]
    
    if "--settings" in args:
        try:
            from settings_gui import SettingsWindow
            from config_manager import ConfigManager
            config = ConfigManager()
            SettingsWindow(config).show()
        except Exception as e:
            logger.error(f"Error in settings process: {e}")
        sys.exit(0)

    if "--overlay" in args or "--preview" in args:
        try:
            from overlay import EyeCareOverlay
            from config_manager import ConfigManager
            from stats_manager import StatsManager
            
            is_preview = "--preview" in args
            config = ConfigManager()
            stats = StatsManager()
            c = config.get_color_scheme()
            
            overlay = EyeCareOverlay(
                rest_seconds=config.get("rest_seconds", 20),
                colors=c,
                opacity=config.get("opacity", 0.92),
                strict_mode=config.get("strict_mode", False),
                fullscreen=config.get("fullscreen_mode", False),
                on_close_callback=(None if is_preview else lambda: stats.record_break()),
                is_preview=is_preview,
                config=config
            )
            overlay.show()
        except Exception as e:
            logger.error(f"Error in overlay process: {e}")
        sys.exit(0)

    if is_already_running():
        sys.exit(0)

    app = EyeCareApp()
    try:
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        os._exit(1)

if __name__ == "__main__":
    main()