from __future__ import annotations

import secrets
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def normalize_utc_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


class UserRole(str, Enum):
    RIDER = 'rider'
    PROVIDER = 'provider'


class VehicleType(str, Enum):
    E_SCOOTER = 'e_scooter'
    E_BIKE = 'e_bike'
    E_CARGO = 'e_cargo'


class VehicleStatus(str, Enum):
    AVAILABLE = 'available'
    RENTED = 'rented'
    MAINTENANCE = 'maintenance'


class RentalStatus(str, Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.RIDER.value)
    payment_method = db.Column(db.String(120), nullable=True)
    api_token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_hex(24))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    provider_vehicles = db.relationship('Vehicle', back_populates='provider', lazy=True)
    rentals = db.relationship('Rental', back_populates='rider', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def regenerate_api_token(self) -> str:
        self.api_token = secrets.token_hex(24)
        return self.api_token


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    battery_level = db.Column(db.Integer, nullable=False, default=100)
    latitude = db.Column(db.Numeric(9, 6), nullable=False)
    longitude = db.Column(db.Numeric(9, 6), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False, default=VehicleType.E_SCOOTER.value)
    status = db.Column(db.String(20), nullable=False, default=VehicleStatus.AVAILABLE.value)
    unlock_code = db.Column(db.String(32), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    provider = db.relationship('User', back_populates='provider_vehicles')
    rentals = db.relationship('Rental', back_populates='vehicle', lazy=True)


class Rental(db.Model):
    __tablename__ = 'rentals'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    start_km = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    end_km = db.Column(db.Numeric(10, 2), nullable=True)
    start_latitude = db.Column(db.Numeric(9, 6), nullable=False)
    start_longitude = db.Column(db.Numeric(9, 6), nullable=False)
    end_latitude = db.Column(db.Numeric(9, 6), nullable=True)
    end_longitude = db.Column(db.Numeric(9, 6), nullable=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('1.50'))
    price_per_minute = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.35'))
    total_price = db.Column(db.Numeric(10, 2), nullable=True)
    distance_km = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=RentalStatus.ACTIVE.value)

    vehicle = db.relationship('Vehicle', back_populates='rentals')
    rider = db.relationship('User', back_populates='rentals')

    def duration_minutes(self) -> int:
        start = normalize_utc_datetime(self.start_time) or utcnow()
        end = normalize_utc_datetime(self.end_time) or utcnow()
        delta = end - start
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 1)

    def calculate_total_price(self) -> Decimal:
        base_price = self.base_price if self.base_price is not None else Decimal('1.50')
        price_per_minute = self.price_per_minute if self.price_per_minute is not None else Decimal('0.35')
        total = Decimal(str(base_price)) + (Decimal(str(price_per_minute)) * self.duration_minutes())
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def calculate_distance(self) -> Decimal:
        if self.end_km is None:
            return Decimal('0.00')
        distance = Decimal(str(self.end_km)) - Decimal(str(self.start_km))
        if distance < 0:
            distance = Decimal('0.00')
        return distance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
