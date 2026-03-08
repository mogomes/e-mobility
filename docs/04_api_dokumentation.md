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

### GET /api/scooters

Alle Scooter auflisten. Kein Token erforderlich.

**Request:**
```bash
curl http://YOUR_HOST/api/scooters
```

**Erfolg (200 OK):**
```json
[
  {
    "id": 1,
    "public_id": "SC-3001",
    "name": "Bahnhof Bern",
    "battery_level": 94,
    "latitude": 46.948799,
    "longitude": 7.439136,
    "status": "available",
    "provider": "provider1"
  },
  {
    "id": 2,
    "public_id": "SC-3002",
    "name": "Bundesplatz",
    "battery_level": 88,
    "latitude": 46.947974,
    "longitude": 7.443131,
    "status": "rented",
    "provider": "provider1"
  }
]
```

---

### GET /api/scooters/\<scooter\_id\>

Detaildaten eines einzelnen Scooters abrufen. Kein Token erforderlich.

**Request:**
```bash
curl http://YOUR_HOST/api/scooters/1
```

**Erfolg (200 OK):**
```json
{
  "id": 1,
  "public_id": "SC-3001",
  "name": "Bahnhof Bern",
  "battery_level": 94,
  "latitude": 46.948799,
  "longitude": 7.439136,
  "status": "available",
  "provider": "provider1"
}
```

**Fehler (404 Not Found):** Scooter-ID existiert nicht.

---

### GET /api/provider/scooters 🔒

Alle Scooter des angemeldeten Anbieters abrufen. Nur für Benutzer mit der Rolle `provider`.

**Request:**
```bash
curl http://YOUR_HOST/api/provider/scooters \
  -H "Authorization: Bearer <provider_token>"
```

**Erfolg (200 OK):** Liste der eigenen Scooter (gleiches Format wie `/api/scooters`)

**Fehler (401):** Kein oder ungültiger Token.  
**Fehler (403):** Benutzer hat nicht die Rolle `provider`.

---

### GET /api/rentals 🔒

Ausleihen des angemeldeten Nutzers abrufen.

- Fahrgäste erhalten ihre eigenen Fahrten.
- Anbieter erhalten alle Fahrten auf ihren Rollern.

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
    "scooter_id": 1,
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

### POST /api/rentals/start/\<scooter\_id\> 🔒

Ausleihe eines Scooters starten. Nur für Fahrgäste (`rider`). Der korrekte Entriegelungscode muss im Request-Body mitgegeben werden.

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
    "scooter_id": 1,
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
{ "error": "Ungültiger Entriegelungscode (QR-Code). Bitte den Code am Roller scannen." }
{ "error": "Roller ist derzeit nicht verfügbar." }
{ "error": "Bitte zuerst ein Zahlungsmittel hinterlegen." }
{ "error": "Es existiert bereits eine aktive Ausleihe." }
{ "error": "Nur Fahrgäste dürfen Fahrzeuge ausleihen." }
```

**Fehler (401):** Kein oder ungültiger Token.

---

### POST /api/rentals/end/\<rental\_id\> 🔒

Aktive Ausleihe beenden und Preis berechnen. Nur der Fahrgast, der die Ausleihe gestartet hat, kann sie beenden.

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
    "scooter_id": 1,
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
| POST | `/api/token` | – | Token beziehen |
| GET | `/api/scooters` | – | Alle Scooter |
| GET | `/api/scooters/<id>` | – | Scooter-Details |
| GET | `/api/provider/scooters` | 🔒 Provider | Eigene Flotte |
| GET | `/api/rentals` | 🔒 | Eigene Ausleihen |
| POST | `/api/rentals/start/<id>` | 🔒 Rider | Ausleihe starten |
| POST | `/api/rentals/end/<id>` | 🔒 Rider | Ausleihe beenden |
