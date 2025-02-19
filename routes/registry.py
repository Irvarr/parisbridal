from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Registry, RegistryItem, GiftSuggestion
from forms import RegistryForm, RegistryItemForm, PurchaseForm
from datetime import datetime
from sqlalchemy import desc
import random

registry = Blueprint('registry', __name__, url_prefix='/registry')

@registry.route('/create/<event_type>/<int:event_id>', methods=['GET', 'POST'])
@login_required
def create(event_type, event_id):
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
        item.purchase_date = datetime.utcnow()
        
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

@registry.route('/<int:registry_id>/suggestions')
@login_required
def suggestions(registry_id):
    registry = Registry.query.get_or_404(registry_id)
    if current_user.id != registry.user_id:
        flash('You cannot view suggestions for this registry', 'error')
        return redirect(url_for('main.index'))

    suggestions = GiftSuggestion.query.filter_by(
        event_type=registry.event_type
    ).order_by(desc(GiftSuggestion.popularity_score)).limit(20).all()

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

    item = RegistryItem(
        registry=registry,
        name=suggestion.name,
        description=suggestion.description,
        item_type='physical',
        price=None
    )

    suggestion.popularity_score += 1

    db.session.add(item)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Item added to registry'
    })
