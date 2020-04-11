import sqlite3
from typing import Optional, Any, List, Union

from flask import Flask, render_template, redirect, url_for, request, g, session, flash

# import os

DATABASE = './assignment3.db'

logged_in = False
instructor = False
student = False
username = ""


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


app = Flask(__name__)


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
    # db = get_db()
    # # apply make_dicts (to change the result from a tuple to a dictioanry -- easier to work with)
    # db.row_factory = make_dicts
    #
    # users=[]
    # # query for all employees
    # for username in query_db('select * from Users'):
    #     users.append(username)
    # # close the database after using it (this is important)
    # db.close()
    global logged_in, student, instructor
    if not logged_in:
        return render_template('index.html')
    else:
        # return redirect(url_for("home"))
        if student:
            return redirect(url_for('student_mark'))
        if instructor:
            return redirect(url_for('instructor_marks'))


@app.route('/logout')
def logout():
    global logged_in, student, instructor
    logged_in = False
    student = False
    instructor = False
    return redirect(url_for('root'))


@app.route('/signup', methods=['POST'])
def sign_up():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    new_user = request.form

    cur.execute('insert into Users (type, username, password) values (?, ?, ?)', [
        new_user['dropdown'],
        new_user['username'],
        new_user['password']])
    cur.execute('insert into Marks (student, A1, Midterm, Final) values (?, "0", "0", "0")', [new_user["username"]])
    db.commit()
    cur.close()
    return redirect(url_for("result", message="You are successfully signed up!", type="signUpSuccess"))


# get an employee by name
@app.route('/signin')
def sign_in():
    global logged_in
    global username
    global student
    global instructor
    db = get_db()
    db.row_factory = make_dicts
    user_type = request.args.get('dropdown')
    user_name = request.args.get('username')
    password_input = request.args.get('password')
    user = query_db('select * from Users where type=? and username=?', [user_type, user_name], one=True)

    db.close()

    if user and user["password"] == password_input:
        logged_in = True
        username = user_name
        if user_type == "instructor":
            instructor = True
        else:
            student = True
    else:
        message = "Access denied, you may sign in again."
        return redirect(url_for("result", message=message, type="loginError"))
    return redirect(url_for("root"))


@app.route('/student_mark', methods=['GET', 'POST'])
def student_mark():
    global username
    db = get_db()
    db.row_factory = make_dicts

    marks = query_db('select * from Marks where student = ?', [username])
    return render_template("student_mark.html", user_name=username, marks=marks)


@app.route('/remark1', methods=['GET', 'POST'])
def remark1():
    global username

    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    try:
        new_request1 = request.form["remark1"]
    finally:
        if new_request1 is not None:
            cur.execute('insert into RemarkRequest (student, type, reason) values (?, ?, ?)',
                        [username, "A1", new_request1])
    db.commit()
    cur.close()
    return redirect(url_for("result", message="Successfully submitted", type="remarkSuccess"))


@app.route('/remark2', methods=['GET', 'POST'])
def remark2():
    global username

    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    try:
        new_request2 = request.form["remark2"]
    finally:
        if new_request2 is not None:
            cur.execute('insert into RemarkRequest (student, type, reason) values (?, ?, ?)',
                        [username, "Midterm", new_request2])
    db.commit()
    cur.close()
    return redirect(url_for("result", message="Successfully submitted", type="remarkSuccess"))


@app.route('/remark3', methods=['GET', 'POST'])
def remark3():
    global username

    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    try:
        new_request3 = request.form["remark3"]
    finally:
        if new_request3 is not None:
            cur.execute('insert into RemarkRequest (student, type, reason) values (?, ?, ?)',
                        [username, "Final", new_request3])
    db.commit()
    cur.close()
    return redirect(url_for("result", message="Successfully submitted", type="remarkSuccess"))


@app.route('/instructor_marks', methods=['GET', 'POST'])
def instructor_marks():
    global username
    # get the database
    db = get_db()
    # apply make_dicts (to change the result from a tuple to a dictioanry -- easier to work with)
    db.row_factory = make_dicts

    marks = []
    for one in query_db('select * from Marks'):
        marks.append(one)
    db.close()
    return render_template('instructor_marks.html', username=username, instructor_marks=marks, length=len(marks))


@app.route('/enter_mark', methods=['GET', 'POST'])
def enter_mark():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    sql_update = "update Marks set "

    student_marks = request.form
    name = student_marks['student']
    a1 = student_marks['A1']
    midterm = student_marks['Midterm']
    final = student_marks['Final']
    if a1 != "":
        # "A1=?,"
        sql_update += "A1=" + a1 + ","
    if midterm != "":
        # "Midterm=?,"
        sql_update += "Midterm=" + midterm + ","
    if final != "":
        # "Final=?"
        sql_update += "Final=" + final
    else:
        # if no final mark, remove the last comma
        sql_update = sql_update[:-1]
    sql_update += " where student=" + '"' + name + '"'

    if name == "" and a1 == "" and midterm == "" and final == "":
        return redirect(url_for("instructor_marks"))

    try:
        cur.execute('insert into Marks (student, A1, Midterm, Final) values (?, ?, ?, ?)', [name, a1, midterm, final])
    except:
        cur.execute(sql_update)

    finally:
        db.commit()
        cur.close()

    return redirect(url_for("instructor_marks"))


@app.route('/instructor_remark')
def instructor_remark():
    global username
    db = get_db()
    db.row_factory = make_dicts

    remarks = query_db("select * from RemarkRequest")

    db.close()

    return render_template("instructor_remark.html", username=username, remarks=remarks)


@app.route('/solve_remark')
def solve_remark():
    return redirect(url_for('instructor_marks'))


@app.route('/feedback')
def feedback():
    db = get_db()
    db.row_factory = make_dicts
    instructor_list = query_db("select * from Users where type='instructor'")
    return render_template("feedback.html", instructors=instructor_list)


@app.route('/result/?<message>_<type>')
def result(message, type):
    global instructor, student, username
    if instructor:
        type = "instructor"
    if student:
        type = "student"
    return render_template("result.html", message=message, type=type, name=username)


@app.route('/jumpto')
def jumpto():
    global instructor, student, username
    if instructor:
        return redirect(url_for("instructor_marks"))
    elif student:
        return redirect(url_for("student_mark"))


@app.route('/send_feedback', methods=['GET', 'POST'])
def send_feedback():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()

    feedbacks = request.form
    name = feedbacks["dropdown"]
    feedback1 = feedbacks["feedback1"]
    feedback2 = feedbacks["feedback2"]
    feedback3 = feedbacks["feedback3"]
    feedback4 = feedbacks["feedback4"]

    cur.execute("insert into Feedback (instructor) values (?)",
                [name])

    if feedback1 != "":
        cur.execute("update Feedback set like = ? where instructor = ?", [feedback1, name])
    if feedback2 != "":
        cur.execute("update Feedback set recommend = ? where instructor = ?", [feedback2, name])
    if feedback3 != "":
        cur.execute("update Feedback set likeLab = ? where instructor = ?", [feedback3, name])
    if feedback4 != "":
        cur.execute("update Feedback set recommendLab = ? where instructor = ?", [feedback4, name])
    db.commit()
    cur.close()
    return redirect(url_for('result'))


@app.route("/instructor_feedback")
def instructor_feedback():
    global username
    db = get_db()
    db.row_factory = make_dicts
    feedbacks = query_db("select * from Feedback where instructor=?", [username])
    db.close()

    return render_template("instructor_feedback.html", feedbacks=feedbacks)


@app.route('/home')
def homepage():
    return render_template("home.html")


@app.route('/calendar')
def calendar():
    return render_template("calendar.html")


@app.route('/news')
def news():
    return render_template("news.html")


@app.route('/lectures')
def lectures():
    return render_template("lectures.html")


@app.route('/labs')
def labs():
    return render_template("labs.html")


@app.route('/assignments')
def assignments():
    return render_template("assignments.html")


@app.route('/tests')
def tests():
    return render_template("tests.html")


@app.route('/resources')
def resources():
    return render_template("resources.html")


# run the app when app.py is run
if __name__ == '__main__':
    app.run(debug=True)
