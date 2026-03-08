from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Rental, Vehicle, UserRole


main_bp = Blueprint('main', __name__)


def serialize_vehicle_map(scooter: Vehicle) -> dict:
    return {
        'id': scooter.id,
        'name': scooter.name,
        'public_id': scooter.public_id,
        'latitude': float(scooter.latitude),
        'longitude': float(scooter.longitude),
        'status': scooter.status,
        'battery_level': scooter.battery_level,
        'unlock_code': scooter.unlock_code,
        'vehicle_type': scooter.vehicle_type,
    }


@main_bp.route('/')
def index():
    scooters = Vehicle.query.order_by(Vehicle.id.asc()).limit(8).all()
    return render_template('main/index.html', scooters=scooters, map_scooters=[serialize_vehicle_map(s) for s in scooters])


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == UserRole.PROVIDER.value:
        scooters = Vehicle.query.filter_by(provider_id=current_user.id).all()
        rentals = Rental.query.join(Vehicle).filter(Vehicle.provider_id == current_user.id).order_by(Rental.id.desc()).limit(10).all()
    else:
        scooters = Vehicle.query.order_by(Vehicle.id.asc()).all()
        rentals = Rental.query.filter_by(rider_id=current_user.id).order_by(Rental.id.desc()).limit(10).all()

    return render_template(
        'main/dashboard.html',
        scooters=scooters,
        rentals=rentals,
        map_scooters=[serialize_vehicle_map(s) for s in scooters],
    )
