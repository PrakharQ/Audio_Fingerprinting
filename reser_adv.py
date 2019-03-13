#!/usr/bin/python
from libs.db_sqlite import SqliteDatabase
import os
if __name__ == '__main__':
 for i in range(0,1):
  if(i<=9):
      file_name="advertisement_data/fingerprints1.db"
  else:
      file_name="20_mins/"+str(i)+"/fingerprints2.db"
  db = SqliteDatabase(file_name)

  #
  # songs table

  db.query("DROP TABLE IF EXISTS songs;")
  print('removed db.audio');

  db.query("""
    CREATE TABLE songs (
      id  INTEGER PRIMARY KEY AUTOINCREMENT,
      name  TEXT,
      filehash  TEXT
    );
  """)
  print('created database= db');

  #
  # fingerprints table

  db.query("DROP TABLE IF EXISTS fingerprints;")
  print('removed db.fingerprints');

  db.query("""
    CREATE TABLE `fingerprints` (
      `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
      `song_fk` INTEGER,
      `hash`  TEXT,
      `offset`  INTEGER
    );
  """)
  print('created db.fingerprints');

  print('done');
  
  
  
  print('created db.fingerprints');

  print('done');
