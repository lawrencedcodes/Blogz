from flask import Flask, render_template, redirect, session, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.secret_key = "y337kGcys&zP3B"
db = SQLAlchemy(app)

class Blog(db.Model):    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    def __init__(self, title, body):
        self.title = title
        self.body = body
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        error = 0
        username = request.form['username']
        password = request.form['password']
        user_error = ''
        pass_error = ''
        user = User.query.filter_by(username=username).first()
        if not user:
            error = error + 1
            user_error = 'User does not exsist'
        elif user.password != password:
            error = error + 1
            pass_error = 'Invaled Password'
        if error == 0:
            if user and user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/new_post')
        else:
            return render_template('login.html', user_error=user_error, pass_error=pass_error)

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            return '<h1>This user already exists</h1>'
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')
    
@app.route('/', methods=['POST', 'GET'])
def index():
    post_id = request.args.get('id')
    title = 'Blogz'
    posts = [] 
    if post_id:
        posts = Blog.query.filter_by(id=post_id).all()
        title = Blog.title 
        return render_template('post.html', title = title, posts = posts, id = id) 
    return redirect('/blog') 

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    posts = Blog.query.all()
    return render_template('blog.html', posts = posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title_error = ''
    text_error = ''
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            title_error = 'Please add a title to continue'
            return render_template('newpost.html', title_error = title_error, text_error = text_error)
        if not body:
            text_error = 'Please add a message body to continue'
            return render_template('newpost.html', title_error = title_error, text_error = text_error) 
        new_post = Blog(title, body)
        posts = [new_post]
        title = new_post.title
        body = new_post.body
        db.session.add(new_post)
        db.session.commit()

        return render_template('post.html', title = title, body=body, posts = posts)
    return render_template('newpost.html', title_error = title_error, text_error = text_error)
if __name__ == '__main__':
    app.run()
