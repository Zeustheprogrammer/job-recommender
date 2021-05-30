from flask import Flask, flash, render_template, request, redirect, url_for, session, g
import requests
import json
from flask_bcrypt import Bcrypt
import os
from flask_mysqldb import MySQL
import MySQLdb.cursors
import smtplib
from dotenv import load_dotenv
load_dotenv()

app= Flask(__name__)
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = os.getenv("MYSQL_ID")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASS")
app.config['MYSQL_DB'] = os.getenv("MYSQL_ID")
mysql = MySQL(app)
bcrypt = Bcrypt()

@app.before_request
def before_request():
    g.firstname = None

    if 'firstname' in session:
        g.firstname = session['firstname']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods =['GET', 'POST'])
def login():
     
    if request.method == 'POST' :
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor() 
        cursor.execute('SELECT * FROM user WHERE email = % s ', (email,))
        account = cursor.fetchone()
        print (account)
        temp = account[4]
        if len(account)>0:
            session.pop('firstname',None)

            if (bcrypt.check_password_hash(temp,password)) == True :
                session['loggedin'] = True
                session['id'] = account[0]
                userid=  account[0]
                session['firstname'] = account[1]            
                flash('Success! You are logged in as:' + session['firstname'])
                return redirect(url_for('jobsearch'))
            else:
                flash('Username and password are not match! Please try again', category='danger')
                return render_template('login.html')
        else:
            flash('Username and password are not match! Please try again', category='danger')
            return render_template('login.html')
    else:
        return render_template('login.html')

   
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        hash_password = bcrypt.generate_password_hash(password)
        

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        print(account)
        if account:
            flash('Account already exists !', category='danger')
       
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s)', (firstname, lastname, email, hash_password))
            mysql.connection.commit()
            flash("Account created successfully!")
            message = "Hello "+firstname + ",\n\n"+ "Thanks for registring at our JOB RECOMMENDER website" 
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(os.getenv("GMAIL"),os.getenv("PASS"))
            server.sendmail(os.getenv("GMAIL"), email, message)
    return render_template('login.html')

@app.route('/about-us')
def aboutus():
    return render_template('about-us.html')

@app.route('/developerinfo')
def developerinfo():
    return render_template('developerinfo.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact-us', methods =['GET', 'POST'])
def contactus():
    if request.method == 'POST' :
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(os.getenv("GMAIL"),os.getenv("PASS"))
        server.sendmail(os.getenv("GMAIL"),"abbojushanthan@gmail.com","From "+name + ",\n"+email +",\n\n"+  message)
        flash("You have succesfully contacted us, we will soon look through it")
        return render_template('index.html')
    else:
        return render_template('contact.html')

@app.route('/newsletter', methods =['GET', 'POST'])
def newsletter():
    if request.method == 'POST' :
        email = request.form['email']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM newsletter WHERE email = % s', (email, ))
        account = cursor.fetchone()
        print(account)
        if account:
            flash('Account already exists !', category='danger')
       
        else:
            cursor.execute('INSERT INTO newsletter VALUES (NULL, % s)', (email))
            mysql.connection.commit()
            flash("Successfully signed up for newsletter!")
            message = "Hello " + ",\n\n"+ "Thanks for registring our newsletter at our JOB RECOMMENDER website" 
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(os.getenv("GMAIL"),os.getenv("PASS"))
            server.sendmail(os.getenv("GMAIL"), email, message)
    return render_template('index.html')             

@app.route('/jobsearch', methods =['GET', 'POST'])
def jobsearch():
    if g.firstname:
        if request.method == 'POST':
             what = request.form['search']
             where = request.form['location']
             req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id=e37ee2b8&app_key=bee4526282b85f00215f62e328cc839d&results_per_page=30&what={what}&where={where}&content-type=application/json')
             data=json.loads(req.content)
             return render_template('jobsearch.html', data=data["results"],where=where)
        else:
             return render_template('jobsearch.html')
    else:
        return redirect(url_for('login'))

@app.route('/jobsearch/<what>/<where>')
def jobsearch1(what,where):
    if g.firstname:
        req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id=e37ee2b8&app_key=bee4526282b85f00215f62e328cc839d&results_per_page=30&what={what}&where={where}&content-type=application/json')
        data = json.loads(req.content)                                  
        return render_template('jobsearch.html', data=data["results"],where=where)
    else:
        return redirect(url_for('login'))
  

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('firstname', None)
   g.firstname= None
  
   return redirect(url_for('home')) 
if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug = True,port = 8080)
