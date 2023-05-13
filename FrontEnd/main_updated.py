import pymysql 
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import dpctl
import numpy as np
# Intel one api modules
from numba import njit, prange

app = Flask(__name__)

app.secret_key = 'secretKey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'K@jol123!!'
app.config['MYSQL_DB'] = 'LOGIN'

mysql = MySQL(app)

def result_page(query):
    df = pd.read_csv('All_nyc_cafes.csv',index_col=[0])
    
    print(df.head())
    try:
        output = df[df['zip_code'] == int(query)]
        # locations = output[['name','location']]
        normalized = pd.json_normalize(output['location'].apply(eval))
        locations = pd.concat([output.drop('location',axis=1),normalized],axis=1)
        locations['location_url'] = 'https://www.google.com/maps/search/' + locations['lat'].apply(str)+ ',' + locations['lng'].apply(str) + '/@' + locations['lat'].apply(str) + ',' + locations['lng'].apply(str) + ',17z'
        results = locations.to_dict('records')
        
        locations_dict = locations[['name','lat','lng']].to_dict('records')
        # print(results[:5])
        # print(locations_dict[:5])

    except Exception as e:
        print(e)
        output = []

    return results,locations_dict


@njit(parallel=True)
def search_restaurants(query,location, radius=10):
    with dpctl.device_context("opencl:gpu"):
        # Perform optimized location search algorithm using Intel OneAPI toolkit
        # This code is optimized for execution on a GPU using DPC++ programming language
        # The algorithm should return a list of nearby cafes
        _, cafes = result_page(query)
        cafes = np.array(restaurants)
        nearby_restaurants = []
        for i in prange(restaurants.shape[0]):
            if np.linalg.norm(location - restaurants[i]['location']) <= radius:
                nearby_restaurants.append(restaurants[i]['name'])
        return nearby_restaurants
        
       

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM form WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
                    # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM form WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO form VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
                        msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/login/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        results = search_restaurants(query,location)
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'],results=results)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/login/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
            # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM form WHERE id = %s', (session['username'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
