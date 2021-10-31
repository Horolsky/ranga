from typing import Set, Tuple


UPD_KEYS = {
    "tbl_files": ['file_path', 'parent_id', 'modified', 'is_dir'],
    "tbl_mkeys": ['mkey', 'mtype', 'mkey_descr'],
    "tbl_mvalues": ['mkey_id', 'mvalue'],
    "tbl_mmap": ['file_id', 'mvalue_id']
}

#ON CONFLICT clause
UPD_CONFL = {
    "tbl_files": """
    ON CONFLICT( [file_path] ) DO UPDATE SET
    [modified] = EXCLUDED.[modified]
    WHERE EXCLUDED.[modified] > [tbl_files].[modified]
    """,

    "tbl_mkeys": """
    ON CONFLICT( [mkey] ) DO UPDATE SET 
    [mtype] = EXCLUDED.[mtype],
    [mkey_descr] = EXCLUDED.[mkey_descr]
    """,
    
    "tbl_mvalues": "",
    "tbl_mmap": ""
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
        return "WHERE [parent_id] = (SELECT [file_id] FROM [tbl_files] WHERE [file_path] = (?) LIMIT 1)"
    elif case == "suffix":
        return "WHERE [file_path] LIKE (?)"
    elif case == "file_id":
        return "WHERE [file_id] IS (?)"
    elif case == "roots":
        return "WHERE [parent_id] IS NULL"
    else:
        raise KeyError("unknown case")

def delete_files() -> str:
    return "DELETE FROM [tbl_files] WHERE [file_path] IN (?)"

def tablenames() -> str:
    return 'SELECT [name] FROM sqlite_master WHERE [type] IN ("table", "view")'
