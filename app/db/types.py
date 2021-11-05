
from typing import Any, NamedTuple

class File(NamedTuple):
    """
    records from files_view  
    
    file_id: int
    file_path: str
    parent_id: int
    modified: float
    is_dir: bool
    filename: str
    parent_path: str
    """
    file_id: int
    file_path: str
    parent_id: int
    modified: float
    is_dir: bool
    filename: str = None
    parent_path: str = None

class MData(NamedTuple):
    """
    file_id : int
    mvkey : str
    mvalue : Any
    """
    file_id : int
    mvkey : str
    mvalue : Any
