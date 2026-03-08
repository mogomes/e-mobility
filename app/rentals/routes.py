from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Rental, Scooter
from ..services import end_rental, start_rental


rentals_bp = Blueprint('rentals', __name__)


@rentals_bp.route('/start/<int:scooter_id>', methods=['POST'])
@login_required
def start(scooter_id):
    scooter = db.get_or_404(Scooter, scooter_id)
    unlock_code = request.form.get('unlock_code', '').strip()
    try:
        start_rental(current_user, scooter, unlock_code=unlock_code)
        flash('Scooter erfolgreich entriegelt und Ausleihe gestartet.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('main.dashboard'))


@rentals_bp.route('/end/<int:rental_id>', methods=['POST'])
@login_required
def end(rental_id):
    rental = db.get_or_404(Rental, rental_id)
    if rental.rider_id != current_user.id:
        flash('Keine Berechtigung für diese Ausleihe.', 'danger')
        return redirect(url_for('main.dashboard'))

    try:
        end_rental(
            rental,
            end_km=float(request.form.get('end_km', rental.start_km)),
            latitude=float(request.form.get('latitude', rental.start_latitude)),
            longitude=float(request.form.get('longitude', rental.start_longitude)),
        )
        flash('Ausleihe beendet und verrechnet.', 'success')
    except ValueError as exc:
        flash(str(exc), 'danger')
    return redirect(url_for('main.dashboard'))
