from flask import Flask, flash, render_template, request, redirect, url_for, session, g
import requests
import json
from flask_bcrypt import Bcrypt
import os
from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
#import MySQLdb.cursors
import smtplib
from dotenv import load_dotenv

load_dotenv()

app= Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
"""mysql = MySQL(app)

app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = os.getenv("MYSQL_ID")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASS")
app.config['MYSQL_DB'] = os.getenv("MYSQL_ID")"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///likhijr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



@app.before_request
def before_request():
    g.firstname = None

    if 'firstname' in session:
        g.firstname = session['firstname']

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password = db.Column(db.String(length=60), nullable=False)
  
        

class Newsletter(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
   
       
@app.route('/')
def home():
    return render_template('index.html')
    

@app.route('/login',methods =['GET', 'POST'])
def login():
     
    if request.method == 'POST' :
        try:
        
            """email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor() 
            cursor.execute('SELECT * FROM user WHERE email = % s ', (email,))
            user = cursor.fetchone()"""
            user = User.query.filter_by(email=request.form['email']).first()  
            if user:
                session.pop('firstname',None)

                if (bcrypt.check_password_hash(user.password,request.form['password'])) == True :
                    session['loggedin'] = True
                    session['id'] = user.id             
                    session['firstname'] = user.firstname           
                    flash('Success! You are logged in as: ' + session['firstname'], category='success')
                    return redirect(url_for('jobsearch'))
                else:
                    flash('Username and password are not match! Please try again', category='danger')
                    return render_template('login.html')
            else:
                flash('Username and password are not match! Please try again', category='danger')
                return render_template('login.html')
        except :
            flash("Error: In Our Database, Please Try Again Later With Valid Details", category='danger') 
            return render_template('login.html')

    else:
        return render_template('login.html')

   
@app.route('/register', methods =['GET', 'POST'])
def register():

    if request.method == 'POST' :     
 
        """firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']"""
        pwd = request.form['password']
            
        hash_password = bcrypt.generate_password_hash(pwd)
            
        try:
            """cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
            user = cursor.fetchone()"""
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                flash('Email already exists !', category='danger')
            
            else:
                new_user = User(firstname=request.form['firstname'],lastname=request.form['lastname'],email=request.form['email'],password=hash_password)
                db.session.add(new_user)
                db.session.commit()

                """cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s)',(firstname, lastname, email, hash_password))
                mysql.connection.commit()"""
                flash("Account created successfully!", category='success')
        except:
            flash("Error: In Our Database, Please Try Again Later With Valid Details", category='danger') 
        try:        
                message = "Hello "+request.form['firstname'] + ",\n\n"+ "Thanks for registring at our job recommender website" 
                server = smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(os.getenv("GMAIL"),os.getenv("PASS"))
                server.sendmail(os.getenv("GMAIL"), request.form['email'], message)
      
        except :
            flash("Sorry, due to some technical issues we are unable to send you welcome email", category='danger')   


    return render_template('login.html')


@app.route('/about-us')
def aboutus():
    return render_template('about-us.html')


@app.route('/contact-us', methods =['GET', 'POST'])
def contactus():
    if request.method == 'POST' :
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        try :
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(os.getenv("GMAIL"),os.getenv("PASS"))
            server.sendmail(os.getenv("GMAIL"),"abbojushanthan@gmail.com","From " + name + ",\n"+ email +",\n\n"+ message)
            flash("You have succesfully contacted us, we will soon look through it", category='success')
        except :
             flash("We are facing some technical issues, Please Try Again Later", category='danger')         
        if g.firstname: 
            return redirect(url_for('jobsearch'))
        else :
            return render_template('index.html')
    else:
        return render_template('contact.html')


@app.route('/newsletter', methods =['GET', 'POST'])
def newsletter():
    if request.method == 'POST' :
 
        mail = request.form['email']
        try:
            """cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM newsletter WHERE email = % s', (email, ))
            user = cursor.fetchone()
            print(user)"""
            user = Newsletter.query.filter_by(email=mail).first()
            if user:
                flash('Account already exists !', category='danger')
            
            else:
                new_user = Newsletter(email=request.form['email'])
                db.session.add(new_user)
                db.session.commit()
        except:
                flash("Error: In Our Database, Please Try Again Later With Valid Details", category='danger')    
        try :
                flash("Successfully signed up for newsletter!", category='success')
                message = "Hello " + ",\n\n"+ "Thanks for registring our newsletter at our job recommender website" 
                server = smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(os.getenv("GMAIL"),os.getenv("PASS"))
                server.sendmail(os.getenv("GMAIL"), request.form['email'], message)
        except :
            flash("Sorry, due to some technical issues we are unable to send you welcome email", category='danger')       


    if g.firstname: 
        return redirect(url_for('jobsearch'))
    else :
        return render_template('index.html')             


@app.route('/jobsearch', methods =['GET', 'POST'])
def jobsearch():
    if g.firstname:
        if request.method == 'POST':
            what = request.form['search']
            where = request.form['location']
            try :
                req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={os.getenv("APP_ID")}&app_key={os.getenv("APP_KEY")}&results_per_page=50&what={what}&where={where}&content-type=application/json')
                data=json.loads(req.content)
                print(len(data))
                return render_template('jobsearch.html', data=data["results"])
                
            except :
                flash("We are facing some technical issues, Please Try Again Later", category='danger')             
        else:
            return render_template('jobsearch.html')
    else:
        return redirect(url_for('login'))


@app.route('/jobsearch/<what>/<where>/<salary_min>')
def jobsearch1(what,where,salary_min):
    if g.firstname:
        try:   
            req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={os.getenv("APP_ID")}&app_key={os.getenv("APP_KEY")}&results_per_page=50&what={what}&where={where}&salary_min={salary_min}&content-type=application/json')
            data = json.loads(req.content) 
        
            return render_template('jobsearch.html', data=data["results"])
           
        except :
            flash("We are facing some technical issues, Please Try Again Later", category='danger')     
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
