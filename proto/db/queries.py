from typing import Set, Tuple


UPD_KEYS = {
    "files": ['path', 'parent', 'modified', 'is_dir'],
    "meta_keys": ['mkey', 'mtype', 'descr'],
    "meta_values": ['mkey_id', 'mvalue'],
    "meta_map": ['file_id', 'mvalue_id']
}

#ON CONFLICT clause
UPD_CONFL = {
    "files": """
    ON CONFLICT(path) DO UPDATE SET
    modified = excluded.modified
    WHERE excluded.modified > files.modified
    """,

    "meta_keys": """
    ON CONFLICT(mkey) DO UPDATE SET 
    mtype = excluded.mtype,
    descr = excluded.descr
    """,
    
    "meta_values": "",
    "meta_map": ""
}

#TODO factory for query templates

def close() -> str:
    return ";\n"

def insert(table:str) -> str:
    return \
        f"""
        INSERT INTO 
        {table}({','.join(UPD_KEYS[table])})
        VALUES
        ({','.join(['?' for _ in UPD_KEYS[table]])})
        """

def conflict_clause(table:str) -> str:
    return UPD_CONFL[table]

def select(table:str) -> str:
    return \
        f"""
        SELECT
        {','.join(UPD_KEYS[table])}
        FROM {table}
        """

def files_where_stmt(case: str) -> str:
    if case == "directory":
        return "WHERE parent = (SELECT id FROM files WHERE path = (?) LIMIT 1)"
    elif case == "suffix":
        return "WHERE path LIKE (?)"
    elif case == "id":
        return "WHERE id IS (?)"
    elif case == "roots":
        return "WHERE parent IS NULL"
    else:
        raise KeyError("unknown case")

def delete_files() -> str:
    return "DELETE FROM files WHERE path IN (?)"

def tablenames() -> str:
    return 'SELECT name FROM sqlite_master WHERE type IN ("table", "view")'
