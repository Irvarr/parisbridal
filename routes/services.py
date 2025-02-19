from flask import Blueprint, render_template

services = Blueprint('services', __name__, url_prefix='/services')

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
