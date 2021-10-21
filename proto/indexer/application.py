#!/usr/bin/env python3

from os import error
from os.path import dirname, realpath 
import argparse
import sys
from typing import List
import yaml

PROG = "ffpam"
SCRIPT_DIR = dirname(realpath(__file__))
COMMANDS_FILE = SCRIPT_DIR + "/commands.yml"

INFO = {
    "prog": "ffpam",
    "description": "local media file indexer",
} 

def search(*args, **kwargs):
    print((args, kwargs))

def show(*args, **kwargs):
    print((args, kwargs))

def tables(*args, **kwargs):
    print((args, kwargs))

def monitor(*args, **kwargs):
    print((args, kwargs))

EXEC = {
    "search": search,
    "show": show,
    "tables": tables,
    "monitor": monitor
}

def build_argparser() -> argparse.ArgumentParser:

    commands_src: dict = None

    with open(COMMANDS_FILE, "r") as stream:
        try:
            commands_src = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error("missing `commands.yml'")
            print(exc)
    parser = argparse.ArgumentParser(**INFO)
    subparsers = parser.add_subparsers(dest='command', help='command help')
    for cmd in commands_src:
        descr = commands_src[cmd].get('help', '')
        cmd_parser = subparsers.add_parser(cmd, help=descr)

        for arg in commands_src[cmd].get('arguments', []):
            names = arg.pop('names')
            cmd_parser.add_argument(*names, **arg)

    return parser

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