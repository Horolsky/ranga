#!/usr/bin/env python3

import sys
from os import walk
import os.path

from typing import List, Tuple
from PyQt5.QtCore import QFileSystemWatcher, QCoreApplication


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
        print(f"monitor init")

        self.__qt_watcher = QFileSystemWatcher(paths)
        self.__qt_watcher.directoryChanged.connect(self.dir_upd)
        self.__qt_watcher.fileChanged.connect(self.file_upd)

    def dir_upd(self, path: str) -> None:
        print('dir upd: %s' % path)

    def file_upd(self, path: str) -> None:
        print('file upd: %s' % path)

INIT_MSG = \
"""
PAM file monitor proto
usage: pass folder path tp watch
"""

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(INIT_MSG)
        exit(0)

    qt_app = QCoreApplication(sys.argv)
    root = sys.argv[1]
    dirs, files = WatchDog.walk_dir(root)

    paths = [path for  path, _ in dirs] + [path for  path, _ in files] + [root]
    w = WatchDog(paths)

    sys.exit(qt_app.exec_()) 