#!/usr/bin/env python3

import sys
from PyQt5.QtCore import QCoreApplication
from .server import Server

def main() -> int:
    
    qt_app = QCoreApplication(sys.argv)
    
    s = Server()
    # s.on_exit.connect(quit)
    return qt_app.exec_()

if __name__ == "__main__":
    sys.exit(main())