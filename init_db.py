import sqlite3

conn = sqlite3.connect('data/textpile.db')
cur = conn.cursor()

cur.executescript(file('schema.sql').read())

cur.execute("insert into label (label_id, tag) values (1, 'bad')")
cur.execute("insert into label (label_id, tag) values (2, 'good')")
cur.execute("insert into meta (key, value) values ('last_updated', '')")

cur.close()
conn.commit()
conn.close()
