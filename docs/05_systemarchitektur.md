# Systemarchitektur

## Architekturprinzip

Die Anwendung folgt einer klassischen **3-Schichten-Architektur**:

1. **Präsentationsschicht** – HTML-Templates (Jinja2), CSS, JavaScript (Leaflet.js für die Karte)
2. **Applikationsschicht** – Flask-Blueprints und Service-Layer (`services.py`)
3. **Datenhaltungsschicht** – PostgreSQL 16 mit SQLAlchemy ORM

Die Geschäftslogik (Ausleihe starten/beenden, Preisberechnung, Validierungen) ist bewusst vom HTTP-Layer getrennt und im Service-Layer konzentriert. Dadurch können dieselben Funktionen sowohl von den Web-Routen als auch von der API verwendet werden.

---

## Flask-Module (Blueprints)

| Modul | URL-Präfix | Aufgabe |
|---|---|---|
| `main` | `/` | Startseite, Dashboard |
| `auth` | `/auth` | Registrierung, Login, Logout |
| `providers` | `/providers` | Scooter-Verwaltung für Anbieter |
| `rentals` | `/rentals` | Start und Ende von Ausleihen (Web) |
| `api` | `/api` | RESTful API-Endpunkte |

---

## Datenmodell (ERD)

```mermaid
erDiagram
    USER ||--o{ SCOOTER : "stellt bereit"
    USER ||--o{ RENTAL  : "bucht"
    SCOOTER ||--o{ RENTAL : "wird genutzt in"

    USER {
        int     id           PK
        string  username     UK
        string  email        UK
        string  password_hash
        string  role
        string  payment_method
        string  api_token    UK
        datetime created_at
    }

    SCOOTER {
        int     id           PK
        string  public_id    UK
        string  name
        int     battery_level
        decimal latitude
        decimal longitude
        string  status
        string  unlock_code
        int     provider_id  FK
        datetime created_at
    }

    RENTAL {
        int     id            PK
        int     scooter_id    FK
        int     rider_id      FK
        datetime start_time
        datetime end_time
        decimal start_km
        decimal end_km
        decimal start_latitude
        decimal start_longitude
        decimal end_latitude
        decimal end_longitude
        decimal base_price
        decimal price_per_minute
        decimal total_price
        decimal distance_km
        string  status
    }
```

**Datenbank-Constraints (PostgreSQL):**
- `users.role` ∈ `{rider, provider}`
- `scooters.status` ∈ `{available, rented, maintenance}`
- `scooters.battery_level` ∈ 0–100
- `rentals.status` ∈ `{active, completed}`
- `rentals.end_km >= rentals.start_km` (wenn gesetzt)
- Fremdschlüssel mit `ON DELETE RESTRICT` (kein Löschen von Usern/Scootern bei offenen Ausleihen)

**Indizes für Performance:**
```sql
idx_scooters_provider_id, idx_scooters_status
idx_rentals_scooter_id, idx_rentals_rider_id, idx_rentals_status
```

---

## Wichtige Abläufe

### Registrierung

```mermaid
sequenceDiagram
    actor Benutzer
    participant Browser
    participant Flask
    participant DB

    Benutzer->>Browser: Formular ausfüllen und absenden
    Browser->>Flask: POST /auth/register
    Flask->>DB: Prüfen: username und email eindeutig?
    DB-->>Flask: Ergebnis
    alt Konflikt
        Flask-->>Browser: Flash-Fehlermeldung
    else OK
        Flask->>DB: Neuen User speichern (Passwort als Hash)
        DB-->>Flask: OK
        Flask-->>Browser: Redirect zu /auth/login
    end
```

### Scooter ausleihen

```mermaid
sequenceDiagram
    actor Fahrgast
    participant Client as Browser / API-Client
    participant Flask as Flask Service Layer
    participant DB

    Fahrgast->>Client: QR-Code eingeben und Ausleihe starten
    Client->>Flask: POST /rentals/start/<id>  {unlock_code}
    Flask->>DB: Scooter laden
    Flask->>Flask: unlock_code validieren
    Flask->>DB: Aktive Ausleihe des Fahrgasts prüfen
    Flask->>DB: Zahlungsmittel prüfen
    Flask->>DB: Rental anlegen
    Flask->>DB: Scooter.status = rented
    DB-->>Flask: OK
    Flask-->>Client: 201 Created / Flash-Erfolgsmeldung
```

### Ausleihe beenden und verrechnen

```mermaid
flowchart TD
    A[Ausleihe aktiv] --> B[Enddaten empfangen]
    B --> C{end_km >= start_km?}
    C -- Fehler --> D[ValueError 400 / Flash]
    C -- OK --> E[end_time = jetzt]
    E --> F[Fahrtdauer berechnen]
    F --> G["Preis: 1.50 + 0.35 x Minuten"]
    G --> H["Distanz: end_km - start_km"]
    H --> I[Scooter-Standort aktualisieren]
    I --> J[Rental.status = completed]
    J --> K[Antwort an Client]
```

---

## Deployment-Varianten

```mermaid
flowchart LR
    Client[Browser / API-Client]

    subgraph DockerCompose["Option A: Docker Compose"]
        Nginx_A[Nginx optional]
        Gunicorn_A[Gunicorn Flask Port 8000]
        DB_A[(PostgreSQL Container)]
        Client --> Nginx_A --> Gunicorn_A --> DB_A
    end

    subgraph BareMetal["Option B: bare metal / VPS"]
        Nginx_B[Nginx Port 80/443]
        Gunicorn_B[Gunicorn systemd Port 8000]
        DB_B[(PostgreSQL auf Server)]
        Client --> Nginx_B --> Gunicorn_B --> DB_B
    end
```

### Option A – Docker Compose (empfohlen für schnellen Start)

```bash
cp .env.example .env   # Secrets anpassen
docker compose up -d
```

Die Anwendung ist anschliessend unter `http://SERVER_IP:8000` erreichbar. Nginx kann optional vorgeschaltet werden.

### Option B – bare metal mit systemd

```bash
# 1. Virtualenv und Abhängigkeiten
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Umgebungsvariablen setzen (.env-Datei)
# DATABASE_URL, SECRET_KEY, APP_BASE_URL

# 3. Systemd-Dienst installieren
sudo cp deploy/escooter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now escooter

# 4. Nginx als Reverse Proxy konfigurieren
sudo cp deploy/nginx.conf /etc/nginx/sites-available/escooter
sudo ln -s /etc/nginx/sites-available/escooter /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## Architekturentscheidungen: Vor- und Nachteile

| Entscheidung | Vorteile | Nachteile |
|---|---|---|
| Flask mit Blueprints | Klare Modularität, gute Testbarkeit | Weniger Konventionen als Django; mehr Konfigurationsaufwand |
| PostgreSQL | Produktionsreif, mächtige Constraints und Indizes | Schwergewichtiger als SQLite; erfordert separaten Dienst |
| Gunicorn | Einfaches Deployment, Multi-Worker-fähig | Kein HTTP/2; für sehr hohe Last wären Load-Balancer nötig |
| Session-Login + API-Token | Zwei getrennte Zugangswege für Browser und API-Clients | Erhöhte Komplexität; Token wird nicht bei Logout invalidiert |
| `db.create_all()` beim Start | Einfach für Lernprojekte | Für Produktionsbetrieb besser: explizite Migrations via Flask-Migrate |
| Unlock-Code als Freitext | Einfache Demo-Implementierung | Produktiv: echter QR-Code-Scanner in mobiler App notwendig |
