# Testprotokoll

## Teststrategie

Die Anwendung wird mit **automatisierten pytest-Tests** und **manuellen Stichproben** geprüft. Die automatisierten Tests laufen gegen eine SQLite-In-Memory-Datenbank, die bei jedem Testlauf neu befüllt und nach dem Test verworfen wird. Demo-Daten werden via `seed_demo_data()` injiziert.

**Tests ausführen:**
```bash
pytest tests/ -v
```

---

## Automatisierte Tests (`tests/test_app.py`)

| Nr. | Testfall / Funktion | Beschreibung | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|---|---|---|---|
| T-01 | `test_smoke` | Basistest: Python und pytest funktionieren | `True == True` | ✅ Bestanden |
| T-02 | `test_homepage_loads` | Startseite abrufbar | HTTP 200, HTML enthält «E-Fahrzeuge» | ✅ Bestanden |
| T-03 | `test_register_user` | Neuen Fahrgast registrieren | HTTP 200, Flash «Registrierung erfolgreich» | ✅ Bestanden |
| T-04 | `test_login_works` | Login mit korrekten Zugangsdaten | HTTP 200, Dashboard erscheint («Übersicht») | ✅ Bestanden |
| T-05 | `test_login_fails_with_wrong_password` | Login mit falschem Passwort | Flash «Ungültige Zugangsdaten», kein Redirect auf Dashboard | ✅ Bestanden |
| T-06 | `test_provider_can_create_scooter` | Anbieter legt neues Fahrzeug an (inkl. `vehicle_type`) | HTTP 200, Fahrzeug `SC-9999` in Datenbank vorhanden | ✅ Bestanden |
| T-07 | `test_rider_can_start_and_end_rental` | Fahrgast startet und beendet Ausleihe mit korrektem QR-Code | Rental `active` → `completed`, `total_price > 0` | ✅ Bestanden |
| T-08 | `test_rental_rejected_with_wrong_unlock_code` | Ausleihe mit falschem Entriegelungscode | Kein Rental angelegt (`active count == 0`) | ✅ Bestanden |
| T-09 | `test_api_token_and_scooter_list` | API-Token beziehen, Scooterliste und Rentals abrufen | Token als JSON, Scooter-/Rental-Liste als Array | ✅ Bestanden |
| T-10 | `test_api_scooter_detail` | Detail-Endpunkt `GET /api/scooters/<id>` | HTTP 200, Felder `public_id` und `battery_level` vorhanden | ✅ Bestanden |
| T-11 | `test_api_rentals_requires_auth` | `GET /api/rentals` ohne Token | HTTP 401, `error: missing_or_invalid_token` | ✅ Bestanden |
| T-12 | `test_api_invalid_token_rejected` | `GET /api/rentals` mit ungültigem Bearer-Token | HTTP 401 | ✅ Bestanden |
| T-13 | `test_unique_registration_constraints` | Doppelten Benutzernamen registrieren | HTTP 200, Flash-Fehlermeldung; nur 1 User in DB | ✅ Bestanden |

---

## Manuelle Tests (Stichproben)

Die folgenden Tests wurden manuell über den Browser und via `curl` durchgeführt.

| Nr. | Testfall | Vorgehen | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|---|---|---|---|
| M-01 | Karte auf Startseite | Startseite öffnen, Karte prüfen | OpenStreetMap-Karte zeigt Bern mit Fahrzeug-Markierungen (Typ im Popup) | ✅ Bestanden |
| M-02 | Provider-Zugriff durch Rider blockiert | Als `rider1` einloggen, `/providers/scooters` aufrufen | HTTP 403 | ✅ Bestanden |
| M-03 | API-Token via curl | `POST /api/token` mit Demo-Zugangsdaten | JSON mit Token und Rolle | ✅ Bestanden |
| M-04 | Ausleihe starten via API | `POST /api/rentals/start/1` mit `unlock_code: QR-3001` | HTTP 201, Rental-Objekt mit `status: active` | ✅ Bestanden |
| M-05 | Ausleihe beenden via API | `POST /api/rentals/end/<id>` mit `end_km`, `latitude`, `longitude` | HTTP 200, `total_price` berechnet | ✅ Bestanden |
| M-06 | Ungültige API-Token-Anfrage | `GET /api/rentals` mit Header `Authorization: Bearer falsch` | HTTP 401 | ✅ Bestanden |

---

## Bekannte Einschränkungen und offene Punkte

| Nr. | Beschreibung | Priorität |
|---|---|---|
| E-01 | QR-Code-Eingabe erfolgt als Freitext im Formular; kein echtes Kamera-Scanning | Mittel – produktiv wäre ein mobiler QR-Scanner nötig |
| E-02 | API-Token wird bei Logout nicht invalidiert; nur ein Token pro User | Niedrig – für Produktion: Token-Rotation oder JWT mit Ablaufzeit |
| E-03 | `db.create_all()` beim App-Start; keine expliziten Migrations-Skripte für Schemaänderungen | Mittel – Flask-Migrate ist installiert, aber nicht aktiv genutzt |
| E-04 | Kein HTTPS auf Applikationsebene; muss auf dem Server via Nginx + Certbot konfiguriert werden | Hoch – vor öffentlicher Bereitstellung zwingend |
| E-05 | Gefahrene Distanz basiert auf manuell eingegebenen Kilometern, nicht auf GPS-Track | Niedrig – für vollständige Lösung wäre GPS-Integration nötig |
