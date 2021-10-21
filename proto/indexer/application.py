#!/usr/bin/env python3

import sys

from proto.indexer.cmd_exec import execute_command
from proto.indexer.cli_parser import build_argparser


def main() -> int:
    parser = build_argparser()
    args = vars(parser.parse_args())
    execute_command(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())