
from typing import Any, NamedTuple

class File(NamedTuple):
    """
    file_id : int
    file_path : str
    parent : int for id or str for path
    modified : float
    is_dir : bool
    """
    file_id : int
    file_path : str
    parent : Any
    modified : float
    is_dir : bool

class MKey(NamedTuple):
    """
    mkey_id : int
    mkey : str
    mtype : str
    mkey_descr : str
    """
    mkey_id : int
    mkey : str
    mtype : str
    mkey_descr : str

class MValue(NamedTuple):
    """
    mvalue_id : int
    mkey_id : int
    mvalue : Any
    """
    mvalue_id : int
    mkey_id : int
    mvalue : Any

class MMap(NamedTuple):
    """
    file_id : int
    mvalue_id : int
    """
    file_id : int
    mvalue_id : int

class MData(NamedTuple):
    """
    file_id : int
    mvkey : str
    mvalue : Any
    """
    file_id : int
    mvkey : str
    mvalue : Any
