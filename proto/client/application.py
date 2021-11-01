#!/usr/bin/env python3

import logging
import sys

from proto.config.configuration import get_user_config
from proto.client.cmd_exec import execute_command
from proto.client.cli_parser import build_argparser

USR_CFG = get_user_config() 
LOGGING_CFG : dict = USR_CFG['logging']
logging.basicConfig(**LOGGING_CFG)
logging.debug("indexer: logging test")


def main() -> int:
    logging.debug("indexer: main call")
    parser = build_argparser()
    args = vars(parser.parse_args())
    logging.debug(f"indexer: args={args}")
    execute_command(args)
    logging.debug("indexer: exit")
    return 0

if __name__ == "__main__":
    sys.exit(main())