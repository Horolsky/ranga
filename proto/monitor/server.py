from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from os.path import isdir

from proto.db.manager import DbManager
from proto.monitor import Monitor

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/pam_demo"
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
        address = QHostAddress('127.0.0.1')
        if not self.tcp_server.listen(address, PORT):
            raise ConnectionError(f'could not establish connection on port {PORT}')
        self.tcp_server.newConnection.connect(self.on_connect)
        
        # TODO: get dirs from db
        paths_to_watch = VIDEOS_DIR
        self.monitor = Monitor(self.db)
        print("monitor: server launched")
        self.monitor.update(paths_to_watch)
        print("monitor: initial update done")

    def exec_command(self, command: str, arg: str) -> str:

        if command == 'list':
            return "return watched paths, arg: [roots|all|dirs|files]"
            
        elif command == 'add':
            if isdir(arg):
                self.monitor.update(arg)
            return "add path to watched paths, arg: path"
            
        elif command == 'remove':
            return "remove path from watched paths, arg: path"
            
        elif command == 'update':
            return "update directory, arg: [path(def=all), recursive]"
            
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
