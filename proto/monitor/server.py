import logging
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpServer

from proto.db.manager import DbManager
from proto.monitor import Monitor

HOME_DIR = str(Path.home())
VIDEOS_DIR = F"{HOME_DIR}/pam_demo"
HOST = '127.0.0.1'
PORT = 8000

class Server(QObject):

    def __init__(self):
        logging.debug("monitor: start server initialisation")
        super().__init__()
        self.on_exit = pyqtSignal(name="exit")
        self.db = DbManager()
        self.tcp_server = QTcpServer(self)        
        address = QHostAddress(HOST)
        if not self.tcp_server.listen(address, PORT):
            errmsg = f'could not establish connection on port {PORT}'
            logging.error(errmsg)
            raise ConnectionError(errmsg)
        self.tcp_server.newConnection.connect(self.on_connect)
        
        paths_to_watch = self.db.get_root_dirs()
        self.monitor = Monitor(self.db)
        logging.info("monitor: server launched")
        self.monitor.update(paths_to_watch)
        logging.info("monitor: initial update done")

    def on_connect(self):
        client_connection = self.tcp_server.nextPendingConnection()
        client_connection.waitForReadyRead()
        
        instr = client_connection.readAll()

        request = str(instr, encoding='ascii')
        logging.debug("monitor request:")
        logging.debug(request)
        command, argv = request.split(':') 
        command = command.lower()
        argv = argv.lower().split(';')

        if command in ('exit','quit', 'stop'):
            logging.info(f"server closed by request, arg: {argv}")
            # self.on_exit.emit()
            quit()
        
        elif command in ('update', 'add'):
            if command == 'update' and len(argv) == 0:
                argv = DbManager().get_root_dirs()
            logging.debug("monitor: adding records")
            self.monitor.update(set(argv))
            response = "fs updated"

        elif command == 'remove':
            self.monitor.unwatch(argv)
            logging.debug("monitor: removing records")
            self.db.remove_files({(path,) for path in argv})
            response = "files removed"


        client_connection.disconnected.connect(client_connection.deleteLater)
        client_connection.write(bytes(response, encoding="ascii"))
        client_connection.disconnectFromHost()
