#!/usr/bin/env python3

import sys
from os.path import isfile, abspath, getmtime, join as joinpath
from os import walk, scandir, listdir
from typing import List, Tuple, Callable

from PyQt5.QtCore import QCoreApplication
from pathlib import Path

from monitor.watchdog import WatchDog
from db.db import DataBase

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/Videos"

class Monitor:
    
    @staticmethod
    def walk_dir( entry: str) -> Tuple[List[str]]:
            
            dirs = []
            files = []
            
            for root, dirnames, filenames in walk(entry, topdown=False):
                    
                for dname in dirnames:
                    dirpath = joinpath(root, dname)
                    modified = getmtime(dirpath)
                    dirs.append((dirpath, modified))

                for fname in filenames:
                    filepath = joinpath(root, fname)
                    modified = getmtime(filepath)
                    files.append((filepath, modified))
                
            return (dirs, files)
    @staticmethod 
    def scan_dir(dirpath: str):
        path = lambda entry: f"{dirpath}/{entry}"
        return [ (path(f), getmtime(path(f)))  for f in listdir(dirpath) if isfile(path(f))]


        
    def __init__(self) -> None:

        dirs, files = Monitor.walk_dir(VIDEOS_DIR)
        paths = [VIDEOS_DIR] + [path for  path, _ in dirs] #+ [path for  path, _ in files]
        
        self.db = DataBase()
        self.watchdog = WatchDog(paths, self.on_upd)
        
        to_delete = [ (path,) for path, _ in set(self.db.get_files()).difference(set(files))]
        
        self.db.remove_files(to_delete)
        self.db.update_files(files)
        
    def on_upd(self, dirpath: str) -> None:
        print(f"dir upd: {dirpath}")

        files = Monitor.scan_dir(dirpath)
        
        to_delete = [ (path,) for path, _ in set(self.db.get_files()).difference(set(files))]
        
        self.db.remove_files(to_delete)
        self.db.update_files(files)


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
