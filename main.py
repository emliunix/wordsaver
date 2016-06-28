# -*- coding: utf-8 -*-

from __future__ import print_function
import sqlite3

dbName = "words.db"

class DB:
    def __init__(self, dbName):
        self.dbName = dbName
        def _trans(fn):
            def _fn(*args):
                conn = sqlite3.connect(self.dbName)
                cur = conn.cursor()
                ret = fn(cur, *args)
                conn.commit()
                conn.close()
                return ret
            return _fn
        self.transaction = _trans

db = DB(dbName)

@db.transaction
def checkDB(cur):
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'words'")
    count = cur.fetchone()[0]
    if not count:
        # table don't exist, create one
        print("DB not found, create a new one.")
        cur.execute("CREATE TABLE words (id INTEGER PRIMARY KEY, word varchar(40) NOT NULL)")
    
@db.transaction
def fetchAll(cur):
    cur.execute("SELECT * FROM words")
    return cur.fetchall()
    
@db.transaction
def sampleData(cur):
    data = [
        ("decay", ),
        ("paradise", ),
        ("hello", ),
        ("world", )
    ]
    return cur.executemany("INSERT INTO words (word) VALUES (?)", data)

checkDB()
sampleData()
print(fetchAll())
