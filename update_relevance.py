
import sqlite3
import datetime as dt
from model import train, predict

# accuracy 0.504783831626 *
#param = {'regu': 0.5, 'bg_weight': 1}
# accuracy 0.78850877193 *
param = dict(regu=0.01, bg_weight=0.03)

def update():
    conn = sqlite3.connect('textpile.db')
    docs, labels = query_train(conn)
    model = train(docs, labels, **param)
    docs, doc_ids = query_predict(conn)
    labels, scores = predict(model, docs)
    conn.execute('DELETE FROM doc_relevance')
    sql = 'INSERT INTO doc_relevance (doc_id, relevance) VALUES (?,?)'
    res = ((id, sco) for id, sco, lab in zip(doc_ids, scores, labels))
    conn.executemany(sql, res)
    sql = 'UPDATE meta SET value = ? WHERE key = \'last_updated\''
    now = dt.datetime.utcnow().isoformat(' ')[:19]
    conn.execute(sql, [now])
    conn.commit()

def query_train(conn):
    sql = '''
        SELECT title, body, IFNULL(label_id, 0) AS label_id
        FROM doc a LEFT JOIN doc_label b USING (doc_id)
    '''
    res = conn.execute(sql).fetchall()
    docs = ((title, body) for title, body, label in res)
    labels = (label for title, body, label in res)
    return docs, labels

def query_predict(conn):
    sql = '''
        SELECT a.doc_id, title, body
        FROM doc a LEFT JOIN doc_label b USING (doc_id)
        WHERE label_id IS NULL
    '''
    res = conn.execute(sql).fetchall()
    docs = ((title, body) for doc_id, title, body in res)
    doc_ids = (doc_id for doc_id, title, body in res)
    return docs, doc_ids

if __name__=='__main__':
    update()
