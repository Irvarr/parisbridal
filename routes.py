from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Registry, RegistryItem
from forms import RegisterForm, LoginForm, RegistryForm, RegistryItemForm

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')
registry = Blueprint('registry', __name__, url_prefix='/registry')

@main.route('/')
def index():
    return render_template('index.html')

# Auth routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            wedding_date=form.wedding_date.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    
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

# Registry routes
@registry.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = RegistryForm()
    if form.validate_on_submit():
        registry = Registry(
            user=current_user,
            title=form.title.data,
            description=form.description.data,
            is_public=form.is_public.data
        )
        db.session.add(registry)
        db.session.commit()
        flash('Registry created successfully!', 'success')
        return redirect(url_for('registry.edit', registry_id=registry.id))
    
    return render_template('registry/create.html', form=form)

@registry.route('/<int:registry_id>')
def view(registry_id):
    registry = Registry.query.get_or_404(registry_id)
    if not registry.is_public and (not current_user.is_authenticated or current_user.id != registry.user_id):
        flash('This registry is private', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('registry/view.html', registry=registry)

@registry.route('/<int:registry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(registry_id):
    registry = Registry.query.get_or_404(registry_id)
    if current_user.id != registry.user_id:
        flash('You cannot edit this registry', 'error')
        return redirect(url_for('main.index'))
    
    form = RegistryItemForm()
    if form.validate_on_submit():
        item = RegistryItem(
            registry=registry,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            amazon_url=form.amazon_url.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('registry.edit', registry_id=registry_id))
    
    return render_template('registry/edit.html', registry=registry, form=form)
