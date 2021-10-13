from typing import List, Callable
from PyQt5.QtCore import QFileSystemWatcher

class WatchDog:
    def __init__(self, paths: List[str], on_upd: Callable[[str], None]) -> None:
        print("watchdog init")

        self.__qt_watcher = QFileSystemWatcher()
        self.__qt_watcher.addPaths(paths)
        self.__qt_watcher.directoryChanged.connect(on_upd)

    def __del__(self):
        print("watchdog shutdown")