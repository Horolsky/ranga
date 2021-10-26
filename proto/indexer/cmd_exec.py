import logging
from os import fork, system
from os.path import abspath
from typing import Callable

from proto.monitor.application import main as monitor_run
from proto.monitor.server import HOST, PORT
from proto.db.manager import DbManager

TIMEOUT = 1000

def run_fork_proc(entry: Callable):
    if fork() != 0:
        return
    entry()

def serv_is_running():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0

def exec_search(**kwargs):
    logging.debug("indexer: search call")
    logging.debug(str(kwargs))

def exec_show(**kwargs):
    logging.debug("indexer: show call")
    logging.debug(str(kwargs))

def exec_tables(**kwargs):
    logging.debug("indexer: tables call")
    logging.debug(str(kwargs))

def exec_monitor(**kwargs):
    logging.debug("indexer: monitor call")
    logging.debug(str(kwargs))

    if kwargs['list']:
        with DbManager() as db:
            paths_to_watch = db.get_root_dirs()
            print('\n'.join(paths_to_watch))

    if kwargs['add']:
        paths = { abspath(path) for path in kwargs["add"] }
        if serv_is_running():
            updcmd = f'printf "add:{";".join(paths)}" | nc {HOST} {PORT} &'
            system(updcmd)
        else:
            with DbManager() as db:
                db.add_roots(paths)
        
    if kwargs['remove']:
        paths = { abspath(path) for path in kwargs["remove"] }
        if serv_is_running():
            updcmd = f'printf "remove:{";".join(paths)}" | nc {HOST} {PORT} &'
            system(updcmd)
        else:
            with DbManager() as db:
                db.remove_files({(path,) for path in paths})

    if kwargs['update']:
        if serv_is_running():
            updcmd = f'printf "update:{";".join(kwargs["update"])}" | nc {HOST} {PORT} &'
            system(updcmd)
        else:
            print("monitor is not launched")
        
    if kwargs['run']:
        run_fork_proc(monitor_run)
        
    if kwargs['stop']:
        stopcmd = f'printf "stop:none" | nc {HOST} {PORT} &'
        system(stopcmd)
    if kwargs['port'] == 'get':
        print(PORT)
        #TODO: move port number to env
    if kwargs['status']:
        running = serv_is_running()
        port = PORT
        print(f"running:\t{running}\nport:\t\t{port}")

EXEC = {
    "search": exec_search,
    "show": exec_show,
    "tables": exec_tables,
    "monitor": exec_monitor
}

def execute_command(args: dict) -> None:
    try:
        cmd = args['command']
        func = EXEC[cmd]
        func(**args)
    except: None