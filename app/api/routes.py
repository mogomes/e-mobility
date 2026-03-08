from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Rental, Vehicle, User
from ..services import end_rental, start_rental


api_bp = Blueprint('api', __name__)


def serialize_vehicle(vehicle: Vehicle) -> dict:
    return {
        'id': vehicle.id,
        'public_id': vehicle.public_id,
        'name': vehicle.name,
        'vehicle_type': vehicle.vehicle_type,
        'battery_level': vehicle.battery_level,
        'latitude': float(vehicle.latitude),
        'longitude': float(vehicle.longitude),
        'status': vehicle.status,
        'provider': vehicle.provider.username,
    }


def serialize_rental(rental: Rental) -> dict:
    return {
        'id': rental.id,
        'vehicle_id': rental.vehicle_id,
        'rider': rental.rider.username,
        'start_time': rental.start_time.isoformat(),
        'end_time': rental.end_time.isoformat() if rental.end_time else None,
        'status': rental.status,
        'total_price': float(rental.total_price) if rental.total_price is not None else None,
        'distance_km': float(rental.distance_km) if rental.distance_km is not None else None,
    }


def api_user_from_request():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.removeprefix('Bearer ').strip()
        return User.query.filter_by(api_token=token).first()
    return None


@api_bp.route('/token', methods=['POST'])
def token():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid_credentials'}), 401

    return jsonify({'token': user.api_token, 'role': user.role})


@api_bp.route('/vehicles', methods=['GET'])
def vehicles():
    vehicles = Vehicle.query.order_by(Vehicle.id.asc()).all()
    return jsonify([serialize_vehicle(v) for v in vehicles])


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def vehicle_detail(vehicle_id):
    vehicle = db.get_or_404(Vehicle, vehicle_id)
    return jsonify(serialize_vehicle(vehicle))


@api_bp.route('/provider/vehicles', methods=['GET'])
def provider_vehicles():
    """Listet alle Vehicle des authentifizierten Anbieters auf."""
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'provider':
        return jsonify({'error': 'forbidden – nur für Anbieter'}), 403
    own = Vehicle.query.filter_by(provider_id=user.id).order_by(Vehicle.id.asc()).all()
    return jsonify([serialize_vehicle(v) for v in own])


@api_bp.route('/rentals', methods=['GET'])
def rentals():
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    if user.role == 'provider':
        rentals = Rental.query.join(Vehicle).filter(Vehicle.provider_id == user.id).all()
    else:
        rentals = Rental.query.filter_by(rider_id=user.id).all()
    return jsonify([serialize_rental(r) for r in rentals])


@api_bp.route('/rentals/start/<int:vehicle_id>', methods=['POST'])
def rentals_start(vehicle_id):
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    vehicle = db.get_or_404(Vehicle, vehicle_id)
    data = request.get_json(silent=True) or {}
    unlock_code = data.get('unlock_code', '').strip()
    try:
        rental = start_rental(user, vehicle, unlock_code=unlock_code)
        return jsonify({'message': 'rental_started', 'rental': serialize_rental(rental)}), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@api_bp.route('/rentals/end/<int:rental_id>', methods=['POST'])
def rentals_end(rental_id):
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    rental = db.get_or_404(Rental, rental_id)
    if rental.rider_id != user.id:
        return jsonify({'error': 'forbidden'}), 403

    data = request.get_json(silent=True) or {}
    try:
        updated = end_rental(
            rental,
            end_km=float(data.get('end_km', rental.start_km)),
            latitude=float(data.get('latitude', rental.start_latitude)),
            longitude=float(data.get('longitude', rental.start_longitude)),
        )
        return jsonify({'message': 'rental_completed', 'rental': serialize_rental(updated)})
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400
