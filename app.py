from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, make_response, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/flask-blog'
app.config['SECRET_KEY'] = '2jZPfZd37nxIHstN'
app.config['UPLOAD_FOLDER'] = 'static/img'

db = SQLAlchemy(app)
app.app_context().push()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter(Users.id == user_id).first()

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.String(100), nullable=True)
    content = db.Column(db.Text, nullable=False)    
    image = db.Column(db.String(255))
    author = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    num_read=db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    comments=db.relationship('Comments', backref='blogs',
    passive_deletes=True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    author = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blogs.id', ondelete='CASCADE'), nullable=False)

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow())
    posts=db.relationship('Blogs', backref='user',
    passive_deletes=True)
    comments=db.relationship('Comments', backref='user',
    passive_deletes=True)
    prof_views=db.Column(db.Integer, default=0)
    prof_image=db.Column(db.String(100), nullable=True)

    def __init__(self, email, password, username):
        self.email = email
        self.username = username
        self.password = password
    def is_active(self):
       return True

@app.route('/')
@login_required
def index():
    posts = Blogs.query.all()
    return render_template('index.html', posts=posts)

@app.route('/update-profile/<int:user_id>', methods=['POST', 'GET'])
@login_required
def update_profile(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password1 = request.form['password1']
        file=request.files['image']

        if file.filename == '':
            flash('No image selected for uploading..', category='error')
            return render_template('create_post.html')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        user = Users.query.filter_by(id=user_id).first()

        if current_user.id != user.id:
            flash('You do not have permission!', category='error')
        elif len(password1) < 6:
            flash('Password is too short!', category='error')
        elif len(password) < 6:
            flash('Password is too short!', category='error')
        elif len(username) < 6:
            flash('Username is too short!', category='error')
        elif password1 == user.password:
            flash('Please try different password!', category='error')
        user.username = username
        user.email = email
        user.password = generate_password_hash(password1,method='sha256')
        user.prof_image=filename
        db.session.commit()
        flash('Profile updated!', category='success')
        return redirect(url_for('profile'))
    
    return redirect(url_for('profile'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user_exists = Users.query.filter_by(username=username).first()
        email_exists = Users.query.filter_by(email=email).first()

        if user_exists:
            flash('Username is already taken!', category='error')
        elif email_exists:
            flash('Email is already taken!', category='error')
        elif len(password) < 6:
            flash('Password is too short!', category='error')
        elif len(username) < 6:
            flash('Username is too short!', category='error')

        hash_pwd = generate_password_hash(password, method='sha256')
        
        user = Users(email=email,username=username,password=hash_pwd)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('User created.', category='success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Password incorrect!', category='error')
        else:
            flash('User does not exist!', category='error')
            
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    posts = Blogs.query.all()
    current_user.prof_views += 1
    db.session.commit()
    return render_template('profile.html', current_user=current_user, posts=posts) 

@app.route('/addpost', methods=['GET','POST'])
@login_required
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        content = request.form['content']
        author=current_user.id

        if not title:
            flash('Title should not be empty!', category='error')
        if not subtitle:
            flash('Subtitle should not be empty!', category='error')
        if not content:
            flash('Content should not be empty!', category='error')
        file=request.files['image']
        if file.filename == '':
            flash('No image selected for uploading..', category='error')
            return render_template('create_post.html')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        blogpost = Blogs(title=title, subtitle=subtitle, content=content, image=filename, author=author)
        db.session.add(blogpost)
        db.session.commit()
        flash('Blog created successfully!', category='success')
        return redirect(url_for('index'))
    
    return render_template('create_post.html')

@app.route('/post/<int:post_id>/addComment/<comment>', methods=['POST'])
@login_required
def add_comment(post_id,comment):
    post = Blogs.query.filter_by(id = post_id).one()
    if post:
        new_comment = Comments(content=comment,author=current_user.id,post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"author": current_user.id, "image": new_comment.user.prof_image, 'username': new_comment.user.username, 'date_created': new_comment.date_created.strftime('%d %B, %Y'), 'content': comment, 'comment_id': new_comment.id})
    return jsonify({'error': 'Post does not exist!'}, 400)

@app.route('/post/<int:post_id>/edit', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    post = Blogs.query.filter_by(id = post_id).one()
    if request.method == 'POST':        
        if post:
            if current_user.id == post.author:
                title = request.form['title']
                subtitle = request.form['subtitle']
                content = request.form['content']
                post.title = title
                post.subtitle = subtitle
                post.content = content
                db.session.commit()
                flash('Post updated!', category='success')
                return redirect('/post/{}'.format(post.id))
            flash('You do not have permission', category='error')
        flash('We can not find that particular post!', category='error')

    return render_template('edit_post.html', post=post)

@app.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Blogs.query.filter_by(id = post_id).one()
    if post:
        if current_user.id == post.author:
            db.session.delete(post)
            db.session.commit()
            flash('Post deleted', category='success')
            return redirect(url_for('index'))
        else:
            flash('You do not have permission to delete this particular post!', category='error')
            return redirect(url_for('index'))
    else:
        flash('Post does not exist!', category='error')
        return redirect(url_for('index'))

@app.route('/post/<int:post_id>/comment/<int:comment_id>/delete')
@login_required
def delete_comment(post_id,comment_id):
    current_post = Blogs.query.filter_by(id=post_id).one()
    current_comment = Comments.query.filter_by(id=comment_id).one()
    if current_comment:
        if current_comment.post_id == current_post.id:
            if current_comment.author == current_user.id:
                db.session.delete(current_comment)
                db.session.commit()
                return redirect('/post/{}'.format(current_post.id))
            flash('You do not have permission', category='error')
    return redirect('/post/{}'.format(current_post.id))

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogs.query.filter_by(id = post_id).one()
    date_posted = post.date_created.strftime('%d %B, %Y')
    post.num_read += 1
    db.session.commit()
    user_id = post.author
    user = Users.query.filter_by(id=user_id).one()
    return render_template('post.html', post=post, date_posted=date_posted, user=user)

@app.route('/search', methods=['GET','POST'])
def about():
    if request.method == 'POST':
        query = request.form['query']
        if not query:
            flash('Please add query!', category='error')
        results = Blogs.query.filter(Blogs.title.like("%"+query+"%")).all()
        return render_template('search.html', results=results)
    return render_template('search.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)