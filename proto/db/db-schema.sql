PRAGMA foreign_keys = ON;

/* file registry */
CREATE TABLE IF NOT EXISTS [files] (
    [id] INTEGER PRIMARY KEY,
    [path] STRING NOT NULL UNIQUE,
    [parent] INTEGER, -- NULL if root entry
    [modified] REAL NOT NULL,
    -- root entry points to itself
    [is_dir] INTEGER NOT NULL,
    FOREIGN KEY(parent) REFERENCES files(id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_files_paths 
ON [files] (path);

CREATE INDEX IF NOT EXISTS idx_files_parent 
ON [files] (parent);


/* put parent as path, replace with id */
CREATE TRIGGER IF NOT EXISTS [files_find_parent] 
AFTER INSERT ON [files]
BEGIN
    UPDATE [files]
    SET
    parent = (SELECT id FROM [files] WHERE path = NEW.parent LIMIT 1)
    WHERE id = NEW.id;
END;

/* file metadata keys */
CREATE TABLE IF NOT EXISTS [meta_keys] (
    [id] INTEGER PRIMARY KEY,
    [mkey] STRING UNIQUE,
    [mtype] STRING,
    [descr] STRING
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mkeys 
ON [meta_keys] (mkey);

/* file metadata store */
CREATE TABLE IF NOT EXISTS [meta_values] (
    [id] INTEGER PRIMARY KEY,
    [mkey_id] INTEGER,
    [mvalue] ANY, -- weak typing
    FOREIGN KEY(mkey_id) REFERENCES meta_keys(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mvalues 
ON [meta_values] (mvalue); -- TODO test performance for weak typing

CREATE INDEX IF NOT EXISTS idx_mvalues_keys 
ON [meta_values] (mkey_id);

/* ignore if record exists */
CREATE TRIGGER IF NOT EXISTS [mvalues_ignore_dupes] 
BEFORE INSERT ON [meta_values]
WHEN 
    (SELECT count(*) 
    FROM meta_values 
    JOIN meta_keys
    ON meta_keys.id = meta_values.mkey_id
    -- mkey_id stores mkey here
    WHERE meta_keys.mkey = NEW.mkey_id AND meta_values.mvalue = NEW.mvalue)
    <> 0
BEGIN
    SELECT(RAISE(IGNORE));
END;

/* add key if not exists */
CREATE TRIGGER IF NOT EXISTS [mvalues_add_key] 
BEFORE INSERT ON [meta_values]
WHEN 
    (SELECT count(*) 
    FROM meta_keys 
    WHERE NEW.mkey_id IN (meta_keys.id, meta_keys.mkey))
    = 0
BEGIN
    INSERT INTO meta_keys(mkey) VALUES
    (NEW.mkey_id);
END;

/* put key_id as mkey string, replace with id */
CREATE TRIGGER IF NOT EXISTS [mvalues_find_key] 
AFTER INSERT ON [meta_values]
BEGIN
    UPDATE [meta_values]
    SET
    mkey_id = (SELECT id FROM meta_keys WHERE mkey_id = NEW.mkey_id LIMIT 1)
    WHERE id = NEW.id;
END;

/* file to metadata map (M:M) */
CREATE TABLE IF NOT EXISTS [meta_map] (
    [file_id] INTEGER,
    [mvalue_id] INTEGER,
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY(mvalue_id) REFERENCES meta_values(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_map_files 
ON [meta_map] (file_id);

CREATE INDEX IF NOT EXISTS idx_map_values 
ON [meta_map] (mvalue_id);

/* metadata + key info */
CREATE VIEW IF NOT EXISTS meta_data AS
SELECT
    mkey,
    mtype,
    mvalue,
    descr
FROM
    meta_keys
    JOIN meta_values ON meta_values.mkey_id = meta_keys.id;

