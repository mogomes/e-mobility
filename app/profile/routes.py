from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Rental, User


profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/', methods=['GET'])
@login_required
def profile():
    rentals = (
        Rental.query
        .filter_by(rider_id=current_user.id)
        .order_by(Rental.id.desc())
        .all()
    )
    return render_template('profile/profile.html', rentals=rentals)


@profile_bp.route('/payment', methods=['POST'])
@login_required
def update_payment():
    payment_method = request.form.get('payment_method', '').strip() or None
    current_user.payment_method = payment_method
    db.session.commit()
    flash('Zahlungsmittel erfolgreich aktualisiert.', 'success')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/email', methods=['POST'])
@login_required
def update_email():
    email = request.form.get('email', '').strip().lower()
    if not email:
        flash('E-Mail-Adresse darf nicht leer sein.', 'danger')
        return redirect(url_for('profile.profile'))
    existing = User.query.filter(User.email == email, User.id != current_user.id).first()
    if existing:
        flash('Diese E-Mail-Adresse ist bereits vergeben.', 'danger')
        return redirect(url_for('profile.profile'))
    current_user.email = email
    db.session.commit()
    flash('E-Mail-Adresse erfolgreich geändert.', 'success')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/password', methods=['POST'])
@login_required
def update_password():
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        flash('Aktuelles Passwort ist falsch.', 'danger')
        return redirect(url_for('profile.profile'))
    if len(new_pw) < 8:
        flash('Das neue Passwort muss mindestens 8 Zeichen lang sein.', 'danger')
        return redirect(url_for('profile.profile'))
    if new_pw != confirm_pw:
        flash('Die neuen Passwörter stimmen nicht überein.', 'danger')
        return redirect(url_for('profile.profile'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Passwort erfolgreich geändert.', 'success')
    return redirect(url_for('profile.profile'))
