from flask import Flask, render_template, request, redirect, session
import pyodbc
import re

machineinfo = Flask(__name__)
machineinfo.secret_key = 'secret' 

#MSSQL connection
#def connection():
#    conn = pyodbc.connect(
#        Trusted_Connection='Yes',
#        Driver='{ODBC Driver 17 for SQL Server}',
#        Server='VICKIBOOK\SQLEXPRESS',
#        Database='Machines'
#    )
#    return conn

#Azure connection
server = 'testingproject.database.windows.net'
database = 'Machines'
username = 'admin0'
password = 'Password0'   
driver= '{ODBC Driver 17 for SQL Server}'
def connection():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn

#Login 
@machineinfo.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dbo.Accounts WHERE username = ? AND password = ?', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account[1]
            msg = 'Successfully logged in.'
            machines = []
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dbo.ProjMachines")
            for row in cursor.fetchall():
                machines.append({"lid": row[0], "name": row[1], "pid": row[2], "time": row[3]})
            conn.close()
            return render_template("machineslist2.html", machines = machines, msg = msg)
        else:
            msg = 'Invalid username and/or password.'
    return render_template('login.html', msg = msg)

#Logout  
@machineinfo.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/')
 
#Register
@machineinfo.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dbo.Accounts WHERE username = ?', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists.'
        elif not username or not password or not email:
            msg = 'Missing registeration details.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address format.'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only alphabets and numbers.'
        else:
            cursor.execute('INSERT INTO dbo.Accounts VALUES (?, ?, ?)', (username, password, email,))
            conn.commit()
            msg = 'Successfully registered.'
    elif request.method == 'POST':
        msg = 'Please fill out the form.'
    return render_template('register.html', msg = msg)

#Home 
@machineinfo.route("/")
def main():
    machines = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.ProjMachines")
    for row in cursor.fetchall():
        machines.append({"lid": row[0], "name": row[1], "pid": row[2], "time": row[3]})
    conn.close()
    return render_template("machineslist.html", machines = machines)

#Home after add machine 
@machineinfo.route("/updated")
def updatelist():
    machines = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.ProjMachines")
    for row in cursor.fetchall():
        machines.append({"lid": row[0], "name": row[1], "pid": row[2], "time": row[3]})
    conn.close()
    return render_template("machineslist2.html", machines = machines)

#Search bar function 
def getmachines(search):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM dbo.ProjMachines WHERE Machine_Name LIKE ?",
        ("%"+search+"%",)
    )
    results = cursor.fetchall()
    conn.close()
    return results

#Search machine
@machineinfo.route("/searchmachine", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = dict(request.form)
        machines = getmachines(data["search"])
    else:
        machines = []
    return render_template("searchmachine.html", machineries=machines)

#Add machine
@machineinfo.route("/addmachine", methods = ['GET','POST'])
def addmachine():
    if request.method == 'GET':
        return render_template("addmachine.html", machine = {})
    if request.method == 'POST':
        lid = int(request.form["lid"])
        name = request.form["name"]
        pid = int(request.form["pid"])
        time = float(request.form["time"])
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dbo.ProjMachines (Line_ID, Machine_Name, Product_ID, Process_time) VALUES (?, ?, ?, ?)", lid, name, pid, time)
        conn.commit()
        conn.close()
        return redirect('/updated')

#Update machine
@machineinfo.route('/updatemachine/<int:pid>',methods = ['GET','POST'])
def updatemachine(pid):
    cr = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.ProjMachines WHERE Product_ID = ?", pid)
        for row in cursor.fetchall():
            cr.append({"lid": row[0], "name": row[1], "pid": row[2], "time": row[3]})
        conn.close()
        return render_template("updatemachine.html", machine = cr[0])
    if request.method == 'POST':
        lid = int(request.form["lid"])
        name = request.form["name"]
        time = float(request.form["time"])
        cursor.execute("UPDATE dbo.ProjMachines SET Line_ID = ?, Machine_Name = ?, Process_time = ? WHERE Product_ID = ?", lid, name, time, pid)
        conn.commit()
        conn.close()
        return redirect('/updated')

#Delete machine
@machineinfo.route('/deletemachine/<int:pid>')
def deletemachine(pid):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.ProjMachines WHERE Product_ID = ?", pid)
    conn.commit()
    conn.close()
    return redirect('/updated')

#Main function
if(__name__ == "__main__"):
    machineinfo.run()