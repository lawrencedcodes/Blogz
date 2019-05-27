from flask import Flask, render_template, redirect, session, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.secret_key = "y337kGcys&zP3B"
db = SQLAlchemy(app)

class Blog(db.Model):    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    ownerid = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, body,owner):
        self.title = title
        self.body = body
        self.owner = owner
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'home', 'allposts', 'newuser', 'index', 'usersposts', 'singlepost','usersignup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    users = User.query.all()
    return render_template('home.html', users=users)

@app.route('/singlepost')
def singlepost():

   
    postid = request.args.get('postid')
    post = Blog.query.get(postid)
    return render_template('singlepost.html', post=post)

@app.route('/allposts', methods=['POST', 'GET'])
def allposts():

    posts = Blog.query.all()
    #user = User.query.all()
    return render_template('allposts.html', posts=posts)

@app.route('/login', methods=['POST', 'GET'])
def login():
   
    if request.method == 'POST':
        error = 0
        username = request.form['username']
        password = request.form['password']
        usererror = ''
        passerror = ''
        user = User.query.filter_by(username=username).first()

        if not user:
            error = error + 1
            usererror = 'User does not exsist'

        elif user.password != password:
            error = error + 1
            passerror = 'Invalid Password'

        if error == 0:
            if user and user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
        else:
            return render_template('login.html', usererror=usererror, passerror=passerror)

    return render_template('login.html')

@app.route('/logout')
def logout():

    del session['username']
    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        name = request.form['blogname']
        storys = request.form['addblog']

        errorblogname = ''
        errorblogstory = ''
        error = 0

        if len(name) == 0:
            errorblogname = 'invalid title'
            error = error + 1
        else:
            errorblogname = ''

        if len(storys) == 0:
            errorblogstory = 'invalid blog'
            error = error + 1
        else:
            errorblogstory = ''

        if error > 0:
            return render_template('newpost.html', 
            errorblogname=errorblogname, 
            errorblogstory=errorblogstory, blogname=name, addblog=storys)

        else:
            newpost = Blog(name, storys, owner)
            db.session.add(newpost)
            db.session.commit()
            userid = request.args.get('userid')
            print (userid)
            return redirect('/usersposts?user_id=' + str(newpost.owner.id))

    return render_template('newpost.html')



@app.route('/usersposts')
def usersposts():              
       
    userid = request.args.get('userid')
    user = User.query.get('userid')
    post = Blog.query.filter_by(ownerid=userid)
    return render_template('usersposts.html', user=user, posts=post)  



@app.route('/usersignup', methods=['POST', 'GET'])
def newuser():    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confpass = request.form["confirmpass"]

        olduser = ''
        usernameerror = ''
        passworderror = ''
        confpasserror = ''
        error = 0

        if len(username) < 3 or len(username) > 20:
            usernameerror = 'Not a valid user name'
            error = error + 1

        for char in username:
            if char == ' ':
                usernameerror = 'Not a valid user name'
                error = error + 1

        if len(password) < 3 or len(password) > 20:
            passworderror = 'Not a valid password'
            error = error + 1

        for char in password:
            if char == ' ':
                passworderror = 'Not a valid user name'
                error = error + 1

        if password != confpass:
            confpasserror = 'Does not match password'
            error = error + 1

        if error == 0:
            existinguser = User.query.filter_by(username=username).first()
            if not existinguser:
                newuser = User(username, password)
                db.session.add(newuser)
                db.session.commit()
                return redirect('/login')
            else:
                olduser = 'User already Registered'
                return render_template('usersignup.html', olduser=olduser, username=username)
        else:
            return render_template('usersignup.html', username=username, 
            usernameerror=usernameerror, passworderror=passworderror, 
            confpasserror=confpasserror)

    return render_template('usersignup.html')


if __name__ == '__main__':
    app.run()