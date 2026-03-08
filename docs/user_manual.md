# User Manual – e-mobility E-Scooter Plattform

## Anforderungen (Übersicht)

| Nr. | Anforderung | Umgesetzt |
|-----|-------------|-----------|
| A1 | Registrierung und Login mit eindeutigem Benutzernamen und E-Mail | ✅ |
| A2 | Rollen: Fahrgast (Rider) und Anbieter (Provider) | ✅ |
| A3 | Provider: Scooter hinzufügen, bearbeiten, löschen | ✅ |
| A4 | Scooter: eindeutige ID, Akkustand, GPS-Koordinaten, Status | ✅ |
| A5 | Rider: Scooter per QR-Code/Entriegelungscode ausleihen | ✅ |
| A6 | Ausleihe: Start-/Endzeit und gefahrene Kilometer erfassen | ✅ |
| A7 | Abrechnung minutengenau: Basispreis + Preis/Minute | ✅ |
| A8 | Zahlungsmittel hinterlegen (Pflicht für Rider) | ✅ |
| A9 | RESTful API mit Token-Authentifizierung | ✅ |
| A10 | Interaktive Karte mit Scooter-Standorten (OpenStreetMap) | ✅ |

---

## Browser-Bedienung

### 1. Registrierung

1. `http://YOUR_HOST/auth/register` aufrufen
2. Benutzername, E-Mail und Passwort eingeben
3. Rolle wählen: **Fahrgast** (Roller ausleihen) oder **Anbieter** (E-Scooter verwalten)
4. Fahrgäste: Zahlungsmittel angeben (Pflichtfeld für Ausleihen, z. B. «Visa **** 4242»)
5. «Konto erstellen» klicken → Weiterleitung zur Anmeldung

### 2. Anmelden / Abmelden

- Login: `http://YOUR_HOST/auth/login`
- Logout: Menü → «Abmelden»

### 3. Dashboard

Nach dem Login erscheint das Dashboard mit:
- **API-Schlüssel** (oben rechts auf der Token-Karte)
- **Karte** mit Scooter-Standorten (Bern)
- **Scooter-Übersicht** (für Rider: verfügbare Roller; für Provider: eigene Flotte)
- **Ausleihen** (letzte Fahrten mit Status und Preis)

### 4. Roller ausleihen (Rider)

1. Im Dashboard unter «Verfügbare Roller» einen Scooter mit Status **Verfügbar** wählen
2. Den **QR-Code / Entriegelungscode** vom Roller eingeben (z. B. `QR-3001`)
3. «Jetzt ausleihen» klicken
4. Bei Erfolg: Ausleihe erscheint unter «Letzte Fahrten» mit Status **Aktiv**

> Hinweis: Codes der Demo-Scooter: `QR-3001` bis `QR-3006`

### 5. Ausleihe beenden (Rider)

1. Im Dashboard unter «Letzte Fahrten» die aktive Ausleihe finden
2. Endkilometerstand, Breitengrad und Längengrad eingeben
3. «Ausleihe beenden» klicken
4. Der Gesamtpreis (Basispreis CHF 1.50 + CHF 0.35/Minute) wird angezeigt

### 6. Flotte verwalten (Provider)

- Navigation: `http://YOUR_HOST/providers/scooters`
- Neuen Roller anlegen: Formular ausfüllen, «Roller speichern»
- Bestehenden Roller bearbeiten: Felder ändern, «Änderungen speichern»
- Roller löschen: «Roller löschen» (rot)

---

## API-Zugriff (ohne Browser)

Alle API-Endpunkte sind unter `/api/` erreichbar. Authentifizierung via Bearer-Token.

**Token beziehen:**
```bash
curl -X POST http://YOUR_HOST/api/token \
  -H "Content-Type: application/json" \
  -d '{"username":"rider1","password":"Rider123!"}'
```

Vollständige API-Dokumentation: siehe `docs/api.md`

---

## Demo-Benutzer

| Rolle | Benutzername | Passwort |
|-------|-------------|---------|
| Anbieter | `provider1` | `Provider123!` |
| Fahrgast | `rider1` | `Rider123!` |

Demo-Scooter-Codes: `QR-3001` … `QR-3006`
