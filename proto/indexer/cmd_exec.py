import logging
from os import fork
from os.path import abspath
import json
from typing import Callable

from multiprocessing.connection import Client

from proto.monitor.application import main as monitor_run
from proto.monitor.server import HOST, PORT
from proto.db.manager import DbManager

TIMEOUT = 1000

def run_fork_proc(entry: Callable):
    if fork() != 0:
        return
    entry()

def serv_is_running() -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0

def exec_search(**kwargs):
    logging.debug(f"indexer: search call, args={str(kwargs)}")

def exec_show(**kwargs):
    logging.debug(f"indexer: show call, args={str(kwargs)}")
    with DbManager() as db:
        table = kwargs['table']
        mode = kwargs['mode']
        header = not kwargs['headless']
        output = db.get_table_as_string(table, mode, header)
        print(output)

def exec_tables(**kwargs):
    # logging.debug(f"indexer: tables call, args={str(kwargs)}")
    with DbManager() as db:
        tables = db.get_tablenames()
        print('\n'.join(tables))

def exec_monitor(**kwargs):
    logging.debug(f"indexer: monitor call, args={str(kwargs)}")

    kwargs = {k : kwargs[k] for k in kwargs if kwargs[k] }
    if len(kwargs) != 1:
        raise KeyError("can execute only one subcommand at once")
    cmd = list(kwargs.keys())[0]
    arg = kwargs[cmd]
    
    if cmd == 'list':
        with DbManager() as db:
            paths_to_watch = db.get_root_dirs()
            print('\n'.join(paths_to_watch))

    elif cmd == 'port':
        if arg == 'get':
            print(PORT)
        #TODO: move port number to env

    elif cmd == 'status':
        running = serv_is_running()
        port = PORT
        print(f"running:\t{running}\nport:\t\t{port}")

    elif cmd == 'run':
        run_fork_proc(monitor_run)

    elif cmd == 'stop':
        conn = Client((HOST, PORT))
        req_obj = bytes(json.dumps({ "command": "stop", "args": True }), encoding='ascii')
        logging.debug(f"indexer req_obj: {req_obj}")
        conn.send_bytes(req_obj)
        conn.close()

    elif cmd in ('add', 'remove', 'update'):
        arg = list({ abspath(path) for path in arg })
        if serv_is_running():
            req_obj = bytes(json.dumps({ "command": cmd, "args": arg }), encoding='ascii')
            logging.debug(f"indexer req_obj: {req_obj}")
            conn = Client((HOST, PORT))
            conn.send_bytes(req_obj)
            conn.close()
        elif cmd == 'add':
            with DbManager() as db:
                db.add_roots(arg)
        elif cmd == 'remove':
            with DbManager() as db:
                db.remove_files({(path,) for path in arg})
        elif cmd == 'update':
            print("monitor is not launched")    

EXEC = {
    "search": exec_search,
    "show": exec_show,
    "tables": exec_tables,
    "monitor": exec_monitor
}

def execute_command(args: dict) -> None:
    try:
        cmd = args.pop('command')
        func = EXEC[cmd]
        func(**args)
    except: None