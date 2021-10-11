#!/usr/bin/env python3

import sys
from os.path import abspath
from PyQt5.QtCore import QCoreApplication
from pathlib import Path

from monitor.watchdog import WatchDog
from db.db import DataBase

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/Videos"

class Monitor:
    def __init__(self) -> None:

        dirs, files = WatchDog.walk_dir(VIDEOS_DIR)
        paths = [VIDEOS_DIR] + [path for  path, _ in dirs] #+ [path for  path, _ in files]
        
        db = DataBase()
        self.watchdog = WatchDog(paths, self.on_upd)
        
        to_delete = list(set(db.get_files()).difference(set(files)))
        
        db.remove_files(to_delete)
        db.update_files(files)
        
    def on_upd(self, dirpath: str) -> None:
        print(f"dir upd: {dirpath}")


INIT_MSG = \
"""
PAM file monitor proto
usage: pass folder path to watch
"""

def main() -> int:
    
    if len(sys.argv) == 1:
        print(INIT_MSG)
        exit(0)
    
    qt_app = QCoreApplication(sys.argv)
    m = Monitor()

    return qt_app.exec_()
