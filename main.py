import flask
import json
import os
import mysql.connector
from flask import Flask, render_template, request, redirect,session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flask_mail import Mail
from datetime import datetime

local_server=True
app = Flask(__name__)
app.secret_key=os.urandom(24)



conn = mysql.connector.connect(host="localhost", user="root", password="", database="arvs_mock")
cursor=conn.cursor()
with open('config.json','r') as c:
    params=json.load(c)["params"]
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_pass']
)

mail = Mail(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/arvs_mock"
db = SQLAlchemy(app)

class Employee(db.Model):
    emp_id= db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    designation = db.Column(db.String(50), unique=False, nullable=True)
    department = db.Column(db.String(50), unique=False, nullable=True)
    contact = db.Column(db.String(12), unique=True, nullable=True)
    em_contact = db.Column(db.String(12), unique=False, nullable=True)

class Leave_count(db.Model):
    emp_id= db.Column(db.Integer, primary_key=True)
    annual = db.Column(db.String(20), unique=False, nullable=False)
    sick = db.Column(db.String(20), unique=False, nullable=False)
    bereavement = db.Column(db.String(20), unique=False, nullable=False)
    babycare = db.Column(db.String(20), unique=False, nullable=False)

class Leave_info(db.Model):
    leave_id= db.Column(db.Integer, primary_key=True)
    TOL = db.Column(db.String(20), unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=False)
    start_date = db.Column(db.String(20), unique=False, nullable=False)
    end_date = db.Column(db.String(20), unique=False, nullable=False)
    days = db.Column(db.String(20), unique=False, nullable=False)
    emp_id = db.Column(db.String(20), unique=False, nullable=False)
    status = db.Column(db.String(20), unique=False, nullable=True)
    pay = db.Column(db.String(20), unique=False, nullable=True)

class Authority(db.Model):
    a_id= db.Column(db.Integer, primary_key=True)
    a_name = db.Column(db.String(30), unique=False, nullable=False)
    a_email = db.Column(db.String(50), unique=True, nullable=False)
    a_password = db.Column(db.String(20), unique=False, nullable=False)
    a_designation = db.Column(db.String(50), unique=False, nullable=True)
    a_department = db.Column(db.String(50), unique=False, nullable=True)

class Events(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=False, nullable=False)
    justtitle = db.Column(db.String(30), unique=False, nullable=False)
    start_event = db.Column(db.String(50), unique=False, nullable=False)
    end_event = db.Column(db.String(20), unique=False, nullable=False)



@app.route('/')
@app.route('/signup' , methods=['POST','GET'])
def signup():
    
    
    if (request.method == 'POST'):
        pemp_id = request.form.get('femp_id')
        pname = request.form.get('fname')
        pemail = request.form.get('femail')
        ppassword = request.form.get('fpassword')
        entry = Employee( emp_id=pemp_id, email=pemail, name=pname, password =ppassword)
        db.session.add(entry)
        db.session.commit()
        cursor.execute("""INSERT INTO `leave_count` (`emp_id`,`annual`,`sick`,`babycare`,`bereavement`)
                  VALUES ('%s','%s', '%s', '%s', '%s')""" % (pemp_id,0,0,0,0))
        conn.commit()
        flash("Sign up successful!")
        return redirect("/signup")
    return render_template("signup.html")



@app.route('/login' , methods=['POST','GET'])
def login():
    
    if (request.method == 'POST'):
        puser_email = request.form.get('fuser_email')
        puser_password = request.form.get('fuser_password')
        print("email:",puser_email)
        print("password:",puser_password)
        cursor.execute("""SELECT * FROM `employee` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(puser_email, puser_password))
        users=cursor.fetchall()
        print(users)
        if len(users)>0:    
            session['emp_id']=users[0][0]
            return redirect('/profile') 
        else:
            #for unsuccessful login attempt
            flash("Incorrect credentials! Try Again.")
            print("login5")
            return redirect('/login')

    if ('emp_id' in session):
        print("heloo not work")
        return redirect('/profile') 
    
    emp=Employee.query.filter_by().first() #1s
    return render_template("login.html", emp=emp) #2s


@app.route('/authloginn' , methods=['POST','GET'])
def authloginn():
    if (request.method == 'POST'):
        puser_email = request.form.get('ath_email')
        puser_password = request.form.get('ath_password')
        cursor.execute("""SELECT * FROM `authority` WHERE `a_email` LIKE '{}' AND `a_password` LIKE '{}'""".format(puser_email, puser_password))
        autho=cursor.fetchall()
        if len(autho)> 0:
            session['a_id'] = autho[0][0]
            return redirect('/authDashboard')
        else:
            return redirect('/authloginn')
        
    if ('a_id' in session):
        return redirect('/authDashboard')
        
    auth =Authority.query.filter_by().first()
    leaves = Leave_info.query.all()
    return render_template("authloginn.html", auth=auth, leaves=leaves)

@app.route('/authDashboard')
def authDashboard():
    if 'a_id' in session:
        a_id = session.get('a_id', None)
        cursor.execute("""SELECT * FROM `authority` WHERE `a_id` LIKE '{}' """.format(a_id))
        autho=cursor.fetchall()
        auname = autho[0][1]
        # print(autho)
        leaves = Leave_info.query.all()
        today = date.today()
        print("leaves: ", leaves)
        cursor.execute("""SELECT * FROM `leave_info` WHERE `status` LIKE '{}' """.format("Approved"))
        approvedx=cursor.fetchall()
        cursor.execute("SELECT * FROM `employee`")
        empx=cursor.fetchall() 
        cursor.execute("""SELECT * FROM `leave_info` WHERE `status` LIKE '{}' """.format("pending"))
        pendingx=cursor.fetchall()
        approved = len(approvedx)
        pending = len(pendingx)
        empcount = len(empx)
        emp = Employee.query.all()
        count = Leave_count.query.all()
        auth = Authority.query.filter_by(a_id=a_id).first()
        return render_template('authDashboard.html', auth=auth, count=count, a_id=a_id, auname=auname,  leaves=leaves, emp=emp, approved=approved, pending=pending, today=today, empcount=empcount)
    else:
        return redirect('/authloginn')

# @app.route('/documents/<string:a_id>')
# def documents():
#     if 'a_id' in session:
#         a_id = session.get('a_id', None)
#         cursor.execute("""SELECT * FROM `authority` WHERE `a_id` LIKE '{}' """.format(a_id))
#         autho=cursor.fetchall()
#         auname = autho[0][1]
#         # print(autho)
#         leaves = Leave_info.query.all()
#         today = date.today()
#         print("today: ", today)
#         cursor.execute("""SELECT * FROM `leave_info` WHERE `status` LIKE '{}' """.format("Approved"))
#         approvedx=cursor.fetchall()
#         cursor.execute("SELECT * FROM `employee`")
#         empx=cursor.fetchall() 
#         cursor.execute("""SELECT * FROM `leave_info` WHERE `status` LIKE '{}' """.format("pending"))
#         pendingx=cursor.fetchall()
#         approved = len(approvedx)
#         pending = len(pendingx)
#         empcount = len(empx)
#         emp = Employee.query.all()
#         auth = Authority.query.filter_by(a_id=a_id).first()
#         return render_template('documents.html')
#         return render_template('documents.html',auth=auth, a_id=a_id, auname=auname,  leaves=leaves, emp=emp, approved=approved, pending=pending, today=today, empcount=empcount)
#     else:
#         return redirect('/authloginn')
    

@app.route('/approve/<string:leave_id>', methods=['GET','POST'])
def approve(leave_id):
    status_approve = "Approved"
    post = Leave_info.query.filter_by(leave_id=leave_id).first()
    emplo = post.emp_id
    count = Leave_count.query.filter_by(emp_id = emplo).first()  
    employee= Employee.query.filter_by(emp_id = emplo).first()
    auth = Authority.query.filter_by().first()
    if(count == None):
        cursor.execute("""INSERT INTO `leave_count` (`emp_id`,`annual`,`sick`,`babycare`,`bereavement`)
                  VALUES ('%s','%s', '%s', '%s', '%s')""" % (emplo,0,0,0,0))
        conn.commit()

    post.status = status_approve

    leave_counter(post, count, employee, auth)

    # print(post.leave_id)
    db.session.commit()
    return redirect('/authDashboard')

@app.route('/reject/<string:leave_id>', methods=['GET','POST'])
def reject(leave_id):
    status_reject = "Rejected"
    post = Leave_info.query.filter_by(leave_id=leave_id).first()
    post.status = status_reject
    emplo= post.emp_id
    count = Leave_count.query.filter_by(emp_id = emplo).first()  
    employee= Employee.query.filter_by(emp_id = emplo).first()
    auth = Authority.query.filter_by().first()
    # print(leave_id)
    db.session.commit()
    print(employee.email)
    mail.send_message('From '+auth.a_name+' to '+ employee.name, sender=params['gmail_user'], 
                            recipients=[employee.email] ,
                            body ='Dear '+employee.name+' your request for leave of '+str(post.days) + ' days has been rejected.')
                            
    return redirect('/authDashboard')


@app.route('/profile')#3
def profile():
    
    if 'emp_id' in session:
        emp_id = session.get('emp_id', None)
        print(emp_id)
        cursor.execute("""SELECT * FROM `employee` WHERE `emp_id` LIKE '{}' """.format(emp_id))
        users=cursor.fetchall()
        hname=users[0][2]
        emp= Employee.query.filter_by(emp_id=emp_id).first() 
        count = Leave_count.query.filter_by(emp_id = emp_id).first()
        hname= emp.name
        return render_template('profile.html', emp_id=emp_id, hname=hname, emp=emp, count=count) #5
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('emp_id')
    # print('logout done')
    return redirect('/login')

@app.route('/alogout')
def alogout():
    session.pop('a_id')
    # print('logout done')
    return redirect('/authloginn')

@app.route('/leave_application/<string:emp_id>')
def leave_application(emp_id):
    if ('emp_id' in session):
        emp_id = session.get('emp_id', None)
        cursor.execute("""SELECT * FROM `employee` WHERE `emp_id` LIKE '{}' """.format(emp_id))
        users=cursor.fetchall()
        count = Leave_count.query.filter_by(emp_id=emp_id).first()
        emp = Employee.query.filter_by(emp_id=emp_id).first()
        hname=emp.name
        return render_template("leave_application.html", count=count , emp_id=emp_id,hname=hname, emp=emp )
    else:
        return redirect('/login')
    emp = Employee.query.filter_by(emp_id=emp_id).first()
    return render_template("leave_application.html" ,emp_id=emp_id,hname=hname, emp=emp)

@app.route('/history/<string:emp_id>')
def history(emp_id):
    if ('emp_id' in session):
        emp_id = session.get('emp_id', None)
        emp = Employee.query.filter_by(emp_id=emp_id).first()
        count = Leave_count.query.filter_by(emp_id=emp_id).first()
        lv_history = Leave_info.query.filter_by(emp_id=emp_id).all()
        hname=emp.name
        return render_template("history.html", emp_id=emp_id, emp=emp, hname=hname, lv_history=lv_history)
    else:
        return redirect('/login')


@app.route('/leaveSubmit', methods=['POST', 'GET'])
def submit_leave_form():
    if 'emp_id' in session:
        emp_id = session.get('emp_id', None)
        leave_status = "pending"

        if request.method == "POST":
            # print("in")
            # geting form data
            # emp_id = request.form.get('emp_id')
            # print(emp_id)
            tol= request.form.get('accountType')
            description = request.form.get('description')
            from_date = request.form.get('from date')
            to_date = request.form.get('till date')
            days = request.form.get('days')
            status = leave_status
            # print(tol, description, from_date, to_date, days, status, emp_id)
            # adding to de
            # cursor.execute("""INSERT INTO `leave_info` (`TOL`,`description`,`start_date`,`end_date`,`days`,`status`,`emp_id`)
            #       VALUES ('%s','%s', '%s', '%s', '%s','%s','%s')""" % (tol, description, from_date, to_date, days, status, emp_id))
            # conn.commit()
            entry = Leave_info( TOL=tol, description=description, start_date= from_date, end_date= to_date, days=days ,emp_id= emp_id, status = status)
            auth = Authority.query.filter_by().first()
            count = Leave_count.query.filter_by(emp_id=emp_id).first()
            db.session.add(entry)
            db.session.commit()
            emp = Leave_info.query.filter_by(emp_id=emp_id).first()
            return render_template("leave_application.html", emp=emp, auth=auth, count=count)
    else:
        return redirect('/login')

@app.route('/edit_profile/<string:emp_id>', methods=['POST','GET'])
def edit_profile(emp_id):
    # print("hello")
    if ('emp_id' in session):
        emp_id = session.get('emp_id', None)
        # print("at the end near the start")
        if (request.method == 'POST'):
            # print("inside post")
            pname = request.form.get('ed_name')
            ppassword = request.form.get('ed_pass')
            pemail = request.form.get('ed_mail')
            pdesg = request.form.get('ed_desg')
            pdept = request.form.get('ed_dept')
            pcontact = request.form.get('ed_contact')
            pemcontact = request.form.get('ed_emcontact')
            entry = Employee.query.filter_by(emp_id=emp_id).first()
            entry.name = pname
            entry.email = pemail
            entry.password = ppassword
            entry.designation = pdesg
            entry.department = pdept
            entry.contact = pcontact
            entry.em_contact =pemcontact
            db.session.commit()
            return redirect("/edit_profile/<string:emp_id>")
    else:
        return redirect('/login')  
    cursor.execute("""SELECT * FROM `employee` WHERE `emp_id` LIKE '{}' """.format(emp_id))
    users=cursor.fetchall()
    emp = Employee.query.filter_by(emp_id=emp_id).first()  
    hname=emp.name
    return render_template("edit_profile.html", hname=hname, emp=emp, emp_id=emp_id)

@app.route('/auth_edit_profile/<string:a_id>', methods=['POST','GET'])
def auth_edit_profile(a_id):
    if ('a_id' in session):
        a_id = session.get('a_id', None)
        if (request.method == 'POST'):
            pname = request.form.get('ed_name') 
            pemail = request.form.get('ed_mail')
            pdesg = request.form.get('ed_desg')
            pdept = request.form.get('ed_dept')           
            entry = Authority.query.filter_by(a_id=a_id).first()
            entry.a_name = pname
            entry.a_email = pemail
            entry.a_designation = pdesg
            entry.a_department = pdept
            db.session.commit()
            return redirect("/auth_edit_profile/<string:a_id>")
    else:
        return redirect('/authloginn')  

    auth = Authority.query.filter_by(a_id=a_id).first()  
    return render_template("auth_edit_profile.html",auth=auth )

@app.route('/updater/<string:a_id>', methods=['POST','GET'])
def updater(a_id):
    if ('a_id' in session):
        a_id = session.get('a_id', None)
        leave_status = "Approved"
        days = 1
        if (request.method == 'POST'):
            emp_id = request.form.get('emp_id')
            datetd = date.today()
            tol= request.form.get('accountType')
            description = request.form.get('description')
            status = leave_status
            entry = Leave_info( TOL=tol, description=description, start_date=datetd, end_date=datetd, days=days ,emp_id= emp_id, status = status)
            db.session.add(entry)
            count = Leave_count.query.filter_by(emp_id = emp_id).first()
            print(count)
            post = Leave_info.query.filter_by(emp_id=emp_id,description=description,TOL=tol,start_date=datetd).first()
            employee= Employee.query.filter_by(emp_id = emp_id).first()
            auth = Authority.query.filter_by(a_id=a_id).first()
            leave_counter(post, count,employee, auth)
            db.session.commit()
            return redirect("/authDashboard")
    else:
        return redirect('/authloginn')  

    auth = Authority.query.filter_by(a_id=a_id).first()  
    return render_template("updater.html",auth=auth )

@app.route('/employeedetails/<string:a_id>', methods=['POST','GET'])
def employeedetails(a_id):
    if ('a_id' in session):
        a_id = session.get('a_id', None)
        auth = Authority.query.filter_by(a_id=a_id).first()
        emp = Employee.query.all()
        leave = Leave_count.query.all()
        cursor.execute("SELECT * FROM `employee`")
        empx=cursor.fetchall()
        cursor.execute("SELECT * FROM `leave_count`")
        countx=cursor.fetchall()
        print(empx)
        print(countx)
        list_info = []
        for n in range(len(empx)):
            x=empx[n] +countx[n]
            list_info.append(x)
        print(list_info)
        print(list_info[0][1])
        # users=cursor.fetchall()
        # list = [emp,leave]
        # print(list) 
        return render_template("employeedetails.html",auth=auth, emp=emp, list_info=list_info)
    else:
        return redirect('/authloginn')

@app.route('/eventadder/<string:a_id>', methods=['POST','GET'])
def eventadder(a_id):
    if ('a_id' in session):
        if request.method == "POST":
            title = request.form.get('aboutevent')
            from_date = request.form.get('from date')
            to_date = request.form.get('till date')
            justtitle = request.form.get('justtitle')
            entry= Events(title=title, start_event= from_date, end_event= to_date, justtitle=justtitle)
            db.session.add(entry)
            db.session.commit()
        auth = Authority.query.filter_by(a_id=a_id).first()
        return render_template('eventadder.html', a_id = a_id, auth=auth)

    else:
        return redirect('/authloginn')

@app.route('/calender')
def calender():
    event = Events.query.all()
    todaydate = date.today
    # current date and time
    return render_template('calender.html', event=event, todaydate=todaydate)

@app.route('/eventfinder', methods=['POST','GET'])
def eventfinder():
    eventdate = request.form.get('seventdate')
    print("event date", eventdate)
    event = Events.query.all()
    event1 = Events.query.filter_by(start_event=eventdate).all()
    print("events all:", event1)
    # current date and time
    return render_template('calender.html', event1=event1, event=event)

@app.route('/emplodatefinder', methods=['POST','GET'])
def emplodatefinder():
    eventdate = request.form.get('emplodate')
    print(eventdate)
    event = Events.query.all()
    cursor.execute("""SELECT * FROM `leave_info` WHERE `start_date` LIKE '{}' """.format(eventdate))
    infox=cursor.fetchall()
    print("this", infox)
    cursor.execute("SELECT * FROM `employee`")
    empx=cursor.fetchall()
    emp_list =[]
    for n in range(len(infox)):
        for k in range(len(empx)):
            if infox[n][7] == empx[k][0]:
                x= infox[n] + empx[k]
                emp_list.append(x)
    print(emp_list)
    return render_template('calender.html',  event=event, emp_list=emp_list) 
 
@app.route('/emplofinder', methods=['POST','GET'])
def emplofinder():
    eventdate = request.form.get('emplo')
    event = Events.query.all()
    cursor.execute("""SELECT * FROM `employee` WHERE `emp_id` LIKE '{}' """.format(eventdate))
    empx=cursor.fetchall()
    cursor.execute("""SELECT * FROM `leave_info` WHERE `emp_id` LIKE '{}' """.format(eventdate))
    infox=cursor.fetchall()
    emp_list2 =[]
    for n in range(len(infox)):
        x = infox[n]+empx[0]
        emp_list2.append(x)
    print(emp_list2)
    return render_template('calender.html',  event=event, emp_list2=emp_list2)  
    


#defined function to count leaves accurately
def leave_counter(post, count, employee,auth):
    if (post.TOL == "Sick Leave"):
        if (count.sick < 10):
            sick_count = count.sick + post.days
            if (sick_count > 10):
                diff = 10 - count.sick
                pay = abs(diff * 200)
                ld = post.leave_id
                cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
                conn.commit()
                count.sick = count.sick + diff
                mailservice(post, count, employee,auth, diff, pay)
                print("Notify employee that leaves were exhausted and extra leaves will be unpaid")
            else:
                count.sick = count.sick + post.days
                mailservice2(post, count, employee,auth)
        else:
            pay = abs(post.days * 200)
            ld = post.leave_id
            cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
            conn.commit()
            mailservice3(post, count, employee,auth,pay)
            print("Notify authority that leaves are exhausted ")

    if (post.TOL == "Breavement Leave"):
        if (count.bereavement < 10):
            bereavement_count = count.bereavement + post.days
            if (bereavement_count > 10):
                diff = 10 - count.bereavement
                pay = abs(diff * 200)
                ld = post.leave_id
                cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
                conn.commit()
                count.bereavement = count.bereavement + diff
                mailservice(post, count, employee,auth, diff,pay)
                print("Notify employee that leaves were exhausted and extra leaves will be unpaid")
            else:
                count.bereavement = count.bereavement + post.days
                mailservice2(post, count, employee,auth)
        else:
            pay = abs(post.days * 200)
            ld = post.leave_id
            cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
            conn.commit()
            mailservice3(post, count, employee,auth,pay)
            print("Notify authority that leaves are exhausted")

    if (post.TOL == "Casual Leave"):
        if (count.annual < 14):
            annual_count = count.annual + post.days
            if(annual_count > 14):
                print("Notify employee that leaves were exhausted and extra leaves will be unpaid")
                diff = 14 - count.annual
                pay = abs(diff * 200)
                # entry= Leave_info(pay = pay)
                # db.session.add(entry)
                # db.session.commit()
                ld = post.leave_id
                cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
                conn.commit()
                count.annual = count.annual + diff
                mailservice(post, count, employee,auth, diff, pay)
            else:
                
                count.annual=count.annual + post.days
                mailservice2(post, count, employee,auth)
        else:
            pay = abs(post.days * 200)
            ld = post.leave_id
            cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
            conn.commit()
            mailservice3(post, count, employee,auth, pay)
            print("Notify authority that leaves are exhausted")

    if (post.TOL == "Baby Care"):
        if (count.babycare < 15):
            babycare_count = count.babycare + post.days
            if(babycare_count > 15):
                diff = 15 - count.babycare
                pay = abs(diff * 200)
                ld = post.leave_id
                cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
                conn.commit()
                count.babycare = count.babycare + diff
                mailservice(post, count, employee,auth, diff, pay)
                print("Notify employee that leaves were exhausted and extra leaves will be unpaid")
            else:
                count.babycare=count.babycare + post.days
                mailservice2(post, count, employee,auth)
        else:
            pay = abs(post.days * 200)
            ld = post.leave_id
            cursor.execute("""Update `leave_info` set `pay` = ('%s') where leave_id = ('%s')"""%(pay,ld))
            conn.commit()
            mailservice3(post, count, employee,auth, pay)
            print("Notify authority that leaves are exhausted")

def mailservice(post, count, employee,auth,diff, pay):
    mail.send_message('From '+auth.a_name+' to '+ employee.name, sender=params['gmail_user'], 
                            recipients=[employee.email] ,
                            body ='Dear '+employee.name+' your leave of '+str(post.days) + '  days has been approved.'+"\n"+
                            'I would like to bring it to your notice that your '+post.TOL+' are now exhausted and extra requested '+str(diff)+
                            'days will cause deduction in salary accounting to ₹'+str(pay)+'. Hope to see you soon!'+"\n"+'( Documents if so any are expected to be submitted as early as possible)')
def mailservice2(post, count, employee,auth):
    mail.send_message('From '+auth.a_name+' to '+ employee.name, sender=params['gmail_user'], 
                            recipients=[employee.email] ,
                            body ='Dear '+employee.name+' your leave of '+str(post.days) + ' days has been approved.'+"\n"+
                            ' Hope to see you soon!'+"\n"+'( Documents if so any are expected to be submitted as early as possible)')
def mailservice3(post, count, employee,auth, pay):
    mail.send_message('From '+auth.a_name+' to '+ employee.name, sender=params['gmail_user'], 
                            recipients=[employee.email] ,
                            body ='Dear '+employee.name+' your ' +post.TOL+ ' are exhausted.'+"\n"+'Looking at your need and appropriate reason your leave of '+str(post.days) + ' days has been approved.'+"\n"+
                            'The salary will be deducted accounting to ₹'+str(pay)+'. Hope to see you soon!'+"\n"+'( Documents if so any are expected to be submitted as early as possible)')

app.run(debug=True,port=5000)



# @app.route('/uploader/<string:emp_id>', methods=['POST', 'GET'])
# def uploader(emp_id):
#     if ('emp_id' in session):
#         if (request.method == 'POST'):
#             file = request.files['inputFile']
#             # return file.filename
#     return render_template("uploader.html", emp_id=emp_id)
