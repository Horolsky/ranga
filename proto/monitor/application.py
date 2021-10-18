#!/usr/bin/env python3

from genericpath import isdir
from posixpath import abspath
import sys
from PyQt5.QtCore import QCoreApplication
from pathlib import Path

from proto.db.manager import DbManager
from proto.monitor import Monitor

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/pam_demo"


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

    db = DbManager()
    
    # path = VIDEOS_DIR
    path = abspath(sys.argv[1]) if isdir(sys.argv[1]) else VIDEOS_DIR
    m = Monitor(path, db)

    return qt_app.exec_()

if __name__ == "__main__":
    sys.exit(main())