--file registry
CREATE TABLE IF NOT EXISTS [Files] (
    [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [Path] STRING NOT NULL UNIQUE,
    [Modified] INTEGER NOT NULL
);

--file metadata keys
CREATE TABLE IF NOT EXISTS [MetaKeys] (
    [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [LLID] STRING NOT NULL UNIQUE, --Low-level ID
    [Label] STRING NOT NULL UNIQUE,
    [ValueType] STRING NOT NULL,
    [Descr] STRING 
);

--file metadata store
CREATE TABLE IF NOT EXISTS [MetaData] (
    [ID] INTEGER PRIMARY KEY AUTOINCREMENT,
    [KeyID] INTEGER,
    [Value] STRING,
    FOREIGN KEY(KeyID) REFERENCES MetaKeys(ID)
);

--file to metadata map (M:M)
CREATE TABLE IF NOT EXISTS [MetaMap] (
    [FileID] INTEGER,
    [MetaDataID] INTEGER,
    FOREIGN KEY(FileID) REFERENCES Files(ID),
    FOREIGN KEY(MetaDataID) REFERENCES MetaData(ID)
    ON DELETE NO ACTION
);

--metadata + key info
CREATE VIEW v_MetaData AS 
SELECT 
    MetaData.ID as ID,
    MetaKeys.ID as KeyID,
    LLID,
    Label,
    valuetype as type,
    descr,
    value
FROM MetaKeys INNER JOIN MetaData 
    ON MetaData.KeyID = MetaKeys.ID;

-- view MetaMap + path
CREATE VIEW v_MetaMap 
AS 
SELECT
    MetaMap.FileID AS FileID,
    MetaMap.MetaDataID AS MetaDataID,
    Path
FROM Files
    INNER JOIN MetaMap ON MetaMap.FileID = Files.ID;