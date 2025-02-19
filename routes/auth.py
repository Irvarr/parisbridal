from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User
from forms import RegisterForm, LoginForm

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if a user with this email already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email address already registered', 'error')
                return render_template('auth/register.html', form=form)

            # Create new user and set password
            user = User(email=form.email.data)
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/register.html', form=form)
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))
            else:
                flash('Invalid email or password', 'error')
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
