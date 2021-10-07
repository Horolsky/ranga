#!/usr/bin/env python3

import sys
from os.path import abspath
from PyQt5.QtCore import QCoreApplication

from monitor.watchdog import WatchDog

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

    root = abspath(sys.argv[1])
    dirs, files = WatchDog.walk_dir(root)
    paths = [root] + [path for  path, _ in dirs] #+ [path for  path, _ in files]
    x = WatchDog(paths)
    
    return qt_app.exec_()
