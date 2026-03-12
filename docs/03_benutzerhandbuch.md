# Benutzerhandbuch

## Demo-Zugangsdaten

Für die Prüfung der Anwendung stehen folgende Demo-Benutzer zur Verfügung:

| Rolle | Benutzername | Passwort |
|---|---|---|
| Anbieter | `provider1` | `Provider123!` |
| Fahrgast | `rider1` | `Rider123!` |

Demo-Fahrzeuge und ihre Entriegelungscodes (18 verfügbar, 2 in Wartung):

| Code | Kennung | Standort | Fahrzeugtyp | Status |
|---|---|---|---|---|
| `QR-3001` | BE-3001 | Bahnhof Bern | 🛴 E-Scooter | Verfügbar |
| `QR-3002` | BE-3002 | Bundesplatz | 🛴 E-Scooter | Verfügbar |
| `QR-3003` | BE-3003 | Zytglogge | 🚲 E-Bike | Verfügbar |
| `QR-3004` | BE-3004 | Bärengraben | 🚲 E-Bike | Verfügbar |
| `QR-3005` | BE-3005 | Rosengarten | 🚐 E-Cargo | Verfügbar |
| `QR-3006` | BE-3006 | Marzili | 🛴 E-Scooter | Verfügbar |
| `QR-3007` | BE-3007 | Kornhausplatz | 🛴 E-Scooter | Verfügbar |
| `QR-3008` | BE-3008 | Münster | 🚲 E-Bike | Verfügbar |
| `QR-3009` | BE-3009 | Helvetiaplatz | 🛴 E-Scooter | Verfügbar |
| `QR-3010` | BE-3010 | Waisenhausplatz | 🚐 E-Cargo | Verfügbar |
| `QR-3011` | BE-3011 | Breitenrain | 🛴 E-Scooter | Verfügbar |
| `QR-3012` | BE-3012 | Länggasse | 🚲 E-Bike | Verfügbar |
| — | BE-3013 | Bremgartenwald | 🚐 E-Cargo | ⚙️ Wartung |
| `QR-3014` | BE-3014 | Burgernziel | 🛴 E-Scooter | Verfügbar |
| `QR-3015` | BE-3015 | Viktoriapark | 🚲 E-Bike | Verfügbar |
| `QR-3016` | BE-3016 | Köniz Dorf | 🛴 E-Scooter | Verfügbar |
| `QR-3017` | BE-3017 | Ostermundigen Zentrum | 🚲 E-Bike | Verfügbar |
| — | BE-3018 | Bümpliz Bahnhof | 🛴 E-Scooter | ⚙️ Wartung |
| `QR-3019` | BE-3019 | Weissenbühl | 🚐 E-Cargo | Verfügbar |
| `QR-3020` | BE-3020 | Universität Bern | 🚲 E-Bike | Verfügbar |

> **Hinweis:** Fahrzeuge mit Status *Wartung* sind nicht ausleihbar und zeigen keinen QR-Code.

---

## 1. Registrierung

1. Die Seite `http://YOUR_HOST/auth/register` aufrufen.
2. **Benutzername**, **E-Mail-Adresse** und **Passwort** eingeben.
3. **Rolle** wählen:
   - *Fahrgast* – kann Fahrzeug ausleihen und Fahrten buchen
   - *Anbieter* – verwaltet eine eigene Scooter-Flotte
4. Fahrgäste sollten ein **Zahlungsmittel** hinterlegen (z. B. `Visa **** 4242`). Ohne Zahlungsmittel ist keine Ausleihe möglich.
5. «Konto erstellen» klicken. Bei Erfolg erfolgt eine Weiterleitung zur Anmeldeseite.

> **Hinweis:** Benutzername und E-Mail-Adresse müssen eindeutig sein. Ein doppelter Eintrag wird mit einer Fehlermeldung abgewiesen.

---

## 2. Anmelden und Abmelden

- **Login:** `http://YOUR_HOST/auth/login` – Benutzername und Passwort eingeben, «Anmelden» klicken.
- **Logout:** Im Navigationsmenü auf «Abmelden» klicken. Die Sitzung wird beendet.

---

## 3. Dashboard

Nach dem Login erscheint das persönliche Dashboard. Die Ansicht ist rollenabhängig:

### Ansicht Fahrgast

- **Token-Karte** (oben): zeigt den persönlichen API-Schlüssel für den Zugriff via API-Client.
- **Karte** (Mitte): interaktive OpenStreetMap-Karte mit den aktuellen Standorten aller Fahrzeuge in Bern.
- **Verfügbare Fahrzeuge**: Übersicht aller Fahrzeuge mit Typ, Status, Akkustand, QR-Code und Standortkoordinaten. Fahrzeuge mit Status *Verfügbar* können direkt ausgeliehen werden.
- **Letzte Fahrten**: Ausleihen mit Start- und Endzeitpunkt, Preis und Status.

### Ansicht Anbieter

- **Token-Karte** (oben): API-Schlüssel für den Zugriff als Anbieter.
- **Karte** (Mitte): zeigt die eigene Flotte auf der Karte.
- **Meine Fahrzeuge**: alle eigenen Fahrzeuge mit Typ, Status, Akku und Koordinaten.
- **Ausleihen im Überblick**: aktuelle und abgeschlossene Fahrten auf den eigenen Fahrzeugen.

---

## 4. Fahrzeug ausleihen (Fahrgast)

1. Im Dashboard unter «Verfügbare Fahrzeuge» ein Fahrzeug mit Status **Verfügbar** (grüner Badge) auswählen. Der Fahrzeugtyp (🛴 E-Scooter, 🚲 E-Bike, 🚐 E-Cargo) ist auf der Karte und der Karte sichtbar.
2. Der QR-Code des Fahrzeugs wird direkt auf der Karte angezeigt. Den **Entriegelungscode** (z. B. `QR-3001`) in das Eingabefeld eingeben.
3. «Jetzt ausleihen» klicken.
4. Bei korrektem Code wird die Ausleihe gestartet: Das Fahrzeug wechselt zu «Ausgeliehen», und unter «Letzte Fahrten» erscheint ein neuer Eintrag mit Status *Aktiv*.

**Fehlermöglichkeiten:**
- Falscher Entriegelungscode → Fehlermeldung, keine Ausleihe
- Fahrzeug bereits ausgeliehen → Fehlermeldung
- Akkustand unter 10 % → Fehlermeldung «Akkustand zu niedrig», bitte anderes Fahrzeug wählen
- Kein Zahlungsmittel hinterlegt → Fehlermeldung mit Hinweis auf Profileinstellung

---

## 5. Ausleihe beenden (Fahrgast)

1. Im Dashboard unter «Letzte Fahrten» die aktive Ausleihe (Status *Aktiv*) finden.
2. Das Rückgabe-Formular ausfüllen:
   - **Endkilometer**: aktueller Kilometerstand des Fahrzeugs
   - **Breitengrad / Längengrad**: aktueller Standort des Fahrzeugs (GPS-Koordinaten)
3. «Ausleihe beenden» klicken.
4. Der Gesamtpreis wird berechnet und angezeigt:

```
Gesamtpreis = CHF 1.50 (Basis) + CHF 0.35 × Fahrtdauer in Minuten
```

Beispiel: 20 Minuten → CHF 1.50 + CHF 7.00 = **CHF 8.50**

> **Akkuabbau:** Nach jeder Fahrt sinkt der Akkustand des Fahrzeugs automatisch um **2 % pro gefahrenen km**. Bei 5 km Fahrt = −10 %. Fahrzeuge mit weniger als 10 % Akkustand können nicht mehr ausgeliehen werden.

> **Akkugrenze:** Die angegebene Distanz darf den verbleibenden Akkustand nicht überschreiten. Beispiel: Hat das Fahrzeug 40 % Akku, können maximal 20 km angegeben werden (20 km × 2 % = 40 %). Eine unmögliche Distanz wird mit einer Fehlermeldung abgewiesen.

---

## 6. Profil und Einstellungen (Fahrgast)

Die Profilseite ist unter `http://YOUR_HOST/profile/` erreichbar (Link «Profil» in der Navigation).

### Zahlungsmittel ändern
Im Abschnitt «Zahlungsmittel» das gewünschte Zahlungsmittel eingeben (z. B. `Mastercard **** 5678`) und «Speichern» klicken. Ohne Zahlungsmittel ist keine Ausleihe möglich.

### E-Mail-Adresse ändern
Neue E-Mail-Adresse eingeben und «Speichern» klicken. Die neue Adresse muss eindeutig sein — eine bereits verwendete E-Mail wird abgewiesen.

### Passwort ändern
1. Aktuelles Passwort eingeben (als Verifikation)
2. Neues Passwort und Bestätigung eingeben (mindestens 8 Zeichen)
3. «Passwort ändern» klicken

### Fahrthistorie
Auf der Profilseite sind **alle eigenen abgeschlossenen und aktiven Fahrten** aufgelistet, mit Fahrzeug, Strecke, Preis und Zeitstempel.

---

## 7. Flotte verwalten (Anbieter)

Die Flottenverwaltung ist unter `http://YOUR_HOST/providers/vehicles` erreichbar (Direktlink im Navigationsmenü).

### Neues Fahrzeug anlegen

1. Formular «Neues Fahrzeug anlegen» ausfüllen:
   - **Öffentliche Kennung** (optional, wird automatisch vergeben falls leer)
   - **Bezeichnung** (Standortname oder Modellbezeichnung)
   - **Fahrzeugtyp**: 🛴 E-Scooter / 🚲 E-Bike / 🚐 E-Cargo
   - **Akkustand** in Prozent (0–100)
   - **Breitengrad und Längengrad** (Startstandort)
   - **Status**: Verfügbar / Wartung / Ausgeliehen
   - **Entriegelungscode** (QR-Code, den Fahrgäste eingeben müssen; wird automatisch generiert falls leer)
2. «Fahrzeug speichern» klicken.

### Fahrzeug bearbeiten

Jedes Fahrzeug in der Flottenliste hat ein eingebettetes Bearbeitungsformular inkl. Fahrzeugtyp-Auswahl. Nach Änderungen «Änderungen speichern» klicken.

### Fahrzeug löschen

«Fahrzeug löschen» (roter Button) – die Aktion ist sofort wirksam und kann nicht rückgängig gemacht werden.

---

## 8. Profil und Einstellungen (Anbieter)

Die Anbieter-Profilseite ist unter `http://YOUR_HOST/providers/profile` erreichbar (Link «Profil» in der Navigation).

### Benutzername ändern

1. Neuen Benutzernamen eingeben (mindestens 3 Zeichen).
2. «Speichern» klicken.
3. Der neue Benutzername muss eindeutig sein — ein bereits vergebener Name wird abgewiesen.

### Passwort ändern

1. Aktuelles Passwort eingeben (als Verifikation).
2. Neues Passwort und Bestätigung eingeben (mindestens 8 Zeichen).
3. «Passwort ändern» klicken.

---

## 9. API-Zugriff ohne Browser (curl / Postman)

Die API ist vollständig ohne Browser nutzbar. Alle Daten — insbesondere die Fahrzeugflotte — lassen sich direkt per `curl`, HTTPie oder Postman abrufen und verwalten.

### Authentifizierung (Token beziehen)

```bash
curl -s -X POST http://YOUR_HOST/api/token \
  -H "Content-Type: application/json" \
  -d '{"username": "rider1", "password": "Rider123!"}'
```

Antwort: `{ "token": "...", "role": "rider" }`

### Fahrzeuge ohne Login abrufen

```bash
curl -s http://YOUR_HOST/api/vehicles | python -m json.tool
```

### Ausleihe starten (mit Token)

```bash
curl -s -X POST http://YOUR_HOST/api/rentals/start/1 \
  -H "Authorization: Bearer IHR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"unlock_code": "QR-3001"}'
```

> **Hinweis:** Der API-Schlüssel wird im Dashboard auf der Token-Karte angezeigt und kann direkt kopiert werden.

Eine vollständige Beschreibung aller API-Endpunkte inkl. Postman-Konfiguration befindet sich im Dokument [04_api_dokumentation.md](04_api_dokumentation.md).
