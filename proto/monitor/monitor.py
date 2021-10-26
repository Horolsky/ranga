import logging
from os.path import isdir, getmtime, join as joinpath
from os import walk, listdir
from typing import List, Set

from PyQt5.QtCore import QFileSystemWatcher

from proto.db.manager import DbManager
from proto.monitor.dumper import get_data

# tuple indexation for file record
PATH, PARENT, MODIFIED, IS_DIR = 0,1,2,3
EMPTY_RECORD = ("",0,0,0)

class Monitor:
    
    @staticmethod
    def walk_dir( directory: str, recursive: bool) -> List[tuple]:

        if not isdir(directory): 
            return []
            
        files = [(directory, None, getmtime(directory), 1)]

        if not recursive:
            is_dir = lambda f: 1 if isdir(f) else 0
            for entry in listdir(directory):
                path = joinpath(directory, entry)
                files.append((path, directory, getmtime(path), is_dir(path)))
        else:
            for root, dirnames, filenames in walk(directory, topdown=False):
                for dname in dirnames:
                    dirpath = joinpath(root, dname)
                    modified = getmtime(dirpath)
                    files.append((dirpath, root, modified, 1))
                for fname in filenames:
                    filepath = joinpath(root, fname)
                    modified = getmtime(filepath)
                    files.append((filepath, root, modified, 0))
                
        return files
        
    def __init__(self, db: DbManager) -> None:
        self.db = db
        self.watchdog = QFileSystemWatcher()
        self.watchdog.directoryChanged.connect(lambda path: self.update( {path} ))
        
    def update(self, nodes: Set[str], deep: bool = False) -> None:
        logging.info(f"update dirs: {nodes}")


        local_files = { file[PATH]: file for node in nodes for file in Monitor.walk_dir(node, deep) }
        db_records = { record[PATH]: record for node in nodes for record in self.db.get_files_in_dir(node) }

        to_remove = { (path,) for path in set(db_records) - set(local_files) }
        to_update = [ file for path, file in local_files.items() if file[MODIFIED] > db_records.get(path, EMPTY_RECORD)[MODIFIED] ]
        to_watch = { path for path in local_files if path not in db_records and local_files[path][IS_DIR] and path not in nodes }

        if to_remove: self.db.remove_files(to_remove)
        if to_update: 
            self.db.update_files(to_update)
            self.upd_meta(to_update)

        self.watchdog.addPaths([ node for node in nodes if isdir(node) ])
        if to_watch: 
            self.watchdog.addPaths(to_watch)
            self.update(to_watch, True)
        # for path in to_watch:
            # self.update(path, True)
    
    #TODO: use threadpool for this
    def upd_meta(self, files: List[tuple]) -> None:
        data = [ get_data(file[PATH]) for file in files if not file[IS_DIR] ]
        self.db.update_meta(data)

    def unwatch(self, paths):
        self.watchdog.removePaths(paths)

    def __del__(self):
        logging.info(f"shutdown monitor on {self.root}")