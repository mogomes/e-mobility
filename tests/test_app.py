from app.extensions import db
from app.models import Rental, Vehicle, User


def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)


# ──────────────────────────────────────────────────────────────────────────────
# Grundlegende Tests
# ──────────────────────────────────────────────────────────────────────────────

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
    response = login(client, 'rider1', 'WrongPassword!')
    assert response.status_code == 200
    assert 'Ungültige Zugangsdaten'.encode('utf-8') in response.data


# ──────────────────────────────────────────────────────────────────────────────
# Passwort-Hashing
# ──────────────────────────────────────────────────────────────────────────────

def test_password_is_hashed_in_db(app):
    with app.app_context():
        user = User.query.filter_by(username='rider1').first()
        assert user.password_hash != 'Rider123!'
        assert user.password_hash.startswith('scrypt:') or user.password_hash.startswith('pbkdf2:')
        assert user.check_password('Rider123!')


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
# API – Token und Authentifizierung
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


def test_api_rentals_requires_auth(client):
    """GET /api/rentals ohne Token liefert HTTP 401."""
    response = client.get('/api/rentals')
    assert response.status_code == 401
    assert response.get_json()['error'] == 'missing_or_invalid_token'
