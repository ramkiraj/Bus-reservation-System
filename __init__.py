from flask import Flask, render_template, request, redirect, url_for,session
import sqlite3 as sql
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('userlogin.html')


# admin site
@app.route('/admin')
def admin():
    if(session.get("username")=="admin"):
        return render_template('admin.html')
    else:
        return redirect(url_for('login'))


# Creating new database
@app.route('/bus.html')
def new_student():
    if(session.get("username")=="admin"):
        conn = sql.connect('database.db')
        print("Opened database successfully")
        conn.execute(
            'CREATE TABLE IF NOT EXISTS buses (id INTEGER PRIMARY KEY,name TEXT, source TEXT, destination TEXT, time TEXT, price INT,nos INT,rem INT)')
        print("Table created successfully")
        conn.close()
        return render_template('bus.html')
    else:
        return redirect(url_for('login'))


# Adding new bus record
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:

            nm = request.form['nm']
            sourc = request.form['src']
            desti = request.form['dest']
            tim = request.form['t']
            pric = request.form['p']
            nos = request.form['nos']
            rem = nos

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("INSERT INTO buses (name,source,destination,time,price,nos,rem) VALUES (?,?,?,?,?,?,?)",
                            (nm, sourc, desti, tim, pric, nos, rem))

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


# renders template to delete a bus record
@app.route('/delete.html')
def deleterecord():
    if(session.get("username")=="admin"):
        return render_template('delete.html')
    else:
        return redirect(url_for('login'))


# delete the record
@app.route('/delrec', methods=['POST', 'GET'])
def delrec():
    if request.method == 'POST':
        try:

            id = request.form['id']

            with sql.connect("database.db") as con:
                cur = con.cursor()

                cur.execute("DELETE FROM buses WHERE id=(?)", (id,))

                con.commit()
                msg = "result of delete operation: Record successfully deleted"
        except:
            con.rollback()
            msg = "Result of delete operation: error in delete operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/find.html')
def findrecord():
    if session.get("username")=="admin":
        return render_template('find.html')
    else:
        return redirect(url_for('login'))


# find the record
@app.route('/findbus', methods=['POST', 'GET'])
def findbus():
    source = request.form['source']
    destination = request.form['destination']
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM buses WHERE source=(?) AND destination=(?) AND rem!=0", (source, destination))

    rows = cur.fetchall();
    if (rows):
        msg = "LIST OF BUSES FOR GIVEN SOURCE AND DESTINATION"
        return render_template("list.html", rows=rows, msg=msg)
    else:
        msg = "NO BUSES AVAILABLE"
        return render_template("result.html", msg=msg)


# list all records
@app.route('/list.html')
def list():
    if("username" in session):
        username = session['username']
        con = sql.connect("database.db")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select * from buses")

        rows = cur.fetchall();
        msg = "LIST OF ALL BUSES"
        return render_template("list.html", rows=rows, msg=msg, user=username)
    else:
        return redirect(url_for('login'))


# list all buses booked by user
@app.route('/userbookinglist.html')
def userbookinglist():
    if("username" in session):
        username = session['username']
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        flag = 1  # to prevent find form  displaying
        cur = con.cursor()
        cur.execute("select * from user where name=(?)", (username,))
        row = cur.fetchone();
        userid = row[0]
        cur.execute("select * from book where userid=(?)", (userid,))
        rows = cur.fetchall();
        msg = "LIST OF ALL BUSES"
        return render_template("list.html", rows=rows, msg=msg, user=username, fl=flag)
    else:
        return redirect(url_for('login'))


@app.route('/bookinglist.html')
def bookinglist():
    if(session.get("username")=="admin"):
        username = session['username']
        con = sql.connect("database.db")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select * from book")

        rows = cur.fetchall();
        msg = "LIST OF ALL BUSES"
        return render_template("list.html", rows=rows, msg=msg, user=username)
    else:
        return redirect(url_for('login'))





# Creating user database
@app.route('/user.html')
def new_user():
    conn = sql.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS user (ids INTEGER PRIMARY KEY,name TEXT, pass TEXT)')
    print("Table created successfully")
    conn.close()
    return render_template('user.html')


# adding user
@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        try:
            name = request.form['name']
            password = request.form['pass']
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            print(pw_hash)
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user (name,pass) VALUES (?,?)", (name, pw_hash))
                con.commit()
                msg = "User record:Record successfully added"
        except:
            con.rollback()
            msg = "User record: error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


# Delete a user
@app.route('/deleteuser.html')
def deleteuserrecord():
    return render_template('delete.html')


@app.route('/deluserrec', methods=['POST', 'GET'])
def deluserrec():
    if request.method == 'POST':
        try:
            id = request.form['id']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("DELETE FROM user WHERE ids=(?)", (id))
                con.commit()
                msg = "result of delete operation: Record successfully deleted"
        except:
            con.rollback()
            msg = "Result of delete operation: error in delete operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/user')  # user and admin login
def user():
    flag = 0
    if 'username' in session :
        username = session.get('username')
        pw = session.get("password")
        if username == 'admin' and pw == 'admin':
            flag = 1
        else:
            con = sql.connect("database.db")
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE name=(?) ", (username,))

            rows = cur.fetchone()
            if (rows):
                if bcrypt.check_password_hash(rows[2],pw)==False:
                    flag =3
                else: flag = 2
        if flag == 1:
            return render_template('admin.html')
        elif flag == 2:
            return render_template('userhome.html', user=username)
        elif flag == 3:
            return "Incorrect password <br><a href = '/login'></b>" + \
                   "click here to log in</b></a>"
        else:
            return "You are not logged in as username or password is incorrect <br><a href = '/login'></b>" + \
                   "click here to log in</b></a>"

    return render_template('userprehome.html')  # initial page for login/sign up


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']

        return redirect(url_for('user'))
    return render_template('userlogin.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('user'))


@app.route('/book.html')
def book():
    if("username" in session):
        conn = sql.connect('database.db')
        print("Opened database successfully")
        conn.execute(
            'CREATE TABLE IF NOT EXISTS book (bookid INTEGER PRIMARY KEY,busid TEXT,busname TEXT,userid TEXT,username TEXT,nopass TEXT)')
        print("Table created successfully")
        conn.close()
        return render_template('find.html')
    else:
        return redirect(url_for('login'))


@app.route('/booking', methods=['POST', 'GET'])
def booking():
    if request.method == 'POST':
        try:
            idbus = request.form['id']
            nop = request.form['nop']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM buses WHERE id=(?)", (idbus,))
                bus = cur.fetchone()
                busn = bus[1]
                num_seats = bus[7]
                username = session['username']
                cur.execute("SELECT * FROM user WHERE name=(?)", (username,))
                rows = cur.fetchone();
                user = rows[0]
                un = rows[1]
                cur.execute("INSERT INTO book (busid,busname,userid,username,nopass) VALUES (?,?,?,?,?)",
                            (idbus, busn, user, un, nop))
                new_rem = int(num_seats) - int(nop)
                cur.execute("UPDATE buses SET rem=(?) WHERE id=(?)", (new_rem, idbus))
                con.commit()
                msg = "Booking success"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/cancel.html')
def cancel():
    if("username" in session):
        conn = sql.connect('database.db')
        print("Opened database successfully")
        conn.execute(
            'CREATE TABLE IF NOT EXISTS cancel (canid INTEGER PRIMARY KEY,bookid TEXT,busid TEXT,busname TEXT,userid TEXT,username TEXT,nopass TEXT)')
        print("Table created successfully")
        conn.close()
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        username = session['username']
        cur.execute("SELECT * FROM user WHERE name=(?)", (username,))
        rows = cur.fetchone();
        user = rows[0]

        cur.execute("SELECT * FROM book WHERE userid=(?)", (user,))

        rows = cur.fetchall();
        if (rows):
            msg = "LIST OF BUSES FOR BOOKED BY YOU"
            return render_template("cancel.html", rows=rows, msg=msg)
        else:
            msg = "NO BUSES BOOKED"
            return render_template("result.html", msg=msg, user=username)
        con.close()
    else:
        return redirect(url_for('login'))


@app.route('/canceling', methods=['POST', 'GET'])
def canceling():
    if("username" in session):
        if request.method == 'POST':
            try:
                canid = request.form['id']
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT * FROM book WHERE bookid=(?)", (canid,))
                    can = cur.fetchone()
                    nop = can[5]
                    cur.execute("INSERT INTO cancel (bookid,busid,busname,userid,username,nopass) VALUES (?,?,?,?,?,?)",
                                (can[0], can[1], can[2], can[3], can[4], can[5]))
                    cur.execute("SELECT * FROM buses WHERE id=(?)", (can[1]))
                    bus = cur.fetchone()
                    rem = bus[7]
                    new_rem = int(rem) + int(nop)
                    cur.execute("UPDATE buses SET rem=(?) WHERE id=(?)", (new_rem, can[1]))
                    cur.execute("DELETE FROM book WHERE bookid=(?)", (canid,))
                    con.commit()
                    msg = "canceling success"
            except:
                con.rollback()
                msg = "error in insert operation"

            finally:
                return render_template("result.html", msg=msg)
                con.close()
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
