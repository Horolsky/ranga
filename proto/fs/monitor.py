from os.path import isfile, getmtime, join as joinpath
from os import walk, listdir
from typing import List, Tuple

from .watchdog import WatchDog
from ..db.manager import DbManager

class Monitor:
    
    @staticmethod
    def walk_dir( entry: str) -> Tuple[List[str]]:
            
            dirs = []
            files = []
            
            for root, dirnames, filenames in walk(entry, topdown=False):
                    
                for dname in dirnames:
                    dirpath = joinpath(root, dname)
                    modified = getmtime(dirpath)
                    dirs.append((dirpath, modified))

                for fname in filenames:
                    filepath = joinpath(root, fname)
                    modified = getmtime(filepath)
                    files.append((filepath, modified))
                
            return (dirs, files)
    @staticmethod 
    def scan_dir(dirpath: str):
        path = lambda entry: f"{dirpath}/{entry}"
        return [ (path(f), getmtime(path(f)))  for f in listdir(dirpath) if isfile(path(f))]


        
    def __init__(self, root: str, db: DbManager) -> None:
        print("monitor init")
        dirs, files = Monitor.walk_dir(root)
        paths = [root] + [path for  path, _ in dirs] #+ [path for  path, _ in files]
        
        self.root = root
        self.paths = paths
        self.db = db
        self.watchdog = WatchDog(paths, self.on_upd)
        
        files_to_delete = [ (path,) for path, _ in set(self.db.get_files()).difference(set(files))]
        
        self.db.remove_files(files_to_delete)
        self.db.update_files(files)
        
    def on_upd(self, dirpath: str) -> None:
        print(f"dir upd: {dirpath}")

        files = Monitor.scan_dir(dirpath)
        
        to_delete = [ (path,) for path, _ in set(self.db.get_files()).difference(set(files))]
        
        self.db.remove_files(to_delete)
        self.db.update_files(files)
    
    def __del__(self):
        print("monitor shutdown")