from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from ..extensions import db
from ..models import User, UserRole


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', UserRole.RIDER.value)
        payment_method = request.form.get('payment_method', '').strip() or None

        if not username or not email or not password:
            flash('Bitte alle Pflichtfelder ausfüllen.', 'danger')
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Benutzername oder E-Mail existiert bereits.', 'danger')
        else:
            user = User(
                username=username,
                email=email,
                role=role if role in {UserRole.RIDER.value, UserRole.PROVIDER.value} else UserRole.RIDER.value,
                payment_method=payment_method,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registrierung erfolgreich. Bitte anmelden.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', user_role=UserRole)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login erfolgreich.', 'success')
            return redirect(url_for('main.dashboard'))

        flash('Ungültige Zugangsdaten.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('main.index'))
