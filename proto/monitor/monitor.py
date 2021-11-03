import logging
from os.path import isdir, getmtime, join as joinpath
from os import walk, listdir
from typing import List, Set

from PyQt5.QtCore import QFileSystemWatcher

from proto.db.manager import DbManager
from proto.db.types import *
from proto.monitor.dumper import get_data

class Monitor:

    @staticmethod
    def walk_dir( directory: str, recursive: bool) -> List[File]:

        if not isdir(directory): 
            return []
            
        files = [File(None, directory, None, getmtime(directory), True)]

        if not recursive:
            for entry in listdir(directory):
                path = joinpath(directory, entry)
                files.append(File(None, path, directory, getmtime(path), isdir(path)))
        else:
            for root, dirnames, filenames in walk(directory, topdown=False):
                for dname in dirnames:
                    dirpath = joinpath(root, dname)
                    modified = getmtime(dirpath)
                    files.append(File(None, dirpath, root, modified, True))

                for fname in filenames:
                    filepath = joinpath(root, fname)
                    modified = getmtime(filepath)
                    files.append(File(None, filepath, root, modified, False))
                
        return files
        
    def __init__(self, db: DbManager) -> None:
        self.db = db
        self.watchdog = QFileSystemWatcher()
        self.watchdog.directoryChanged.connect(lambda path: self.update( {path} ))
        
    def update(self, nodes: Set[str], deep: bool = False) -> None:
        filtered = list(set(nodes))
        filtered.sort()
        filtered = filtered[:1] + [ path for i, path in enumerate(filtered[1:]) if path.find(filtered[i-1]) == -1 ]
        nodes = set(filtered)

        if not nodes: return
        logging.info(f"updating dirs: {nodes}")

        fs_records = { file.file_path: file for node in nodes for file in Monitor.walk_dir(node, deep) }
        db_records = { file.file_path: file for node in nodes for file in self.db.get_files_in_dir(node) }

        db_paths = set(db_records)
        fs_paths = set(fs_records)
        paths_to_delete = db_paths - fs_paths
        paths_to_insert = fs_paths - db_paths
        paths_to_update = fs_paths & db_paths

        files_to_insert = { fs_records[path] for path in paths_to_insert }
        files_to_update = { fs_records[path] for path in paths_to_update }
        
        files_to_watch =  { path for path, file in fs_records.items() if file.is_dir and path not in nodes }
        
        if paths_to_delete: self.db.remove_files(paths_to_delete)
        if files_to_insert: self.db.insert_files(files_to_insert)
        if files_to_update: self.db.update_files(files_to_update)
        
        updated_files = self.db.get_files_by_paths(list(paths_to_insert | paths_to_update))   #TODO: optimise?
        metamap = []
        for file in updated_files:
            data = get_data(file.file_path)
            data.pop('filename', None)
            for key, value in data.items():
                metamap.append((file.file_id, key, value))
        if metamap: self.db.insert_metadata(metamap)

        self.watchdog.addPaths(nodes)
        if files_to_watch: 
            self.watchdog.addPaths(files_to_watch)
            self.update(files_to_watch, True)

    def unwatch(self, paths):
        self.watchdog.removePaths(paths)

    def __del__(self):
        logging.info(f"shutdown monitor on {self.root}")