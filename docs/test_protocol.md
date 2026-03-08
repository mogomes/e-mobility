# Testprotokoll

| Nr. | Testfall | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|---|---|---|
| 1 | Startseite öffnen | HTTP 200, Startseite sichtbar | Erfolgreich |
| 2 | Registrierung neuer Rider | Neuer User wird gespeichert | Erfolgreich |
| 3 | Login mit gültigen Credentials | Dashboard erscheint | Erfolgreich |
| 4 | Provider legt Scooter an | Neuer Scooter in DB vorhanden | Erfolgreich |
| 5 | Rider startet Ausleihe | Rental aktiv, Scooter rented | Erfolgreich |
| 6 | Rider beendet Ausleihe | Preis berechnet, Scooter available | Erfolgreich |
| 7 | API Token beziehen | Token wird als JSON geliefert | Erfolgreich |
| 8 | API Rentals ohne Token | HTTP 401 | Erfolgreich |

Die Testfälle 1-7 sind automatisiert mit `pytest` umgesetzt. Testfall 8 kann zusätzlich manuell oder automatisiert geprüft werden.
