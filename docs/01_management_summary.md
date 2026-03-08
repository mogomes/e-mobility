# Management Summary

## Vorhaben

Im Rahmen der Praxisarbeit DBWE.TA1A.PA wurde eine internetfähige Webanwendung für den Verleih von E-Scootern entwickelt. Die Plattform richtet sich an zwei Nutzergruppen: **Anbieter**, die eine Roller-Flotte verwalten, und **Fahrgäste**, die Roller ausleihen, fahren und bezahlen. Das Projekt setzt die Normaufgabe gemäss Aufgabenstellung vollständig um.

## Technologie und Infrastruktur

| Komponente | Gewählte Technologie |
|---|---|
| Programmiersprache | Python 3.12 |
| Web-Framework | Flask 3.1 mit Blueprints |
| Datenbank | PostgreSQL 16 |
| ORM | Flask-SQLAlchemy 3.1 |
| WSGI-Server | Gunicorn 23 |
| Reverse Proxy | Nginx (optional) |
| Containerisierung | Docker / Docker Compose |
| Prozessverwaltung (bare metal) | systemd |

Die Anwendung ist wahlweise als Docker-Stack (`docker compose up`) oder als systemd-Dienst auf einem Linux-Server betreibbar. Die Datenbankschicht ist vollständig vom Applikationsserver getrennt.

## Erzielte Ergebnisse

Die Webanwendung ist vollständig lauffähig und erfüllt alle gestellten Anforderungen:

- Registrierung und Login mit Rollen (Fahrgast / Anbieter)
- Interaktive Karte mit Echtzeit-Scooterstandorten (OpenStreetMap)
- QR-Code-basierte Entriegelung und minutengenaue Abrechnung
- RESTful API mit Bearer-Token-Authentifizierung
- 13 automatisierte pytest-Tests

## Mehrwert

Die klare Rollentrennung zwischen Anbieter und Fahrgast sowie die Kombination aus Weboberfläche und API erlaubt eine flexible Nutzung – sowohl interaktiv im Browser als auch automatisiert über HTTP-Clients und mobile Apps.

## Risiken

Das grösste Risiko im produktiven Betrieb liegt in der Absicherung des Servers: Ohne HTTPS, Firewall-Regeln und regelmässige Backups ist die Plattform angreifbar. Für den produktiven Einsatz sind zwingend erforderlich:

- TLS-Zertifikat (z. B. Let's Encrypt via Certbot)
- Firewall (UFW: nur Port 80/443 öffentlich)
- Datenbankpasswörter und `SECRET_KEY` als Umgebungsvariablen (`.env`-Datei, nie im Repository)
- Regelmässige PostgreSQL-Backups (`pg_dump`)

## Wartbarkeit, Skalierbarkeit, Verfügbarkeit

**Wartbarkeit:** Die Anwendung ist mit Flask-Blueprints modular aufgebaut. Jede Funktion (Auth, Provider, Rentals, API) liegt in einem eigenen Modul. Die Geschäftslogik ist im Service-Layer (`services.py`) von den HTTP-Routen getrennt.

**Skalierbarkeit:** Mehrere Gunicorn-Worker können parallel betrieben werden. Die Trennung von App- und Datenbankschicht ermöglicht horizontales Skalieren der Applikation bei gleichbleibendem Datenbankserver.

**Verfügbarkeit:** systemd startet den Dienst nach Absturz automatisch neu (`Restart=always`). Docker Compose verwendet `restart: unless-stopped`. Ein vorgeschalteter Nginx-Reverse-Proxy erhöht die Stabilität zusätzlich.
