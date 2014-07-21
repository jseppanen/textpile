from flask import Flask, request
from flask import Flask, request, session, g, jsonify, \
    redirect, url_for, abort, render_template, flash
import sqlite3
import json

app=Flask(__name__)
app.config.from_object(__name__)
app.config.update(DATABASE=app.root_path + '/textpile.db')
app.config.from_pyfile(app.root_path + '/server.conf')

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/stats')
def stats():
    results = {}
    db = get_db()
    sql = '''
        SELECT COUNT(*) FROM doc
    '''
    cur = db.execute(sql)
    results['num_docs'] = cur.fetchone()[0]
    sql = '''
        SELECT tag, COUNT(*)
        FROM doc_label JOIN label USING (label_id)
        GROUP BY 1
    '''
    cur = db.execute(sql)
    for tag, num in db.execute(sql):
        results['num_' + tag] = num
    sql = '''
        SELECT value FROM meta WHERE key='last_updated'
    '''
    cur = db.execute(sql)
    results['last_updated'] = cur.fetchone()[0]
    return jsonify(results=results)

@app.route('/most_relevant')
def most_relevant():
    db = get_db()
    offset = request.args.get('offset', 0, type=int)
    num = request.args.get('num', 10, type=int)
    sql = '''
        SELECT a.doc_id, a.relevance, a.explain_json,
            b.title, b.body, b.url, b.published_date
        FROM doc_relevance a JOIN doc b USING (doc_id)
        ORDER BY a.relevance DESC LIMIT ? OFFSET ?
    '''
    cur = db.execute(sql, [num, offset])
    res = cur.fetchall()
    res = map(dict, res)
    for r in res:
        r['explain'] = json.loads(r.pop('explain_json'))
    return jsonify(results=res)

@app.route('/tagged/<tag>')
def tagged(tag):
    db = get_db()
    offset = request.args.get('offset', 0, type=int)
    num = request.args.get('num', 10, type=int)
    sql = '''
        SELECT doc_id, title, body, url, published_date
        FROM doc_label
        JOIN doc USING (doc_id) 
        JOIN label USING (label_id)
        WHERE tag = ?
        ORDER BY published_date DESC LIMIT ? OFFSET ?
    '''
    cur = db.execute(sql, [tag, num, offset])
    res = cur.fetchall()
    return jsonify(results=map(dict, res))

@app.route('/random')
def random():
    db = get_db()
    offset = request.args.get('offset', 0, type=int)
    num = request.args.get('num', 10, type=int)
    sql = '''
        SELECT a.doc_id, a.title, a.body, a.url, a.published_date
        FROM doc a
        LEFT JOIN doc_label b USING (doc_id)
        WHERE b.doc_id IS NULL
        ORDER BY RANDOM() LIMIT ? OFFSET ?
    '''
    cur = db.execute(sql, [num, offset])
    res = cur.fetchall()
    return jsonify(results=map(dict, res))

@app.route('/doc/<int:doc_id>', methods=['GET', 'POST'])
def doc(doc_id):
    db = get_db()
    if request.method=='POST':
        label = request.form['label']
        cur = db.execute('SELECT label_id FROM label WHERE tag = ?',
                         [label])
        label_id, = cur.fetchone()
        db.execute('INSERT INTO doc_label (doc_id, label_id) VALUES (?,?)',
                   [doc_id, label_id])
        db.execute('DELETE FROM doc_relevance WHERE doc_id = ?',
                   [doc_id])
        db.commit()
        return jsonify()
    else:
        cur = db.execute('SELECT * FROM doc WHERE doc_id = ?',
                         [doc_id])
        doc = cur.fetchone()
        if doc is None:
            return jsonify(error='Doc not found: %d' % doc_id), 404
        return jsonify(**dict(doc))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

def get_db():
    if not hasattr(g, 'db_conn'):
        g.db_conn = sqlite3.connect(app.config['DATABASE'])
        g.db_conn.row_factory = sqlite3.Row
    return g.db_conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_conn'):
        g.db_conn.close()

if __name__=='__main__':
    app.run()
