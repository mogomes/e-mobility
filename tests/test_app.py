from app.extensions import db
from app.models import Rental, Scooter, User


def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_smoke():
    assert 1 == 1


def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'E-Scooter' in response.data


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


def test_provider_can_create_scooter(client, provider_credentials, app):
    login(client, provider_credentials['username'], provider_credentials['password'])
    response = client.post(
        '/providers/scooters',
        data={
            'public_id': 'SC-9999',
            'name': 'Test Scooter',
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
        assert Scooter.query.filter_by(public_id='SC-9999').first() is not None


def test_rider_can_start_and_end_rental(client, rider_credentials, app):
    login(client, rider_credentials['username'], rider_credentials['password'])
    with app.app_context():
        scooter = Scooter.query.filter_by(status='available').first()
    start_response = client.post(f'/rentals/start/{scooter.id}', follow_redirects=True)
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


def test_api_token_and_scooter_list(client, rider_credentials):
    token_response = client.post('/api/token', json=rider_credentials)
    assert token_response.status_code == 200
    token = token_response.get_json()['token']

    scooters_response = client.get('/api/scooters')
    assert scooters_response.status_code == 200
    assert isinstance(scooters_response.get_json(), list)

    rentals_response = client.get('/api/rentals', headers={'Authorization': f'Bearer {token}'})
    assert rentals_response.status_code == 200
    assert isinstance(rentals_response.get_json(), list)


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
