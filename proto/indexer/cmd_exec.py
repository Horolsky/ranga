import multiprocessing
import os 
import subprocess
from os.path import abspath
# from multiprocessing.connection import Client

from proto.monitor.application import main as monitor_run
from proto.monitor.server import HOST, PORT
from proto.db.manager import DbManager
# from proto.monitor.qtclient import Client

TIMEOUT = 1000
# from proto.monitor.client import Client

def serv_is_running():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0

def exec_search(**kwargs):
    print(kwargs)

def exec_show(**kwargs):
    print(kwargs)

def exec_tables(**kwargs):
    print(kwargs)

def exec_monitor(**kwargs):
    
    if kwargs['list']:
        paths_to_watch = DbManager().get_root_dirs()
        print('\n'.join(paths_to_watch))

    if kwargs['add']:
        paths = { abspath(path) for path in kwargs["add"] }
        if serv_is_running():
            updcmd = f'printf "add:{";".join(paths)}" | nc {HOST} {PORT} &'
            os.system(updcmd)
        else:
            DbManager().add_roots(paths)
        
    if kwargs['remove']:
        paths = { abspath(path) for path in kwargs["remove"] }
        if serv_is_running():
            updcmd = f'printf "remove:{";".join(paths)}" | nc {HOST} {PORT} &'
            os.system(updcmd)
        else:
            DbManager().remove_files(paths)

    if kwargs['update']:
        if serv_is_running():
            updcmd = f'printf "update:{";".join(kwargs["update"])}" | nc {HOST} {PORT} &'
            os.system(updcmd)
        else:
            print("monitor is not launched")
        
    if kwargs['run']:
        process = multiprocessing.Process(target=monitor_run, daemon=True)
        process.start()
        
    if kwargs['stop']:
        stopcmd = f'printf "stop:none" | nc {HOST} {PORT} &'
        os.system(stopcmd)
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