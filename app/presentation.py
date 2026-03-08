from .models import RentalStatus, ScooterStatus, UserRole


def status_label(value: str) -> str:
    mapping = {
        ScooterStatus.AVAILABLE.value: 'Verfügbar',
        ScooterStatus.RENTED.value: 'Ausgeliehen',
        ScooterStatus.MAINTENANCE.value: 'Wartung',
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
