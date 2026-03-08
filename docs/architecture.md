# Architektur und Lösungsansatz

## Anforderungen

- Interaktive Weboberfläche
- Registrierung mit eindeutigem Benutzername und E-Mail
- Passwortgeschützte Benutzerkonten
- Relationale Datenbank mit PostgreSQL
- Eigene Geschäftslogik für Ausleihe, Rückgabe und Preisberechnung
- RESTful API für ausgewählte Daten ohne Browser
- Deployment über Linux/Gunicorn, optional Nginx

## Gewählte Domäne

Es wurde die Normaufgabe umgesetzt: eine Plattform zum Verleih von E-Scootern.

## Architekturprinzip

Die Anwendung verwendet eine klassische 3-Schichten-Struktur:

1. Präsentation: HTML-Templates und Browser-Interaktion
2. Applikation: Flask-Blueprints und Service-Layer für Geschäftslogik
3. Datenhaltung: PostgreSQL mit relationalem Schema

## Flask-Module

- `main`: Startseite und Dashboard
- `auth`: Registrierung, Login, Logout
- `providers`: Verwaltung der Scooter-Flotte
- `rentals`: Start und Ende von Ausleihen
- `api`: REST-Endpunkte und Token-Authentifizierung

## Datenmodell (ERD in Textform)

```mermaid
erDiagram
    USER ||--o{ SCOOTER : provides
    USER ||--o{ RENTAL : books
    SCOOTER ||--o{ RENTAL : used_in

    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        string payment_method
        string api_token UK
    }

    SCOOTER {
        int id PK
        string public_id UK
        string name
        int battery_level
        decimal latitude
        decimal longitude
        string status
        string unlock_code
        int provider_id FK
    }

    RENTAL {
        int id PK
        int scooter_id FK
        int rider_id FK
        datetime start_time
        datetime end_time
        decimal start_km
        decimal end_km
        decimal total_price
        decimal distance_km
        string status
    }
```

## Wichtige Abläufe

### Registrierung

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Flask
    participant DB
    User->>Browser: Registrierungsformular senden
    Browser->>Flask: POST /auth/register
    Flask->>DB: Prüfen auf eindeutigen Username/E-Mail
    DB-->>Flask: Ergebnis
    Flask->>DB: Neuen User speichern
    DB-->>Flask: OK
    Flask-->>Browser: Redirect auf Login
```

### Scooter ausleihen

```mermaid
sequenceDiagram
    actor Rider
    participant BrowserOrAPI as Browser/API
    participant Flask as Flask Service Layer
    participant DB
    Rider->>BrowserOrAPI: QR-Code scannen + Ausleihe starten
    BrowserOrAPI->>Flask: POST /rentals/start/<id> {unlock_code}
    Flask->>DB: Verfügbarkeit Scooter prüfen
    Flask->>DB: Unlock-Code gegen Scooter.unlock_code validieren
    Flask->>DB: Prüfen aktive Ausleihe / Zahlungsmittel
    Flask->>DB: Rental anlegen, Scooter auf rented setzen
    DB-->>Flask: OK
    Flask-->>BrowserOrAPI: Erfolgsmeldung (201)
```

### Rückgabe und Verrechnung

```mermaid
flowchart TD
    A[Rental aktiv] --> B[Enddaten empfangen]
    B --> C[Dauer berechnen]
    C --> D[Preis berechnen]
    D --> E[Distanz berechnen]
    E --> F[Scooter Standort aktualisieren]
    F --> G[Status auf available setzen]
    G --> H[Rental abschliessen]
```

## Deployment / Bereitstellung

```mermaid
flowchart LR
    UserBrowser[Browser oder API Client] --> Nginx[Nginx optional]
    Nginx --> Gunicorn[Gunicorn / Flask App]
    Gunicorn --> PostgreSQL[(PostgreSQL)]
```

## Begründung der Architektur

### Vorteile

- Gute Wartbarkeit durch Blueprints und klar getrennte Verantwortlichkeiten
- Relationales Modell passt gut zu User, Scooter und Rentals
- PostgreSQL ist robust, verbreitet und produktionsgeeignet
- Gunicorn + optional Nginx ist ein üblicher Linux-Stack
- API-Token erlaubt Zugriff ohne Browser und erfüllt die Vorgabe

### Nachteile

- Session-Login und API-Token sind zwei Authentifizierungswege und erhöhen die Komplexität leicht
- Kein asynchrones Processing; für sehr hohe Last wären zusätzliche Optimierungen nötig
- `db.create_all()` ist für Lernprojekte akzeptabel, für harte Produktion wären Migrationen strikter zu verwenden

## Skalierbarkeit, Wartbarkeit, Verfügbarkeit

- **Wartbarkeit:** Modularisierung, Service-Layer, Tests
- **Skalierbarkeit:** Mehrere Gunicorn-Worker, Trennung von Web und DB, Containerisierung
- **Verfügbarkeit:** systemd Restart, Docker Restart Policy, Reverse Proxy, Backups, Monitoring
