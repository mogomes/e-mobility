# e-mobility Bern

Webplattform für den Verleih von E-Fahrzeugen in Bern. Entwickelt als Lernprojekt im Rahmen des Moduls DBWE.

## Funktionen

- Benutzerkonten mit den Rollen **Anbieter** (Provider) und **Fahrgast** (Rider)
- E-Fahrzeuge-Verwaltung: Standort, Akkustand, Status, Fahrzeugtyp (E-Scooter, E-Bike, E-Cargo)
- Ausleihe und Rückgabe mit automatischer Preisberechnung; **Akkuabbau −2 % pro km**
- Fahrgast-Profil: Zahlungsmittel, E-Mail und Passwort ändern, vollständige Fahrthistorie
- Anbieter-Name wird pro Fahrzeug auf Start- und Dashboardseite angezeigt
- Interaktive Kartenansicht (Leaflet.js) mit allen 20 Fahrzeugen in Bern
- RESTful API mit Token-Authentifizierung und `POST /api/register` (inkl. Duplikat-Fehlercodes)
- PostgreSQL **Stored Procedures** `sp_start_rental` / `sp_end_rental` (werden automatisch angelegt)
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
  __init__.py          # App-Factory (create_app, Stored-Procedure-Setup)
  models.py            # User, Vehicle, Rental + Enums
  services.py          # Geschäftslogik: start_rental, end_rental, seed_demo_data
  extensions.py        # db, migrate, login_manager
  presentation.py      # Jinja-Helpers: status_label, role_label
  api/                 # Blueprint: REST-Endpunkte, Token-Auth, /api/register
  auth/                # Blueprint: Registrierung, Login, Logout
  main/                # Blueprint: Startseite, Dashboard
  profile/             # Blueprint: Nutzerprofil (Zahlungsmittel, E-Mail, Passwort)
  providers/           # Blueprint: Fahrzeug-Flottenverwaltung
  rentals/             # Blueprint: Ausleihe und Rückgabe
  static/              # CSS, JS, SVG-Assets
  templates/           # Jinja2-Templates
db/
  conf/                # postgresql.conf
  init/                # 01-init.sql (Bootstrap für leere DB)
  schema/              # schema.sql, schema.md
  stored_procedures.sql  # sp_start_rental, sp_end_rental (PostgreSQL)
deploy/                # Deployment-Skripte und Konfiguration
docs/                  # Architektur, API, Testprotokoll, Handbuch
tests/
  test_app.py          # 27 automatisierte pytest-Tests
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

## Demo-Flotte (20 Fahrzeuge in Bern)

| Kennung | Standort | Typ | Status |
|---------|----------|-----|--------|
| BE-3001 | Bahnhof Bern | 🛴 E-Scooter | Verfügbar |
| BE-3002 | Bundesplatz | 🛴 E-Scooter | Verfügbar |
| BE-3003 | Zytglogge | 🚲 E-Bike | Verfügbar |
| BE-3004 | Bärengraben | 🚲 E-Bike | Verfügbar |
| BE-3005 | Rosengarten | 🚐 E-Cargo | Verfügbar |
| BE-3006 | Marzili | 🛴 E-Scooter | Verfügbar |
| BE-3007 | Kornhausplatz | 🛴 E-Scooter | Verfügbar |
| BE-3008 | Münster | 🚲 E-Bike | Verfügbar |
| BE-3009 | Helvetiaplatz | 🛴 E-Scooter | Verfügbar |
| BE-3010 | Waisenhausplatz | 🚐 E-Cargo | Verfügbar |
| BE-3011 | Breitenrain | 🛴 E-Scooter | Verfügbar |
| BE-3012 | Länggasse | 🚲 E-Bike | Verfügbar |
| BE-3013 | Bremgartenwald | 🚐 E-Cargo | ⚙️ Wartung |
| BE-3014 | Burgernziel | 🛴 E-Scooter | Verfügbar |
| BE-3015 | Viktoriapark | 🚲 E-Bike | Verfügbar |
| BE-3016 | Köniz Dorf | 🛴 E-Scooter | Verfügbar |
| BE-3017 | Ostermundigen Zentrum | 🚲 E-Bike | Verfügbar |
| BE-3018 | Bümpliz Bahnhof | 🛴 E-Scooter | ⚙️ Wartung |
| BE-3019 | Weissenbühl | 🚐 E-Cargo | Verfügbar |
| BE-3020 | Universität Bern | 🚲 E-Bike | Verfügbar |

## Umgebungsvariablen

Datei `.env` im Projektwurzelverzeichnis anlegen (Vorlage: `.env.example`):

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=bitte-durch-langen-zufallswert-ersetzen
DATABASE_URL=postgresql+psycopg://emobility:strongpassword@localhost:5432/emobilitydb
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

> **Hinweis:** Falls die Datenbank bereits mit anderen Zugangsdaten existiert, Volume zuerst löschen:
> ```bash
> docker compose down -v && docker compose up --build -d
> ```

## Lokaler Start ohne Docker

### 1. PostgreSQL-Datenbank anlegen

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE emobilitydb;
CREATE USER emobility WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE emobilitydb TO emobility;
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

Vollständige API-Dokumentation: [docs/04_api_dokumentation.md](docs/04_api_dokumentation.md)

## Tests

```bash
pytest
```

Die 13 automatisierten Tests in [tests/test_app.py](tests/test_app.py) verwenden eine SQLite-In-Memory-Datenbank und prüfen Registrierung, Login, Fahrzeug-Anlage, Ausleihe, Rückgabe sowie API-Authentifizierung. Alle Tests laufen erfolgreich durch.

Vollständiges Testprotokoll: [docs/06_testprotokoll.md](docs/06_testprotokoll.md)

## Datenbankdateien

| Datei | Inhalt |
|-------|--------|
| `db/init/01-init.sql` | Initialisierung für leere PostgreSQL-Instanz |
| `db/conf/postgresql.conf` | Projektkonfiguration für PostgreSQL |
| `db/schema/schema.sql` | Relationales Datenbankschema (DDL) |
| `db/schema/schema.md` | Beschreibung Tabellen, Schlüssel und Beziehungen |

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| [docs/01_management_summary.md](docs/01_management_summary.md) | Management Summary |
| [docs/02_anforderungen.md](docs/02_anforderungen.md) | Funktionale und nicht-funktionale Anforderungen |
| [docs/03_benutzerhandbuch.md](docs/03_benutzerhandbuch.md) | Benutzerhandbuch für Rider und Provider |
| [docs/04_api_dokumentation.md](docs/04_api_dokumentation.md) | Vollständige REST-API-Referenz mit Beispielen |
| [docs/05_systemarchitektur.md](docs/05_systemarchitektur.md) | Architekturentscheid, Schichtenmodell, ERD |
| [docs/06_testprotokoll.md](docs/06_testprotokoll.md) | Testprotokoll mit allen 13 Testfällen |
