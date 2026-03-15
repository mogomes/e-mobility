# e-mobility Bern

Webplattform für den Verleih von E-Fahrzeugen in Bern. Entwickelt als Lernprojekt im Rahmen des Moduls DBWE.

## Funktionen

- Benutzerkonten mit den Rollen **Anbieter** (Provider) und **Fahrgast** (Rider)
- E-Fahrzeuge-Verwaltung: Standort, Akkustand, Status, Fahrzeugtyp (E-Scooter, E-Bike, E-Cargo)
- Ausleihe und Rückgabe mit automatischer Preisberechnung; **Akkuabbau −2 % pro km**
- **Akkugrenze:** Rückgabe mit unmöglicher Distanz (mehr Akku nötig als vorhanden) wird verweigert
- Fahrgast-Profil: Zahlungsmittel, E-Mail und Passwort ändern, vollständige Fahrthistorie
- **Anbieter-Profil:** Benutzername und Passwort änderbar; vollständige Ausleihenhistorie der eigenen Flotte
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
  profile/             # Blueprint: Nutzerprofil Fahrgast (Zahlungsmittel, E-Mail, Passwort)
  providers/           # Blueprint: Fahrzeug-Flottenverwaltung + Anbieter-Profil
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
  test_app.py          # 12 automatisierte pytest-Tests
```

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
| POST | `/api/register` | – | Neuen Benutzer registrieren |
| GET | `/api/vehicles` | – | Fahrzeuge (ohne Wartung) |
| GET | `/api/vehicles/<id>` | – | Einzelnes Fahrzeug |
| GET | `/api/provider/vehicles` | Provider | Eigene Fahrzeugflotte |
| GET | `/api/rentals` | Rider/Provider | Eigene Ausleihen |
| POST | `/api/rentals/start/<vehicle_id>` | Rider | Ausleihe starten |
| POST | `/api/rentals/end/<rental_id>` | Rider | Ausleihe beenden |

## Tests

```bash
pytest
```

Die 12 automatisierten Tests in [tests/test_app.py](tests/test_app.py) verwenden eine SQLite-In-Memory-Datenbank und prüfen Registrierung, Login, Fahrzeug-Anlage, Ausleihe, Rückgabe, Akkugrenze sowie API-Authentifizierung. Alle Tests laufen erfolgreich durch.

## Datenbankdateien

| Datei | Inhalt |
|-------|--------|
| `db/init/01-init.sql` | Initialisierung für leere PostgreSQL-Instanz |
| `db/conf/postgresql.conf` | Projektkonfiguration für PostgreSQL |
| `db/schema/schema.sql` | Relationales Datenbankschema (DDL) |
| `db/schema/schema.md` | Beschreibung Tabellen, Schlüssel und Beziehungen |