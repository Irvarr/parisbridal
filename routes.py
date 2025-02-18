from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from models import User, Registry, RegistryItem
from forms import RegisterForm, LoginForm, RegistryForm, RegistryItemForm, RegistrySearchForm, PurchaseForm

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')
registry = Blueprint('registry', __name__, url_prefix='/registry')

@main.route('/')
def index():
    search_form = RegistrySearchForm()
    return render_template('index.html', search_form=search_form)

@main.route('/search')
def search():
    query = request.args.get('search', '').strip()
    if not query:
        return redirect(url_for('main.index'))

    # Search for users by name or email
    users = User.query.filter(
        (User.name.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
    ).all()

    # Get public registries for found users
    registries = []
    for user in users:
        if user.registry and user.registry.is_public:
            registries.append(user.registry)

    return render_template('registry/search_results.html', registries=registries, query=query)

# Auth routes
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already registered', 'error')
            return render_template('auth/register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            wedding_date=form.wedding_date.data
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
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

@registry.route('/item/<int:item_id>/purchase', methods=['GET', 'POST'])
def purchase(item_id):
    item = RegistryItem.query.get_or_404(item_id)
    if item.is_purchased:
        flash('This item has already been purchased', 'warning')
        return redirect(url_for('registry.view', registry_id=item.registry_id))

    form = PurchaseForm()
    if form.validate_on_submit():
        item.is_purchased = True
        item.purchased_by = form.purchased_by.data

        delivery_choice = request.form.get('delivery_choice')
        if delivery_choice == 'ship_to_couple':
            item.ship_to_couple = True
            item.bring_to_wedding = False
            item.shipping_address = None
        elif delivery_choice == 'ship_to_me':
            item.ship_to_couple = False
            item.bring_to_wedding = False
            item.shipping_address = form.shipping_address.data
        else:  # bring_to_wedding
            item.ship_to_couple = False
            item.bring_to_wedding = True
            item.shipping_address = None

        item.purchase_date = datetime.utcnow()

        try:
            db.session.commit()
            flash('Thank you for your purchase!', 'success')
            return redirect(url_for('registry.view', registry_id=item.registry_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')

    return render_template('registry/purchase.html', form=form, item=item)