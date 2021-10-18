PRAGMA foreign_keys = ON;

/* 
DATA TABLES
*/

/* file registry */
CREATE TABLE IF NOT EXISTS [files] (
    [id] INTEGER PRIMARY KEY,
    [path] STRING NOT NULL UNIQUE,
    [parent] INTEGER, -- NULL if root entry
    [modified] REAL NOT NULL,
    [is_dir] INTEGER NOT NULL,
    FOREIGN KEY(parent) REFERENCES files(id) ON UPDATE CASCADE ON DELETE CASCADE
);

/* file metadata keys */
CREATE TABLE IF NOT EXISTS [meta_keys] (
    [id] INTEGER PRIMARY KEY,
    [mkey] STRING UNIQUE,
    [mtype] STRING,
    [descr] STRING
);

/* file metadata store */
CREATE TABLE IF NOT EXISTS [meta_values] (
    [id] INTEGER PRIMARY KEY,
    [mkey_id] INTEGER,
    [mvalue] ANY, -- weak typing
    FOREIGN KEY(mkey_id) REFERENCES meta_keys(id) ON DELETE CASCADE
);

/* file to metadata map (M:M) */
CREATE TABLE IF NOT EXISTS [meta_map] (
    [file_id] INTEGER,
    [mvalue_id] INTEGER,
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY(mvalue_id) REFERENCES meta_values(id) ON DELETE CASCADE
);

/* 
DATA INDICI
*/

CREATE INDEX IF NOT EXISTS idx_files_paths 
ON [files] (path);

CREATE INDEX IF NOT EXISTS idx_files_parent 
ON [files] (parent);

CREATE UNIQUE INDEX IF NOT EXISTS idx_mkeys 
ON [meta_keys] (mkey);

CREATE INDEX IF NOT EXISTS idx_mvalues 
ON [meta_values] (mvalue); -- TODO test performance for weak typing

CREATE INDEX IF NOT EXISTS idx_mvalues_keys 
ON [meta_values] (mkey_id);

CREATE INDEX IF NOT EXISTS idx_map_files 
ON [meta_map] (file_id);

CREATE INDEX IF NOT EXISTS idx_map_values 
ON [meta_map] (mvalue_id);

/*
UTILITY LAST_ROWS TABLE & TRIGGERS
*/

CREATE TABLE IF NOT EXISTS [last_rows] (
    id INTEGER PRIMARY KEY,
    file_id INTEGER,
    mkey_id INTEGER,
    mvalue_id INTEGER,
    mmap_rowid INTEGER
);

INSERT OR IGNORE INTO last_rows(id) VALUES (0);

CREATE TRIGGER IF NOT EXISTS [mkeys_lastrow] 
AFTER INSERT ON [files]
BEGIN
    UPDATE [last_rows]
    SET
    file_id = NEW.id
    WHERE id = 0;
END;

CREATE TRIGGER IF NOT EXISTS [mkeys_lastrow] 
AFTER INSERT ON [meta_keys]
BEGIN
    UPDATE [last_rows]
    SET
    mkey_id = NEW.id
    WHERE id = 0;
END;

CREATE TRIGGER IF NOT EXISTS [mvalues_lastrow] 
AFTER INSERT ON [meta_values]
BEGIN
    UPDATE [last_rows]
    SET
    mvalue_id = NEW.id
    WHERE id = 0;
END;

CREATE TRIGGER IF NOT EXISTS [mmap_lastrow] 
AFTER INSERT ON [meta_map]
BEGIN
    UPDATE [last_rows]
    SET
    mmap_rowid = NEW.rowid
    WHERE id = 0;
END;

/*
VIEWS
*/

/* metadata + key info */
CREATE VIEW IF NOT EXISTS meta_data AS
SELECT
    meta_values.id as mvalue_id,
    mkey_id,
    mkey,
    mtype,
    mvalue,
    descr
FROM
    meta_keys
    JOIN meta_values ON meta_values.mkey_id = meta_keys.id;

/* parent path and filename map, does not include entry nodes*/
CREATE VIEW IF NOT EXISTS files_view AS
SELECT 
    t1.id,
    t1.path,
    SUBSTR(t1.path, LENGTH(t2.path) + 2) as filename,
    t1.modified,
    t1.is_dir,
    t1.parent as parent_id,
    t2.path as parent_path
FROM
   (SELECT * FROM files) as t1
   JOIN
   (SELECT id, path FROM files) as t2
   ON 
   t1.parent = t2.id;

/* file + metadata view */
CREATE VIEW IF NOT EXISTS files_metadata_map AS
SELECT
    filename,
    mkey,
    mvalue,
    mtype,
    descr,
    path,
    parent_path,
    modified,
    file_id,
    parent_id,
    meta_data.mvalue_id,    
    meta_data.mkey_id   
FROM meta_data 
    JOIN meta_map ON meta_data.mvalue_id = meta_map.mvalue_id 
    JOIN files_view ON meta_map.file_id = files_view.id;

/*
DATA TRIGGERS
*/

/* put parent as path, replace with id */

CREATE TRIGGER IF NOT EXISTS  metadata_insertion_handler
    INSTEAD OF INSERT ON files_metadata_map
BEGIN
    INSERT INTO meta_keys(mkey, mtype, descr)
    VALUES(
        NEW.mkey, 
        NEW.mtype, 
        NEW.descr
        )
        ON CONFLICT(mkey) DO UPDATE SET 
        mtype = CASE WHEN excluded.mtype = NULL THEN mtype ELSE excluded.mtype END,
        descr = CASE WHEN excluded.descr = NULL THEN descr ELSE excluded.descr END;

    UPDATE [last_rows] SET
        mkey_id = (SELECT id FROM meta_keys WHERE mkey = NEW.mkey LIMIT 1)
    WHERE id = 0;

    INSERT INTO meta_values(mkey_id, mvalue)
    VALUES(
        (SELECT mkey_id FROM last_rows WHERE id = 0 LIMIT 1),
        NEW.mvalue
        );
    -- duplicate key-value pair is handled by separate trigger for meta_values

    UPDATE [last_rows] SET
        mvalue_id = (SELECT id FROM meta_values 
        WHERE mkey_id = (SELECT id FROM meta_keys WHERE mkey = NEW.mkey LIMIT 1)
        AND mvalue = NEW.mvalue 
        LIMIT 1)
    WHERE id = 0;

    UPDATE [last_rows] SET
        file_id = (SELECT id FROM files WHERE path = NEW.path LIMIT 1)  
    WHERE id = 0;

    -- use the artist id to insert a new album
    INSERT INTO meta_map(file_id, mvalue_id)
    VALUES(
        (SELECT file_id FROM last_rows WHERE id = 0 LIMIT 1),
        (SELECT mvalue_id FROM last_rows WHERE id = 0 LIMIT 1)
        );
END;

/* put parent as path, replace with id */
CREATE TRIGGER IF NOT EXISTS [files_find_parent] 
AFTER INSERT ON [files]
    WHEN TYPEOF(NEW.parent) <> 'INTEGER'
BEGIN
    UPDATE [files]
    SET
    parent = (SELECT id FROM [files] WHERE path = NEW.parent LIMIT 1)
    WHERE id = NEW.id;
END;
