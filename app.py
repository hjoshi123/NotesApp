'''
Flask App for python_web Workshop by Developer Student Club, Ramaiah Institute of Technology
This app covers concepts of using templates using jinja, routes, mongodb, sessions, logging in
and API requests for the users using JWT tokens.
This app allows you to sign up and log in and add notes. It also returns the list of notes 
based on the username through a REST API. 

License: GNU GPL 3.0
Author: @Hemant.Joshi
'''

from flask import Flask, request, render_template, redirect, session, url_for
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)

client = MongoClient('mongodb://elliotalderson:mrrobot@ds241019.mlab.com:41019/notesflask')
db = client.notesflask


# login route or default route
@app.route("/", methods=['GET', 'POST'])
def login():
    # Check if its login or signup by default its login
    status = 1
    if request.method == 'POST':
        status = int(request.form['status'])
        print(status)

    return render_template("login.html", status=status, err=None)


# Get data from user and log him in
@app.route("/login", methods=['POST'])
def userLogin():
    users = db.users
    login_user = users.find_one({'name': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return render_template("login.html", status=1, err="Invalid Username/Password")


@app.route("/signup", methods=['POST'])
def signup():
    users = db.users
    existing_user = users.find_one({'name': request.form['username']})

    if existing_user is None:
        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users.insert({'name': request.form['username'], 'password': hashpass})
        session['username'] = request.form['username']
        return redirect(url_for('index'))

    return 'That username already exists!'


@app.route("/check", methods=['GET'])
def check():
    users = db.users
    existing_user = users.find_one({'name': session['username']})

    if existing_user is not None:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route("/index", methods=['GET'])
def index():
    """
    users = db.users
    posts = db.posts
    # implement DRY with a separate function to check if he has logged in first to access /index
    existing_user = users.find_one({'name': session['username']})

    if existing_user is not None:

    else:
        return redirect(url_for('login'))
    """
    users = db.users
    existing_user = users.find_one({'name': session['username']})
    posts = db.posts
    posts_list = posts.find({'username': existing_user['name']})
    print(type(posts_list))
    return render_template("index.html", posts_list=posts_list)


@app.route("/logout", methods=['POST'])
def userLogout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/add", methods=['POST'])
def addNotes():
    users = db.users
    posts = db.posts

    if request.method == 'POST':
        existing_user = users.find_one({'name': session['username']})
        if existing_user is not None:
            title = request.form['title']
            desc = request.form['description']
            post = {
                'username': existing_user['name'],
                'title': title,
                'description': desc
            }
            posts.insert_one(post)
            return redirect('/index')
        else:
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'Mr.Robot_is_awesome'
    app.run(host='localhost', port=8080, debug=True)
