UPD_KEYS = {
    "Files": ['Path', 'Modified'],
    "MetaKeys": ['LLID', 'Label', 'ValueType', 'Descr'],
    "MetaData": ['KeyID', 'Value'],
    "MetaMap": ['FileID', 'MetaDataID']
}

#ON CONFLICT clause
UPD_CONFL = {
    "Files": """
    ON CONFLICT(Path) DO UPDATE SET
    Modified=excluded.Modified
    WHERE excluded.Modified>Files.Modified
    """,
    "MetaKeys": """
    ON CONFLICT(LLID) DO UPDATE SET 
    label = excluded.label,
    valuetype = excluded.valuetype,
    descr = excluded.descr
    """,
    "MetaData": "",
    "MetaMap": ""
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
