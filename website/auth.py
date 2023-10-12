from flask import Blueprint, render_template, flash, request, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import Users, Blogs
import cloudinary
import cloudinary.uploader
from flask import current_app as app

cloudinary.config(
    cloud_name= app.config['CLOUD_NAME'],
    api_key=app.config['API_KEY'],
    api_secret=app.config['API_SECRET']
)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user)
                return redirect(url_for('views.index'))
            else:
                flash('Password incorrect!', category='error')
        else:
            flash('User does not exist!', category='error')
            
    return render_template('login.html')

@auth.route('/register', methods=['GET','POST'])
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
        return redirect(url_for('views.index'))
    
    return render_template('register.html')

@auth.route('/profile')
@login_required
def profile():
    posts = Blogs.query.all()
    current_user.prof_views += 1
    db.session.commit()
    return render_template('profile.html', current_user=current_user, posts=posts)

@auth.route('/update-profile/<int:user_id>', methods=['POST', 'GET'])
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
            response = cloudinary.uploader.upload(file)

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
        user.prof_image=response['url']
        db.session.commit()
        flash('Profile updated!', category='success')
        return redirect(url_for('auth.profile'))
    
    return redirect(url_for('auth.profile'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out!')
    return redirect(url_for('auth.login'))