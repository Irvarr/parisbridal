from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Guest, WeddingPartyMember, Wedding, Quinceanera, Registry
from forms import GuestForm, WeddingPartyMemberForm, CreateWeddingForm, CreateQuinceaneraForm
import logging

guest = Blueprint('guest', __name__, url_prefix='/guest')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@guest.route('/wedding-details/<int:event_id>')
@login_required
def wedding_details(event_id):
    logger.debug(f"Accessing wedding details for event_id: {event_id}")
    wedding = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    if not wedding:
        flash('Wedding not found.', 'error')
        return redirect(url_for('main.profile'))

    return render_template('guest/wedding_details.html', 
                         wedding=wedding, 
                         Registry=Registry)

@guest.route('/quinceanera-details/<int:event_id>')
@login_required
def quinceanera_details(event_id):
    logger.debug(f"Accessing quinceanera details for event_id: {event_id}")
    quinceanera = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()
    if not quinceanera:
        flash('Quinceañera not found.', 'error')
        return redirect(url_for('main.profile'))

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
    wedding = Wedding.query.filter_by(id=event_id, user_id=current_user.id).first()
    quinceanera = Quinceanera.query.filter_by(id=event_id, user_id=current_user.id).first()

    if not wedding and not quinceanera:
        flash('Event not found.', 'error')
        return redirect(url_for('main.profile'))

    event_type = 'wedding' if wedding else 'quinceanera'
    
    party_members = WeddingPartyMember.query.filter_by(
        event_id=event_id,
        user_id=current_user.id
    ).order_by(WeddingPartyMember.role_type, WeddingPartyMember.created_at).all()

    bridesmaids = [m for m in party_members if m.role_type == 'bridesmaid']
    groomsmen = [m for m in party_members if m.role_type == 'groomsman']
    sponsors = [m for m in party_members if m.role_type == 'sponsor']

    template = 'guest/wedding_party.html' if event_type == 'wedding' else 'guest/quinceanera_court.html'

    return render_template(template,
                       event_id=event_id,
                       event=wedding or quinceanera,
                       bridesmaids=bridesmaids,
                       groomsmen=groomsmen,
                       sponsors=sponsors,
                       event_type=event_type)

@guest.route('/wedding-party/add/<int:event_id>', methods=['GET', 'POST'])
@login_required
def add_party_member(event_id):
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
                    + (f" ({form.role_title.data})" if form.role_title.data else "")
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
        return redirect(url_for('guest.wedding_party', event_id=member.event_id))

    db.session.delete(member)
    db.session.commit()
    flash('Wedding party member removed successfully.', 'success')
    return redirect(url_for('guest.wedding_party', event_id=member.event_id))

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
