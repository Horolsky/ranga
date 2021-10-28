import sqlite3
from os.path import dirname, realpath 
from sqlite3.dbapi2 import Connection, Cursor
from typing import List, Set, Tuple
from pathlib import Path
import subprocess

import proto.db.queries as queries

SCRIPT_DIR = dirname(realpath(__file__))
HOME_DIR = str(Path.home())
DB_PATH = f'{HOME_DIR}/.pam-index.db' #TODO move this to yml config
DB_SCHEMA = f'{SCRIPT_DIR}/db-schema.sql'


TYPEMAP = {
    int: "INTEGER",
    float: "REAL",
    str: "STRING"
}

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
        sql = queries.tablenames() + queries.close()
        self.__cursor.execute(sql)
        tables = [ row[0] for row in self.__cursor.fetchall() ]

        return tables

    def add_roots(self, paths: List[str]):
        """
        add files with modified=0
        used for adding root dirs
        """    
        files = {(path, None, 0, 1) for path in paths}
        sql_upd_files = queries.insert('files') + queries.conflict_clause('files') + queries.close()
        self.__cursor.executemany(sql_upd_files, files) 
        self.__db.commit()
    
    def update_files(self, files: List[Tuple[str, float]]):
        """
        upsert files table
        files: (path, modified)
        """    
        sql_upd_files = queries.insert('files') + queries.conflict_clause('files') + queries.close()
        self.__cursor.executemany(sql_upd_files, files) 
        self.__db.commit()

    def get_root_dirs(self) -> Set[str]:
        sql = queries.select('files') + queries.files_where_stmt("roots") + queries.close()
        self.__cursor.execute(sql)
        return { entry[0] for entry in self.__cursor.fetchall() }

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

        
    def remove_files(self, paths: Set[str]) -> None:
        sql = queries.delete_files() + queries.close()
        self.__cursor.executemany(sql, paths)
        self.__db.commit()
    
    def update_meta(self, datalist: List[dict]):
        """
        upsert meta keys, malues and file mapping
        """    
        sql_upd_mvals = queries.insert('meta_values') + queries.conflict_clause('meta_values') + queries.close()
        sql_upd_mapping = queries.insert('meta_map') + queries.conflict_clause('meta_map') + queries.close()
        
        for filedata in datalist:    
            if not filedata:
                continue
            filename = filedata.pop("filename")
            for key, value in filedata.items():
                
                #TODO remove query literal
                self.__cursor.execute(
                    "INSERT INTO files_metadata_map(path, mkey, mvalue) VALUES (?,?,?)",
                    (filename, key, value)
                )
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

        sql_mvalues = "SELECT mvalue_id FROM meta_data WHERE" + keywords_filter('mvalue')
        if not categories: categories = []
        kw_categories = set(categories).difference({'filename', 'path'})
        kw_categories = [f'"{key}"' for key in kw_categories]
        if kw_categories:
            sql_mvalues += f" AND mkey IN ({','.join(kw_categories)})"
        sql_mvalues += ";"
                
        self.__cursor.execute(sql_mvalues)
        mval_ids = [ str(row[0]) for row in self.__cursor.fetchall()]
        
        self.__cursor.execute(f"SELECT file_id FROM meta_map WHERE mvalue_id IN ({','.join(mval_ids)})")
        file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
        
        if not categories or 'path' in categories:
            sql_path = "SELECT id FROM files WHERE" + keywords_filter('path')
            self.__cursor.execute(sql_path)
            file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
        
        if 'filename' in categories or (not categories and exact):
            sql_fnames = "SELECT id FROM files_view WHERE" + keywords_filter('filename')
            self.__cursor.execute(sql_fnames)
            file_ids += [ str(row[0]) for row in self.__cursor.fetchall()]
    
        ########
        if mode is None: mode = "list"
        if mode not in ( "csv", "column", "html", "line", "list" ):
            raise ValueError("invalid mode option")
        header = "-header" if header else ""

        sql = f"SELECT filename, mkey, mvalue, parent_path as dir FROM files_metadata_map WHERE file_id IN ({','.join([str(id) for id in file_ids])});"
        command = f'sqlite3 {DB_PATH} "{sql}" -{mode} {header}'

        output = subprocess.check_output(command, shell=True)
        output = str(output, encoding="ascii")
        return output
