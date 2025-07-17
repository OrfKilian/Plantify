# Plantify Webinterface - Umfassende API-Dokumentation

## Übersicht

Das Plantify Webinterface ist eine Flask-basierte Webanwendung zur Verwaltung von Pflanzen und deren Überwachung. Die Anwendung bietet eine benutzerfreundliche Oberfläche zur Verwaltung von Zimmern, Pflanzen und Benutzerprofilen.

## Inhaltsverzeichnis

1. [Installation und Setup](#installation-und-setup)
2. [Architektur](#architektur)
3. [Öffentliche APIs](#öffentliche-apis)
4. [Authentifizierung](#authentifizierung)
5. [Hilfsfunktionen](#hilfsfunktionen)
6. [Frontend-Komponenten](#frontend-komponenten)
7. [Template-System](#template-system)
8. [JavaScript-Funktionalität](#javascript-funktionalität)
9. [Styling-Komponenten](#styling-komponenten)
10. [Verwendungsbeispiele](#verwendungsbeispiele)

## Installation und Setup

### Abhängigkeiten

```bash
pip install -r requirements.txt
```

**Erforderliche Pakete:**
- `Flask` - Web-Framework
- `email-validator` - E-Mail-Validierung
- `requests` - HTTP-Anfragen an die API

### Umgebungsvariablen

```bash
export SECRET_KEY="ihr-geheimer-schlüssel"
```

### Anwendung starten

```bash
python app.py
```

Die Anwendung läuft standardmäßig auf `http://localhost:8080`

## Architektur

### Systemkomponenten

- **Frontend**: Flask-Templates mit HTML/CSS/JavaScript
- **Backend**: Flask-Anwendung mit Session-Management
- **API-Integration**: Kommunikation mit `plantify-api:5001`
- **Authentifizierung**: PBKDF2-basierte Passwort-Hashing

### Datenfluss

```
Browser → Flask App → Plantify API → Datenbank
```

## Öffentliche APIs

### 1. Authentifizierung

#### `/login` (GET, POST)

**Beschreibung**: Benutzeranmeldung

**Parameter (POST)**:
- `email` (string): Benutzer-E-Mail
- `password` (string): Passwort

**Antwort**:
- Bei Erfolg: Weiterleitung zur Startseite
- Bei Fehler: Login-Seite mit Fehlermeldung

**Beispiel**:
```html
<form method="POST" action="/login">
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <button type="submit">Anmelden</button>
</form>
```

#### `/logout` (GET)

**Beschreibung**: Benutzerabmeldung

**Antwort**: Weiterleitung zur Login-Seite

#### `/register` (GET, POST)

**Beschreibung**: Benutzerregistrierung

**Parameter (POST)**:
- `email` (string): E-Mail-Adresse
- `password` (string): Passwort
- `confirm_password` (string): Passwort-Bestätigung

**Validierung**:
- E-Mail-Format wird überprüft
- Passwörter müssen übereinstimmen
- E-Mail darf nicht bereits existieren

**Beispiel**:
```html
<form method="POST" action="/register">
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <input type="password" name="confirm_password" required>
    <button type="submit">Registrieren</button>
</form>
```

### 2. Dashboard und Übersicht

#### `/` (GET)

**Beschreibung**: Startseite (Login erforderlich)

**Antwort**: Hauptseite der Anwendung

#### `/dashboard/<slug>` (GET)

**Beschreibung**: Zimmer-Dashboard mit Pflanzenübersicht

**Parameter**:
- `slug` (string): URL-freundlicher Zimmername

**Funktionalität**:
- Zeigt alle Pflanzen im Zimmer
- Lädt aktuelle Sensordaten
- Zeigt Diagramme für Temperatur, Luftfeuchtigkeit, etc.

**Beispiel**:
```python
# URL: /dashboard/wohnzimmer
# Zeigt alle Pflanzen im Wohnzimmer
```

#### `/rooms` (GET)

**Beschreibung**: Zimmerverwaltung

**Antwort**: Liste aller verfügbaren Zimmer

### 3. Pflanzenverwaltung

#### `/pflanze/<slug>` (GET)

**Beschreibung**: Detailansicht einer Pflanze

**Parameter**:
- `slug` (string): Pflanzenname oder Name-ID-Kombination

**Funktionalität**:
- Zeigt Pflanzendetails
- Ermöglicht Bearbeitung von Zielwerten
- Zimmerzuordnung

**Beispiel**:
```python
# URL: /pflanze/monstera-deliciosa-123
# Zeigt Details der Monstera mit ID 123
```

#### `/api/plant/<int:plant_id>` (POST)

**Beschreibung**: Aktualisierung von Pflanzendaten

**Parameter**:
- `plant_id` (int): Pflanzen-ID

**Request Body (JSON)**:
```json
{
    "name": "Neuer Pflanzenname",
    "facts": "Pflanzeninformationen",
    "room": "Zimmer",
    "target_temperature": 22,
    "target_air_humidity": 60,
    "target_ground_humidity": 40
}
```

**Antwort**:
```json
{
    "success": true
}
```

**Beispiel**:
```javascript
await fetch('/api/plant/123', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "Monstera Deliciosa",
        target_temperature: 24
    })
});
```

### 4. Benutzereinstellungen

#### `/settings` (GET)

**Beschreibung**: Einstellungsseite

**Antwort**: Formular für E-Mail- und Passwort-Änderung

#### `/settings/change-email` (POST)

**Beschreibung**: E-Mail-Adresse ändern

**Parameter**:
- `new_email` (string): Neue E-Mail-Adresse

**Validierung**:
- E-Mail-Format wird überprüft
- Benutzer muss angemeldet sein

**Beispiel**:
```html
<form method="POST" action="/settings/change-email">
    <input type="email" name="new_email" required>
    <button type="submit">Speichern</button>
</form>
```

#### `/settings/change-password` (POST)

**Beschreibung**: Passwort ändern

**Parameter**:
- `current_password` (string): Aktuelles Passwort
- `new_password` (string): Neues Passwort
- `confirm_password` (string): Passwort-Bestätigung

**Validierung**:
- Aktuelles Passwort wird überprüft
- Neue Passwörter müssen übereinstimmen

## Authentifizierung

### Login-Decorator

```python
@login_required
def protected_route():
    # Nur für angemeldete Benutzer zugänglich
    pass
```

**Funktionalität**:
- Überprüft Session auf `user_id`
- Leitet zur Login-Seite weiter wenn nicht angemeldet
- Speichert ursprüngliche URL für Weiterleitung nach Login

### Passwort-Hashing

```python
def hash_password(password: str, iterations: int = 100_000) -> str
```

**Parameter**:
- `password`: Klartextpasswort
- `iterations`: PBKDF2-Iterationen (Standard: 100.000)

**Rückgabe**: URL-kodierter Hash-String

**Beispiel**:
```python
hashed = hash_password("mein_passwort")
# Rückgabe: "100000%24salt_base64%24hash_base64"
```

### Passwort-Verifikation

```python
def check_password(password: str, hashed: str) -> bool
```

**Parameter**:
- `password`: Klartextpasswort
- `hashed`: Gespeicherter Hash

**Rückgabe**: Boolean (True bei korrektem Passwort)

## Hilfsfunktionen

### E-Mail-Validierung

```python
def is_valid_email(email: str) -> bool
```

**Beschreibung**: Überprüft E-Mail-Format mit `email-validator`

**Parameter**:
- `email`: Zu prüfende E-Mail-Adresse

**Rückgabe**: Boolean

**Beispiel**:
```python
if is_valid_email("test@example.com"):
    print("Gültige E-Mail")
```

### URL-Slugify

```python
def slugify(value: str) -> str
```

**Beschreibung**: Konvertiert String zu URL-freundlichem Format

**Parameter**:
- `value`: Zu konvertierender String

**Rückgabe**: Kleingeschriebener String mit Bindestrichen

**Beispiel**:
```python
slug = slugify("Mein Zimmer")  # "mein-zimmer"
```

### Datenabruf-Funktionen

#### `fetch_rooms()`

**Beschreibung**: Lädt alle Zimmer des angemeldeten Benutzers

**Rückgabe**: Liste von Zimmer-Objekten
```python
[
    {"name": "Wohnzimmer", "id": "pot_123"},
    {"name": "Schlafzimmer", "id": "pot_456"}
]
```

#### `fetch_plants()`

**Beschreibung**: Lädt alle Pflanzen des angemeldeten Benutzers

**Rückgabe**: Liste von Pflanzen-Objekten
```python
[
    {
        "id": 123,
        "name": "Monstera",
        "facts": "Benötigt viel Licht",
        "room": "Wohnzimmer",
        "target_temperature": 22,
        "target_air_humidity": 60,
        "target_ground_humidity": 40
    }
]
```

### Context Processor

```python
@app.context_processor
def inject_sidebar_data()
```

**Beschreibung**: Stellt Zimmer- und Pflanzendaten für alle Templates zur Verfügung

**Verfügbare Variablen**:
- `rooms`: Liste aller Zimmer
- `plants`: Liste aller Pflanzen

## Frontend-Komponenten

### JavaScript-Funktionalität

#### Diagramm-Laden (`plots.js`)

```javascript
function loadPlots(baseUrl)
```

**Beschreibung**: Lädt Plotly-Diagramme von der API

**Parameter**:
- `baseUrl`: API-Basis-URL

**Unterstützte Diagramme**:
- `sunlight`: Sonnenstunden
- `temperature`: Temperaturverlauf
- `soil`: Bodenfeuchtigkeit
- `luftfeuchtigkeit`: Luftfeuchtigkeit

**Beispiel**:
```javascript
loadPlots('http://localhost:5001');
```

#### Aktuelle Werte laden

```javascript
function loadLatestValues(baseUrl)
```

**Beschreibung**: Lädt aktuelle Sensorwerte für Dashboard-Tabelle

**Parameter**:
- `baseUrl`: API-Basis-URL

**Funktionalität**:
- Aktualisiert Temperatur-, Luftfeuchtigkeits- und Bodenfeuchtigkeitswerte
- Verwendet `data-pot-id` Attribut zur Identifikation

### UI-Komponenten

#### Sidebar-Toggle

```javascript
// Sidebar ein-/ausblenden
document.getElementById('sidebar-toggle').addEventListener('click', function(e) {
    e.stopPropagation();
    document.body.classList.toggle('sidebar-collapsed');
});
```

#### Dark Mode

```javascript
// Dark Mode umschalten
const darkPref = localStorage.getItem('darkMode') === 'true';
document.body.classList.toggle('dark-mode', darkPref);
```

#### Profil-Dropdown

```javascript
// Profil-Dropdown öffnen/schließen
avatarBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    dropdownParent.classList.toggle('open');
});
```

## Template-System

### Base Template (`base.html`)

**Beschreibung**: Grundlayout für alle Seiten

**Blöcke**:
- `title`: Seitentitel
- `page_title`: Überschrift in der Topbar
- `content`: Hauptinhalt

**Features**:
- Responsive Design
- Sidebar mit Zimmer- und Pflanzennavigation
- Profil-Dropdown
- Dark Mode Toggle

**Beispiel**:
```html
{% extends 'base.html' %}

{% block title %}Meine Seite{% endblock %}
{% block page_title %}Seitenüberschrift{% endblock %}

{% block content %}
<div class="dashboard">
    <!-- Seiteninhalt -->
</div>
{% endblock %}
```

### Dashboard Template (`dashboard.html`)

**Beschreibung**: Zimmer-Dashboard mit Pflanzenübersicht

**Funktionen**:
- Schnellübersicht-Tabelle mit Ist/Soll-Werten
- Diagramme für verschiedene Sensordaten
- Pflanzen-Fakten-Box

**Verwendung**:
```python
return render_template('dashboard.html', 
                      room="Wohnzimmer", 
                      room_slug="wohnzimmer",
                      room_plants=pflanzen_liste)
```

### Pflanzen-Detail Template (`plant.html`)

**Beschreibung**: Detailansicht und Bearbeitung einer Pflanze

**Funktionen**:
- Bearbeitung von Zielwerten
- Fakten-Eingabe
- Zimmerzuordnung
- Automatisches Speichern via API

**JavaScript-Integration**:
```javascript
// Automatisches Speichern bei Klick
document.getElementById('save-facts-btn').addEventListener('click', async function() {
    const data = {
        facts: document.getElementById('facts-textarea').value,
        // ... weitere Felder
    };
    await fetch('/api/plant/{{ plant.id }}', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
});
```

### Authentifizierungs-Templates

#### Login (`login.html`)

**Beschreibung**: Anmeldeformular

**Features**:
- E-Mail/Passwort-Eingabe
- Fehlerbehandlung
- Weiterleitung nach erfolgreicher Anmeldung

#### Registrierung (`register.html`)

**Beschreibung**: Registrierungsformular

**Features**:
- E-Mail-Validierung
- Passwort-Bestätigung
- Fehlerbehandlung

#### Einstellungen (`settings.html`)

**Beschreibung**: Benutzereinstellungen

**Features**:
- E-Mail-Änderung
- Passwort-Änderung
- Dark Mode Toggle
- Erfolgsmeldungen

## Styling-Komponenten

### CSS-Architektur

#### Layout-System

```css
/* Hauptlayout */
.topbar { /* Obere Navigationsleiste */ }
.sidebar { /* Seitennavigation */ }
.content { /* Hauptinhalt */ }
```

#### Responsive Design

```css
@media (max-width: 650px) {
    .topbar {
        flex-direction: column;
        height: auto;
    }
}
```

#### Dark Mode

```css
body.dark-mode {
    background-color: #1a1a1a;
    color: #e0e0e0;
}
```

### Komponenten-Klassen

#### Karten-System

```css
.card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.full-width-card {
    width: 100%;
    margin-bottom: 20px;
}
```

#### Tabellen

```css
.care-table {
    width: 100%;
    border-collapse: collapse;
}

.care-table th,
.care-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}
```

#### Formulare

```css
.auth-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
    max-width: 400px;
}

.auth-form input {
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
}
```

## Verwendungsbeispiele

### 1. Neue Pflanze hinzufügen

```python
# Backend: Pflanze über API hinzufügen
@app.route('/api/plant', methods=['POST'])
@login_required
def add_plant():
    data = request.get_json()
    # API-Aufruf zur Pflanzenerstellung
    response = requests.post(f"{API_BASE}/plants", json=data)
    return jsonify(response.json())
```

### 2. Sensordaten abrufen

```javascript
// Frontend: Aktuelle Werte laden
async function loadCurrentValues(potId) {
    const response = await fetch(`/api/latest-values?pot_id=${potId}`);
    const data = await response.json();
    
    document.querySelector('.val-temp').textContent = data.temperature;
    document.querySelector('.val-air').textContent = data.air_humidity;
    document.querySelector('.val-soil').textContent = data.soil_moisture;
}
```

### 3. Benutzerregistrierung

```python
# Vollständiges Registrierungsbeispiel
@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validierung
    if not is_valid_email(email):
        return render_template('register.html', 
                             error='Ungültige E-Mail-Adresse!')
    
    # Passwort hashen
    hashed = hash_password(password)
    
    # Benutzer erstellen
    response = requests.get(f"{API_BASE}/insert/insert-user",
                          params={"user_mail": email, 
                                "password_hash": hashed})
    
    if response.status_code == 200:
        session['user_id'] = email
        return redirect(url_for('index'))
    
    return render_template('register.html', 
                         error='Registrierung fehlgeschlagen!')
```

### 4. Dashboard-Daten laden

```python
# Dashboard mit Pflanzenübersicht
@app.route('/dashboard/<slug>')
@login_required
def dashboard(slug):
    # Zimmer finden
    rooms = fetch_rooms()
    room = next((r for r in rooms if slugify(r['name']) == slug), None)
    
    if not room:
        return "Zimmer nicht gefunden", 404
    
    # Pflanzen im Zimmer
    plants = fetch_plants()
    room_plants = [p for p in plants if p.get('room') == room['name']]
    
    return render_template('dashboard.html', 
                         room=room['name'], 
                         room_slug=slug,
                         room_plants=room_plants)
```

### 5. Pflanzendaten aktualisieren

```javascript
// Frontend: Pflanzendaten speichern
async function savePlantData(plantId) {
    const data = {
        name: document.getElementById('plant-name').value,
        facts: document.getElementById('facts-textarea').value,
        target_temperature: document.getElementById('target-temperature').value,
        target_air_humidity: document.getElementById('target-air-humidity').value,
        target_ground_humidity: document.getElementById('target-ground-humidity').value,
        room: document.getElementById('room-select').value
    };
    
    const response = await fetch(`/api/plant/${plantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        alert('Gespeichert');
    } else {
        alert('Fehler beim Speichern');
    }
}
```

## Fehlerbehebung

### Häufige Probleme

1. **API-Verbindung fehlgeschlagen**
   - Überprüfen Sie die `API_BASE` Konfiguration
   - Stellen Sie sicher, dass die Plantify-API läuft

2. **Session-Probleme**
   - Setzen Sie `SECRET_KEY` Umgebungsvariable
   - Überprüfen Sie Browser-Cookies

3. **Template-Fehler**
   - Überprüfen Sie Template-Pfade
   - Stellen Sie sicher, dass alle Template-Variablen verfügbar sind

### Debug-Modus

```python
# Aktivierung des Debug-Modus
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
```

## Sicherheitshinweise

1. **SECRET_KEY**: Verwenden Sie immer einen sicheren, zufälligen Schlüssel in Produktion
2. **HTTPS**: Verwenden Sie HTTPS für alle Produktionsumgebungen
3. **Input-Validierung**: Alle Benutzereingaben werden validiert
4. **Passwort-Hashing**: PBKDF2 mit 100.000 Iterationen
5. **Session-Management**: Sichere Session-Cookies

## Lizenz und Support

Diese Dokumentation beschreibt die öffentlichen APIs und Komponenten des Plantify Webinterfaces. Für weitere Fragen oder Support wenden Sie sich an das Entwicklungsteam.

---

*Dokumentation erstellt am: $(date)*
*Version: 1.0*