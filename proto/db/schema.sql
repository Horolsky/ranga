PRAGMA foreign_keys = ON;

-- DATA TABLES

/* file registry */
CREATE TABLE IF NOT EXISTS [tbl_files] (
    [file_id] INTEGER PRIMARY KEY,
    [file_path] STRING NOT NULL UNIQUE,
    [parent_id] INTEGER, -- NULL if root entry
    [modified] REAL NOT NULL,
    [is_dir] INTEGER NOT NULL,
    FOREIGN KEY( [parent_id] ) 
        REFERENCES [tbl_files]( [file_id] ) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE
);

/* file metadata keys */
CREATE TABLE IF NOT EXISTS [tbl_mkeys] (
    [mkey_id] INTEGER PRIMARY KEY,
    [mkey] STRING UNIQUE,
    [mtype] STRING,
    [mkey_descr] STRING
);

/* file metadata store */
CREATE TABLE IF NOT EXISTS [tbl_mvalues] (
    [mvalue_id] INTEGER PRIMARY KEY,
    [mkey_id] INTEGER NOT NULL,
    [mvalue] ANY, -- weak typing
    FOREIGN KEY( [mkey_id] ) 
        REFERENCES [tbl_mkeys]( [mkey_id] ) 
        ON DELETE CASCADE
);    

/* file to metadata map (M:M) */
CREATE TABLE IF NOT EXISTS [tbl_mmap] (
    [file_id] INTEGER NOT NULL,
    [mvalue_id] INTEGER NOT NULL,
    FOREIGN KEY( [file_id] ) 
        REFERENCES [tbl_files]( [file_id] ) 
        ON DELETE CASCADE,
    FOREIGN KEY( [mvalue_id] ) 
        REFERENCES [tbl_mvalues]( [mvalue_id] ) 
        ON DELETE CASCADE
);
 
-- DATA INDICI

CREATE INDEX IF NOT EXISTS [idx_files_paths] 
ON [tbl_files] ( [file_path] );

CREATE INDEX IF NOT EXISTS [idx_files_parent] 
ON [tbl_files] ( [parent_id] );

CREATE UNIQUE INDEX IF NOT EXISTS [idx_mkeys] 
ON [tbl_mkeys] ( [mkey] );

CREATE INDEX IF NOT EXISTS [idx_mvalues] 
ON [tbl_mvalues] ( [mvalue] ); 
-- TODO test performance for weak typing

CREATE INDEX IF NOT EXISTS [idx_mvalues_keys] 
ON [tbl_mvalues] ( [mkey_id] );

CREATE INDEX IF NOT EXISTS [idx_map_files] 
ON [tbl_mmap] ( [file_id] );

CREATE INDEX IF NOT EXISTS [idx_map_values] 
ON [tbl_mmap] ( [mvalue_id] );


-- DATA VIEWS

/* metadata + key info */
CREATE VIEW IF NOT EXISTS [view_meta] AS
SELECT
    [tbl_mvalues].[mkey_id],
    [mkey],
    [mtype],
    [mkey_descr],
    [tbl_mvalues].[mvalue_id],
    [mvalue]
FROM
    [tbl_mkeys]
    JOIN [tbl_mvalues] ON [tbl_mvalues].[mkey_id] = [tbl_mkeys].[mkey_id];

/* parent path and filename map, does not include entry nodes*/
CREATE VIEW IF NOT EXISTS [view_files] AS
SELECT 
/*
file_id
file_path
parent_id
modified
is_dir
--
filename
parent_path
*/
    [tmp_1].[file_id],
    [tmp_1].[file_path],
    [tmp_1].[parent_id],
    [tmp_1].[modified],
    [tmp_1].[is_dir],
    SUBSTR(
        [tmp_1].[file_path], LENGTH( [tmp_2].[file_path] ) + 2
        ) as [filename],
    [tmp_2].[file_path] as [parent_path]
FROM
   (SELECT * FROM [tbl_files] ) as [tmp_1]
   JOIN
   (SELECT [file_id], [file_path] FROM [tbl_files] ) as [tmp_2]
   ON 
   [tmp_1].[parent_id] = [tmp_2].[file_id];

/* file + metadata view */
CREATE VIEW IF NOT EXISTS [view_data] AS
SELECT
    [view_files].[file_id],
    [view_files].[file_path],
    [view_files].[parent_id],
    [view_files].[modified],
    [view_files].[is_dir],
    [view_files].[filename],
    [view_files].[parent_path],
    
    [view_meta].[mkey_id],
    [view_meta].[mkey],
    [view_meta].[mtype],
    [view_meta].[mkey_descr],
    
    [view_meta].[mvalue_id],
    [view_meta].[mvalue]
       
FROM [view_meta] 
    JOIN [tbl_mmap] ON [view_meta].[mvalue_id] = [tbl_mmap].[mvalue_id] 
    JOIN [view_files] ON [tbl_mmap].[file_id] = [view_files].[file_id];


-- UTILITY

CREATE TABLE IF NOT EXISTS [tbl_variables] (
    [var_key] VARCHAR(16) UNIQUE,
    [var_value] ANY
);

CREATE TRIGGER IF NOT EXISTS [trg_variables_setter]
    BEFORE INSERT ON [tbl_variables]
BEGIN
    DELETE FROM [tbl_variables] WHERE [var_key]=NEW.[var_key];
END;

-- INSERTION FILTERS

CREATE TRIGGER IF NOT EXISTS [trg_mvalues_filter]
BEFORE INSERT ON [tbl_mvalues]
    WHEN EXISTS (
        SELECT mkey_id FROM [tbl_mvalues] 
        WHERE [mkey_id] = NEW.[mkey_id] 
        AND [mvalue] = NEW.[mvalue])
BEGIN
    SELECT RAISE(IGNORE);
END;

CREATE TRIGGER IF NOT EXISTS [trg_mmap_filter]
BEFORE INSERT ON [tbl_mmap]
    WHEN EXISTS (
        SELECT mvalue_id FROM [tbl_mmap] 
        WHERE [file_id] = NEW.[file_id] 
        AND [mvalue_id] = NEW.[mvalue_id])
BEGIN
    SELECT RAISE(IGNORE);
END;

-- SETTERS

CREATE TRIGGER IF NOT EXISTS [trg_file_setter]
INSTEAD OF INSERT ON [view_files]
BEGIN
    INSERT INTO [tbl_files] VALUES
    (
        NULL,
        NEW.[file_path],
        CASE 
            WHEN NEW.[parent_id] IS NULL AND NEW.[parent_path] IS NOT NULL
            THEN (
                SELECT [file_id] FROM [tbl_files]
                WHERE [file_path] = NEW.[parent_path]
                LIMIT 1)
            ELSE NEW.[parent_id] END
        ,
        NEW.[modified],
        NEW.[is_dir]
    )
    ON CONFLICT( [file_path] ) DO UPDATE SET
        [modified] = NEW.[modified]
        WHERE NEW.[modified] > [tbl_files].[modified];
END;

CREATE TRIGGER IF NOT EXISTS [trg_mmap_setter]
INSTEAD OF INSERT ON [view_data]
-- (file_id, mkey, mvalue) VALUES
BEGIN
    INSERT OR IGNORE INTO [tbl_mkeys] VALUES
    (
        NULL,
        NEW.[mkey],
        TYPEOF(NEW.[mvalue]),
        NULL
    );    

    INSERT OR IGNORE INTO [tbl_mvalues] VALUES
    (
        NULL,
        (SELECT [mkey_id] FROM [tbl_mkeys] 
        WHERE [mkey] = NEW.[mkey] LIMIT 1),
        NEW.[mvalue]
    );    

    INSERT INTO [tbl_mmap] VALUES
    (
        NEW.[file_id],
        (SELECT [mvalue_id] FROM [view_meta] 
        WHERE [mvalue] = NEW.[mvalue] 
        AND [mkey] = NEW.[mkey] LIMIT 1)
    );    
END;
