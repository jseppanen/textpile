import sqlite3
import sys
from parse import load_ilmo

# load_ilmo.py ilmoituksia_2014.html

conn = sqlite3.connect('textpile.db')
cur = conn.cursor()

doc_id, = cur.execute('select max(doc_id)+1 from doc').fetchone()

sql = 'insert into doc (doc_id, title, body) values (?,?,?)'
cur.executemany(sql, ((doc_id+i, doc['title'], doc['desc'])
                      for i,doc in enumerate(load_ilmo(sys.argv[1]))))
num_loaded = cur.rowcount

sql = 'insert into doc_label (doc_id, label_id) values (?,?)'
cur.executemany(sql, ((id, 2) for id in range(doc_id, doc_id+num_loaded)))

cur.close()
conn.commit()
conn.close()
