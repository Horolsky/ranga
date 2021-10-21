import argparse
from os import error
import yaml
from os.path import dirname, realpath 

INFO = {
    "prog": "ffpam",
    "description": "local media file indexer",
} 
SCRIPT_DIR = dirname(realpath(__file__))
COMMANDS_FILE = SCRIPT_DIR + "/cli_schema.yml"

def build_argparser() -> argparse.ArgumentParser:

    commands_src: dict = None

    with open(COMMANDS_FILE, "r") as stream:
        try:
            commands_src = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error(f"missing {COMMANDS_FILE}")
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