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
| T-06 | `test_password_is_hashed_in_db` | Passwort-Hash prüfen | `password_hash` ≠ Klartext, beginnt mit `scrypt:` oder `pbkdf2:` | ✅ Bestanden |
| T-07 | `test_unique_registration_constraints` | Doppelten Benutzernamen registrieren | HTTP 200, Flash-Fehlermeldung; nur 1 User in DB | ✅ Bestanden |
| T-08 | `test_api_register_success` | `POST /api/register` erfolgreich | HTTP 201, `token` im JSON enthalten | ✅ Bestanden |
| T-09 | `test_api_register_duplicate_username` | `POST /api/register` mit bereits vergebenem Benutzernamen | HTTP 409, `error: username_taken` | ✅ Bestanden |
| T-10 | `test_api_register_duplicate_email` | `POST /api/register` mit bereits vergebener E-Mail | HTTP 409, `error: email_taken` | ✅ Bestanden |
| T-11 | `test_api_register_missing_fields` | `POST /api/register` ohne Pflichtfelder | HTTP 400, `error: missing_fields` | ✅ Bestanden |
| T-12 | `test_provider_can_create_scooter` | Anbieter legt neues Fahrzeug an (inkl. `vehicle_type`) | HTTP 200, Fahrzeug `SC-9999` in Datenbank vorhanden | ✅ Bestanden |
| T-13 | `test_rider_can_start_and_end_rental` | Fahrgast startet und beendet Ausleihe mit korrektem QR-Code | Rental `active` → `completed`, `total_price > 0` | ✅ Bestanden |
| T-14 | `test_battery_drains_after_rental` | Akkustand sinkt nach 5 km Fahrt um 10 % | `battery_level` = Startwert − 10 (min. 0) | ✅ Bestanden |
| T-15 | `test_rental_rejected_when_battery_too_low` | Ausleihe mit Fahrzeug < 10 % Akku | Kein Rental angelegt, Flash «Akkustand zu niedrig» | ✅ Bestanden |
| T-16 | `test_rental_rejected_with_wrong_unlock_code` | Ausleihe mit falschem Entriegelungscode | Kein Rental angelegt (`active count == 0`) | ✅ Bestanden |
| T-17 | `test_profile_page_loads` | Profil-Seite für Fahrgast abrufbar | HTTP 200, Benutzername sichtbar | ✅ Bestanden |
| T-18 | `test_profile_update_payment` | Zahlungsmittel im Profil ändern | HTTP 200, neues Zahlungsmittel in DB gespeichert | ✅ Bestanden |
| T-19 | `test_profile_update_email` | E-Mail-Adresse im Profil ändern | HTTP 200, neue E-Mail in DB gespeichert | ✅ Bestanden |
| T-20 | `test_profile_update_email_duplicate_rejected` | Änderung auf bereits vergebene E-Mail | Flash «bereits vergeben» | ✅ Bestanden |
| T-21 | `test_profile_update_password` | Passwort im Profil ändern | HTTP 200, neues Passwort gültig | ✅ Bestanden |
| T-22 | `test_profile_update_password_wrong_current` | Passwortänderung mit falschem aktuellen Passwort | Flash «Aktuelles Passwort ist falsch» | ✅ Bestanden |
| T-23 | `test_profile_update_password_mismatch` | Neue Passwörter stimmen nicht überein | Flash «stimmen nicht überein» | ✅ Bestanden |
| T-24 | `test_api_token_and_vehicle_list` | API-Token beziehen, Fahrzeugliste und Rentals abrufen | Token als JSON, Fahrzeug-/Rental-Liste als Array | ✅ Bestanden |
| T-25 | `test_api_vehicle_detail` | Detail-Endpunkt `GET /api/vehicles/<id>` inkl. Anbieter | HTTP 200, Felder `public_id`, `battery_level`, `provider` vorhanden | ✅ Bestanden |
| T-26 | `test_api_rentals_requires_auth` | `GET /api/rentals` ohne Token | HTTP 401, `error: missing_or_invalid_token` | ✅ Bestanden |
| T-27 | `test_api_invalid_token_rejected` | `GET /api/rentals` mit ungültigem Bearer-Token | HTTP 401 | ✅ Bestanden |
| T-28 | `test_api_invalid_credentials_rejected` | `POST /api/token` mit falschem Passwort | HTTP 401, `error: invalid_credentials` | ✅ Bestanden |
| T-29 | `test_rental_end_rejected_when_battery_insufficient` | Ausleihe beenden mit Distanz, die mehr Akku erfordert als vorhanden (z. B. 100 km bei 80 % Akku) | ValueError / Flash-Fehlermeldung, Ausleihe bleibt aktiv | ✅ Bestanden |
| T-30 | `test_provider_profile_page_loads` | Anbieter-Profilseite `/providers/profile` abrufen | HTTP 200, Benutzername sichtbar | ✅ Bestanden |
| T-31 | `test_provider_update_username` | Anbieter ändert Benutzernamen | HTTP 200, neuer Benutzername in DB gespeichert | ✅ Bestanden |
| T-32 | `test_provider_update_username_duplicate_rejected` | Anbieter versucht, einen bereits vergebenen Benutzernamen zu verwenden | Flash «bereits vergeben» | ✅ Bestanden |
| T-33 | `test_provider_update_password` | Anbieter ändert Passwort | HTTP 200, neues Passwort gültig | ✅ Bestanden |

---

## Manuelle Tests (Stichproben)

Die folgenden Tests wurden manuell über den Browser und via `curl` durchgeführt.

| Nr. | Testfall | Vorgehen | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|---|---|---|---|
| M-01 | Karte auf Startseite | Startseite öffnen, Karte prüfen | OpenStreetMap-Karte zeigt Bern mit Fahrzeug-Markierungen (Typ im Popup) | ✅ Bestanden |
| M-02 | Provider-Zugriff durch Rider blockiert | Als `rider1` einloggen, `/providers/vehicles` aufrufen | HTTP 403 | ✅ Bestanden |
| M-03 | API-Token via curl | `POST /api/token` mit Demo-Zugangsdaten | JSON mit Token und Rolle | ✅ Bestanden |
| M-04 | Ausleihe starten via API | `POST /api/rentals/start/1` mit `unlock_code: QR-3001` | HTTP 201, Rental-Objekt mit `status: active` | ✅ Bestanden |
| M-05 | Ausleihe beenden via API | `POST /api/rentals/end/<id>` mit `end_km`, `latitude`, `longitude` | HTTP 200, `total_price` berechnet | ✅ Bestanden |
| M-06 | Ungültige API-Token-Anfrage | `GET /api/rentals` mit Header `Authorization: Bearer falsch` | HTTP 401 | ✅ Bestanden |
| M-07 | Akkugrenze beim Beenden | Im Dashboard Endkilometer > verfügbarer Akku/2 eingeben | Flash-Fehlermeldung mit Akkudetails, Ausleihe bleibt aktiv | ✅ Bestanden |
| M-08 | Anbieter-Profil im Browser | Als `provider1` einloggen, «Profil» in der Navigation anklicken | Profilseite mit Formularen für Benutzername und Passwort | ✅ Bestanden |
| M-09 | Rider-Zugriff auf Anbieter-Profil blockiert | Als `rider1` einloggen, `/providers/profile` aufrufen | HTTP 403 | ✅ Bestanden |

---

## Bekannte Einschränkungen und offene Punkte

| Nr. | Beschreibung | Priorität |
|---|---|---|
| E-01 | QR-Code-Eingabe erfolgt als Freitext im Formular; kein echtes Kamera-Scanning | Mittel – produktiv wäre ein mobiler QR-Scanner nötig |
| E-02 | API-Token wird bei Logout nicht invalidiert; nur ein Token pro User | Niedrig – für Produktion: Token-Rotation oder JWT mit Ablaufzeit |
| E-03 | `db.create_all()` beim App-Start; keine expliziten Migrations-Skripte für Schemaänderungen | Mittel – Flask-Migrate ist installiert, aber nicht aktiv genutzt |
| E-04 | Kein HTTPS auf Applikationsebene; muss auf dem Server via Nginx + Certbot konfiguriert werden | Hoch – vor öffentlicher Bereitstellung zwingend |
| E-05 | Gefahrene Distanz basiert auf manuell eingegebenen Kilometern, nicht auf GPS-Track | Niedrig – für vollständige Lösung wäre GPS-Integration nötig |
