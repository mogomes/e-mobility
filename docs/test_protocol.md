# Testprotokoll – e-mobility E-Scooter Plattform

Alle Tests 1–12 sind als automatisierte `pytest`-Tests implementiert (siehe `tests/test_app.py`).
Die Testumgebung verwendet eine SQLite-In-Memory-Datenbank.

| Nr. | Testfall | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|-----|----------|---------------------|------------------------|
| 1 | Startseite öffnen (`GET /`) | HTTP 200, Seite enthält «E-Scooter» | Erfolgreich |
| 2 | Registrierung neuer Rider mit gültigen Daten | HTTP 200, Flash «Registrierung erfolgreich» | Erfolgreich |
| 3 | Login mit korrekten Zugangsdaten | Dashboard erscheint, HTTP 200 | Erfolgreich |
| 4 | Login mit falschem Passwort | Flash «Ungültige Zugangsdaten», kein Login | Erfolgreich |
| 5 | Provider legt neuen Scooter an | Scooter in DB gespeichert, HTTP 200 | Erfolgreich |
| 6 | Rider startet Ausleihe mit korrektem QR-Code | Rental aktiv, Scooter auf «rented» gesetzt | Erfolgreich |
| 7 | Rider versucht Ausleihe mit falschem QR-Code | Fehlermeldung, kein Rental angelegt | Erfolgreich |
| 8 | Rider beendet Ausleihe mit Endkilometern | Preis > 0 berechnet, Status «completed» | Erfolgreich |
| 9 | API-Token beziehen (`POST /api/token`) | Token und Rolle als JSON | Erfolgreich |
| 10 | `GET /api/rentals` ohne Token | HTTP 401, error: missing_or_invalid_token | Erfolgreich |
| 11 | `GET /api/rentals` mit ungültigem Token | HTTP 401 | Erfolgreich |
| 12 | `POST /api/token` mit falschem Passwort | HTTP 401, error: invalid_credentials | Erfolgreich |

## Offene Punkte / bekannte Einschränkungen

- Die QR-Code-Eingabe erfolgt manuell als Textfeld. In einer produktiven Lösung würde eine echte Kamera-App den Code scannen und automatisch übermitteln.
- Die Preisberechnung startet mit mindestens 1 Minute; sehr kurze Tests können daher einen Mindestbetrag erzeugen.
- Automatisierte Tests für Datenbankfehler (z. B. DB-Ausfall) sind in der aktuellen Version nicht implementiert.
