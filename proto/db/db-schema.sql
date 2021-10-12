/* file registry */
CREATE TABLE IF NOT EXISTS [files] (
    [id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [path] STRING NOT NULL UNIQUE,
    [modified] REAL NOT NULL
);

/* file metadata keys */
CREATE TABLE IF NOT EXISTS [meta_keys] (
    [id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [llid] STRING NOT NULL UNIQUE, -- low-level ID
    [label] STRING NOT NULL UNIQUE,
    [type] STRING NOT NULL, -- value type
    [descr] STRING
);

/* file metadata store */
CREATE TABLE IF NOT EXISTS [meta_values] (
    [id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [key_id] INTEGER,
    [value] STRING,
    FOREIGN KEY(key_id) REFERENCES meta_keys(id)
);

/* file to metadata map (M:M) */
CREATE TABLE IF NOT EXISTS [meta_map] (
    [file_id] INTEGER,
    [mvalue_id] INTEGER,
    FOREIGN KEY(file_id) REFERENCES files(id),
    FOREIGN KEY(mvalue_id) REFERENCES meta_values(id) ON DELETE NO ACTION
);

/* metadata + key info */
CREATE VIEW IF NOT EXISTS meta_data AS
SELECT
    meta_values.id as id,
    meta_keys.id as key_id,
    llid,
    label,
    type,
    descr,
    value
FROM
    meta_keys
    INNER JOIN meta_values ON meta_values.key_id = meta_keys.id;

/* directories to watch recursively */
CREATE TABLE IF NOT EXISTS [dirs] (
    [path] STRING PRIMARY KEY,
    [modified] REAL NOT NULL
);
