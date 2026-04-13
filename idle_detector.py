"""idle_detector.py — Eye Care v3"""

import time, threading, logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

try:
    from pynput import mouse, keyboard as kb
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class IdleDetector:
    def __init__(self, idle_threshold_seconds=300,
                 on_idle: Optional[Callable] = None,
                 on_active: Optional[Callable] = None):
        self.threshold = idle_threshold_seconds
        self.on_idle   = on_idle
        self.on_active = on_active
        self._last     = time.monotonic()
        self._is_idle  = False
        self._running  = False
        self._lock     = threading.Lock()

    def _activity(self, *_):
        with self._lock:
            self._last = time.monotonic()
            if self._is_idle:
                self._is_idle = False
                if self.on_active:
                    threading.Thread(target=self.on_active, daemon=True).start()

    def _monitor(self):
        while self._running:
            time.sleep(5)
            with self._lock:
                if time.monotonic() - self._last >= self.threshold and not self._is_idle:
                    self._is_idle = True
                    if self.on_idle:
                        threading.Thread(target=self.on_idle, daemon=True).start()

    def start(self):
        if not PYNPUT_AVAILABLE:
            return
        self._running = True
        try:
            mouse.Listener(on_move=self._activity, on_click=self._activity,
                           on_scroll=self._activity).start()
            kb.Listener(on_press=self._activity).start()
            threading.Thread(target=self._monitor, daemon=True).start()
        except Exception as e:
            logger.error(f"IdleDetector: {e}")

    def stop(self):
        self._running = False

    def reset(self):
        with self._lock:
            self._last = time.monotonic()
            self._is_idle = False

    @property
    def is_idle(self):
        with self._lock:
            return self._is_idle
