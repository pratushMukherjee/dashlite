import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.utils.file_types import is_supported


class FileWatchHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and is_supported(event.src_path):
            self.callback("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory and is_supported(event.src_path):
            self.callback("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.callback("deleted", event.src_path)


class FileWatcherService:
    def __init__(self):
        self.observer = Observer()
        self._watching = False

    def start_watching(self, directory: str, callback):
        path = Path(directory)
        if not path.exists():
            return

        handler = FileWatchHandler(callback)
        self.observer.schedule(handler, str(path), recursive=True)
        self.observer.start()
        self._watching = True

    def stop_watching(self):
        if self._watching:
            self.observer.stop()
            self.observer.join()
            self._watching = False
