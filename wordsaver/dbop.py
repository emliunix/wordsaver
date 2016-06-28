# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.pool
import wordsaver.dbconfig as dbconfig
import os
import itertools
import wordsaver.bing as bing

minconn = dbconfig.poolconfig["minconn"]
maxconn = dbconfig.poolconfig["maxconn"]

pool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, **dbconfig.dbconfig)

def dbinit(cur):
    filepath = os.path.dirname(__file__)
    sqlpath = os.path.join(filepath, "dbinit.sql")
    with open(sqlpath, "r") as sqlfile:
        sql = sqlfile.read()
        # for l in sqlfile:
        #     if not l.startswith("--") and not l.strip() == "" :
        #         cur.execute(l)
    cur.execute(sql)

def check(conn):
    cur = conn.cursor()
    try:
        cur.execute("SELECT key, value FROM metadata")
        return True
    except psycopg2.DatabaseError:
        conn.rollback()
        return False

def checkandinit(conn):
    if not check(conn):
        try:
            cur = conn.cursor()
            dbinit(cur)
            conn.commit()
        except psycopg2.DatabaseError as err:
            print(err)
            print("Database Init error.")
            conn.rollback()

def template(f):
    def fun(*args, **kwargs):
        conn = pool.getconn()
        cur = conn.cursor()
        try:
            ret = f(cur, *args, **kwargs)
            conn.commit()
            return ret
        except StandardError as err:
            conn.rollback()
            raise err
        finally:
            pool.putconn(conn)
    return fun

class Word(object):
    def __init__(self, wid, word, **attrs):
        self.wid = wid
        self.word = word
        keys = attrs.keys()
        keys += {"wid", "word"}
        self.keys = keys
        for (name, value) in attrs.items():
            self.__setattr__(name, value)

    def __str__(self):
        return "Word(%d: %s)" % (self.wid, self.word)

    def __repr__(self):
        return self.__str__()

    def todict(self):
        return dict((k, self.__getattribute__(k)) for k in self.keys)

WordKeys = ("wid", "word", "pronounce_eng", "pronounce_us")

def marshal(keys, data):
    return dict(itertools.izip(keys, data))

@template   
def addword(cur, word):
    cur.execute("INSERT INTO word (word) VALUES (%s) RETURNING wid", (word, ))
    result = cur.fetchone()
    if result:
        return marshal(("wid", "word"), (result[0], word))
    else:
        return None

@template
def delword(cur, wid):
    cur.execute("DELETE FROM word WHERE wid = %s", (wid, ))
    return True

@template
def getword(cur, wid):
    cur.execute("SELECT wid, word, pronounce_eng, pronounce_us FROM word WHERE wid = %s", (wid, ))
    w = cur.fetchone()
    if w:
        return marshal(WordKeys, w)
    else:
        return None

@template
def getallword(cur):
    cur.execute("SELECT wid, word, pronounce_eng, pronounce_us FROM word ORDER BY wid DESC")
    words = [marshal(WordKeys, w) for w in cur.fetchall()]
    return words

@template
def updateword(cur, word):
    cur.execute("UPDATE word SET word = %s WHERE wid = %s",
        (word.word, word.wid))
    return True

@template
def getworddetail(cur, wid):
    cur.execute("SELECT type, definition FROM word_definition WHERE wid = %s", (wid, ))
    defs = [marshal(("type", "definition"), d) for d in cur.fetchall()]
    cur.execute("SELECT kind, word FROM word_variants WHERE wid = %s", (wid, ))
    varis = [marshal(("kind", "word"), v) for v in cur.fetchall()]
    return {
        "definitions": defs,
        "variants": varis
    }

@template
def refreshworddetail(cur, wid):
    cur.execute("SELECT word FROM word WHERE wid = %s", (wid, ))
    word = cur.fetchone()
    if word:
        word = word[0]
    if word:
        # clear old data
        cur.execute("DELETE FROM word_definition WHERE wid = %s", (wid, ))
        cur.execute("DELETE FROM word_variants WHERE wid = %s", (wid, ))
        # request bing server for word detail
        word = bing.search(word)
        if None == word:
            return False
        # pronounce
        prus = word["pronounces"].get("us")
        preng = word["pronounces"].get("eng")
        cur.execute("UPDATE word SET pronounce_eng = %s, pronounce_us = %s WHERE wid = %s", (preng, prus, wid))
        # definitions
        params = ((wid, defi["pos"], defi["def"]) for defi in word["definitions"])
        cur.executemany("INSERT INTO word_definition (wid, type, definition) VALUES (%s, %s, %s)", params)
        # variants
        params = ((wid, v["kind"], v["word"]) for v in word["variants"])
        cur.executemany("INSERT INTO word_variants (wid, kind, word) VALUES (%s, %s, %s)", params)
        return True
    else:
        return None


conn = pool.getconn()
try:
    checkandinit(conn)
except StandardError:
    pass
finally:
    pool.putconn(conn)
del conn
