import sqlite3
from parse import load_ilmo

conn = sqlite3.connect('textpile.db')
cur = conn.cursor()

cur.executescript(file('schema.sql').read())

# load positive postings
start_row = 1
sql = 'insert into doc (title, body) values (?,?)'
cur.executemany(sql, ((doc['title'], doc['desc'])
                      for doc in load_ilmo()))
end_row = start_row + cur.rowcount
cur.execute("insert into label (label_id, tag) values (1, 'bad')")
cur.execute("insert into label (label_id, tag) values (2, 'good')")
sql = 'insert into doc_label (doc_id, label_id) values (?,?)'
cur.executemany(sql, ((id, 2) for id in range(start_row, end_row)))

cur.execute("insert into meta (key, value) values ('last_updated', '')")

cur.close()
conn.commit()
