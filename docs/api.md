# API-Dokumentation – e-mobility E-Scooter Plattform

Basis-URL:

```text
http://YOUR_PUBLIC_IP/api
```

Alle Endpunkte geben JSON zurück. Endpunkte mit 🔒 erfordern einen Bearer-Token im `Authorization`-Header.

---

## Authentifizierung

### POST /api/token

Token für API-Zugriff beziehen. Rückgabe: `{ "token": "...", "role": "rider|provider" }`.

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"rider1","password":"Rider123!"}'
```

---

## Scooter

### GET /api/scooters

Alle verfügbaren Scooter auflisten (kein Token erforderlich).

```bash
curl http://YOUR_PUBLIC_IP/api/scooters
```

**Antwort (Beispiel):**
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
  }
]
```

### GET /api/scooters/\<scooter_id\>

Detaildaten eines einzelnen Scooters.

```bash
curl http://YOUR_PUBLIC_IP/api/scooters/1
```

### GET /api/provider/scooters 🔒

Alle Scooter des angemeldeten Anbieters (nur für Provider-Accounts).

```bash
curl http://YOUR_PUBLIC_IP/api/provider/scooters \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Ausleihen

### GET /api/rentals 🔒

Ausleihen des angemeldeten Nutzers (Rider: eigene Fahrten; Provider: Fahrten auf eigenen Scootern).

```bash
curl http://YOUR_PUBLIC_IP/api/rentals \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/rentals/start/\<scooter_id\> 🔒

Ausleihe starten. Pflichtfeld: `unlock_code` (QR-Code am Roller).

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/rentals/start/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"unlock_code":"QR-3001"}'
```

**Antwort (201 Created):**
```json
{
  "message": "rental_started",
  "rental": {
    "id": 5,
    "scooter_id": 1,
    "rider": "rider1",
    "start_time": "2025-06-01T09:00:00",
    "end_time": null,
    "status": "active",
    "total_price": null,
    "distance_km": null
  }
}
```

**Fehlerfälle:**
- `400` – Scooter nicht verfügbar, ungültiger Code, kein Zahlungsmittel hinterlegt
- `401` – kein oder ungültiger Token

### POST /api/rentals/end/\<rental_id\> 🔒

Ausleihe beenden und Preis berechnen.

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/rentals/end/5 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"end_km":5.4,"latitude":46.947974,"longitude":7.443131}'
```

**Antwort (200 OK):**
```json
{
  "message": "rental_completed",
  "rental": {
    "id": 5,
    "status": "completed",
    "total_price": 7.10,
    "distance_km": 5.40
  }
}
```
