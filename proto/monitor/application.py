#!/usr/bin/env python3

import logging
import sys
from PyQt5.QtCore import QCoreApplication
from proto.config.configuration import get_user_config
from proto.monitor.server import Server

USR_CFG = get_user_config() 
LOGGING_CFG : dict = USR_CFG['logging']
logging.basicConfig(**LOGGING_CFG)
logging.debug("monitor application test")

def main() -> int:
    logging.debug("monitor: main call")
    qt_app = QCoreApplication(sys.argv)
    s = Server()
    # s.on_exit.connect(quit)
    ret = qt_app.exec_()
    logging.debug(f"monitor: exit, exitcode={ret}")
    return ret 

if __name__ == "__main__":
    logging.debug("monitor: call as module")
    sys.exit(main())