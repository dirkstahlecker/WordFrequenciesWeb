import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Response
from .model.WordFrequenciesClass import WordFrequencies
# from flaskext.xmlrpc import XMLRPCHandler, Fault
from jsonrpcserver import methods

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file, flaskr.py

####################################
# RPC
# handler = XMLRPCHandler('api')
# handler.connect(app, '/api')

# @handler.register
# def hello(name="world"):
#     if not name:
#         raise Fault("unknown_recipient", "I need someone to greet!")
#     return "Hello, %s!" % name

####################################

wf = WordFrequencies()

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#Connects to the specific database.
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

#Opens a new database connection if there is none yet for the current application context.
def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#Closes the database again at the end of the request.
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

#Initializes the database.
@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

@app.route('/', methods=['POST'])
def show_entries():
    db = get_db()
    cur = db.execute('select date, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()

    markedUpText = wf.addMarkupToText(request.form['text'])

    db.execute('insert into entries (date, text) values (?, ?)', [request.form['date'], markedUpText])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))




@methods.add
def ping():
    return 'pong'

@app.route('/rpc', methods=['POST'])
def rpc_main():
    print('in rpc_main')
    req = request.get_data().decode()
    response = methods.dispatch(req)
    print(response)
    return Response(str(response), response.http_status, mimetype='application/json')


