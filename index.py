from flask import Flask, g, render_template, flash, request, session, redirect, url_for, abort
import sqlite3
import os

from flask import Flask


app = Flask(__name__)
app.config.from_object(__name__)
db_location = 'var/index.db'
app.secret_key = os.urandom(24)

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = sqlite3.connect(db_location)
        g.db = db
    return db


@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = get_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/comments')
def comments():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('comments.html', entries=entries)

@app.route('/comments/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into entries (title, text) values (?, ?)',[request.form['title'], request.form['text']])
    g.db.commit()
    flash('Submit successfully !')
    return redirect(url_for('comments'))



@app.route("/")
def index():
    return render_template('index.html'), 200

@app.route("/products")
def inheritance_one():
    return render_template('products.html')


@app.route('/login/',methods=["GET","POST"])
def login():
    error=None
    if request.method == "POST":
        attempted_username = request.form['username']
        attempted_password = request.form['password']
      
        if attempted_username == "Danni" and attempted_password == "123":
            return redirect(url_for('index'))
        else:
            flash(message='Try Again.',category='error')
    return render_template('login.html',error=error)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
  init_db
  app.run(host='0.0.0.0')

