# API-Dokumentation

Die RESTful API ist unter dem Pfad `/api` erreichbar. Alle Endpunkte liefern und akzeptieren JSON. Endpunkte mit dem Hinweis 🔒 erfordern eine Authentifizierung via Bearer-Token.

**Basis-URL:**
```
http://YOUR_PUBLIC_IP_OR_DOMAIN/api
```

---

## Authentifizierung

Die API verwendet Token-basierte Authentifizierung. Der Token wird einmalig pro Benutzer erzeugt und im Dashboard angezeigt. Er wird bei jedem geschützten Request im `Authorization`-Header übermittelt:

```
Authorization: Bearer <token>
```

---

## Endpunkte

### POST /api/register

Neuen Benutzer registrieren. Gibt bei Konflikten einen strukturierten Fehler zurück. Kein Token erforderlich.

**Request:**
```bash
curl -X POST http://YOUR_HOST/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "newrider", "email": "new@example.com", "password": "Secret123!", "role": "rider"}'
```

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `username` | `string` | ✅ | Eindeutiger Benutzername |
| `email` | `string` | ✅ | Eindeutige E-Mail-Adresse |
| `password` | `string` | ✅ | Passwort (wird gehasht gespeichert) |
| `role` | `string` | – | `rider` (Standard) oder `provider` |
| `payment_method` | `string` | – | Zahlungsmittel für Fahrgäste |

**Erfolg (201 Created):**
```json
{
  "message": "Registrierung erfolgreich.",
  "token": "a3f9c2e1b7d4...",
  "role": "rider"
}
```

**Fehler (400 Bad Request):**
```json
{ "error": "missing_fields", "message": "username, email und password sind Pflichtfelder." }
```

**Fehler (409 Conflict):**
```json
{ "error": "username_taken", "message": "Benutzername bereits vergeben." }
{ "error": "email_taken",    "message": "E-Mail-Adresse bereits vergeben." }
```

---

### POST /api/token

Token für den API-Zugriff beziehen. Kein Bearer-Token erforderlich.

**Request:**
```bash
curl -X POST http://YOUR_HOST/api/token \
  -H "Content-Type: application/json" \
  -d '{"username": "rider1", "password": "Rider123!"}'
```

**Erfolg (200 OK):**
```json
{
  "token": "a3f9c2e1b7d4...",
  "role": "rider"
}
```

**Fehler (401 Unauthorized):**
```json
{
  "error": "invalid_credentials"
}
```

---

### GET /api/vehicles

Alle Fahrzeuge auflisten. Kein Token erforderlich.

**Request:**
```bash
curl http://YOUR_HOST/api/vehicles
```

**Erfolg (200 OK):**
```json
[
  {
    "id": 1,
    "public_id": "SC-3001",
    "name": "Bahnhof Bern",
    "vehicle_type": "e_scooter",
    "battery_level": 94,
    "latitude": 46.948799,
    "longitude": 7.439136,
    "status": "available",
    "provider": "provider1"
  },
  {
    "id": 3,
    "public_id": "SC-3003",
    "name": "Zytglogge",
    "vehicle_type": "e_bike",
    "battery_level": 81,
    "latitude": 46.948271,
    "longitude": 7.447599,
    "status": "rented",
    "provider": "provider1"
  }
]
```

---

### GET /api/vehicles/\<vehicle\_id\>

Detaildaten eines einzelnen Fahrzeugs abrufen. Kein Token erforderlich.

**Request:**
```bash
curl http://YOUR_HOST/api/vehicles/1
```

**Erfolg (200 OK):**
```json
{
  "id": 1,
  "public_id": "SC-3001",
  "name": "Bahnhof Bern",
  "vehicle_type": "e_scooter",
  "battery_level": 94,
  "latitude": 46.948799,
  "longitude": 7.439136,
  "status": "available",
  "provider": "provider1"
}
```

**Mögliche Werte für `vehicle_type`:** `e_scooter` 🛴, `e_bike` 🚲, `e_cargo` 🚐

**Fehler (404 Not Found):** Fahrzeug-ID existiert nicht.

---

### GET /api/provider/vehicles 🔒

Alle Fahrzeuge des angemeldeten Anbieters abrufen. Nur für Benutzer mit der Rolle `provider`.

**Request:**
```bash
curl http://YOUR_HOST/api/provider/vehicles \
  -H "Authorization: Bearer <provider_token>"
```

**Erfolg (200 OK):** Liste der eigenen Fahrzeuge (gleiches Format wie `/api/vehicles`)

**Fehler (401):** Kein oder ungültiger Token.
**Fehler (403):** Benutzer hat nicht die Rolle `provider`.

---

### GET /api/rentals 🔒

Ausleihen des angemeldeten Nutzers abrufen.

- Fahrgäste erhalten ihre eigenen Fahrten.
- Anbieter erhalten alle Fahrten auf ihren Fahrzeugen.

**Request:**
```bash
curl http://YOUR_HOST/api/rentals \
  -H "Authorization: Bearer <token>"
```

**Erfolg (200 OK):**
```json
[
  {
    "id": 3,
    "vehicle_id": 1,
    "rider": "rider1",
    "start_time": "2025-06-01T09:00:00",
    "end_time": "2025-06-01T09:22:00",
    "status": "completed",
    "total_price": 9.2,
    "distance_km": 4.3
  }
]
```

**Fehler (401):** Kein oder ungültiger Token.

---

### POST /api/rentals/start/\<vehicle\_id\> 🔒

Ausleihe eines Fahrzeugs starten. Nur für Fahrgäste (`rider`). Der korrekte Entriegelungscode muss im Request-Body mitgegeben werden.

**Request:**
```bash
curl -X POST http://YOUR_HOST/api/rentals/start/1 \
  -H "Authorization: Bearer <rider_token>" \
  -H "Content-Type: application/json" \
  -d '{"unlock_code": "QR-3001"}'
```

**Erfolg (201 Created):**
```json
{
  "message": "rental_started",
  "rental": {
    "id": 5,
    "vehicle_id": 1,
    "rider": "rider1",
    "start_time": "2025-06-01T10:00:00",
    "end_time": null,
    "status": "active",
    "total_price": null,
    "distance_km": null
  }
}
```

**Fehlerfälle (400 Bad Request):**
```json
{ "error": "Ungültiger Entriegelungscode (QR-Code). Bitte den Code am Fahrzeug scannen." }
{ "error": "Fahrzeug ist derzeit nicht verfügbar." }
{ "error": "Bitte zuerst ein Zahlungsmittel hinterlegen." }
{ "error": "Es existiert bereits eine aktive Ausleihe." }
{ "error": "Nur Fahrgäste dürfen Fahrzeuge ausleihen." }
```

**Fehler (401):** Kein oder ungültiger Token.

---

### POST /api/rentals/end/\<rental\_id\> 🔒

Aktive Ausleihe beenden, Preis berechnen und Akkustand des Fahrzeugs reduzieren (**−2 % pro km**). Nur der Fahrgast, der die Ausleihe gestartet hat, kann sie beenden.

**Request:**
```bash
curl -X POST http://YOUR_HOST/api/rentals/end/5 \
  -H "Authorization: Bearer <rider_token>" \
  -H "Content-Type: application/json" \
  -d '{"end_km": 5.4, "latitude": 46.947974, "longitude": 7.443131}'
```

| Feld | Typ | Beschreibung |
|---|---|---|
| `end_km` | `float` | Endkilometerstand (muss ≥ Startkilometerstand sein) |
| `latitude` | `float` | Breitengrad des Abgabeorts (−90 bis 90) |
| `longitude` | `float` | Längengrad des Abgabeorts (−180 bis 180) |

**Erfolg (200 OK):**
```json
{
  "message": "rental_completed",
  "rental": {
    "id": 5,
    "vehicle_id": 1,
    "rider": "rider1",
    "start_time": "2025-06-01T10:00:00",
    "end_time": "2025-06-01T10:22:00",
    "status": "completed",
    "total_price": 9.2,
    "distance_km": 5.4
  }
}
```

**Fehlerfälle (400 Bad Request):**
```json
{ "error": "Ausleihe ist bereits beendet." }
{ "error": "Der Endkilometerstand darf nicht kleiner als der Startkilometerstand sein." }
{ "error": "Ungültiger Breitengrad." }
```

**Fehler (401):** Kein oder ungültiger Token.
**Fehler (403):** Ausleihe gehört einem anderen Fahrgast.

---

## Übersicht aller Endpunkte

| Methode | Endpunkt | Auth | Beschreibung |
|---|---|---|---|
| POST | `/api/register` | – | Neuen Benutzer registrieren |
| POST | `/api/token` | – | Token beziehen |
| GET | `/api/vehicles` | – | Alle Fahrzeuge inkl. Anbieter |
| GET | `/api/vehicles/<id>` | – | Fahrzeug-Details inkl. Anbieter |
| GET | `/api/provider/vehicles` | 🔒 Provider | Eigene Flotte |
| GET | `/api/rentals` | 🔒 | Eigene Ausleihen |
| POST | `/api/rentals/start/<id>` | 🔒 Rider | Ausleihe starten |
| POST | `/api/rentals/end/<id>` | 🔒 Rider | Ausleihe beenden (inkl. Akkuabbau) |
