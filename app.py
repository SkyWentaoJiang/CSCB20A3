import sqlite3
from flask import Flask, render_template, redirect, url_for, request, g

DATABASE='./assignment3.db'

# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv



app=Flask(__name__)

# this function gets called when the Flask app shuts down
# tears down the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()

@app.route('/')
@app.route('/login')
def root():
    # get the database
    db = get_db()
    # apply make_dicts (to change the result from a tuple to a dictioanry -- easier to work with)
    db.row_factory = make_dicts

    Users=[]
    # query for all employees
    for username in query_db('select * from Users'):
        Users.append(username)
    # close the database after using it (this is important)
    db.close()
    return render_template('index.html', user=Users)


# add a new employee
@app.route('/sign-up', methods=['POST'])
def sign_up():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    new_user = request.form

    cur.execute('insert into Users (type, username, password) values (?, ?, ?)', [
        new_user['dropdown'],
        new_user['username'],
        new_user['password']])
    db.commit()
    cur.close()

    return redirect(url_for('root'))


# run the app when app.py is run
if __name__ == '__main__':
    app.run(debug=True)