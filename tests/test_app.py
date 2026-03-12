from app.extensions import db
from app.models import Rental, Vehicle, User


def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)


# ──────────────────────────────────────────────────────────────────────────────
# Grundlegende Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_smoke():
    assert 1 == 1


def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'E-Fahrzeuge'.encode('utf-8') in response.data


def test_register_user(client):
    response = client.post(
        '/auth/register',
        data={
            'username': 'newrider',
            'email': 'newrider@example.com',
            'password': 'Secret123!',
            'role': 'rider',
            'payment_method': 'Visa **** 1111',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'Registrierung erfolgreich' in response.data


def test_login_works(client, rider_credentials):
    response = login(client, rider_credentials['username'], rider_credentials['password'])
    assert response.status_code == 200
    assert 'Übersicht'.encode('utf-8') in response.data


def test_login_fails_with_wrong_password(client):
    """Ungültige Zugangsdaten werden korrekt abgelehnt."""
    response = login(client, 'rider1', 'WrongPassword!')
    assert response.status_code == 200
    assert 'Ungültige Zugangsdaten'.encode('utf-8') in response.data


# ──────────────────────────────────────────────────────────────────────────────
# Passwort-Hashing
# ──────────────────────────────────────────────────────────────────────────────

def test_password_is_hashed_in_db(app):
    """Das Passwort darf nicht im Klartext in der Datenbank gespeichert sein."""
    with app.app_context():
        user = User.query.filter_by(username='rider1').first()
        assert user.password_hash != 'Rider123!'
        assert user.password_hash.startswith('scrypt:') or user.password_hash.startswith('pbkdf2:')
        assert user.check_password('Rider123!')


# ──────────────────────────────────────────────────────────────────────────────
# Einzigartigkeits-Constraints (Web)
# ──────────────────────────────────────────────────────────────────────────────

def test_unique_registration_constraints(client, app):
    response = client.post(
        '/auth/register',
        data={
            'username': 'rider1',
            'email': 'rider@example.com',
            'password': 'Secret123!',
            'role': 'rider',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username='rider1').count() == 1


# ──────────────────────────────────────────────────────────────────────────────
# API – Registrierung
# ──────────────────────────────────────────────────────────────────────────────

def test_api_register_success(client):
    """POST /api/register legt einen neuen Benutzer an und gibt Token zurück."""
    response = client.post('/api/register', json={
        'username': 'apiuser1',
        'email': 'apiuser1@example.com',
        'password': 'Secure123!',
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Registrierung erfolgreich.'
    assert 'token' in data


def test_api_register_duplicate_username(client):
    """POST /api/register gibt 409 zurück wenn der Benutzername bereits vergeben ist."""
    response = client.post('/api/register', json={
        'username': 'rider1',
        'email': 'unique@example.com',
        'password': 'Secret123!',
    })
    assert response.status_code == 409
    assert response.get_json()['error'] == 'username_taken'


def test_api_register_duplicate_email(client):
    """POST /api/register gibt 409 zurück wenn die E-Mail bereits vergeben ist."""
    response = client.post('/api/register', json={
        'username': 'uniqueuser',
        'email': 'rider@example.com',
        'password': 'Secret123!',
    })
    assert response.status_code == 409
    assert response.get_json()['error'] == 'email_taken'


def test_api_register_missing_fields(client):
    """POST /api/register gibt 400 zurück wenn Pflichtfelder fehlen."""
    response = client.post('/api/register', json={'username': 'onlyname'})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'missing_fields'


# ──────────────────────────────────────────────────────────────────────────────
# Anbieter – Fahrzeugverwaltung
# ──────────────────────────────────────────────────────────────────────────────

def test_provider_can_create_scooter(client, provider_credentials, app):
    login(client, provider_credentials['username'], provider_credentials['password'])
    response = client.post(
        '/providers/vehicles',
        data={
            'public_id': 'SC-9999',
            'name': 'Test Vehicle',
            'vehicle_type': 'e_scooter',
            'battery_level': 88,
            'latitude': 46.948799,
            'longitude': 7.439136,
            'status': 'available',
            'unlock_code': 'QR-9999',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert Vehicle.query.filter_by(public_id='SC-9999').first() is not None


# ──────────────────────────────────────────────────────────────────────────────
# Ausleihen – Start / Ende / Akkuabbau
# ──────────────────────────────────────────────────────────────────────────────

def test_rider_can_start_and_end_rental(client, rider_credentials, app):
    login(client, rider_credentials['username'], rider_credentials['password'])
    with app.app_context():
        scooter = Vehicle.query.filter_by(status='available').first()
        vehicle_id = scooter.id
        unlock_code = scooter.unlock_code
    start_response = client.post(
        f'/rentals/start/{vehicle_id}',
        data={'unlock_code': unlock_code},
        follow_redirects=True,
    )
    assert start_response.status_code == 200
    with app.app_context():
        rental = Rental.query.filter_by(status='active').first()
        assert rental is not None
    end_response = client.post(
        f'/rentals/end/{rental.id}',
        data={'end_km': 4.2, 'latitude': 46.947974, 'longitude': 7.443131},
        follow_redirects=True,
    )
    assert end_response.status_code == 200
    with app.app_context():
        finished = db.session.get(Rental, rental.id)
        assert finished.status == 'completed'
        assert float(finished.total_price) > 0


def test_battery_drains_after_rental(client, rider_credentials, app):
    """Der Akkustand sinkt nach der Ausleihe um 2 % pro km."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    with app.app_context():
        scooter = Vehicle.query.filter_by(status='available').first()
        vehicle_id = scooter.id
        unlock_code = scooter.unlock_code
        battery_before = scooter.battery_level

    client.post(
        f'/rentals/start/{vehicle_id}',
        data={'unlock_code': unlock_code},
        follow_redirects=True,
    )
    with app.app_context():
        rental = Rental.query.filter_by(status='active').first()

    # 5 km fahren → Akkuabbau sollte 10 % betragen
    client.post(
        f'/rentals/end/{rental.id}',
        data={'end_km': 5.0, 'latitude': 46.947974, 'longitude': 7.443131},
        follow_redirects=True,
    )
    with app.app_context():
        vehicle = db.session.get(Vehicle, vehicle_id)
        expected_drain = min(int(5.0 * 2), battery_before)
        assert vehicle.battery_level == max(0, battery_before - expected_drain)


def test_rental_rejected_when_battery_too_low(client, rider_credentials, app):
    """Ausleihe schlägt fehl wenn der Akkustand unter 10 % liegt."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    with app.app_context():
        scooter = Vehicle.query.filter_by(status='available').first()
        scooter.battery_level = 5
        db.session.commit()
        vehicle_id = scooter.id
        unlock_code = scooter.unlock_code
    response = client.post(
        f'/rentals/start/{vehicle_id}',
        data={'unlock_code': unlock_code},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert Rental.query.filter_by(status='active').count() == 0
    assert 'Akkustand zu niedrig'.encode('utf-8') in response.data


def test_rental_rejected_with_wrong_unlock_code(client, rider_credentials, app):
    """Ausleihe schlägt fehl wenn der Entriegelungscode falsch ist."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    with app.app_context():
        scooter = Vehicle.query.filter_by(status='available').first()
        vehicle_id = scooter.id
    response = client.post(
        f'/rentals/start/{vehicle_id}',
        data={'unlock_code': 'FALSCHER-CODE'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        assert Rental.query.filter_by(status='active').count() == 0


# ──────────────────────────────────────────────────────────────────────────────
# Profil – Fahrgast
# ──────────────────────────────────────────────────────────────────────────────

def test_profile_page_loads(client, rider_credentials):
    """Profil-Seite ist für angemeldete Fahrgäste erreichbar."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.get('/profile/', follow_redirects=True)
    assert response.status_code == 200
    assert b'rider1' in response.data


def test_profile_update_payment(client, rider_credentials, app):
    """Zahlungsmittel kann über das Profil geändert werden."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/payment',
        data={'payment_method': 'Mastercard **** 9876'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='rider1').first()
        assert user.payment_method == 'Mastercard **** 9876'


def test_profile_update_email(client, rider_credentials, app):
    """E-Mail-Adresse kann über das Profil geändert werden."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/email',
        data={'email': 'newemail@example.com'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='rider1').first()
        assert user.email == 'newemail@example.com'


def test_profile_update_email_duplicate_rejected(client, rider_credentials, app):
    """Doppelte E-Mail-Adresse wird beim Ändern abgelehnt."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/email',
        data={'email': 'provider@example.com'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert 'bereits vergeben'.encode('utf-8') in response.data


def test_profile_update_password(client, rider_credentials, app):
    """Passwort kann über das Profil geändert werden."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/password',
        data={
            'current_password': 'Rider123!',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='rider1').first()
        assert user.check_password('NewPass456!')


def test_profile_update_password_wrong_current(client, rider_credentials):
    """Falsches aktuelles Passwort wird abgelehnt."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/password',
        data={
            'current_password': 'WrongPassword!',
            'new_password': 'NewPass456!',
            'confirm_password': 'NewPass456!',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert 'Aktuelles Passwort ist falsch'.encode('utf-8') in response.data


def test_profile_update_password_mismatch(client, rider_credentials):
    """Nicht übereinstimmende neue Passwörter werden abgelehnt."""
    login(client, rider_credentials['username'], rider_credentials['password'])
    response = client.post(
        '/profile/password',
        data={
            'current_password': 'Rider123!',
            'new_password': 'NewPass456!',
            'confirm_password': 'DifferentPass!',
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert 'stimmen nicht'.encode('utf-8') in response.data


# ──────────────────────────────────────────────────────────────────────────────
# API – Token und Fahrzeugliste
# ──────────────────────────────────────────────────────────────────────────────

def test_api_token_and_vehicle_list(client, rider_credentials):
    token_response = client.post('/api/token', json=rider_credentials)
    assert token_response.status_code == 200
    token = token_response.get_json()['token']

    vehicles_response = client.get('/api/vehicles')
    assert vehicles_response.status_code == 200
    assert isinstance(vehicles_response.get_json(), list)

    rentals_response = client.get('/api/rentals', headers={'Authorization': f'Bearer {token}'})
    assert rentals_response.status_code == 200
    assert isinstance(rentals_response.get_json(), list)


def test_api_vehicle_detail(client, app):
    """GET /api/vehicles/<id> liefert Detaildaten eines einzelnen Fahrzeugs inkl. Anbieter."""
    with app.app_context():
        vehicle = Vehicle.query.first()
        vehicle_id = vehicle.id
    response = client.get(f'/api/vehicles/{vehicle_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert 'public_id' in data
    assert 'battery_level' in data
    assert 'provider' in data


def test_api_rentals_requires_auth(client):
    """GET /api/rentals ohne Token liefert HTTP 401."""
    response = client.get('/api/rentals')
    assert response.status_code == 401
    assert response.get_json()['error'] == 'missing_or_invalid_token'


def test_api_invalid_token_rejected(client):
    """Ungültiger Bearer-Token liefert HTTP 401."""
    response = client.get('/api/rentals', headers={'Authorization': 'Bearer ungueltig1234'})
    assert response.status_code == 401


def test_api_invalid_credentials_rejected(client):
    """POST /api/token mit falschem Passwort liefert HTTP 401."""
    response = client.post('/api/token', json={'username': 'rider1', 'password': 'wrong'})
    assert response.status_code == 401
    assert response.get_json()['error'] == 'invalid_credentials'
