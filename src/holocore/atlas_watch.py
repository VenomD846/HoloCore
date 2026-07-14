"""Safe polling watch loop for Atlas refreshes."""
from __future__ import annotations
import time
from typing import Any, Callable

def watch(atlas: Any, *, interval: float = 1.0, once: bool = False, callback: Callable[[dict[str, Any]], None] | None = None, max_cycles: int | None = None) -> int:
    cycles = 0
    while True:
        status = atlas.freshness()
        if not status.get("fresh"):
            result = atlas.refresh()
            if callback: callback(result)
        cycles += 1
        if once or (max_cycles is not None and cycles >= max_cycles): return cycles
        time.sleep(max(0.05, interval))


def native_watch(atlas: Any, *, callback: Callable[[dict[str, Any]], None] | None = None) -> Any:
    """Use watchdog events when installed, with a clear optional dependency boundary."""
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        raise RuntimeError("native watching requires the optional 'watchdog' package; use watch() for polling") from exc
    class Handler(FileSystemEventHandler):
        def on_any_event(self, event: Any) -> None:
            if not getattr(event, "is_directory", False):
                result = atlas.refresh()
                if callback: callback(result)
    observer = Observer(); observer.schedule(Handler(), str(atlas.root), recursive=True); observer.start(); return observer
