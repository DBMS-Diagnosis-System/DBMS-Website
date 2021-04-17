from flask import *
from flask_mysqldb import MySQL
import yaml
import datetime
import random
app = Flask(__name__)
app.secret_key = "Hello"





# configure db

db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] =  db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL()
mysql.init_app(app)




@app.route('/', methods = ['get','post'])
def index():
    return render_template('index.html')

@app.route('/newpatient',methods = ['GET','POST'])
def newpatient():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        mobileone = userDetails['mob1']
        mobiletwo = userDetails['mob2']
        complaint = userDetails['comments']
        rating = userDetails['rating']
        age = userDetails['age']
        dt = datetime.datetime.now()
        time = dt.time()
        cur = mysql.connection.cursor()
        cur.execute("SELECT PID FROM PATIENT")
        data = cur.fetchall()
        pid = random.randint(10000,100000)
        flag = True
        while(flag):
            if (len(data) == 0):
                break
            for d in data:
                if (d[0] != pid):
                    flag = False
                else :
                    flag = True
                    pid = random.randint(10000,100000)
                    break
        cur.execute("INSERT INTO patient(pid,pname,page) VALUES(%s,%s,%s)",(pid,name,age))
        cur.execute("INSERT INTO patient_mob(pid,mob_num) values (%s,%s)",(pid,mobileone))
        if mobiletwo != "":
            cur.execute("INSERT INTO patient_mob(pid,mob_num) values (%s,%s)",(pid,mobiletwo))
        cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
        getdoctor = "select eid from (select * from emp_doc left join employee on eid = docid) as s where s.intime < (%s) and (%s) < s.outtime and rating >= (%s)"
        cur.execute(getdoctor,(time,time,rating))
        doc = cur.fetchall()
        if doc is None:
            return redirect("/nodoctor.html")
        for d in doc:
            cur.execute("select docid from emp_doc_patient where docid = (%s)",(d[0],))
            dd = cur.fetchone()
            if not dd:
                cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,dt,complaint,d[0]))
                mysql.connection.commit()
                cur.close()
                return redirect("http://127.0.0.1:5000/patiententer", code=302)
            cur.execute("select count(*)as num_patients,docid from emp_doc_patient group by docid having docid = (%s) and num_patients <3",(d[0],))
            doctorData = cur.fetchone()
            if(doctorData):
                cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,dt,complaint,d[0]))
                mysql.connection.commit()
                cur.close()
                return redirect("http://127.0.0.1:5000/patiententer", code=302)
        return redirect("/nodoctor.html")
    return render_template('newpatient.html')

@app.route('/oldpatient',methods = ['GET','POST'])
def oldpatient():
    if request.method == "POST":
        userDetails = request.form
        pid = userDetails['patientid']
        complaint = userDetails['comments']
        samedoctor = userDetails['samedoctorornot']
        rating = userDetails['rating']
        dt = datetime.datetime.now()
        time = dt.time()
        cur = mysql.connection.cursor()
        cur.execute("SELECT PID FROM PATIENT")
        patientids = cur.fetchall()
        flag = False
        for p in patientids:
            if (int(pid) == int(p[0])):
                flag = True
                break
        if (flag != True):
            return redirect('http://127.0.0.1:5000/nopatient',code = 302)

        if (samedoctor == "yes"):
            cur.execute("SELECT docid from patient_visit where pid = %s order by tm_stamp desc",(pid,))
            doctorid = cur.fetchone() # going to the previous record
            docid = doctorid[0]
            getdoctor = "select eid from (select * from emp_doc left join employee on eid = docid) as s where s.intime < (%s) and (%s) < s.outtime and eid = (%s)"
            cur.execute(getdoctor,(time,time,docid))
            doc = cur.fetchone()
            flag = False
            if not doc:
                return redirect("/nodoctor.html")
            #for d in doc:
            #    if (docid == d[0]):
            #        flag = True
            #        break
            #if (flag == False):
            #    return redirect("/nodoctor.html")
            cur.execute("select count(*)as num_patients,docid from emp_doc_patient group by docid having docid = (%s) and num_patients <3",(docid,))
            doctorData = cur.fetchone()
            if not doctorData:
                return redirect("/nodoctor.html")
            cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
            cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(doc[0],pid,dt))
            cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,dt,complaint,doc[0]))
            mysql.connection.commit()
            cur.close()
            return redirect("http://127.0.0.1:5000/patiententer", code=302)


        else:
            getdoctor = "select eid from (select * from emp_doc left join employee on eid = docid) as s where s.intime < (%s) and (%s) < s.outtime and rating >= (%s)"
            cur.execute(getdoctor,(time,time,rating))
            doc = cur.fetchall()
            if doc is None:
                return redirect("/nodoctor.html")
            for d in doc:
                cur.execute("select docid from emp_doc_patient where docid = (%s)",(d[0],))
                dd = cur.fetchone()
                if not dd:
                    cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
                    cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                    cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,dt,complaint,d[0]))
                    mysql.connection.commit()
                    cur.close()
                    return redirect("http://127.0.0.1:5000/patiententer", code=302)
                cur.execute("select count(*)as num_patients,docid from emp_doc_patient group by docid having docid = (%s) and num_patients <3",(d[0],))
                doctorData = cur.fetchone()
                if(doctorData):
                    cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
                    cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                    cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,dt,complaint,d[0]))
                    mysql.connection.commit()
                    cur.close()
                    return redirect("http://127.0.0.1:5000/patiententer", code=302)
            return redirect("/nodoctor.html")
    return render_template('oldpatient.html')

@app.route('/patientregistration.html',methods = ['GET','POST'])
def patientregistration():
    return render_template('patientregistration.html')

@app.route('/patiententer',methods = ['GET','POST'])
def patiententer():
    cur = mysql.connection.cursor()
    query = """select docid, tm_stamp,ename, s.pid,pname from
((select docid,pid,tm_stamp,ename
 from (emp_doc_patient left join employee on eid = docid) order by tm_stamp desc) as s left join patient p on s.pid = p.pid)
 order by tm_stamp desc;
"""
    cur.execute(query)
    mysql.connection.commit()
    data = cur.fetchone()
    cur.close()
    return render_template('patiententer.html',data = data)

@app.route('/doclogin',methods = ['GET','POST'])
def login():
    msg = ""
    if request.method == "POST":
        cur = mysql.connection.cursor()
        userDetails = request.form
        docid = userDetails['userid']
        docpass = userDetails['password']
        checkquery = "select docid,pwd from emp_doc where docid = (%s) and pwd = (%s)"
        cur.execute(checkquery,(docid,docpass))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = docid
            mysql.connection.commit()
            cur.close()
            msg = ""
            return redirect('doctormain')
        else:
            msg = 'Incorrect username/password!'
    return render_template('doclogin.html',msg=msg)

@app.route('/nodoctor.html')
def nodoctor():
    return render_template('nodoctor.html')

@app.route('/nopatient')
def nopatient():
    return render_template('nopatient.html')






@app.route('/doctormain')
def doctormain():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        docid = session["id"]
        cur.execute("select ename from employee where eid = (%s)",(docid,))
        data = cur.fetchone()
        return render_template("doctormain.html",data = data)
    else:
        return redirect('doclogin')

@app.route('/doctorDetails')
def doctorDetails():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        docid = session["id"]
        getdetailsquery = """select ename,eid,esal,eage,intime,outtime,rating from employee,
        emp_doc where eid = docid and eid = (%s)"""
        cur.execute(getdetailsquery,(docid,))
        data = cur.fetchone()
        return render_template("doctorDetails.html",data = data)
    else:
        return redirect('doclogin')


@app.route('/doctorDiagnosisForm')
def doctorDiagnosisForm():
    cur = mysql.connection.cursor()
    return render_template('doctorDiagnosisForm.html')

@app.route('/doctorHistory')
def doctorHistory():
    cur = mysql.connection.cursor()
    return render_template('doctorHistory.html')

@app.route('/doctorPatients')
def doctorPatients():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        docid = session["id"]
        query = "select p.pid,p.pname,pv.complaint from patient p,patient_visit pv where p.pid = pv.pid and p.pid in (select pid from emp_doc_patient where docid = (%s))"
        cur.execute(query,(docid,))
        data = cur.fetchall()
    return render_template('doctorPatients.html',data = data)

@app.route('/doclogout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   return redirect(url_for('doclogin'))









if __name__ == '__main__':
    app.run(debug = True)
