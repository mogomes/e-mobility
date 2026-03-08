from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Rental, Scooter, UserRole


main_bp = Blueprint('main', __name__)


def serialize_scooter_map(scooter: Scooter) -> dict:
    return {
        'id': scooter.id,
        'name': scooter.name,
        'public_id': scooter.public_id,
        'latitude': float(scooter.latitude),
        'longitude': float(scooter.longitude),
        'status': scooter.status,
        'battery_level': scooter.battery_level,
    }


@main_bp.route('/')
def index():
    scooters = Scooter.query.order_by(Scooter.id.asc()).limit(8).all()
    return render_template('main/index.html', scooters=scooters, map_scooters=[serialize_scooter_map(s) for s in scooters])


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == UserRole.PROVIDER.value:
        scooters = Scooter.query.filter_by(provider_id=current_user.id).all()
        rentals = Rental.query.join(Scooter).filter(Scooter.provider_id == current_user.id).order_by(Rental.id.desc()).limit(10).all()
    else:
        scooters = Scooter.query.order_by(Scooter.id.asc()).all()
        rentals = Rental.query.filter_by(rider_id=current_user.id).order_by(Rental.id.desc()).limit(10).all()

    return render_template(
        'main/dashboard.html',
        scooters=scooters,
        rentals=rentals,
        map_scooters=[serialize_scooter_map(s) for s in scooters],
    )
