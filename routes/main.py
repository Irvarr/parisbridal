from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from models import User, Registry

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

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

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/my-events')
@login_required
def my_events():
    weddings = current_user.weddings
    quinceaneras = current_user.quinceaneras
    event_type = request.args.get('type', None)

    return render_template('my_events.html', 
                         weddings=weddings,
                         quinceaneras=quinceaneras,
                         selected_type=event_type,
                         Registry=Registry)
