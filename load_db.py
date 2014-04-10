#!/usr/bin/env python

import sys
import sqlite3
from parse import load

# load_db.py data/*.2014-03-22.msgpack

paths = sys.argv[1:]
assert paths

conn = sqlite3.connect('textpile.db')
cur = conn.cursor()

# load postings (unknown labels)
sql = 'insert into doc (title, body, url, published_date) values (?,?,?,?)'
cur.executemany(sql, ((doc['title'], doc['desc'], doc['url'], doc['published'])
                      for doc in load(paths)))
print "loaded %d docs" % cur.rowcount

cur.close()
conn.commit()
