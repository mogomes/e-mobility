from datetime import timedelta

from .extensions import db
from .models import Rental, RentalStatus, Scooter, ScooterStatus, User, UserRole, utcnow

BERN_SCOOTERS = [
    {
        'public_id': 'SC-3001',
        'name': 'Bahnhof Bern',
        'battery_level': 94,
        'latitude': 46.948799,
        'longitude': 7.439136,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3001',
    },
    {
        'public_id': 'SC-3002',
        'name': 'Bundesplatz',
        'battery_level': 88,
        'latitude': 46.947974,
        'longitude': 7.443131,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3002',
    },
    {
        'public_id': 'SC-3003',
        'name': 'Zytglogge',
        'battery_level': 81,
        'latitude': 46.948271,
        'longitude': 7.447599,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3003',
    },
    {
        'public_id': 'SC-3004',
        'name': 'Bärengraben',
        'battery_level': 76,
        'latitude': 46.947357,
        'longitude': 7.458099,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3004',
    },
    {
        'public_id': 'SC-3005',
        'name': 'Rosengarten',
        'battery_level': 69,
        'latitude': 46.955118,
        'longitude': 7.460742,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3005',
    },
    {
        'public_id': 'SC-3006',
        'name': 'Marzili',
        'battery_level': 91,
        'latitude': 46.944328,
        'longitude': 7.442301,
        'status': ScooterStatus.AVAILABLE.value,
        'unlock_code': 'QR-3006',
    },
]

HISTORIC_ROUTE = {
    'start_latitude': 46.948799,
    'start_longitude': 7.439136,
    'end_latitude': 46.947974,
    'end_longitude': 7.443131,
}


def seed_demo_data() -> None:
    provider = User.query.filter_by(username='provider1').first()
    if provider is None:
        provider = User(
            username='provider1',
            email='provider@example.com',
            role=UserRole.PROVIDER.value,
        )
        provider.set_password('Provider123!')
        db.session.add(provider)
        db.session.flush()

    rider = User.query.filter_by(username='rider1').first()
    if rider is None:
        rider = User(
            username='rider1',
            email='rider@example.com',
            role=UserRole.RIDER.value,
            payment_method='Visa **** 4242',
        )
        rider.set_password('Rider123!')
        db.session.add(rider)
        db.session.flush()
    elif not rider.payment_method:
        rider.payment_method = 'Visa **** 4242'

    _ensure_bern_scooters(provider.id)
    _relocate_legacy_scooters_to_bern(provider.id)
    db.session.flush()

    if Rental.query.count() == 0:
        first_scooter = Scooter.query.filter_by(public_id='SC-3001').first() or Scooter.query.order_by(Scooter.id.asc()).first()
        if first_scooter is not None:
            historic_rental = Rental(
                scooter_id=first_scooter.id,
                rider_id=rider.id,
                start_time=utcnow() - timedelta(minutes=24),
                end_time=utcnow() - timedelta(minutes=8),
                start_km=12.50,
                end_km=16.30,
                start_latitude=HISTORIC_ROUTE['start_latitude'],
                start_longitude=HISTORIC_ROUTE['start_longitude'],
                end_latitude=HISTORIC_ROUTE['end_latitude'],
                end_longitude=HISTORIC_ROUTE['end_longitude'],
                status=RentalStatus.COMPLETED.value,
            )
            historic_rental.total_price = historic_rental.calculate_total_price()
            historic_rental.distance_km = historic_rental.calculate_distance()
            db.session.add(historic_rental)

    db.session.commit()


def _ensure_bern_scooters(provider_id: int) -> None:
    for scooter_data in BERN_SCOOTERS:
        scooter = Scooter.query.filter_by(public_id=scooter_data['public_id']).first()
        if scooter is None:
            scooter = Scooter(provider_id=provider_id, **scooter_data)
            db.session.add(scooter)
            continue

        scooter.name = scooter_data['name']
        scooter.battery_level = scooter_data['battery_level']
        scooter.latitude = scooter_data['latitude']
        scooter.longitude = scooter_data['longitude']
        scooter.unlock_code = scooter_data['unlock_code']
        scooter.provider_id = provider_id
        if scooter.status != ScooterStatus.RENTED.value:
            scooter.status = scooter_data['status']




def _relocate_legacy_scooters_to_bern(provider_id: int) -> None:
    bern_positions = [(item['latitude'], item['longitude']) for item in BERN_SCOOTERS]
    legacy_scooters = Scooter.query.filter(~Scooter.public_id.in_([item['public_id'] for item in BERN_SCOOTERS])).order_by(Scooter.id.asc()).all()
    for index, scooter in enumerate(legacy_scooters):
        latitude, longitude = bern_positions[index % len(bern_positions)]
        # Frühere Standarddaten aus Zürich konsequent auf Bern umstellen.
        scooter.latitude = latitude
        scooter.longitude = longitude
        scooter.provider_id = provider_id
        if scooter.status != ScooterStatus.RENTED.value:
            scooter.status = ScooterStatus.AVAILABLE.value

def start_rental(user: User, scooter: Scooter) -> Rental:
    if user.role != UserRole.RIDER.value:
        raise ValueError('Nur Fahrgäste dürfen Fahrzeuge ausleihen.')
    if not user.payment_method:
        raise ValueError('Bitte zuerst ein Zahlungsmittel hinterlegen.')
    if scooter.status != ScooterStatus.AVAILABLE.value:
        raise ValueError('Roller ist derzeit nicht verfügbar.')
    active_rental = Rental.query.filter_by(rider_id=user.id, status=RentalStatus.ACTIVE.value).first()
    if active_rental:
        raise ValueError('Es existiert bereits eine aktive Ausleihe.')

    rental = Rental(
        scooter_id=scooter.id,
        rider_id=user.id,
        start_km=0,
        start_latitude=scooter.latitude,
        start_longitude=scooter.longitude,
    )
    scooter.status = ScooterStatus.RENTED.value
    db.session.add(rental)
    db.session.commit()
    return rental



def end_rental(rental: Rental, end_km: float, latitude: float, longitude: float) -> Rental:
    if rental.status != RentalStatus.ACTIVE.value:
        raise ValueError('Ausleihe ist bereits beendet.')
    if end_km < float(rental.start_km):
        raise ValueError('Der Endkilometerstand darf nicht kleiner als der Startkilometerstand sein.')
    if not (-90 <= latitude <= 90):
        raise ValueError('Ungültiger Breitengrad.')
    if not (-180 <= longitude <= 180):
        raise ValueError('Ungültiger Längengrad.')

    rental.end_time = utcnow()
    rental.end_km = end_km
    rental.end_latitude = latitude
    rental.end_longitude = longitude
    rental.status = RentalStatus.COMPLETED.value
    rental.total_price = rental.calculate_total_price()
    rental.distance_km = rental.calculate_distance()

    rental.scooter.latitude = latitude
    rental.scooter.longitude = longitude
    rental.scooter.status = ScooterStatus.AVAILABLE.value

    db.session.commit()
    return rental
