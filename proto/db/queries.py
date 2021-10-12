UPD_KEYS = {
    "files": ['path', 'modified'],
    "meta_keys": ['llid', 'label', 'type', 'descr'],
    "meta_values": ['key_id', 'value'],
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
    ON CONFLICT(llid) DO UPDATE SET 
    label = excluded.label,
    type = excluded.type,
    descr = excluded.descr
    """,
    
    "meta_values": "",
    "meta_map": ""
}

def update_query(table:str) -> str:
    # norm_values = map(lambda s: f'"{s}"', values)
    return \
        f"""
        INSERT INTO 
        {table}({','.join(UPD_KEYS[table])})
        VALUES
        ({','.join(['?' for _ in UPD_KEYS[table]])})
        {UPD_CONFL[table]}
        ;\n
        """
