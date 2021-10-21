#!/usr/bin/env python3

import sys

from .cli_parser import build_argparser

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


def main() -> int:
    parser = build_argparser()
    args = vars(parser.parse_args())
    try:
        cmd = args['command']
        func = EXEC[cmd]
        func(**args)
    except: None
    return 0

if __name__ == "__main__":
    sys.exit(main())