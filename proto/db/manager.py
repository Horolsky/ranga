import sqlite3
from os.path import dirname, realpath 
from sqlite3.dbapi2 import Connection, Cursor
from typing import List, Tuple
from pathlib import Path

import proto.db.queries as queries

SCRIPT_DIR = dirname(realpath(__file__))
HOME_DIR = str(Path.home())
DB_PATH = f'{HOME_DIR}/.pam-index.db' #TODO move this to yml config
DB_SCHEMA = f'{SCRIPT_DIR}/db-schema.sql'


class DbManager:
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
        sql_upd_files = queries.insert('files') + queries.conflict_clause('files') + queries.close()
        self.__cursor.executemany(sql_upd_files, files) 
        self.__db.commit()

    def get_all_files(self) -> List[Tuple[str, float]]:
        self.__cursor.execute(queries.select('files') + queries.close()) 
        return self.__cursor.fetchall()

    def get_files_in_dir(self, dirpath: str) -> List[Tuple[str, float]]:
        sql = queries.select('files') + queries.files_where_stmt("directory") + queries.close()
        self.__cursor.execute(sql, (dirpath,))
        return self.__cursor.fetchall()

    def get_files_by_suffix(self, sfx: str) -> List[Tuple[str, float]]:
        sql = queries.select('files') + queries.files_where_stmt("suffix") + queries.close()
        self.__cursor.execute(sql,  (f"%.{sfx}",))
        return self.__cursor.fetchall()
        
    def remove_files(self, paths: List[str]) -> None:
        sql = queries.delete_files() + queries.close()
        self.__cursor.executemany(sql, paths)
        self.__db.commit()