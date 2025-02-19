from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from models import Appointment
from forms import AppointmentForm
from datetime import datetime
import logging

appointments = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments.route('/book', methods=['GET', 'POST'])
def book():
    form = AppointmentForm()
    if form.validate_on_submit():
        try:
            appointment = Appointment(
                user_id=current_user.id if current_user.is_authenticated else None,
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                service_type=form.service_type.data,
                preferred_date=form.preferred_date.data,
                alternate_date=form.alternate_date.data,
                notes=form.notes.data,
                status='pending'
            )
            db.session.add(appointment)
            db.session.commit()
            flash('Your appointment request has been submitted! We will contact you shortly to confirm.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            logging.error(f"Error booking appointment: {str(e)}")
            db.session.rollback()
            flash('An error occurred while booking your appointment. Please try again.', 'error')
    
    return render_template('appointments/book.html', form=form)

@appointments.route('/my-appointments')
@login_required
def my_appointments():
    appointments = Appointment.query.filter_by(user_id=current_user.id)\
        .order_by(Appointment.preferred_date.desc()).all()
    return render_template('appointments/list.html', appointments=appointments)

@appointments.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != current_user.id:
        flash('You are not authorized to cancel this appointment.', 'error')
        return redirect(url_for('appointments.my_appointments'))
    
    appointment.status = 'cancelled'
    db.session.commit()
    flash('Your appointment has been cancelled.', 'success')
    return redirect(url_for('appointments.my_appointments'))
