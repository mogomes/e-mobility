import secrets

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import User, Vehicle, VehicleStatus, UserRole, VehicleType, Rental


providers_bp = Blueprint('providers', __name__)

def serialize_vehicle_map(scooter: Vehicle) -> dict:
    return {
        'id': scooter.id,
        'name': scooter.name,
        'public_id': scooter.public_id,
        'latitude': float(scooter.latitude),
        'longitude': float(scooter.longitude),
        'status': scooter.status,
        'battery_level': scooter.battery_level,
        'vehicle_type': scooter.vehicle_type,
    }


def ensure_provider():
    if not current_user.is_authenticated or current_user.role != UserRole.PROVIDER.value:
        abort(403)


@providers_bp.route('/vehicles', methods=['GET', 'POST'])
@login_required
def vehicles():
    ensure_provider()

    if request.method == 'POST':
        vehicle = Vehicle(
            public_id=request.form.get('public_id', '').strip() or f'BE-{secrets.randbelow(9999):04d}',
            name=request.form.get('name', '').strip(),
            battery_level=int(request.form.get('battery_level', 100)),
            latitude=float(request.form.get('latitude', 46.94809)),
            longitude=float(request.form.get('longitude', 7.44744)),
            vehicle_type=request.form.get('vehicle_type', VehicleType.E_SCOOTER.value),
            status=request.form.get('status', VehicleStatus.AVAILABLE.value),
            unlock_code=request.form.get('unlock_code', '').strip() or secrets.token_hex(4).upper(),
            provider_id=current_user.id,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Fahrzeug wurde erstellt.', 'success')
        return redirect(url_for('providers.vehicles'))

    vehicles = Vehicle.query.filter_by(provider_id=current_user.id).order_by(Vehicle.id.desc()).all()
    return render_template('providers/vehicles.html', scooters=vehicles, scooter_status=VehicleStatus, vehicle_type=VehicleType, map_scooters=[serialize_vehicle_map(v) for v in vehicles])


@providers_bp.route('/vehicles/<int:vehicle_id>/update', methods=['POST'])
@login_required
def update_vehicle(vehicle_id):
    ensure_provider()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, provider_id=current_user.id).first_or_404()
    vehicle.name = request.form.get('name', vehicle.name).strip()
    vehicle.battery_level = int(request.form.get('battery_level', vehicle.battery_level))
    vehicle.latitude = float(request.form.get('latitude', vehicle.latitude))
    vehicle.longitude = float(request.form.get('longitude', vehicle.longitude))
    vehicle.vehicle_type = request.form.get('vehicle_type', vehicle.vehicle_type)
    vehicle.status = request.form.get('status', vehicle.status)
    db.session.commit()
    flash('Fahrzeug wurde aktualisiert.', 'success')
    return redirect(url_for('providers.vehicles'))


@providers_bp.route('/vehicles/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    ensure_provider()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, provider_id=current_user.id).first_or_404()
    db.session.delete(vehicle)
    db.session.commit()
    flash('Fahrzeug wurde gelöscht.', 'info')
    return redirect(url_for('providers.vehicles'))


@providers_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    ensure_provider()
    rentals = (
        Rental.query
        .join(Vehicle)
        .filter(Vehicle.provider_id == current_user.id)
        .order_by(Rental.id.desc())
        .all()
    )
    return render_template('providers/profile.html', rentals=rentals)


@providers_bp.route('/profile/username', methods=['POST'])
@login_required
def update_username():
    ensure_provider()
    username = request.form.get('username', '').strip()
    if not username:
        flash('Benutzername darf nicht leer sein.', 'danger')
        return redirect(url_for('providers.profile'))
    if len(username) < 3:
        flash('Benutzername muss mindestens 3 Zeichen lang sein.', 'danger')
        return redirect(url_for('providers.profile'))
    existing = User.query.filter(User.username == username, User.id != current_user.id).first()
    if existing:
        flash('Dieser Benutzername ist bereits vergeben.', 'danger')
        return redirect(url_for('providers.profile'))
    current_user.username = username
    db.session.commit()
    flash('Benutzername erfolgreich geändert.', 'success')
    return redirect(url_for('providers.profile'))


@providers_bp.route('/profile/password', methods=['POST'])
@login_required
def update_password():
    ensure_provider()
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        flash('Aktuelles Passwort ist falsch.', 'danger')
        return redirect(url_for('providers.profile'))
    if len(new_pw) < 8:
        flash('Das neue Passwort muss mindestens 8 Zeichen lang sein.', 'danger')
        return redirect(url_for('providers.profile'))
    if new_pw != confirm_pw:
        flash('Die neuen Passwörter stimmen nicht überein.', 'danger')
        return redirect(url_for('providers.profile'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Passwort erfolgreich geändert.', 'success')
    return redirect(url_for('providers.profile'))
