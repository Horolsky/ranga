def exec_search(**kwargs):
    print(kwargs)

def exec_show(**kwargs):
    print(kwargs)

def exec_tables(**kwargs):
    print(kwargs)

def exec_monitor(**kwargs):
    print(kwargs)

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