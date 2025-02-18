from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import logging
from app import db
from models import User, Registry, RegistryItem, Guest, WeddingPartyMember, Wedding, Quinceanera, GiftSuggestion # Added GiftSuggestion
from forms import (RegisterForm, LoginForm, RegistryForm, RegistryItemForm, 
                  RegistrySearchForm, PurchaseForm, GuestForm, WeddingPartyMemberForm,
                  CreateWeddingForm, CreateQuinceaneraForm)
from sqlalchemy import desc
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Keep existing blueprint definitions...
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')
registry = Blueprint('registry', __name__, url_prefix='/registry')
guest = Blueprint('guest', __name__, url_prefix='/guest')
services = Blueprint('services', __name__, url_prefix='/services')

@main.route('/')
def index():
    search_form = RegistrySearchForm()
    return render_template('index.html', search_form=search_form)

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

@guest.route('/wedding-details/<int:event_id>')
@login_required
def wedding_details(event_id):
    logger.debug(f"Accessing wedding details for event_id: {event_id}")
    logger.debug(f"Current user weddings: {[w.id for w in current_user.weddings]}")
    logger.debug(f"Current user: {current_user.id}")

    wedding = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    if not wedding:
        logger.error(f"Wedding not found for event_id: {event_id}, user_id: {current_user.id}")
        flash('Wedding not found.', 'error')
        return redirect(url_for('main.profile'))

    logger.debug(f"Found wedding: {wedding.id}")
    return render_template('guest/wedding_details.html', wedding=wedding)

@guest.route('/quinceanera-details/<int:event_id>')
@login_required
def quinceanera_details(event_id):
    logger.debug(f"Accessing quinceanera details for event_id: {event_id}")
    logger.debug(f"Current user quinceaneras: {[q.id for q in current_user.quinceaneras]}")
    logger.debug(f"Current user: {current_user.id}")

    quinceanera = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()
    if not quinceanera:
        logger.error(f"Quinceanera not found for event_id: {event_id}, user_id: {current_user.id}")
        flash('Quinceañera not found.', 'error')
        return redirect(url_for('main.profile'))

    logger.debug(f"Found quinceanera: {quinceanera.id}")
    return render_template('guest/quinceanera_details.html', quinceanera=quinceanera)

@guest.route('/list')
@login_required
def list_guests():
    guests = Guest.query.filter_by(user_id=current_user.id).order_by(Guest.name).all()
    return render_template('guest/list.html', guests=guests)

@guest.route('/add', methods=['GET', 'POST'])
@login_required
def add_guest():
    form = GuestForm()
    if form.validate_on_submit():
        guest = Guest(
            user_id=current_user.id,
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            number_of_guests=form.number_of_guests.data,
            table_assignment=form.table_assignment.data,
            meal_choice=form.meal_choice.data,
            dietary_restrictions=form.dietary_restrictions.data,
            notes=form.notes.data
        )
        db.session.add(guest)
        db.session.commit()
        flash('Guest added successfully!', 'success')
        return redirect(url_for('guest.list_guests'))
    return render_template('guest/add.html', form=form)

@guest.route('/<int:guest_id>/rsvp/<status>')
def update_rsvp(guest_id, status):
    guest = Guest.query.get_or_404(guest_id)
    if status in ['attending', 'not_attending']:
        guest.rsvp_status = status
        db.session.commit()
        flash('RSVP status updated!', 'success')
    return redirect(url_for('guest.list_guests'))

@guest.route('/wedding-party/<int:event_id>')
@login_required
def wedding_party(event_id=None):
    # Get the specific event
    wedding = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    quinceanera = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not wedding and not quinceanera:
        flash('Event not found.', 'error')
        return redirect(url_for('main.profile'))

    event_type = 'wedding' if wedding else 'quinceanera'

    # Get party members for this specific event
    party_members = WeddingPartyMember.query.filter_by(
        event_id=event_id,
        user_id=current_user.id
    ).order_by(WeddingPartyMember.role_type, WeddingPartyMember.created_at).all()

    # Organize members by role
    bridesmaids = [m for m in party_members if m.role_type == 'bridesmaid']
    groomsmen = [m for m in party_members if m.role_type == 'groomsman']
    sponsors = [m for m in party_members if m.role_type == 'sponsor']

    template = 'guest/wedding_party.html' if event_type == 'wedding' else 'guest/quinceanera_court.html'

    return render_template(template,
                         event=wedding or quinceanera,
                         bridesmaids=bridesmaids,
                         groomsmen=groomsmen,
                         sponsors=sponsors,
                         event_type=event_type)

@guest.route('/wedding-party/add/<int:event_id>', methods=['GET', 'POST'])
@login_required
def add_party_member(event_id):
    # Verify event exists and belongs to user
    wedding = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    quinceanera = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not wedding and not quinceanera:
        flash('Event not found.', 'error')
        return redirect(url_for('main.profile'))

    form = WeddingPartyMemberForm()
    if form.validate_on_submit():
        try:
            member = WeddingPartyMember(
                user_id=current_user.id,
                event_id=event_id,
                name=form.name.data,
                role_type=form.role_type.data,
                role_title=form.role_title.data,
                email=form.email.data,
                phone=form.phone.data,
                notes=form.notes.data
            )

            # Add to guest list if not already present
            existing_guest = Guest.query.filter_by(
                event_id=event_id,
                user_id=current_user.id,
                email=form.email.data,
                name=form.name.data
            ).first()

            if not existing_guest:
                guest = Guest(
                    user_id=current_user.id,
                    event_id=event_id,
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    rsvp_status='attending',
                    number_of_guests=1,
                    notes=f"{'Wedding' if wedding else 'Quinceañera'} Party Member - {form.role_type.data.title()}"
                    + (f" ({form.role_title.data})" if form.role_title.data else ""),
                    table_assignment=form.table_assignment.data if hasattr(form, 'table_assignment') else None,
                    meal_choice=form.meal_choice.data if hasattr(form, 'meal_choice') else 'no_preference'
                )
                db.session.add(guest)

            db.session.add(member)
            db.session.commit()
            flash('Party member added successfully and automatically added to guest list!', 'success')

            return redirect(url_for('guest.wedding_party', event_id=event_id))

        except Exception as e:
            logger.error(f"Error adding party member: {str(e)}")
            db.session.rollback()
            flash('An error occurred while adding the party member. Please try again.', 'error')

    return render_template('guest/add_party_member.html', form=form, event_id=event_id)

@guest.route('/wedding-party/<int:member_id>/delete', methods=['POST'])
@login_required
def delete_party_member(member_id):
    member = WeddingPartyMember.query.get_or_404(member_id)
    if member.user_id != current_user.id:
        flash('You are not authorized to delete this member.', 'error')
        return redirect(url_for('guest.wedding_party', event_id=member.event_id)) # added event_id

    db.session.delete(member)
    db.session.commit()
    flash('Wedding party member removed successfully.', 'success')
    return redirect(url_for('guest.wedding_party', event_id=member.event_id)) # added event_id

@guest.route('/<int:guest_id>/update-count', methods=['POST'])
@login_required
def update_guest_count(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    if guest.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    count = data.get('count', 1)

    if count < 1:
        return jsonify({'error': 'Guest count must be at least 1'}), 400

    guest.number_of_guests = count
    db.session.commit()
    return jsonify({'success': True})

@guest.route('/<int:guest_id>/update-table', methods=['POST'])
@login_required
def update_table_assignment(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    if guest.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    table = data.get('table')
    guest.table_assignment = table
    db.session.commit()
    return jsonify({'success': True})

@guest.route('/<int:guest_id>/update-meal', methods=['POST'])
@login_required
def update_meal_choice(guest_id):
    guest = Guest.query.get_or_404(guest_id)
    if guest.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    meal = data.get('meal')
    if meal not in ['no_preference', 'chicken', 'salmon', 'steak', 'vegan']:
        return jsonify({'error': 'Invalid meal choice'}), 400

    guest.meal_choice = meal
    db.session.commit()
    return jsonify({'success': True})

@guest.route('/create-wedding', methods=['GET', 'POST'])
@login_required
def create_wedding():
    # Check if user has any weddings
    existing_weddings = current_user.weddings
    if existing_weddings and len(existing_weddings) > 0:
        flash('You already have a wedding created.', 'warning')
        return redirect(url_for('guest.wedding_details', event_id=existing_weddings[0].id))

    form = CreateWeddingForm()
    if request.method == 'POST':
        logger.debug(f"Form data: {request.form}")

        if form.validate_on_submit():
            try:
                wedding = Wedding(
                    user_id=current_user.id,
                    partner1_name=form.partner1_name.data,
                    partner2_name=form.partner2_name.data,
                    celebration_date=form.celebration_date.data,
                    celebration_location=form.celebration_location.data
                )
                db.session.add(wedding)
                db.session.commit()
                flash('Wedding details created successfully!', 'success')
                return redirect(url_for('guest.wedding_details', event_id=wedding.id))
            except Exception as e:
                logger.error(f"Error creating wedding: {str(e)}")
                db.session.rollback()
                flash(f'An error occurred while creating your wedding details. Please try again.', 'error')
        else:
            logger.debug(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')

    return render_template('guest/create_wedding.html', form=form)

@guest.route('/create-quinceanera', methods=['GET', 'POST'])
@login_required
def create_quinceanera():
    # Check if user has any quinceaneras
    existing_quinceaneras = current_user.quinceaneras
    if existing_quinceaneras and len(existing_quinceaneras) > 0:
        flash('You already have a quinceañera created.', 'warning')
        return redirect(url_for('guest.quinceanera_details', event_id=existing_quinceaneras[0].id))

    form = CreateQuinceaneraForm()
    if request.method == 'POST':
        logger.debug(f"Form data: {request.form}")

        if form.validate_on_submit():
            try:
                quinceanera = Quinceanera(
                    user_id=current_user.id,
                    celebrant_name=form.celebrant_name.data,
                    celebration_date=form.celebration_date.data,
                    celebration_location=form.celebration_location.data
                )
                db.session.add(quinceanera)
                db.session.commit()
                flash('Quinceañera details created successfully!', 'success')
                return redirect(url_for('guest.quinceanera_details', event_id=quinceanera.id))
            except Exception as e:
                logger.error(f"Error creating quinceañera: {str(e)}")
                db.session.rollback()
                flash(f'An error occurred while creating your quinceañera details. Please try again.', 'error')
        else:
            logger.debug(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')

    return render_template('guest/create_quinceanera.html', form=form)

@registry.route('/create/<event_type>/<int:event_id>', methods=['GET', 'POST'])
@login_required
def create(event_type, event_id):
    # Verify event exists and belongs to user
    event = None
    if event_type == 'wedding':
        event = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    else:
        event = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not event:
        flash('Event not found.', 'error')
        return redirect(url_for('main.index'))

    form = RegistryForm()
    if form.validate_on_submit():
        registry = Registry(
            user=current_user,
            event_type=event_type,
            event_id=event_id,
            title=form.title.data,
            description=form.description.data,
            is_public=form.is_public.data
        )
        db.session.add(registry)
        db.session.commit()
        flash('Registry created successfully!', 'success')
        return redirect(url_for('registry.edit', registry_id=registry.id))

    return render_template('registry/create.html', form=form, event=event)

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
            item_type=form.item_type.data,
            price=form.price.data if form.item_type.data in ['physical', 'experience'] else None,
            target_amount=form.target_amount.data if form.item_type.data == 'cash' else None,
            amazon_url=form.amazon_url.data if form.item_type.data == 'physical' else None,
            experience_date=form.experience_date.data if form.item_type.data == 'experience' else None,
            experience_location=form.experience_location.data if form.item_type.data == 'experience' else None
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

@registry.route('/item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = RegistryItem.query.get_or_404(item_id)
    if item.registry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main.route('/search')
def search():
    query = request.args.get('search', '').strip()
    celebration_type = request.args.get('celebration_type', 'wedding')

    if not query:
        return redirect(url_for('main.index'))

    users = User.query.filter(
        (User.partner1_name.ilike(f'%{query}%')) |
        (User.partner2_name.ilike(f'%{query}%')) |
        (User.email.ilike(f'%{query}%'))
    ).all()

    registries = []
    for user in users:
        if user.registry and user.registry.is_public:
            registries.append(user.registry)

    return render_template('registry/search_results.html', 
                         registries=registries, 
                         query=query, 
                         celebration_type=celebration_type)


@services.route('/bridal-gowns')
def bridal_gowns():
    return render_template('services/bridal_gowns.html')

@services.route('/quinceanera-dresses')
def quinceanera_dresses():
    return render_template('services/quinceanera_dresses.html')

@services.route('/tuxedo-rentals')
def tuxedo_rentals():
    return render_template('services/tuxedo_rentals.html')

@services.route('/accessories')
def accessories():
    return render_template('services/accessories.html')

@services.route('/decorations')
def decorations():
    return render_template('services/decorations.html')

@services.route('/planning-services')
def planning_services():
    return render_template('services/planning_services.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@registry.route('/<int:registry_id>/suggestions')
@login_required
def suggestions(registry_id):
    registry = Registry.query.get_or_404(registry_id)
    if current_user.id != registry.user_id:
        flash('You cannot view suggestions for this registry', 'error')
        return redirect(url_for('main.index'))

    # Get suggested gifts based on event type and popularity
    suggestions = GiftSuggestion.query.filter_by(
        event_type=registry.event_type
    ).order_by(desc(GiftSuggestion.popularity_score)).limit(20).all()

    # Randomize suggestions to provide variety
    suggestions = random.sample(suggestions, min(len(suggestions), 12))

    return render_template('registry/suggestions.html', 
                         registry=registry, 
                         suggestions=suggestions)

@registry.route('/add-suggestion/<int:registry_id>/<int:suggestion_id>', methods=['POST'])
@login_required
def add_suggestion(registry_id, suggestion_id):
    registry = Registry.query.get_or_404(registry_id)
    suggestion = GiftSuggestion.query.get_or_404(suggestion_id)

    if current_user.id != registry.user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Create new registry item from suggestion
    item = RegistryItem(
        registry=registry,
        name=suggestion.name,
        description=suggestion.description,
        item_type='physical',
        price=None  # Will be updated when Amazon product is selected
    )

    # Increment popularity score
    suggestion.popularity_score += 1

    db.session.add(item)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Item added to registry'
    })

# Add after the profile route
@main.route('/my-events')
@login_required
def my_events():
    # Get user's events
    weddings = current_user.weddings
    quinceaneras = current_user.quinceaneras

    # Get the event type from query param if provided
    event_type = request.args.get('type', None)

    return render_template('my_events.html', 
                         weddings=weddings,
                         quinceaneras=quinceaneras,
                         selected_type=event_type)