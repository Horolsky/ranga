from os import walk
import os.path
from typing import List, Tuple
from PyQt5.QtCore import QFileSystemWatcher

class WatchDog:

    @staticmethod
    def walk_dir( entry: str) -> Tuple[List[str]]:
            
            dirs = []
            files = []
            
            for root, dirnames, filenames in walk(entry, topdown=False):
                    
                for dname in dirnames:
                    dirpath = os.path.join(root, dname)
                    modified = os.path.getmtime(dirpath)
                    dirs.append((dirpath, modified))

                for fname in filenames:
                    filepath = os.path.join(root, fname)
                    modified = os.path.getmtime(filepath)
                    files.append((filepath, modified))
                
            return (dirs, files)

    def __init__(self, paths: List[str]) -> None:
        print("monitor init")

        self.__qt_watcher = QFileSystemWatcher()
        self.__qt_watcher.addPaths(paths)
        self.__qt_watcher.directoryChanged.connect(self.dir_upd)
        self.__qt_watcher.fileChanged.connect(self.file_upd)

    def dir_upd(self, path: str) -> None:
        print(f"dir upd: {path}")

    def file_upd(self, path: str) -> None:
        print(f"file upd: {path}")

    def __del__(self):
        print("monitor shutdown")