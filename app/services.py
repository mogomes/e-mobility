from datetime import timedelta

from .extensions import db
from .models import Rental, RentalStatus, Vehicle, VehicleStatus, User, UserRole, VehicleType, utcnow

BERN_VEHICLES = [
    {
        'public_id': 'BE-3001',
        'name': 'Bahnhof Bern',
        'battery_level': 94,
        'latitude': 46.948799,
        'longitude': 7.439136,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3001',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3002',
        'name': 'Bundesplatz',
        'battery_level': 88,
        'latitude': 46.947974,
        'longitude': 7.443131,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3002',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3003',
        'name': 'Zytglogge',
        'battery_level': 81,
        'latitude': 46.948271,
        'longitude': 7.447599,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3003',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3004',
        'name': 'Bärengraben',
        'battery_level': 76,
        'latitude': 46.947357,
        'longitude': 7.458099,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3004',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3005',
        'name': 'Rosengarten',
        'battery_level': 69,
        'latitude': 46.955118,
        'longitude': 7.460742,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3005',
        'vehicle_type': VehicleType.E_CARGO.value,
    },
    {
        'public_id': 'BE-3006',
        'name': 'Marzili',
        'battery_level': 91,
        'latitude': 46.944328,
        'longitude': 7.442301,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3006',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3007',
        'name': 'Kornhausplatz',
        'battery_level': 73,
        'latitude': 46.951290,
        'longitude': 7.443870,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3007',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3008',
        'name': 'Münster',
        'battery_level': 55,
        'latitude': 46.946980,
        'longitude': 7.450620,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3008',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3009',
        'name': 'Helvetiaplatz',
        'battery_level': 82,
        'latitude': 46.943150,
        'longitude': 7.435870,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3009',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3010',
        'name': 'Waisenhausplatz',
        'battery_level': 65,
        'latitude': 46.950340,
        'longitude': 7.445010,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3010',
        'vehicle_type': VehicleType.E_CARGO.value,
    },
    {
        'public_id': 'BE-3011',
        'name': 'Breitenrain',
        'battery_level': 78,
        'latitude': 46.957620,
        'longitude': 7.447390,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3011',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3012',
        'name': 'Länggasse',
        'battery_level': 90,
        'latitude': 46.952810,
        'longitude': 7.431540,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3012',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3013',
        'name': 'Bremgartenwald',
        'battery_level': 47,
        'latitude': 46.950460,
        'longitude': 7.414220,
        'status': VehicleStatus.MAINTENANCE.value,
        'unlock_code': 'QR-3013',
        'vehicle_type': VehicleType.E_CARGO.value,
    },
    {
        'public_id': 'BE-3014',
        'name': 'Burgernziel',
        'battery_level': 86,
        'latitude': 46.941780,
        'longitude': 7.466540,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3014',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3015',
        'name': 'Viktoriapark',
        'battery_level': 61,
        'latitude': 46.953900,
        'longitude': 7.437580,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3015',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3016',
        'name': 'Köniz Dorf',
        'battery_level': 72,
        'latitude': 46.924610,
        'longitude': 7.411350,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3016',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3017',
        'name': 'Ostermundigen Zentrum',
        'battery_level': 84,
        'latitude': 46.951230,
        'longitude': 7.481940,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3017',
        'vehicle_type': VehicleType.E_BIKE.value,
    },
    {
        'public_id': 'BE-3018',
        'name': 'Bümpliz Bahnhof',
        'battery_level': 33,
        'latitude': 46.943050,
        'longitude': 7.393710,
        'status': VehicleStatus.MAINTENANCE.value,
        'unlock_code': 'QR-3018',
        'vehicle_type': VehicleType.E_SCOOTER.value,
    },
    {
        'public_id': 'BE-3019',
        'name': 'Weissenbühl',
        'battery_level': 95,
        'latitude': 46.937420,
        'longitude': 7.438860,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3019',
        'vehicle_type': VehicleType.E_CARGO.value,
    },
    {
        'public_id': 'BE-3020',
        'name': 'Universität Bern',
        'battery_level': 79,
        'latitude': 46.950680,
        'longitude': 7.438260,
        'status': VehicleStatus.AVAILABLE.value,
        'unlock_code': 'QR-3020',
        'vehicle_type': VehicleType.E_BIKE.value,
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

    _ensure_bern_vehicles(provider.id)
    db.session.flush()

    if Rental.query.count() == 0:
        first_vehicle = Vehicle.query.filter_by(public_id='BE-3001').first() or Vehicle.query.order_by(Vehicle.id.asc()).first()
        if first_vehicle is not None:
            historic_rental = Rental(
                vehicle_id=first_vehicle.id,
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


def _ensure_bern_vehicles(provider_id: int) -> None:
    # Alle bestehenden Ausleihen und Fahrzeuge löschen und neu anlegen
    Rental.query.delete()
    Vehicle.query.delete()
    db.session.flush()

    for vehicle_data in BERN_VEHICLES:
        vehicle = Vehicle(provider_id=provider_id, **vehicle_data)
        db.session.add(vehicle)




def _relocate_legacy_vehicles_to_bern(provider_id: int) -> None:
    bern_positions = [(item['latitude'], item['longitude']) for item in BERN_VEHICLES]
    legacy_vehicles = Vehicle.query.filter(~Vehicle.public_id.in_([item['public_id'] for item in BERN_VEHICLES])).order_by(Vehicle.id.asc()).all()
    for index, vehicle in enumerate(legacy_vehicles):
        latitude, longitude = bern_positions[index % len(bern_positions)]
        # Frühere Standarddaten aus Zürich konsequent auf Bern umstellen.
        vehicle.latitude = latitude
        vehicle.longitude = longitude
        vehicle.provider_id = provider_id
        if vehicle.status != VehicleStatus.RENTED.value:
            vehicle.status = VehicleStatus.AVAILABLE.value

MIN_BATTERY_LEVEL = 10  # Mindest-Akkustand in % für eine Ausleihe


def start_rental(user: User, vehicle: Vehicle, unlock_code: str | None = None) -> Rental:
    if user.role != UserRole.RIDER.value:
        raise ValueError('Nur Fahrgäste dürfen Fahrzeuge ausleihen.')
    if not user.payment_method:
        raise ValueError('Bitte zuerst ein Zahlungsmittel hinterlegen.')
    if vehicle.status != VehicleStatus.AVAILABLE.value:
        raise ValueError('Fahrzeug ist derzeit nicht verfügbar.')
    if vehicle.battery_level < MIN_BATTERY_LEVEL:
        raise ValueError(f'Akkustand zu niedrig ({vehicle.battery_level} %). Bitte ein anderes Fahrzeug wählen.')
    if unlock_code is None or unlock_code.strip() != vehicle.unlock_code:
        raise ValueError('Ungültiger Entriegelungscode (QR-Code). Bitte den Code am Fahrzeug scannen.')
    active_rental = Rental.query.filter_by(rider_id=user.id, status=RentalStatus.ACTIVE.value).first()
    if active_rental:
        raise ValueError('Es existiert bereits eine aktive Ausleihe.')

    rental = Rental(
        vehicle_id=vehicle.id,
        rider_id=user.id,
        start_km=0,
        start_latitude=vehicle.latitude,
        start_longitude=vehicle.longitude,
    )
    vehicle.status = VehicleStatus.RENTED.value
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

    # Akkustand um 2 % pro gefahrenen km senken
    battery_drain = min(int(rental.distance_km * 2), rental.vehicle.battery_level)
    rental.vehicle.battery_level = max(0, rental.vehicle.battery_level - battery_drain)

    rental.vehicle.latitude = latitude
    rental.vehicle.longitude = longitude
    rental.vehicle.status = VehicleStatus.AVAILABLE.value

    db.session.commit()
    return rental
