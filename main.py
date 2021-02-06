from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os
import math
from werkzeug.utils import secure_filename
from datetime import datetime
import urllib.request
#'''-------------------------------------------------------------------------------------------------------------'''



with open('config.json', 'r') as c:
    params = json.load(c)["params"]
app = Flask(__name__)
app.secret_key='super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
#'''--------------------------------------------------s'''
local_server = True
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

#'''-----------------------------------------------------------------------------------------------------------------'''


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    message = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(150), nullable=False)
    Slug = db.Column(db.String(25), nullable=False)
    Content = db.Column(db.String(500), nullable=False)
    Tagline = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(20), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    for i in range(9):
        if (i < 3):
            with urllib.request.urlopen(
                    "https://newsapi.org/v2/top-headlines?country=in&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
                data = json.loads(url.read())
            topheadlines = data['articles']
        if (i > 2 and i < 6):
            with urllib.request.urlopen(
                    "http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
                data = json.loads(url.read())
            business = data['articles']
        if (i > 5 and i < 9):
            with urllib.request.urlopen(
                    "http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
                data = json.loads(url.read())
            tech = data['articles']
    return render_template('index.html', params=params, topheadlines=topheadlines, business=business, tech=tech, i=i,posts=posts)


#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route('/about')
def about():
    return render_template('about.html', params=params)
#------------------------------------------------------------------------------------------------------------------
@app.route('/topheadlines')
def topheadlines():
    posts = Posts.query.filter_by().all()
    with urllib.request.urlopen(
            "https://newsapi.org/v2/top-headlines?country=in&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
        data = json.loads(url.read())
    topheadlines = data['articles']
    return render_template('topheadlines.html', params=params,topheadlines=topheadlines,posts=posts)
#------------------------------------------------------------------------------------------------------------------
@app.route('/business')
def business():
    posts = Posts.query.filter_by().all()
    with urllib.request.urlopen(
            "http://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
        data = json.loads(url.read())
    business= data['articles']
    return render_template('business.html', params=params,business=business,posts=posts)
#------------------------------------------------------------------------------------------------------------------
@app.route('/tech')
def tech():
    posts = Posts.query.filter_by().all()
    with urllib.request.urlopen(
            "http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=b25124c3cdcb4cccbcee8fd9f3ebc022") as url:
        data = json.loads(url.read())
    tech = data['articles']
    return render_template('tech.html', params=params,tech=tech,posts=posts)

#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route("/dashboard", methods = ['Get' , 'Post'])

def dashboard():
    if ('user' in session and session['user'] == params["admin_user"]):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params,posts=posts)

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params["admin_user"] and userpass == params["admin_password"]):
            session['user'] = username
            posts =Posts.query.all()
            return render_template('dashboard.html', params=params,posts=posts)

    return render_template('login.html', params=params)

#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(Slug=post_slug).first()
    return render_template('post.html', params=params, post=post)
#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params["admin_user"]):
        if request.method == 'POST':
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            if sno == '0':
                post=Posts(Title = box_title,Slug=slug, Content=content,Tagline = tline,img_file=img_file,Date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.Title = box_title
                post.Slug = slug
                post.Content = content
                post.Tagline = tline
                post.img_file = img_file
                post.Date=date
                db.session.commit()
                return redirect("/edit/" + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno)
#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route("/uploader", methods = ['Get' , 'Post'])
def uploader():
    if ('user' in session and session['user'] == params["admin_user"]):

        if (request.method == 'POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "uploaded successfully"
#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

#--------------------------------------------------------------------------------------------------------------------'''
@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params["admin_user"]):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')
#'''-----------------------------------------------------------------------------------------------------------------'''
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''add entry ro post'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contact(name=name, email=email, phone_no=phone, message=message, )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', params=params)

#'''-----------------------------------------------------------------------------------------------------------------'''
app.run(debug=True)

