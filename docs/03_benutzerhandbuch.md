# Benutzerhandbuch

## Demo-Zugangsdaten

Für die Prüfung der Anwendung stehen folgende Demo-Benutzer zur Verfügung:

| Rolle | Benutzername | Passwort |
|---|---|---|
| Anbieter | `provider1` | `Provider123!` |
| Fahrgast | `rider1` | `Rider123!` |

Demo-Scooter und ihre Entriegelungscodes: `QR-3001` (Bahnhof Bern), `QR-3002` (Bundesplatz), `QR-3003` (Zytglogge), `QR-3004` (Bärengraben), `QR-3005` (Rosengarten), `QR-3006` (Marzili)

---

## 1. Registrierung

1. Die Seite `http://YOUR_HOST/auth/register` aufrufen.
2. **Benutzername**, **E-Mail-Adresse** und **Passwort** eingeben.
3. **Rolle** wählen:
   - *Fahrgast* – kann Roller ausleihen und Fahrten buchen
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
- **Karte** (Mitte): interaktive OpenStreetMap-Karte mit den aktuellen Standorten aller Scooter in Bern.
- **Verfügbare Roller**: Übersicht aller Scooter mit Status, Akkustand und Standortkoordinaten. Scooter mit Status *Verfügbar* können direkt ausgeliehen werden.
- **Letzte Fahrten**: Ausleihen mit Start- und Endzeitpunkt, Preis und Status.

### Ansicht Anbieter

- **Token-Karte** (oben): API-Schlüssel für den Zugriff als Anbieter.
- **Karte** (Mitte): zeigt die eigene Flotte auf der Karte.
- **Meine Roller**: alle eigenen Scooter mit Status, Akku und Koordinaten.
- **Ausleihen im Überblick**: aktuelle und abgeschlossene Fahrten auf den eigenen Rollern.

---

## 4. Roller ausleihen (Fahrgast)

1. Im Dashboard unter «Verfügbare Roller» einen Scooter mit Status **Verfügbar** (grüner Badge) auswählen.
2. Im Formular des gewünschten Rollers den **QR-Code / Entriegelungscode** eingeben (z. B. `QR-3001` für den Roller am Bahnhof Bern).
3. «Jetzt ausleihen» klicken.
4. Bei korrektem Code wird die Ausleihe gestartet: Der Roller wechselt zu «Ausgeliehen», und unter «Letzte Fahrten» erscheint ein neuer Eintrag mit Status *Aktiv*.

**Fehlermöglichkeiten:**
- Falscher Entriegelungscode → Fehlermeldung, keine Ausleihe
- Scooter bereits ausgeliehen → Fehlermeldung
- Kein Zahlungsmittel hinterlegt → Fehlermeldung mit Hinweis auf Profileinstellung

---

## 5. Ausleihe beenden (Fahrgast)

1. Im Dashboard unter «Letzte Fahrten» die aktive Ausleihe (Status *Aktiv*) finden.
2. Das Rückgabe-Formular ausfüllen:
   - **Endkilometer**: aktueller Kilometerstand des Rollers
   - **Breitengrad / Längengrad**: aktueller Standort des Rollers (GPS-Koordinaten)
3. «Ausleihe beenden» klicken.
4. Der Gesamtpreis wird berechnet und angezeigt:

```
Gesamtpreis = CHF 1.50 (Basis) + CHF 0.35 × Fahrtdauer in Minuten
```

Beispiel: 20 Minuten → CHF 1.50 + CHF 7.00 = **CHF 8.50**

---

## 6. Flotte verwalten (Anbieter)

Die Flottenverwaltung ist unter `http://YOUR_HOST/providers/scooters` erreichbar (Direktlink im Navigationsmenü).

### Neuen Roller anlegen

1. Formular «Neuen Roller anlegen» ausfüllen:
   - **Öffentliche Kennung** (optional, wird automatisch vergeben falls leer)
   - **Bezeichnung** (Standortname oder Modellbezeichnung)
   - **Akkustand** in Prozent (0–100)
   - **Breitengrad und Längengrad** (Startstandort)
   - **Status**: Verfügbar / Wartung / Ausgeliehen
   - **Entriegelungscode** (QR-Code, den Fahrgäste eingeben müssen; wird automatisch generiert falls leer)
2. «Roller speichern» klicken.

### Roller bearbeiten

Jeder Roller in der Flottenliste hat ein eingebettetes Bearbeitungsformular. Nach Änderungen «Änderungen speichern» klicken.

### Roller löschen

«Roller löschen» (roter Button) – die Aktion ist sofort wirksam und kann nicht rückgängig gemacht werden.

---

## 7. API-Schlüssel verwenden

Der API-Schlüssel wird im Dashboard auf der Token-Karte angezeigt. Er wird als Bearer-Token im `Authorization`-Header mitgegeben:

```bash
curl http://YOUR_HOST/api/rentals \
  -H "Authorization: Bearer IHR_TOKEN_HIER"
```

Eine vollständige Beschreibung aller API-Endpunkte befindet sich im Dokument [04_api_dokumentation.md](04_api_dokumentation.md).
