from .models import RentalStatus, VehicleStatus, UserRole, VehicleType


def status_label(value: str) -> str:
    mapping = {
        VehicleStatus.AVAILABLE.value: 'Verfügbar',
        VehicleStatus.RENTED.value: 'Ausgeliehen',
        VehicleStatus.MAINTENANCE.value: 'Wartung',
        RentalStatus.ACTIVE.value: 'Laufend',
        RentalStatus.COMPLETED.value: 'Beendet',
    }
    return mapping.get(value, str(value))


def role_label(value: str) -> str:
    mapping = {
        UserRole.RIDER.value: 'Fahrgast',
        UserRole.PROVIDER.value: 'Anbieter',
    }
    return mapping.get(value, str(value))


def vehicle_type_label(value: str) -> str:
    mapping = {
        VehicleType.E_SCOOTER.value: 'E-Scooter',
        VehicleType.E_BIKE.value: 'E-Bike',
        VehicleType.E_CARGO.value: 'E-Cargo',
    }
    return mapping.get(value, str(value))


def vehicle_type_emoji(value: str) -> str:
    mapping = {
        VehicleType.E_SCOOTER.value: '🛴',
        VehicleType.E_BIKE.value: '🚲',
        VehicleType.E_CARGO.value: '🚐',
    }
    return mapping.get(value, '🛴')
