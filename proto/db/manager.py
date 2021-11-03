import logging
import sqlite3
from os.path import dirname, realpath, isdir
from sqlite3.dbapi2 import Connection, Cursor
from typing import Dict, Iterable, List, Set, Tuple
from pathlib import Path
import subprocess

from proto.db.types import *

SCRIPT_DIR = dirname(realpath(__file__))
HOME_DIR = str(Path.home())
DB_PATH = f'{HOME_DIR}/.pam-index.db' #TODO move this to yml config
DB_SCHEMA = f'{SCRIPT_DIR}/schema.sql'


class DbManager:
    __db: Connection = None
    __cursor: Cursor = None
    
    def __init__(self) -> None:
        self.__db: Connection = sqlite3.connect(DB_PATH)
        self.__cursor: Cursor = self.__db.cursor()
        self.load_schema()

    def __enter__(self):
        # self.__init__()
        return self
  
    def __exit__(self):
        self.__del__()

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

    def get_tablenames(self) -> List[str]:
        sql = 'SELECT [name] FROM sqlite_master WHERE [type] IN ("table", "view");'
        self.__cursor.execute(sql)
        tables = [ row[0] for row in self.__cursor.fetchall() ]

        return tables
    
    def insert_metadata(self, values: Iterable[MData]):
        """
        insert or update records in mkeys, mvalues and mmap tables
        """    
        qmarks = ','.join( ['?'] * len(MData._fields) )

        insert_sql = f"INSERT OR IGNORE INTO [view_data] ([file_id], [mkey], [mvalue]) VALUES ({qmarks});"

        self.__cursor.executemany(insert_sql, [tuple(value) for value in values]) 
        self.__db.commit()
    
    def insert_values(self, table: str, values: Iterable[tuple]):
        """
        insert or update records into mvalues table
        """    
        if not values: return
        qmarks = ','.join( ['?'] * len(values[0]) )

        insert_sql = f"INSERT OR IGNORE INTO [{table}] VALUES ({qmarks});"

        self.__cursor.executemany(insert_sql, values) 
        self.__db.commit()

    def get_files_by_paths(self, paths: Iterable[str]) -> Set[File]:
        if not paths: return set()
        qmarks = ','.join( ['?'] * len(paths) )
        select_sql = f"SELECT * FROM [tbl_files] WHERE [file_path] IN ({qmarks});"
        self.__cursor.execute(select_sql, paths) 
        rows = self.__cursor.fetchall()
        return { File(*row) for row in rows }

    def insert_roots(self, paths: List[str]) -> Set[str]:
        """
        add root directories records
        """    
        
        sql = "SELECT [file_path] FROM [tbl_files] WHERE [is_dir] IS 1;"
        self.__cursor.execute(sql)
        db_records = { row[0] for row in self.__cursor.fetchall() }
        filtered = { path for path in paths if isdir(path) } - db_records
        files = {File(None, path, None, 0, 1) for path in filtered}
        # TODO filter invalid roots
        self.insert_files(files)
        return filtered

    def insert_files(self, files: List[File]):
        """
        insert or update records into files table  
        """    
        qmarks = ','.join( ['?'] * 7 )
        insert_sql = f"INSERT INTO [view_files] VALUES ({qmarks});"
           
        parent_id = lambda v: v if type(v) is int else None
        parent_path = lambda v: v if type(v) is str else None
        _files = [(
            file.file_id,               # file_id
            None,                       # filename
            parent_id(file.parent),     # parent_id
            parent_path(file.parent),   # parent_path
            file.file_path,             # file_path
            file.modified,              # modified
            file.is_dir                 # is_dir
            ) for file in files]
        self.__cursor.executemany(insert_sql, _files) 
        self.__db.commit()
    
    def update_files(self, files: List[File]):
        """
        update records in files table
        """    
        
        update_sql = "UPDATE [tbl_files] SET " + \
            "[modified] = ? " + \
            "WHERE [file_id] = ? ;"
        update_params = [ (file.modified, file.file_id) for file in files ]

        self.__cursor.executemany(update_sql, update_params) 
        self.__db.commit()

    def get_root_dirs(self) -> Set[str]:
        sql = "SELECT [file_path] FROM [tbl_files] WHERE [parent_id] IS NULL;"
        self.__cursor.execute(sql)
        return { row[0] for row in self.__cursor.fetchall() }

    def get_files_in_dir(self, dirpath: str) -> List[File]:
        sql = \
            "SELECT * FROM [tbl_files] " \
            "WHERE [parent_id] = "\
            "(SELECT [file_id] FROM [tbl_files] WHERE [file_path] = ? LIMIT 1);"
        
        self.__cursor.execute(sql, (dirpath,))
        result = self.__cursor.fetchall()
        return [ File(*file) for file in result ]
        
    def remove_files(self, paths: Set[str]) -> None:
        sql = "DELETE FROM [tbl_files] WHERE [file_path] IN (?);"
        self.__cursor.executemany(sql, paths)
        self.__db.commit()

    def get_table_as_string(self, table: str, mode: str, header: bool):
        """
        return output of the sqlite3 CLI command as a string
        """
        if mode is None: mode = "list"
        if mode not in ( "csv", "column", "html", "line", "list" ):
            raise ValueError("invalid mode option")

        sql = f"SELECT * FROM {table};"
        #header = "-header" if mode == "column" else "" 
        header = "-header" if header else ""
        command = f'sqlite3 {DB_PATH} "{sql}" -{mode} {header}'

        output = subprocess.check_output(command, shell=True)
        output = str(output, encoding="ascii")
        return output

    def search_by_keyword(self, keywords: List[str], categories: list, exact: bool, mode: str, header: bool) -> str:
        """
        return ids of files that meets the search conditions
        """
        file_ids = []
        keywords = [ f'"{kw}"' if exact else f'"%{kw}%"' for kw in keywords ]
        keywords_filter = lambda column: ''.join([ f" {column} LIKE {kw}" for kw in keywords ])

        sql_mvalues = "SELECT [mvalue_id] FROM [view_meta] WHERE" + keywords_filter('mvalue')
        if not categories: categories = []
        kw_categories = set(categories).difference({'filename', 'file_path'}) #TODO: better options for name, path
        kw_categories = [f'"{key}"' for key in kw_categories]
        if kw_categories:
            sql_mvalues += f" AND [mkey] IN ({','.join(kw_categories)})" 
        sql_mvalues += ";"
                
        self.__cursor.execute(sql_mvalues)
        mval_ids = [ str(row[0]) for row in self.__cursor.fetchall()]
        
        self.__cursor.execute(f"SELECT [file_id] FROM [tbl_mmap] WHERE [mvalue_id] IN ({','.join(mval_ids)})")
        file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
        
        if not categories or 'file_path' in categories:
            sql_path = "SELECT [file_id] FROM [tbl_files] WHERE" + keywords_filter('file_path')
            self.__cursor.execute(sql_path)
            file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
        
        if 'filename' in categories or (not categories and exact):
            sql_fnames = "SELECT [file_id] FROM [view_files] WHERE" + keywords_filter('filename')
            self.__cursor.execute(sql_fnames)
            file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
    
        ########
        if mode is None: mode = "list"
        if mode not in ( "csv", "column", "html", "line", "list" ):
            raise ValueError("invalid mode option")
        header = "-header" if header else ""

        sql = f"SELECT [filename], [mkey], [mvalue], [parent_path] as [dir] FROM [view_data] WHERE [file_id] IN ({','.join([str(id) for id in file_ids])});"
        command = f'sqlite3 {DB_PATH} "{sql}" -{mode} {header}'

        output = subprocess.check_output(command, shell=True)
        output = str(output, encoding="ascii")
        return output
