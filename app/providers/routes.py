import secrets

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Scooter, ScooterStatus, UserRole


providers_bp = Blueprint('providers', __name__)

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


def ensure_provider():
    if not current_user.is_authenticated or current_user.role != UserRole.PROVIDER.value:
        abort(403)


@providers_bp.route('/scooters', methods=['GET', 'POST'])
@login_required
def scooters():
    ensure_provider()

    if request.method == 'POST':
        scooter = Scooter(
            public_id=request.form.get('public_id', '').strip() or f'BE-{secrets.randbelow(9999):04d}',
            name=request.form.get('name', '').strip(),
            battery_level=int(request.form.get('battery_level', 100)),
            latitude=float(request.form.get('latitude', 46.94809)),
            longitude=float(request.form.get('longitude', 7.44744)),
            status=request.form.get('status', ScooterStatus.AVAILABLE.value),
            unlock_code=request.form.get('unlock_code', '').strip() or secrets.token_hex(4).upper(),
            provider_id=current_user.id,
        )
        db.session.add(scooter)
        db.session.commit()
        flash('Roller wurde erstellt.', 'success')
        return redirect(url_for('providers.scooters'))

    scooters = Scooter.query.filter_by(provider_id=current_user.id).order_by(Scooter.id.desc()).all()
    return render_template('providers/scooters.html', scooters=scooters, scooter_status=ScooterStatus, map_scooters=[serialize_scooter_map(s) for s in scooters])


@providers_bp.route('/scooters/<int:scooter_id>/update', methods=['POST'])
@login_required
def update_scooter(scooter_id):
    ensure_provider()
    scooter = Scooter.query.filter_by(id=scooter_id, provider_id=current_user.id).first_or_404()
    scooter.name = request.form.get('name', scooter.name).strip()
    scooter.battery_level = int(request.form.get('battery_level', scooter.battery_level))
    scooter.latitude = float(request.form.get('latitude', scooter.latitude))
    scooter.longitude = float(request.form.get('longitude', scooter.longitude))
    scooter.status = request.form.get('status', scooter.status)
    db.session.commit()
    flash('Roller wurde aktualisiert.', 'success')
    return redirect(url_for('providers.scooters'))


@providers_bp.route('/scooters/<int:scooter_id>/delete', methods=['POST'])
@login_required
def delete_scooter(scooter_id):
    ensure_provider()
    scooter = Scooter.query.filter_by(id=scooter_id, provider_id=current_user.id).first_or_404()
    db.session.delete(scooter)
    db.session.commit()
    flash('Roller wurde gelöscht.', 'info')
    return redirect(url_for('providers.scooters'))
