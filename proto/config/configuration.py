from genericpath import isdir, isfile
from os import error
from os.path import dirname, realpath
from pathlib import Path
from shutil import copy as shutil_copy
import yaml

SCRIPT_DIR = dirname(realpath(__file__))
CFG_FILE_NAME = "/config.yml"
CONFIG_TEMPLATE = SCRIPT_DIR + CFG_FILE_NAME

HOME_DIR = str(Path.home())
USR_CFG_DIR = f"{HOME_DIR}/.config/ffindex"
USR_CFG_FILE = USR_CFG_DIR + CFG_FILE_NAME

def get_config_template() -> dict:
    with open(CONFIG_TEMPLATE, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error(f"missing {CONFIG_TEMPLATE}")
            return None
def init_user_config() -> None:
    if not isfile(USR_CFG_FILE):
        Path(USR_CFG_DIR).mkdir(parents=True, exist_ok=True)
        shutil_copy(CONFIG_TEMPLATE, USR_CFG_FILE)

def get_user_config() -> dict:
    init_user_config()
    with open(USR_CFG_FILE, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            return None