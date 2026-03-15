import secrets

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Rental, Vehicle, VehicleStatus, VehicleType, User, UserRole
from ..services import end_rental, start_rental


api_bp = Blueprint('api', __name__)


def serialize_vehicle(vehicle: Vehicle) -> dict:
    return {
        'id': vehicle.id,
        'public_id': vehicle.public_id,
        'name': vehicle.name,
        'vehicle_type': vehicle.vehicle_type,
        'battery_level': vehicle.battery_level,
        'latitude': float(vehicle.latitude),
        'longitude': float(vehicle.longitude),
        'status': vehicle.status,
        'provider': vehicle.provider.username,
    }


def serialize_rental(rental: Rental) -> dict:
    return {
        'id': rental.id,
        'vehicle_id': rental.vehicle_id,
        'rider': rental.rider.username,
        'start_time': rental.start_time.isoformat(),
        'end_time': rental.end_time.isoformat() if rental.end_time else None,
        'status': rental.status,
        'total_price': float(rental.total_price) if rental.total_price is not None else None,
        'distance_km': float(rental.distance_km) if rental.distance_km is not None else None,
    }


def api_user_from_request():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.removeprefix('Bearer ').strip()
        return User.query.filter_by(api_token=token).first()
    return None


@api_bp.route('/register', methods=['POST'])
def api_register():
    """
    Neuen Benutzer registrieren.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: rider42
            email:
              type: string
              example: rider42@example.com
            password:
              type: string
              example: Sicher123!
            role:
              type: string
              enum: [rider, provider]
              default: rider
            payment_method:
              type: string
              example: Kreditkarte
    responses:
      201:
        description: Registrierung erfolgreich
        schema:
          type: object
          properties:
            message:
              type: string
            token:
              type: string
              description: API-Token für weitere Anfragen
            role:
              type: string
      400:
        description: Pflichtfelder fehlen
      409:
        description: Benutzername oder E-Mail bereits vergeben
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', UserRole.RIDER.value)
    payment_method = data.get('payment_method', '') or None

    if not username or not email or not password:
        return jsonify({'error': 'missing_fields', 'message': 'username, email und password sind Pflichtfelder.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'username_taken', 'message': 'Benutzername bereits vergeben.'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email_taken', 'message': 'E-Mail-Adresse bereits vergeben.'}), 409

    if role not in {UserRole.RIDER.value, UserRole.PROVIDER.value}:
        role = UserRole.RIDER.value

    user = User(username=username, email=email, role=role, payment_method=payment_method)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registrierung erfolgreich.', 'token': user.api_token, 'role': user.role}), 201


@api_bp.route('/token', methods=['POST'])
def token():
    """
    API-Token abrufen.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: rider1
            password:
              type: string
              example: Rider123!
    responses:
      200:
        description: Token erfolgreich ausgestellt
        schema:
          type: object
          properties:
            token:
              type: string
            role:
              type: string
      401:
        description: Ungültige Zugangsdaten
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid_credentials'}), 401

    return jsonify({'token': user.api_token, 'role': user.role})


@api_bp.route('/vehicles', methods=['GET'])
def vehicles():
    """
    Alle verfügbaren Fahrzeuge auflisten.
    ---
    tags:
      - Fahrzeuge
    responses:
      200:
        description: Liste aller Fahrzeuge (ohne Wartungsfahrzeuge)
        schema:
          type: array
          items:
            $ref: '#/definitions/Vehicle'
    definitions:
      Vehicle:
        type: object
        properties:
          id:
            type: integer
          public_id:
            type: string
          name:
            type: string
          vehicle_type:
            type: string
            enum: [e_scooter, e_bike, e_cargo]
          battery_level:
            type: integer
            description: Ladestand in Prozent (0-100)
          latitude:
            type: number
          longitude:
            type: number
          status:
            type: string
            enum: [available, rented, maintenance]
          provider:
            type: string
            description: Benutzername des Anbieters
      Rental:
        type: object
        properties:
          id:
            type: integer
          vehicle_id:
            type: integer
          rider:
            type: string
          start_time:
            type: string
            format: date-time
          end_time:
            type: string
            format: date-time
          status:
            type: string
            enum: [active, completed]
          total_price:
            type: number
          distance_km:
            type: number
    """
    all_vehicles = Vehicle.query.filter(Vehicle.status != 'maintenance').order_by(Vehicle.id.asc()).all()
    return jsonify([serialize_vehicle(v) for v in all_vehicles])


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def vehicle_detail(vehicle_id):
    """
    Einzelnes Fahrzeug abrufen.
    ---
    tags:
      - Fahrzeuge
    parameters:
      - name: vehicle_id
        in: path
        required: true
        type: integer
        description: Datenbank-ID des Fahrzeugs
    responses:
      200:
        description: Fahrzeugdetails
        schema:
          $ref: '#/definitions/Vehicle'
      404:
        description: Fahrzeug nicht gefunden
    """
    vehicle = db.get_or_404(Vehicle, vehicle_id)
    return jsonify(serialize_vehicle(vehicle))


@api_bp.route('/provider/vehicles', methods=['GET'])
def provider_vehicles():
    """
    Fahrzeuge des eigenen Anbieters auflisten.
    ---
    tags:
      - Fahrzeuge
    security:
      - Bearer: []
    responses:
      200:
        description: Eigene Fahrzeuge des authentifizierten Anbieters
        schema:
          type: array
          items:
            $ref: '#/definitions/Vehicle'
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Nur für Anbieter (provider) zugänglich
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'provider':
        return jsonify({'error': 'forbidden – nur für Anbieter'}), 403
    own = Vehicle.query.filter_by(provider_id=user.id).order_by(Vehicle.id.asc()).all()
    return jsonify([serialize_vehicle(v) for v in own])


@api_bp.route('/rentals', methods=['GET'])
def rentals():
    """
    Miethistorie abrufen.
    ---
    tags:
      - Mieten
    security:
      - Bearer: []
    description: Rider sehen ihre eigenen Mieten. Provider sehen alle Mieten ihrer Fahrzeuge.
    responses:
      200:
        description: Liste der Mieten
        schema:
          type: array
          items:
            $ref: '#/definitions/Rental'
      401:
        description: Fehlender oder ungültiger Token
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    if user.role == 'provider':
        all_rentals = Rental.query.join(Vehicle).filter(Vehicle.provider_id == user.id).all()
    else:
        all_rentals = Rental.query.filter_by(rider_id=user.id).all()
    return jsonify([serialize_rental(r) for r in all_rentals])


@api_bp.route('/rentals/start/<int:vehicle_id>', methods=['POST'])
def rentals_start(vehicle_id):
    """
    Miete starten.
    ---
    tags:
      - Mieten
    security:
      - Bearer: []
    parameters:
      - name: vehicle_id
        in: path
        required: true
        type: integer
        description: ID des zu mietenden Fahrzeugs
      - in: body
        name: body
        schema:
          type: object
          properties:
            unlock_code:
              type: string
              description: Optionaler Entsperrcode des Fahrzeugs
    responses:
      201:
        description: Miete erfolgreich gestartet
        schema:
          type: object
          properties:
            message:
              type: string
            rental:
              $ref: '#/definitions/Rental'
      400:
        description: Fahrzeug nicht verfügbar oder falscher Code
      401:
        description: Fehlender oder ungültiger Token
      404:
        description: Fahrzeug nicht gefunden
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    vehicle = db.get_or_404(Vehicle, vehicle_id)
    data = request.get_json(silent=True) or {}
    unlock_code = data.get('unlock_code', '').strip()
    try:
        rental = start_rental(user, vehicle, unlock_code=unlock_code)
        return jsonify({'message': 'rental_started', 'rental': serialize_rental(rental)}), 201
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


@api_bp.route('/rentals/end/<int:rental_id>', methods=['POST'])
def rentals_end(rental_id):
    """
    Miete beenden.
    ---
    tags:
      - Mieten
    security:
      - Bearer: []
    parameters:
      - name: rental_id
        in: path
        required: true
        type: integer
        description: ID der aktiven Miete
      - in: body
        name: body
        schema:
          type: object
          properties:
            end_km:
              type: number
              description: Kilometerstand bei Rückgabe
            latitude:
              type: number
              description: GPS-Breitengrad der Rückgabeposition
            longitude:
              type: number
              description: GPS-Längengrad der Rückgabeposition
    responses:
      200:
        description: Miete erfolgreich beendet
        schema:
          type: object
          properties:
            message:
              type: string
            rental:
              $ref: '#/definitions/Rental'
      400:
        description: Miete bereits beendet oder ungültige Daten
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Diese Miete gehört nicht dem authentifizierten Nutzer
      404:
        description: Miete nicht gefunden
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    rental = db.get_or_404(Rental, rental_id)
    if rental.rider_id != user.id:
        return jsonify({'error': 'forbidden'}), 403

    data = request.get_json(silent=True) or {}
    try:
        updated = end_rental(
            rental,
            end_km=float(data.get('end_km', rental.start_km)),
            latitude=float(data.get('latitude', rental.start_latitude)),
            longitude=float(data.get('longitude', rental.start_longitude)),
        )
        return jsonify({'message': 'rental_completed', 'rental': serialize_rental(updated)})
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400


# ---------------------------------------------------------------------------
# Fahrzeug-Verwaltung (Provider)
# ---------------------------------------------------------------------------

@api_bp.route('/vehicles', methods=['POST'])
def create_vehicle():
    """
    Neues Fahrzeug erstellen.
    ---
    tags:
      - Fahrzeuge
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Scooter Bern-01
            public_id:
              type: string
              description: Öffentliche ID (wird automatisch generiert wenn leer)
              example: BE-0042
            battery_level:
              type: integer
              default: 100
            latitude:
              type: number
              default: 46.94809
            longitude:
              type: number
              default: 7.44744
            vehicle_type:
              type: string
              enum: [e_scooter, e_bike, e_cargo]
              default: e_scooter
            status:
              type: string
              enum: [available, rented, maintenance]
              default: available
            unlock_code:
              type: string
              description: Entsperrcode (wird automatisch generiert wenn leer)
    responses:
      201:
        description: Fahrzeug erfolgreich erstellt
        schema:
          $ref: '#/definitions/Vehicle'
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Nur für Anbieter zugänglich
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'provider':
        return jsonify({'error': 'forbidden'}), 403

    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'missing_fields', 'message': 'name ist ein Pflichtfeld.'}), 400

    vehicle = Vehicle(
        public_id=data.get('public_id', '').strip() or f'BE-{secrets.randbelow(9999):04d}',
        name=name,
        battery_level=int(data.get('battery_level', 100)),
        latitude=float(data.get('latitude', 46.94809)),
        longitude=float(data.get('longitude', 7.44744)),
        vehicle_type=data.get('vehicle_type', VehicleType.E_SCOOTER.value),
        status=data.get('status', VehicleStatus.AVAILABLE.value),
        unlock_code=data.get('unlock_code', '').strip() or secrets.token_hex(4).upper(),
        provider_id=user.id,
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify(serialize_vehicle(vehicle)), 201


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    """
    Fahrzeug aktualisieren.
    ---
    tags:
      - Fahrzeuge
    security:
      - Bearer: []
    parameters:
      - name: vehicle_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            battery_level:
              type: integer
            latitude:
              type: number
            longitude:
              type: number
            vehicle_type:
              type: string
              enum: [e_scooter, e_bike, e_cargo]
            status:
              type: string
              enum: [available, rented, maintenance]
    responses:
      200:
        description: Fahrzeug erfolgreich aktualisiert
        schema:
          $ref: '#/definitions/Vehicle'
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Nur für den zugehörigen Anbieter zugänglich
      404:
        description: Fahrzeug nicht gefunden
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'provider':
        return jsonify({'error': 'forbidden'}), 403

    vehicle = Vehicle.query.filter_by(id=vehicle_id, provider_id=user.id).first_or_404()
    data = request.get_json(silent=True) or {}

    if 'name' in data:
        vehicle.name = data['name'].strip()
    if 'battery_level' in data:
        vehicle.battery_level = int(data['battery_level'])
    if 'latitude' in data:
        vehicle.latitude = float(data['latitude'])
    if 'longitude' in data:
        vehicle.longitude = float(data['longitude'])
    if 'vehicle_type' in data:
        vehicle.vehicle_type = data['vehicle_type']
    if 'status' in data:
        vehicle.status = data['status']

    db.session.commit()
    return jsonify(serialize_vehicle(vehicle))


@api_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """
    Fahrzeug löschen.
    ---
    tags:
      - Fahrzeuge
    security:
      - Bearer: []
    parameters:
      - name: vehicle_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Fahrzeug erfolgreich gelöscht
        schema:
          type: object
          properties:
            message:
              type: string
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Nur für den zugehörigen Anbieter zugänglich
      404:
        description: Fahrzeug nicht gefunden
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'provider':
        return jsonify({'error': 'forbidden'}), 403

    vehicle = Vehicle.query.filter_by(id=vehicle_id, provider_id=user.id).first_or_404()
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Fahrzeug wurde gelöscht.'})


# ---------------------------------------------------------------------------
# Profil-Verwaltung (alle Rollen)
# ---------------------------------------------------------------------------

@api_bp.route('/profile/username', methods=['PATCH'])
def update_username():
    """
    Benutzernamen ändern.
    ---
    tags:
      - Profil
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
          properties:
            username:
              type: string
              example: neuerName42
    responses:
      200:
        description: Benutzername erfolgreich geändert
      400:
        description: Ungültiger oder fehlender Benutzername
      401:
        description: Fehlender oder ungültiger Token
      409:
        description: Benutzername bereits vergeben
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    if not username or len(username) < 3:
        return jsonify({'error': 'invalid_username', 'message': 'Benutzername muss mindestens 3 Zeichen lang sein.'}), 400
    if User.query.filter(User.username == username, User.id != user.id).first():
        return jsonify({'error': 'username_taken', 'message': 'Benutzername bereits vergeben.'}), 409

    user.username = username
    db.session.commit()
    return jsonify({'message': 'Benutzername erfolgreich geändert.'})


@api_bp.route('/profile/email', methods=['PATCH'])
def update_email():
    """
    E-Mail-Adresse ändern.
    ---
    tags:
      - Profil
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: neu@example.com
    responses:
      200:
        description: E-Mail erfolgreich geändert
      400:
        description: Fehlende oder leere E-Mail-Adresse
      401:
        description: Fehlender oder ungültiger Token
      409:
        description: E-Mail-Adresse bereits vergeben
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    if not email:
        return jsonify({'error': 'missing_fields', 'message': 'email ist ein Pflichtfeld.'}), 400
    if User.query.filter(User.email == email, User.id != user.id).first():
        return jsonify({'error': 'email_taken', 'message': 'E-Mail-Adresse bereits vergeben.'}), 409

    user.email = email
    db.session.commit()
    return jsonify({'message': 'E-Mail-Adresse erfolgreich geändert.'})


@api_bp.route('/profile/password', methods=['PATCH'])
def update_password():
    """
    Passwort ändern.
    ---
    tags:
      - Profil
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
            new_password:
              type: string
              description: Mindestens 8 Zeichen
    responses:
      200:
        description: Passwort erfolgreich geändert
      400:
        description: Aktuelles Passwort falsch oder neues Passwort zu kurz
      401:
        description: Fehlender oder ungültiger Token
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401

    data = request.get_json(silent=True) or {}
    current_pw = data.get('current_password', '')
    new_pw = data.get('new_password', '')

    if not user.check_password(current_pw):
        return jsonify({'error': 'wrong_password', 'message': 'Aktuelles Passwort ist falsch.'}), 400
    if len(new_pw) < 8:
        return jsonify({'error': 'password_too_short', 'message': 'Das neue Passwort muss mindestens 8 Zeichen lang sein.'}), 400

    user.set_password(new_pw)
    db.session.commit()
    return jsonify({'message': 'Passwort erfolgreich geändert.'})


@api_bp.route('/profile/payment', methods=['PATCH'])
def update_payment():
    """
    Zahlungsmethode ändern (nur Rider).
    ---
    tags:
      - Profil
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            payment_method:
              type: string
              example: Kreditkarte
              description: Leer lassen zum Entfernen der Zahlungsmethode
    responses:
      200:
        description: Zahlungsmethode erfolgreich aktualisiert
      401:
        description: Fehlender oder ungültiger Token
      403:
        description: Nur für Rider zugänglich
    """
    user = api_user_from_request()
    if not user:
        return jsonify({'error': 'missing_or_invalid_token'}), 401
    if user.role != 'rider':
        return jsonify({'error': 'forbidden', 'message': 'Nur für Rider zugänglich.'}), 403

    data = request.get_json(silent=True) or {}
    user.payment_method = data.get('payment_method', '').strip() or None
    db.session.commit()
    return jsonify({'message': 'Zahlungsmethode erfolgreich aktualisiert.'})
