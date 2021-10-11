from typing import List, Tuple, Callable
from PyQt5.QtCore import QFileSystemWatcher

class WatchDog:
    def __init__(self, paths: List[str], on_upd: Callable[[str], None]) -> None:
        print("monitor init")

        self.__qt_watcher = QFileSystemWatcher()
        self.__qt_watcher.addPaths(paths)
        self.__qt_watcher.directoryChanged.connect(on_upd)
        # self.__qt_watcher.fileChanged.connect(self.file_upd)

    def dir_upd(self, path: str) -> None:
        print(f"dir upd: {path}")

    def file_upd(self, path: str) -> None:
        print(f"file upd: {path}")

    def __del__(self):
        print("monitor shutdown")