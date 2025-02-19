from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Wedding, Quinceanera
from forms import RegisterForm, LoginForm

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered', 'error')
            return render_template('auth/register.html', form=form)

        user = User(email=form.email.data)
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()

            if form.celebration_type.data == 'wedding':
                wedding = Wedding(
                    user_id=user.id,
                    partner1_name=form.partner1_name.data,
                    partner2_name=form.partner2_name.data,
                    celebration_date=form.celebration_date.data,
                    celebration_location=form.celebration_location.data
                )
                db.session.add(wedding)
            else:  # quinceanera
                quinceanera = Quinceanera(
                    user_id=user.id,
                    celebrant_name=form.celebrant_name.data,
                    celebration_date=form.celebration_date.data,
                    celebration_location=form.celebration_location.data
                )
                db.session.add(quinceanera)

            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/register.html', form=form)

    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
