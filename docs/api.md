# API-Dokumentation

Basis-URL Beispiel:

```text
http://YOUR_PUBLIC_IP/api
```

## Authentifizierung

### POST /api/token

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"rider1","password":"Rider123!"}'
```

## Endpunkte

### GET /api/scooters

```bash
curl http://YOUR_PUBLIC_IP/api/scooters
```

### GET /api/rentals

```bash
curl http://YOUR_PUBLIC_IP/api/rentals \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/rentals/start/<scooter_id>

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/rentals/start/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /api/rentals/end/<rental_id>

```bash
curl -X POST http://YOUR_PUBLIC_IP/api/rentals/end/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"end_km":5.4,"latitude":46.947974,"longitude":7.443131}'
```
