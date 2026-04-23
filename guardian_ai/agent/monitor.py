from __future__ import annotations

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from guardian_ai.agent.detection import FeatureWindow
import queue


class EventHandler(FileSystemEventHandler):
    def __init__(self, q: queue.Queue) -> None:
        self.q = q

    def on_created(self, event):
        if not event.is_directory:
            self.q.put(("created", event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self.q.put(("modified", event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            self.q.put(("deleted", event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.q.put(("moved", event.dest_path))


class FolderMonitor:
    def __init__(self, protected_dir: Path, feature_window: FeatureWindow) -> None:
        self.protected_dir = protected_dir
        self.feature_window = feature_window
        self.q: queue.Queue = queue.Queue()
        self.observer = Observer()

    def start(self) -> None:
        handler = EventHandler(self.q)
        self.observer.schedule(handler, str(self.protected_dir), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(timeout=5)

    def drain(self) -> list[str]:
        touched: list[str] = []
        while True:
            try:
                event_type, path = self.q.get_nowait()
            except queue.Empty:
                break
            self.feature_window.add_event(event_type, path)
            touched.append(path)
        return touched
