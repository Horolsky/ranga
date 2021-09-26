-- update the MetaKey registry (categories)
INSERT INTO MetaKeys(LLID, label, valuetype, descr)
VALUES 
    ("auth", "author", "string", NULL),
    ("cmps", "composer", "string", "music composer"),
    ("lang", "language", "string", "lanuage of original") 
ON CONFLICT(LLID) DO UPDATE SET 
    label = excluded.label,
    valuetype = excluded.valuetype,
    descr = excluded.descr;

-- update the file registry
INSERT INTO Files(Path, Modified)
VALUES 
("file_1", 0),
("file_2", 23465),
("file_3", 3322354),
("file_4", 132546),
("file_5", 23465),
("file_1", 436535742) -- conflict example
ON CONFLICT(Path) DO UPDATE SET 
    Modified = excluded.Modified
    WHERE excluded.Modified > Files.Modified;

-- adding values to meta keys, no conflict handling needed
INSERT INTO MetaData(KeyID, Value)
VALUES 
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "auth"), "Pasolini"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "auth"), "Tarantino"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "auth"), "Kusturica"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "auth"), "Danelia"),

((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Gibbons"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Purcell"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Lawes"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Locke"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Dunstable"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Dowland"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Marais"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "cmps"), "Lully"),

((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "lang"), "English"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "lang"), "Mandarin"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "lang"), "Deutch"),
((SELECT ID FROM MetaKeys WHERE MetaKeys.LLID = "lang"), "Klingon");


-- mapping files to meta, duplicates from diff cats handled
-- actual ids can be retieved on the app side, so final query will be reduced
INSERT INTO MetaMap(FileID, MetaDataID)
VALUES 
((SELECT ID FROM Files WHERE Files.Path = "file_1" ),
(SELECT ID FROM v_MetaData WHERE LLID = "auth" AND Value = "Pasolini")),
((SELECT ID FROM Files WHERE Files.Path = "file_1"), 
(SELECT ID FROM v_MetaData WHERE  LLID = "auth" AND Value = "Tarantino")),
((SELECT ID FROM Files WHERE Files.Path = "file_1"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Gibbons")),

((SELECT ID FROM Files WHERE Files.Path = "file_2" ),
(SELECT ID FROM v_MetaData WHERE LLID = "auth" AND Value = "Kusturica")),

((SELECT ID FROM Files WHERE Files.Path = "file_3"), 
(SELECT ID FROM v_MetaData WHERE  LLID = "auth" AND Value = "Danelia")),
((SELECT ID FROM Files WHERE Files.Path = "file_3"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Dowland")),
((SELECT ID FROM Files WHERE Files.Path = "file_3"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Marais")),
((SELECT ID FROM Files WHERE Files.Path = "file_3"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Lully")),
((SELECT ID FROM Files WHERE Files.Path = "file_3"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Dunstable")),
((SELECT ID FROM Files WHERE Files.Path = "file_3"),
(SELECT ID FROM v_MetaData WHERE  LLID = "cmps" AND Value = "Lawes"));


-- list fields in concat form 
SELECT
FileID,
Path,
SUM(CASE WHEN v_MetaData.LLID = "auth" THEN 1 ELSE 0 END) as auth_n,
SUM(CASE WHEN v_MetaData.LLID = "cmps" THEN 1 ELSE 0 END) as cmps_n,
GROUP_CONCAT(CASE WHEN v_MetaData.LLID = "auth" THEN v_MetaData.Value ELSE NULL END) as authors,
GROUP_CONCAT(CASE WHEN v_MetaData.LLID = "cmps" THEN v_MetaData.Value ELSE NULL END) as composers
FROM
v_MetaData INNER JOIN v_MetaMap ON v_MetaData.ID = v_MetaMap.MetaDataID
GROUP BY Path;