from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import BlogPost, db
from datetime import datetime

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def index():
    """Show all blog posts"""
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(published=True)\
        .order_by(BlogPost.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('blog/index.html', posts=posts)

@blog.route('/blog/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """Create a new blog post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        event_type = request.form.get('event_type')
        image_url = request.form.get('image_url')

        if not title or not content or not event_type:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('blog.new_post'))

        post = BlogPost(
            title=title,
            content=content,
            event_type=event_type,
            image_url=image_url,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Your blog post has been created!', 'success')
        return redirect(url_for('blog.index'))

    return render_template('blog/new.html')

@blog.route('/blog/<int:post_id>')
def view_post(post_id):
    """View a single blog post"""
    post = BlogPost.query.get_or_404(post_id)
    return render_template('blog/view.html', post=post)

@blog.route('/blog/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Edit a blog post"""
    post = BlogPost.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You can only edit your own posts.', 'error')
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.event_type = request.form.get('event_type')
        post.image_url = request.form.get('image_url')
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('blog.view_post', post_id=post.id))

    return render_template('blog/edit.html', post=post)
