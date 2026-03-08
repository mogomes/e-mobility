# e-mobility Bern

Webplattform für den Verleih von E-Fahrzeugen in Bern. Entwickelt als Lernprojekt im Rahmen des Moduls DBWE.

## Funktionen

- Benutzerkonten mit den Rollen **Anbieter** (Provider) und **Fahrgast** (Rider)
- E-Fahrzeuge-Verwaltung: Standort, Akkustand, Status
- Ausleihe und Rückgabe mit automatischer Preisberechnung
- Interaktive Kartenansicht (Leaflet.js) mit allen verfügbaren Rollern in Bern
- RESTful API mit Token-Authentifizierung
- Deployment via Docker Compose oder Gunicorn/Nginx auf Linux

## Technologie-Stack

| Schicht | Technologie |
|---------|-------------|
| Backend | Python 3.13, Flask 3.1 |
| ORM / Migrationen | Flask-SQLAlchemy 3.1, Flask-Migrate 4.1 |
| Authentifizierung | Flask-Login 0.6 |
| Datenbank | PostgreSQL (psycopg3) |
| Karte | Leaflet.js |
| Deployment | Gunicorn 23, optional Nginx |
| Tests | pytest 8.3, pytest-flask 1.3 |

## Projektstruktur

```text
app/
  __init__.py          # App-Factory (create_app)
  models.py            # User, Vehicle, Rental + Enums
  services.py          # Geschäftslogik: start_rental, end_rental, seed_demo_data
  extensions.py        # db, migrate, login_manager
  presentation.py      # Jinja-Helpers: status_label, role_label
  api/                 # Blueprint: REST-Endpunkte, Token-Auth
  auth/                # Blueprint: Registrierung, Login, Logout
  main/                # Blueprint: Startseite, Dashboard
  providers/           # Blueprint: Fahrzeug-Flottenverwaltung
  rentals/             # Blueprint: Ausleihe und Rückgabe
  static/              # CSS, JS, SVG-Assets
  templates/           # Jinja2-Templates
db/
  conf/                # postgresql.conf
  init/                # 01-init.sql (Bootstrap für leere DB)
  schema/              # schema.sql, schema.md
deploy/                # Deployment-Skripte und Konfiguration
docs/                  # Architektur, API, Testprotokoll, Handbuch
tests/
  test_app.py          # 12 automatisierte pytest-Tests
```

## Datenmodell

```mermaid
erDiagram
    USER ||--o{ VEHICLE : provides
    USER ||--o{ RENTAL : books
    VEHICLE ||--o{ RENTAL : used_in

    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        string payment_method
        string api_token UK
    }

    VEHICLE {
        int id PK
        string public_id UK
        string name
        string vehicle_type
        int battery_level
        decimal latitude
        decimal longitude
        string status
        string unlock_code
        int provider_id FK
    }

    RENTAL {
        int id PK
        int vehicle_id FK
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

## Umgebungsvariablen

Datei `.env` im Projektwurzelverzeichnis anlegen (Vorlage: `.env.example`):

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=bitte-durch-langen-zufallswert-ersetzen
DATABASE_URL=postgresql+psycopg://escooter:strongpassword@localhost:5432/escooterdb
APP_BASE_URL=http://127.0.0.1:5000
PORT=5000
```

Geheimschlüssel erzeugen:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Start mit Docker (empfohlen)

```bash
docker compose up --build -d
```

Anwendung erreichbar unter `http://localhost:8000`.

Beim ersten Start wird die Datenbank automatisch initialisiert und mit Demo-Daten befüllt.

## Lokaler Start ohne Docker

### 1. PostgreSQL-Datenbank anlegen

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE escooterdb;
CREATE USER escooter WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE escooterdb TO escooter;
```

### 2. Virtuelle Umgebung und Abhängigkeiten

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Umgebungsvariablen setzen

```bash
cp .env.example .env
# .env anpassen (DATABASE_URL auf lokale Instanz zeigen lassen)
```

### 4. Anwendung starten

```bash
flask run
```

Anwendung erreichbar unter `http://127.0.0.1:5000`.

## Start mit Gunicorn auf Linux

```bash
source .venv/bin/activate
gunicorn -b 0.0.0.0:8000 run:app
```

## Demo-Zugänge

| Rolle | Benutzername | Passwort |
|-------|-------------|----------|
| Anbieter | `provider1` | `Provider123!` |
| Fahrgast | `rider1` | `Rider123!` |

## REST API

Basis-URL: `http://YOUR_HOST/api`

Authentifizierung über Bearer-Token im `Authorization`-Header. Token beziehen:

```bash
curl -X POST http://YOUR_HOST/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"rider1","password":"Rider123!"}'
```

| Methode | Endpunkt | Auth | Beschreibung |
|---------|----------|------|-------------|
| POST | `/api/token` | – | Token beziehen |
| GET | `/api/vehicles` | – | Alle Fahrzeuge |
| GET | `/api/vehicles/<id>` | – | Einzelnes Fahrzeug |
| GET | `/api/provider/vehicles` | Provider | Eigene Fahrzeugflotte |
| GET | `/api/rentals` | Rider/Provider | Eigene Ausleihen |
| POST | `/api/rentals/start/<vehicle_id>` | Rider | Ausleihe starten |
| POST | `/api/rentals/end/<rental_id>` | Rider | Ausleihe beenden |

Vollständige API-Dokumentation: [docs/api.md](docs/api.md)

## Tests

```bash
pytest
```

Die 13 automatisierten Tests in [tests/test_app.py](tests/test_app.py) verwenden eine SQLite-In-Memory-Datenbank und prüfen Registrierung, Login, Fahrzeug-Anlage, Ausleihe, Rückgabe sowie API-Authentifizierung. Alle Tests laufen erfolgreich durch.

Vollständiges Testprotokoll: [docs/test_protocol.md](docs/test_protocol.md)

## Datenbankdateien

| Datei | Inhalt |
|-------|--------|
| `db/init/01-init.sql` | Initialisierung für leere PostgreSQL-Instanz |
| `db/conf/postgresql.conf` | Projektkonfiguration für PostgreSQL |
| `db/schema/schema.sql` | Relationales Datenbankschema (DDL) |
| `db/schema/schema.md` | Beschreibung Tabellen, Schlüssel und Beziehungen |

## Weiterführende Dokumentation

- [docs/architecture.md](docs/architecture.md) — Architekturentscheid, Schichtenmodell, Sequenzdiagramme
- [docs/api.md](docs/api.md) — Vollständige REST-API-Referenz mit Beispielen
- [docs/user_manual.md](docs/user_manual.md) — Benutzerhandbuch für Rider und Provider
- [docs/test_protocol.md](docs/test_protocol.md) — Testprotokoll mit allen 12 Testfällen
- [docs/management_summary.md](docs/management_summary.md) — Management Summary
