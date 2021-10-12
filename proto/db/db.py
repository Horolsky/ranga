import sqlite3
from os.path import dirname, realpath 
from sqlite3.dbapi2 import Connection, Cursor
from typing import List, Tuple
from pathlib import Path

from .queries import update_query

SCRIPT_DIR = dirname(realpath(__file__))
HOME_DIR = str(Path.home())
DB_PATH = f'{HOME_DIR}/.pam-index.db' #TODO move this to yml config
DB_SCHEMA = f'{SCRIPT_DIR}/db-schema.sql'


class DataBase:
    __db: Connection = None
    __cursor: Cursor = None
    
    def __init__(self) -> None:
        self.__db: Connection = sqlite3.connect(DB_PATH)
        self.__cursor: Cursor = self.__db.cursor()
        self.load_schema()

    def __del__(self) -> None:
        self.__db.close()

    def load_schema(self) -> None:
        """
        create tables if not exists
        """
        with open(DB_SCHEMA, 'r') as sql_file:
            sql_script = sql_file.read()
            self.__cursor.executescript(sql_script)
            self.__db.commit()


    def update_files(self, files: List[Tuple[str, float]]):
        """
        upsert files table
        files: (path, modified)
        """    
        sql_upd_files = update_query('files')        
        self.__cursor.executemany(sql_upd_files, files) 
        self.__db.commit()

    def get_files(self) -> List[Tuple[str, float]]:
        self.__cursor.execute("SELECT path, modified from files;")
        return self.__cursor.fetchall()
        
    def remove_files(self, paths: List[str]) -> None:
        self.__cursor.executemany("DELETE FROM files WHERE path IN (?);", paths)
        self.__db.commit()