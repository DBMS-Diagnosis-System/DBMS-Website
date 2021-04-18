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
        #cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
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
                cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,0,complaint,d[0]))
                mysql.connection.commit()
                cur.close()
                return redirect("http://127.0.0.1:5000/patiententer", code=302)
            cur.execute("select count(*)as num_patients,docid from emp_doc_patient group by docid having docid = (%s) and num_patients <3",(d[0],))
            doctorData = cur.fetchone()
            if(doctorData):
                cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,0,complaint,d[0]))
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
            #cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
            cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(doc[0],pid,dt))
            cur.execute("INSERT INTO patient_visit(pid,tm_stamp,complaint,docid) values (%s,%s,%s,%s)",(pid,0,complaint,d[0]))
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
                    #cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
                    cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                    cur.execute("INSERT INTO patient_visit(pid,complaint,docid) values (%s,%s,%s)",(pid,complaint,d[0]))
                    mysql.connection.commit()
                    cur.close()
                    return redirect("http://127.0.0.1:5000/patiententer", code=302)
                cur.execute("select count(*)as num_patients,docid from emp_doc_patient group by docid having docid = (%s) and num_patients <3",(d[0],))
                doctorData = cur.fetchone()
                if(doctorData):
                    #cur.execute("INSERT INTO patient_tests(pid,tm_stamp) values (%s,%s)",(pid,dt))
                    cur.execute("INSERT INTO EMP_DOC_PATIENT values (%s,%s,%s)",(d[0],pid,dt))
                    cur.execute("INSERT INTO patient_visit(pid,complaint,docid) values (%s,%s,%s)",(pid,complaint,d[0]))
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


@app.route('/doctorDiagnosisForm',methods = ['GET','POST'])
def doctorDiagnosisForm():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        print(1)
        docid = session['id']
        if request.method == "POST":
            if "addtest" in request.form:
                print(12)
                data = request.form
                patientid = data['patientid']
                testids = data['addtest']
                testids_list = testids.split(',')
                dt = datetime.datetime.now()
                for t in testids_list:
                    cur.execute("insert into patient_tests (pid,tm_stamp,tid) values (%s,%s,%s)",(patientid,dt,t))
                    cur.execute("insert into emp_labtech_testlist values (%s,%s,%s)",(patientid,t,dt)) # patient_tests is used for the bil.
                cur.execute("select t.tid,t.tname from patient_tests pt,tests t where t.tid = pt.tid and pid = (%s) and tm_stamp = (%s)",(patientid,dt))
                data = cur.fetchall()
                mysql.connection.commit()
                cur.close()
                for d  in data:
                    print(d[0],end = " ")
                    print(d[1])
                return render_template('doctorDiagnosisForm.html',data = data)
            if "pid" in request.form:
                data = request.form
                pid = data['pid']
                diagnosis = data['diagnosis']
                dnotes = data['dnotes']
                dt = datetime.datetime.now()
                cur.execute("update patient_visit set tm_stamp = (%s),diagnosis = (%s),docnotes = (%s) where pid = (%s) and docid = (%s) and tm_stamp = 0",(dt,diagnosis,dnotes,pid,docid))
                mysql.connection.commit()
                cur.close()
                return render_template('doctorDiagnosisForm.html')
    return render_template('doctorDiagnosisForm.html')

@app.route('/doctorHistory')
def doctorHistory():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        docid = session["id"]
        pids = []
        cur.execute("select pid from patient_visit where docid = (%s)",(docid,))
        ps = cur.fetchall()
        for p in ps:
            pids.append(p[0])
        pids = tuple(pids)
        cur.execute("select pat.pname,temp.pid,temp.complaint,temp.diagnosis,t.tid,t.tname,temp.cost_of_treatment from tests t,(select pv.pid,tm_stamp,complaint,diagnosis,cost_of_treatment,tid from patient_visit pv,(select pid, tid from emp_labtech_testlist) elt where pv.pid = elt.pid) temp,patient pat where temp.tid = t.tid and pat.pid = temp.pid and temp.pid in "+str(pids));
        data = cur.fetchall()
        return render_template('doctorHistory.html',data = data)
    return render_template('doctorHistory.html')

@app.route('/doctorPatients')
def doctorPatients():
    cur = mysql.connection.cursor()
    if "loggedin" in session:
        docid = session["id"]
        query = "select p.pid,p.pname,pv.complaint from patient p,patient_visit pv where p.pid = pv.pid and p.pid in (select pid from emp_doc_patient where docid = (%s))"
        cur.execute(query,(docid,))
        data = cur.fetchall()
    else:
        return redirect('doclogin')
    return render_template('doctorPatients.html',data = data)

@app.route('/doclogout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   return redirect('doclogin',code = 302)

@app.route('/bill',methods = ['get','post'])
def bill():
     cur = mysql.connection.cursor()
     if "loggedin" in session:
         docid = session['id']
         if request.method == "POST":
             if "patientbill" in request.form:
                 userdata = request.form
                 pid = userdata['patientbill']
                 query = """select p.pid,p.docid,p.pname,p.complaint,p.diagnosis,p.docnotes,p.tm_stamp,t.tid,t.tname,t.cost,p.mob_num,p.ename,sum.total from (select pid,tm_stamp,pt.tid,tname,cost from patient_tests pt, tests t where t.tid = pt.tid) t,(select pv.pid,pv.docid,p.pname,pv.complaint,pv.diagnosis,pv.docnotes,pv.tm_stamp,pm.mob_num,ename from patient_visit pv ,patient p,patient_mob pm,employee where pv.pid = p.pid and pm.pid = pv.pid and docid = eid) p,(select pid,sum(cost) as total from patient_tests pt,tests t where pt.tid = t.tid group by pid having pid = (%s)) sum where p.pid = t.pid and sum.pid = p.pid and p.pid = (%s)"""
                 cur.execute(query,(pid,pid))
                 data = cur.fetchall()
                 cur.execute("select pid,sum(cost) as total from patient_tests pt, tests t where pt.tid = t.tid and pid = (%s) order by pid",(pid,))
                 costdetails = cur.fetchone()
                 cur.execute("update patient_visit set cost_of_treatment = (%s) where cost_of_treatment is null",(costdetails[1],))
                 cur.execute("delete from patient_tests where pid = (%s)",(pid,))
                 cur.execute("delete from emp_doc_patient where pid = (%s) and docid = (%s)",(pid,docid))
                 mysql.connection.commit()
                 cur.close()
                 return render_template("bill.html", data = data)
     else:
        return redirect('doclogin')
     return render_template('bill.html')

@app.route('/employeeDetails')
def employeeDetails():
    cur = mysql.connection.cursor()
    query = "select * from employee;"
    cur.execute(query)
    data = cur.fetchall()
    return render_template('employeeDetails.html',data = data)

@app.route('/availableDoctors')
def availableDoctors():
    cur = mysql.connection.cursor()
    query = "select eid,ename,(select rating from emp_doc where docid = eid) from employee where eid in (select docid from emp_doc) and in_time<CURRENT_TIME and out_time>CURRENT_TIME;"
    cur.execute(query)
    data = cur.fetchall()
    return render_template('availableDoctors.html',data = data)

@app.route('/allHistory')
def allHistory():
    cur = mysql.connection.cursor()
    query = "select * from patient_visit;"
    cur.execute(query)
    data = cur.fetchall()
    return render_template('allHistory.html',data = data)

@app.route('/adminmain')
def adminmain():
    cur = mysql.connection.cursor()
    query = "select sum(cost_of_treatment) from patient_visit"
    cur.execute(query)
    revenue = cur.fetchall()
    d = []
    for r in revenue:
        d.append(int(r[0]))
    d = tuple(d)
    revenue = d
    return render_template('adminmain.html',revenue = revenue)

@app.route('/doctorSalary')
def doctorSalary():
    cur = mysql.connection.cursor()
    query = "select eid,ename,esal,timediff(outtime,intime) from employee where eid in (select docid from emp_doc);"
    cur.execute(query)
    data = cur.fetchall()
    return render_template('doctorSalary.html',data = data)





if __name__ == '__main__':
    app.run(debug = True)
