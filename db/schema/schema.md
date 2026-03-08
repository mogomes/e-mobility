# Datenbankschema

## Tabellenübersicht

### `users`
Speichert alle Benutzerkonten der Anwendung.

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | Integer | Primärschlüssel |
| `username` | Varchar(80) | Eindeutiger Benutzername |
| `email` | Varchar(255) | Eindeutige E-Mail-Adresse |
| `password_hash` | Varchar(255) | Gehashter Passwortwert |
| `role` | Varchar(20) | Rolle: `rider` oder `provider` |
| `payment_method` | Varchar(120) | Optionales Zahlungsmittel |
| `api_token` | Varchar(64) | Eindeutiger API-Token |
| `created_at` | Timestamp with time zone | Erstellungszeitpunkt |

### `scooters`
Speichert die von Providern angebotenen E-Scooter.

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | Integer | Primärschlüssel |
| `public_id` | Varchar(32) | Öffentliche Rollernummer |
| `name` | Varchar(120) | Rollerbezeichnung |
| `battery_level` | Integer | Akkustand 0 bis 100 |
| `latitude` | Numeric(9,6) | Breitengrad |
| `longitude` | Numeric(9,6) | Längengrad |
| `status` | Varchar(20) | `available`, `rented`, `maintenance` |
| `unlock_code` | Varchar(32) | Entsperrcode |
| `provider_id` | Integer | Fremdschlüssel auf `users.id` |
| `created_at` | Timestamp with time zone | Erstellungszeitpunkt |

### `rentals`
Speichert Ausleihen und Rückgaben.

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | Integer | Primärschlüssel |
| `scooter_id` | Integer | Fremdschlüssel auf `scooters.id` |
| `rider_id` | Integer | Fremdschlüssel auf `users.id` |
| `start_time` | Timestamp with time zone | Startzeit |
| `end_time` | Timestamp with time zone | Endzeit |
| `start_km` | Numeric(10,2) | Kilometerstand beim Start |
| `end_km` | Numeric(10,2) | Kilometerstand beim Ende |
| `start_latitude` | Numeric(9,6) | Start-Breitengrad |
| `start_longitude` | Numeric(9,6) | Start-Längengrad |
| `end_latitude` | Numeric(9,6) | End-Breitengrad |
| `end_longitude` | Numeric(9,6) | End-Längengrad |
| `base_price` | Numeric(10,2) | Grundpreis |
| `price_per_minute` | Numeric(10,2) | Preis pro Minute |
| `total_price` | Numeric(10,2) | Gesamtpreis |
| `distance_km` | Numeric(10,2) | Gefahrene Distanz |
| `status` | Varchar(20) | `active` oder `completed` |

## Schlüsselbeziehungen

- `scooters.provider_id` → `users.id`
- `rentals.scooter_id` → `scooters.id`
- `rentals.rider_id` → `users.id`

## Kardinalitäten

- Ein **Provider** kann **mehrere Scooter** besitzen.
- Ein **Scooter** kann **mehrere Ausleihen** haben.
- Ein **Rider** kann **mehrere Ausleihen** haben.

## Vereinfachtes ER-Modell

```text
users (1) ----- (n) scooters
users (1) ----- (n) rentals
scooters (1) -- (n) rentals
```
