from pathlib import Path
from typing import List
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from os.path import isdir

from proto.db.manager import DbManager
from proto.monitor import Monitor

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/pam_demo"
HOST = '127.0.0.1'
PORT = 8000

INIT_MSG = \
"""
PAM file monitor proto
usage: pass folder path to watch
"""

class Server(QObject):

    def __init__(self):
        super().__init__()
        self.on_exit = pyqtSignal(name="exit")
        self.db = DbManager()
        self.tcp_server = QTcpServer(self)        
        address = QHostAddress(HOST)
        if not self.tcp_server.listen(address, PORT):
            raise ConnectionError(f'could not establish connection on port {PORT}')
        self.tcp_server.newConnection.connect(self.on_connect)
        
        # TODO: get dirs from db
        # paths_to_watch = VIDEOS_DIR
        paths_to_watch = self.db.get_root_dirs()
        self.monitor = Monitor(self.db)
        print("monitor: server launched")
        self.monitor.update(paths_to_watch)
        print("monitor: initial update done")

    def exec_command(self, command: str, argv: List[str]) -> str:

        if command == 'list':
            paths_to_watch = self.db.get_root_dirs()
            return paths_to_watch
            
        elif command == 'add':
            self.monitor.update(set(argv))
            return "paths added"
            
        elif command == 'remove':
            self.monitor.db.remove_files(argv)
            return "paths removed"
            
        elif command == 'update':
            self.monitor.update(set(argv))
            return "fs updated"
        else:
            return "return help msg"

    def on_connect(self):
        client_connection = self.tcp_server.nextPendingConnection()
        client_connection.waitForReadyRead()
        
        instr = client_connection.readAll()

        request = str(instr, encoding='ascii')
        command, arg = [ s.lower() if s else None for s in request.split(':')]

        if command in ('exit','quit', 'stop'):
            print(f"closed by request, arg: {arg}")
            self.on_exit.emit()

        response = self.exec_command(command, arg)
        
        client_connection.disconnected.connect(client_connection.deleteLater)
        client_connection.write(bytes(response, encoding="ascii"))
        client_connection.disconnectFromHost()
