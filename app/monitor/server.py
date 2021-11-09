import logging
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpServer
import json
from os import makedirs
from os.path import isdir

from app.db.manager import DbManager
from app.monitor import Monitor

HOME_DIR = str(Path.home())
CONFIG_DIR = f"{HOME_DIR}/.config/ranga"
HOST = '127.0.0.1'
PORT = 0


def get_port():
    f = open(f"{CONFIG_DIR}/PORT", 'r')
    port = f.read()
    f.close()
    return int(port)
def get_host():
    return HOST

class Server(QObject):
    def __init__(self):
        logging.debug("monitor: start server initialisation")
        super().__init__()
        self.on_exit = pyqtSignal(name="exit")
        self.db = DbManager()
        self.tcp_server = QTcpServer(self)        
        address = QHostAddress(HOST)
        if not self.tcp_server.listen(address, PORT):
            errmsg = 'could not establish connection'
            logging.error(errmsg)
            raise ConnectionError(errmsg)
            
        port = self.tcp_server.serverPort()
        if not isdir(CONFIG_DIR):
            makedirs(CONFIG_DIR)
        f = open(f"{CONFIG_DIR}/PORT", 'w')
        f.write(str(port))
        f.close()

        self.tcp_server.newConnection.connect(self.on_connect)

        dirs_to_watch = self.db.get_root_dirs()
        self.monitor = Monitor(self.db)
        logging.info(f"monitor: server launched on port {port}")
        self.monitor.update(dirs_to_watch)
        logging.info("monitor: initial update done")

    def on_connect(self):
        client_connection = self.tcp_server.nextPendingConnection()
        client_connection.waitForReadyRead()
        
        instr = client_connection.readAll()
        logging.debug(f"monitor: instr: {instr}")
        instr.remove(0, 4) #TODO handle this better
        request = str(bytes(instr), encoding='ascii')
        logging.debug(f"monitor: request: {request}")
        command, args = None, None
        response = "404"
        try:
            req_obj = json.loads(request)
            command = req_obj['command']
            args = set(req_obj['args'])
        except:
            logging.error("monitor: invalid request object")

        logging.debug(f"monitor cmd: {command}")
        logging.debug(f"monitor arg: {args}")
        if command in ('exit','quit', 'stop'):
            logging.info(f"server closed by request, arg: {args}")
            # self.on_exit.emit()
            quit()

        elif command in ('update', 'add'):
            if command == 'update' and 'all' in args:
                args = DbManager().get_root_dirs()
            logging.debug("monitor: adding records")
            logging.debug(args)

            inserted_files = self.db.insert_roots(args)
            logging.debug("monitor: inserted")
            logging.debug(inserted_files)
            self.monitor.update(inserted_files)
            response = "fs updated"

        elif command == 'remove':
            self.monitor.unwatch(args)
            logging.debug("monitor: removing records")
            self.db.delete_files(args)
            response = "files removed"

        client_connection.disconnected.connect(client_connection.deleteLater)
        client_connection.write(bytes(response, encoding="ascii"))
        client_connection.disconnectFromHost()
