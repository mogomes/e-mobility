# Anforderungen

## Funktionale Anforderungen

### FA-01 – Registrierung und Authentifizierung

| ID | Beschreibung | Status |
|---|---|---|
| FA-01.1 | Neue Benutzer registrieren sich mit eindeutigem Benutzernamen und E-Mail-Adresse | ✅ umgesetzt |
| FA-01.2 | Passwörter werden als Hash gespeichert (Werkzeug `generate_password_hash`) | ✅ umgesetzt |
| FA-01.3 | Login und Logout über Formular im Browser | ✅ umgesetzt |
| FA-01.4 | Zwei Rollen: `rider` (Fahrgast) und `provider` (Anbieter) | ✅ umgesetzt |
| FA-01.5 | Fahrgäste hinterlegen ein Zahlungsmittel (Pflicht für Ausleihen) | ✅ umgesetzt |

### FA-02 – Fahrzeugverwaltung (Anbieter)

| ID | Beschreibung | Status |
|---|---|---|
| FA-02.1 | Anbieter legen Fahrzeuge mit öffentlicher ID, Name, Fahrzeugtyp, Akkustand, GPS-Koordinaten und Status an | ✅ umgesetzt |
| FA-02.2 | Anbieter können Fahrzeug-Attribute bearbeiten (Name, Fahrzeugtyp, Akkustand, Standort, Status) | ✅ umgesetzt |
| FA-02.3 | Anbieter können eigene Fahrzeuge löschen | ✅ umgesetzt |
| FA-02.4 | Jedes Fahrzeug erhält einen eindeutigen Entriegelungscode (`unlock_code`) | ✅ umgesetzt |
| FA-02.5 | Fahrzeug-Status: `available`, `rented`, `maintenance` | ✅ umgesetzt |
| FA-02.6 | Fahrzeugtypen: `e_scooter` 🛴, `e_bike` 🚲, `e_cargo` 🚐 | ✅ umgesetzt |

### FA-03 – Ausleihe und Rückgabe (Fahrgast)

| ID | Beschreibung | Status |
|---|---|---|
| FA-03.1 | Fahrgast gibt QR-Code / Entriegelungscode ein, um Fahrzeug zu entriegeln | ✅ umgesetzt |
| FA-03.2 | Nur ein aktives Rental pro Fahrgast gleichzeitig möglich | ✅ umgesetzt |
| FA-03.3 | Startzeitpunkt wird automatisch gesetzt; Endkilometer und Endstandort werden bei Rückgabe erfasst | ✅ umgesetzt |
| FA-03.4 | Nach Rückgabe wechselt der Fahrzeug-Status zurück zu `available`, Standort wird aktualisiert | ✅ umgesetzt |

### FA-04 – Abrechnung

| ID | Beschreibung | Status |
|---|---|---|
| FA-04.1 | Abrechnung minutengenau: `Basispreis + (Preis/Minute × Dauer)` | ✅ umgesetzt |
| FA-04.2 | Basispreis: CHF 1.50; Preis pro Minute: CHF 0.35 | ✅ umgesetzt |
| FA-04.3 | Mindestdauer: 1 Minute | ✅ umgesetzt |
| FA-04.4 | Gefahrene Distanz wird aus Endkilometer − Startkilometer berechnet | ✅ umgesetzt |
| FA-04.5 | Gesamtpreis wird beim Abschluss der Ausleihe gespeichert | ✅ umgesetzt |

### FA-05 – RESTful Web-API

| ID | Beschreibung | Status |
|---|---|---|
| FA-05.1 | Token-basierte Authentifizierung via `POST /api/token` (Bearer-Token) | ✅ umgesetzt |
| FA-05.2 | Öffentliche Fahrzeugliste ohne Authentifizierung (`GET /api/scooters`) | ✅ umgesetzt |
| FA-05.3 | Detail-Abfrage einzelner Fahrzeuge (`GET /api/scooters/<id>`) — Feld `vehicle_type` enthalten | ✅ umgesetzt |
| FA-05.4 | Ausleihe starten und beenden per API (`POST /api/rentals/start/<id>`, `POST /api/rentals/end/<id>`) | ✅ umgesetzt |
| FA-05.5 | Ausleihen des angemeldeten Nutzers abrufen (`GET /api/rentals`) | ✅ umgesetzt |
| FA-05.6 | Anbieter-spezifische Fahrzeugliste (`GET /api/provider/scooters`) | ✅ umgesetzt |

### FA-06 – Benutzeroberfläche

| ID | Beschreibung | Status |
|---|---|---|
| FA-06.1 | Interaktive Karte mit Fahrzeugstandorten auf der Start- und Dashboardseite (OpenStreetMap / Leaflet.js) | ✅ umgesetzt |
| FA-06.2 | Dashboard zeigt rollenspezifische Ansicht: Flotte (Anbieter) bzw. verfügbare Fahrzeuge (Fahrgast) | ✅ umgesetzt |
| FA-06.3 | API-Token wird im Dashboard angezeigt | ✅ umgesetzt |

---

## Nicht-funktionale Anforderungen

| ID | Anforderung | Umsetzung |
|---|---|---|
| NFA-01 | Erweiterbarkeit auf weitere Fahrzeugtypen (E-Bikes, E-Cargo) | Umgesetzt: `VehicleType`-Enum (`e_scooter`, `e_bike`, `e_cargo`), Spalte `vehicle_type` im Modell, Anzeige in UI und API | ✅ umgesetzt |
| NFA-02 | Performance: bis zu 500 gleichzeitige Ausleihen | Gunicorn mit mehreren Workern; PostgreSQL-Indizes auf `status`, `rider_id`, `scooter_id` |
| NFA-03 | Sicherheit: Passwörter gehasht, Tokens einmalig, Secrets via Umgebungsvariablen | Werkzeug PBKDF2, `secrets.token_hex(24)` für API-Token |
| NFA-04 | Wartbarkeit: modulare Struktur | Flask-Blueprints, separater Service-Layer |
| NFA-05 | Verfügbarkeit: automatischer Neustart | systemd `Restart=always` / Docker `restart: unless-stopped` |

---

## Abgrenzung (nicht umgesetzt / Ausblick)

- Echtes QR-Code-Scanning via Kamera (aktuell: manuelle Texteingabe des Codes)
- Zahlungsverarbeitung (aktuell: Hinterlegung eines Zahlungsmittels als Freitext)
- Push-Benachrichtigungen und GPS-Tracking in Echtzeit
- HTTPS / TLS (muss auf dem Zielserver konfiguriert werden)
