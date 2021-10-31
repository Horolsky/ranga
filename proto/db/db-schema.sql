PRAGMA foreign_keys = ON;

/* 
DATA TABLES
*/

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
    [mkey_id] INTEGER,
    [mvalue] ANY, -- weak typing
    FOREIGN KEY( [mkey_id] ) 
        REFERENCES [tbl_mkeys]( [mkey_id] ) 
        ON DELETE CASCADE
);

/* file to metadata map (M:M) */
CREATE TABLE IF NOT EXISTS [tbl_mmap] (
    [file_id] INTEGER,
    [mvalue_id] INTEGER,
    FOREIGN KEY( [file_id] ) 
        REFERENCES [tbl_files]( [file_id] ) 
        ON DELETE CASCADE,
    FOREIGN KEY( [mvalue_id] ) 
        REFERENCES [tbl_mvalues]( [mvalue_id] ) 
        ON DELETE CASCADE
);

/* 
DATA INDICI
*/

CREATE INDEX IF NOT EXISTS [idx_files_paths] 
ON [tbl_files] ( [file_path] );

CREATE INDEX IF NOT EXISTS [idx_files_parent] 
ON [tbl_files] ( [parent_id] );

CREATE UNIQUE INDEX IF NOT EXISTS [idx_mkeys] 
ON [tbl_mkeys] ( [mkey] );

CREATE INDEX IF NOT EXISTS [idx_mvalues] 
ON [tbl_mvalues] ( [mvalue] ); -- TODO test performance for weak typing

CREATE INDEX IF NOT EXISTS [idx_mvalues_keys] 
ON [tbl_mvalues] ( [mkey_id] );

CREATE INDEX IF NOT EXISTS [idx_map_files] 
ON [tbl_mmap] ( [file_id] );

CREATE INDEX IF NOT EXISTS [idx_map_values] 
ON [tbl_mmap] ( [mvalue_id] );

/*
UTILITY var TABLE & TRIGGERS
*/

CREATE TABLE IF NOT EXISTS [tbl_variables] (
    [var_key] VARCHAR(16) UNIQUE,
    [var_value] ANY
);

CREATE TRIGGER IF NOT EXISTS [trg_variables_setter]
    BEFORE INSERT ON [tbl_variables]
BEGIN
    DELETE FROM [tbl_variables] WHERE [var_key]=NEW.[var_key];
END;


-- CREATE TRIGGER IF NOT EXISTS [mkeys_lastrow] 
-- AFTER INSERT ON [tbl_files]
-- BEGIN
    -- INSERT INTO [tbl_variables]
    -- VALUES ("last_file_id", NEW.file_id);
-- END;
-- 
-- CREATE TRIGGER IF NOT EXISTS [mkeys_lastrow] 
-- AFTER INSERT ON [tbl_mkeys]
-- BEGIN
    -- INSERT INTO [tbl_variables]
    -- VALUES ("last_mkey_id", NEW.mkey_id);
-- END;
-- 
-- CREATE TRIGGER IF NOT EXISTS [mvalues_lastrow] 
-- AFTER INSERT ON [tbl_mvalues]
-- BEGIN
    -- INSERT INTO [tbl_variables]
    -- VALUES ("last_mvalue_id", NEW.mvalue_id);
-- END;
-- 
-- CREATE TRIGGER IF NOT EXISTS [mmap_lastrow] 
-- AFTER INSERT ON [tbl_mmap]
-- BEGIN
    -- INSERT INTO [tbl_variables]
    -- VALUES ("last_mmap_row", NEW.rowid);
-- END;

/*
VIEWS
*/

/* metadata + key info */
CREATE VIEW IF NOT EXISTS [view_metadata] AS
SELECT
    -- tbl_mvalues.mvalue_id,
    [tbl_mvalues].[mkey_id],
    [tbl_mvalues].[mvalue_id],
    [mkey],
    [mtype],
    [mvalue],
    [mkey_descr]
FROM
    [tbl_mkeys]
    JOIN [tbl_mvalues] ON [tbl_mvalues].[mkey_id] = [tbl_mkeys].[mkey_id];

/* parent path and filename map, does not include entry nodes*/
CREATE VIEW IF NOT EXISTS view_files AS
SELECT 
    [tmp_1].[file_id],
    SUBSTR(
        [tmp_1].[file_path], LENGTH( [tmp_2].[file_path] ) + 2
        ) as [filename],
    [tmp_1].[parent_id],
    [tmp_2].[file_path] as [parent_path],
    [tmp_1].[file_path],
    [tmp_1].[modified],
    [tmp_1].[is_dir]
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
    [filename],
    [file_path],
    [modified],

    [parent_id],
    [parent_path],
    
    
    
    [view_metadata].[mkey_id],
    [mkey],
    [mtype],
    [mkey_descr],
    
    [view_metadata].[mvalue_id],
    [mvalue]
       
FROM [view_metadata] 
    JOIN [tbl_mmap] ON [view_metadata].[mvalue_id] = [tbl_mmap].[mvalue_id] 
    JOIN [view_files] ON [tbl_mmap].[file_id] = [view_files].[file_id];

/*
DATA TRIGGERS
*/

/* put parent_id as path, replace with file_id */

CREATE TRIGGER IF NOT EXISTS  [trg_data_setter]
    INSTEAD OF INSERT ON [view_data]
BEGIN
    INSERT INTO [tbl_mkeys]( [mkey], [mtype], [mkey_descr] )
    VALUES(
        NEW.[mkey], 
        NEW.[mtype], 
        NEW.[mkey_descr]
        )
        ON CONFLICT( [mkey] ) DO UPDATE SET 
        [mtype] = CASE WHEN EXCLUDED.[mtype] = NULL THEN [mtype] ELSE EXCLUDED.[mtype] END,
        [mkey_descr] = CASE WHEN EXCLUDED.[mkey_descr] = NULL THEN [mkey_descr] ELSE EXCLUDED.[mkey_descr] END;

    INSERT INTO [tbl_variables] VALUES
        (
            "last_mkey_id", 
            (SELECT [mkey_id] FROM [tbl_mkeys] WHERE [mkey] = NEW.[mkey] LIMIT 1)
        );

    INSERT INTO [tbl_mvalues]( [mkey_id], [mvalue] ) VALUES
        (
            (SELECT [var_value] FROM [tbl_variables] WHERE [var_key] = "last_mkey_id" LIMIT 1),
            NEW.[mvalue]
        );
    -- duplicate key-value pair is handled by separate trigger for tbl_mvalues

    INSERT INTO [tbl_variables] VALUES
        (
            "last_mvalue_id", 
            (SELECT [mvalue_id] FROM [tbl_mvalues] 
                WHERE [mkey_id] = (SELECT [mkey_id] FROM [tbl_mkeys] WHERE [mkey] = NEW.[mkey] LIMIT 1)
                AND [mvalue] = NEW.[mvalue] 
                LIMIT 1)
        );

    INSERT INTO [tbl_variables] VALUES
        (
            "last_file_id",
            (SELECT [file_id] FROM [tbl_files] WHERE [file_path] = NEW.[file_path] LIMIT 1)
        );

    INSERT INTO tbl_mmap( [file_id], [mvalue_id] ) VALUES
        (
            (SELECT [var_value] FROM [tbl_variables] WHERE [var_key] = "last_file_id" LIMIT 1),
            (SELECT [var_value] FROM [tbl_variables] WHERE [var_key] = "last_mvalue_id" LIMIT 1)
        );
END;

/* put parent_id as path, replace with file_id */
CREATE TRIGGER IF NOT EXISTS [trg_files_setter] 
    AFTER INSERT ON [tbl_files]
    WHEN TYPEOF(NEW.[parent_id] ) <> 'INTEGER'
BEGIN
    UPDATE [tbl_files]
    SET
    [parent_id] = (SELECT [file_id] FROM [tbl_files] WHERE [file_path] = NEW.[parent_id] LIMIT 1)
    WHERE [file_id] = NEW.[file_id];
END;
