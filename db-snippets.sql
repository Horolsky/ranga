-- an example of bad solution, ID is modified on update
INSERT OR REPLACE INTO Files(Path, Modified)
VALUES
("some_path_1", 42),
("some_path_2", 43);

-- correct upsert clause, update only if file changed
INSERT INTO Files(Path, Modified)
  VALUES
  ("some_path", 12345678)
  ON CONFLICT(Path) DO UPDATE SET
    Modified=excluded.Modified
  WHERE excluded.Modified>Files.Modified;