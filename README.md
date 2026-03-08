# e-mobility Bern

Moderne Flask-Webanwendung für die Verwaltung und Ausleihe von E‑Scootern in Bern mit PostgreSQL, Weboberfläche, Programmierschnittstelle und Kartenansicht.

## Funktionen

- Benutzerkonten mit Rollen **Anbieter** und **Fahrgast**
- E‑Scooter-Verwaltung mit Standort, Akkustand und Status
- Ausleihe und Rückgabe mit Preisberechnung
- Kartenansicht für Roller-Standorte in Bern
- PostgreSQL als Datenbank
- Betrieb mit Docker **oder lokal direkt mit Flask**

## Projektstruktur

```text
app/
  api/
  auth/
  main/
  providers/
  rentals/
  static/
  templates/
db/
  conf/
  init/
  schema/
deploy/
docs/
tests/
```

## Umgebungsvariablen

Beispiel für `.env`:

```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=bitte-durch-langen-zufallswert-ersetzen
DATABASE_URL=postgresql+psycopg://escooter:strongpassword@localhost:5432/escooterdb
APP_BASE_URL=http://localhost:8000
PORT=8000
```

### Geheimschlüssel erzeugen

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Start mit Docker

```bash
docker compose down -v
docker compose up --build -d
```

Die Anwendung ist danach unter `http://localhost:8000` erreichbar.

## Lokaler Start ohne Docker

### 1. PostgreSQL lokal installieren und Datenbank anlegen

Beispiel unter Linux:

```bash
sudo -u postgres psql
```

Dann in PostgreSQL:

```sql
CREATE DATABASE escooterdb;
CREATE USER escooter WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE escooterdb TO escooter;
```

### 2. Virtuelle Umgebung anlegen

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Umgebungsvariablen setzen

```bash
cp .env.example .env
```

Danach `.env` so anpassen, dass `DATABASE_URL` auf deine lokale PostgreSQL-Instanz zeigt:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=bitte-durch-langen-zufallswert-ersetzen
DATABASE_URL=postgresql+psycopg://escooter:strongpassword@localhost:5432/escooterdb
APP_BASE_URL=http://127.0.0.1:5000
PORT=5000
```

### 4. Anwendung starten

```bash
source .venv/bin/activate
flask run
```

Die Anwendung läuft dann unter `http://127.0.0.1:5000`.

## Start mit Gunicorn auf Linux

```bash
source .venv/bin/activate
gunicorn -b 0.0.0.0:8000 run:app
```

## Demo-Zugänge

- Anbieter: `provider1` / `Provider123!`
- Fahrgast: `rider1` / `Rider123!`

## Hinweise zur Datenbank

- `db/init/01-init.sql` enthält Initialisierung für einen leeren PostgreSQL-Start
- `db/conf/postgresql.conf` enthält Projektkonfiguration für PostgreSQL
- `db/schema/schema.sql` enthält das relationale Datenbankschema
- `db/schema/schema.md` beschreibt Tabellen, Schlüssel und Beziehungen

## Tests

```bash
pytest
```
