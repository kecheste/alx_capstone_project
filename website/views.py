from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from . import db
from .models import Blogs, Users, Comments
import cloudinary
import cloudinary.uploader
from flask import current_app as app

cloudinary.config(
    cloud_name= app.config['CLOUD_NAME'],
    api_key=app.config['API_KEY'],
    api_secret=app.config['API_SECRET']
)

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def index():
    posts = Blogs.query.all()
    return render_template('index.html', posts=posts)

@views.route('/addpost', methods=['GET','POST'])
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
            response = cloudinary.uploader.upload(file)
        try:
            blogpost = Blogs(title=title, subtitle=subtitle, content=content, image=response['url'], author=author)
            db.session.add(blogpost)
            db.session.commit()
            flash('Blog created successfully!', category='success')
            return redirect(url_for('views.index'))
        except:
            return 'Something went wrong!' 

    return render_template('create_post.html')

@views.route('/post/<int:post_id>')
def post(post_id):
    try:
        post = Blogs.query.filter_by(id = post_id).one()
        date_posted = post.date_created.strftime('%d %B, %Y')
        post.num_read += 1
        db.session.commit()
        user_id = post.author
        user = Users.query.filter_by(id=user_id).one()
        return render_template('post.html', post=post, date_posted=date_posted, user=user)
    except:
        return 'Something went wrong!'

@views.route('/search', methods=['GET','POST'])
def about():
    if request.method == 'POST':
        query = request.form['query']
        if not query:
            flash('Please add query!', category='error')
        try:
            results = Blogs.query.filter(Blogs.title.like("%"+query+"%")).all()
            return render_template('search.html', results=results)
        except:
            return 'Something went wrong!'
    return render_template('search.html')

@views.route('/post/<int:post_id>/edit', methods=['GET','POST'])
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

@views.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Blogs.query.filter_by(id = post_id).one()
    if post:
        if current_user.id == post.author:
            db.session.delete(post)
            db.session.commit()
            try:
                cloudinary.uploader.destroy(post.image)
            except cloudinary.exceptions.Error as e:
                return f"Failed to delete image."
            flash('Post deleted', category='success')
            return redirect(url_for('views.index'))
        else:
            flash('You do not have permission to delete this particular post!', category='error')
            return redirect(url_for('views.index'))
    else:
        flash('Post does not exist!', category='error')
        return redirect(url_for('views.index'))

@views.route('/post/<int:post_id>/addComment/<comment>', methods=['POST'])
@login_required
def add_comment(post_id,comment):
    post = Blogs.query.filter_by(id = post_id).one()
    if post:
        new_comment = Comments(content=comment,author=current_user.id,post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({"author": current_user.id, "image": new_comment.user.prof_image, 'username': new_comment.user.username, 'date_created': new_comment.date_created.strftime('%d %B, %Y'), 'content': comment, 'comment_id': new_comment.id})
    return jsonify({'error': 'Post does not exist!'}, 400)

@views.route('/post/<int:post_id>/comment/<int:comment_id>/delete')
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