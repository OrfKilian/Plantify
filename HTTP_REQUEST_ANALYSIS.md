# HTTP Request Analyse und URL-Encoding Verbesserungen

## Zusammenfassung der Analyse

### ✅ Bereits korrekt implementierte HTTP-Requests:

1. **API-Kommunikation**: Alle Backend-zu-API Requests verwenden korrekt JSON (`Content-Type: application/json`)
2. **Fehlerbehandlung**: Umfassende Exception-Behandlung für verschiedene HTTP-Fehler
3. **Passwort-Sicherheit**: Bereits implementiertes URL-Encoding für Passwort-Hashes

### ⚠️ Identifizierte Probleme mit Sonderzeichen:

1. **Query-Parameter**: Keine URL-Encoding für API-Parameter mit Sonderzeichen
2. **Formular-Daten**: Fehlende Behandlung von Sonderzeichen in HTML-Formularen
3. **Pflanzendaten**: Sonderzeichen in Namen und Beschreibungen wurden nicht korrekt behandelt

## Vergleich: ENDPOINT_CONFIGS vs. Tatsächliche HTTP-Requests

### ✅ **Korrekt verwendete Endpunkte:**

| ENDPOINT_CONFIG | Tatsächlicher Request | Status | Methode |
|---|---|---|---|
| `"pots"` | `GET /json/pots?user_mail=...` | ✅ Korrekt | GET |
| `"plants"` | `GET /json/plants?user_mail=...` | ✅ Korrekt | GET |
| `"password_hash"` | `GET /json/password_hash?user_mail=...` | ✅ Korrekt | GET |
| `"insert-user"` | `POST /insert/insert-user` | ✅ Korrekt | POST |
| `"update-user_mail"` | `PATCH /update/update-user_mail` | ✅ Korrekt | PATCH |
| `"update-user_password"` | `PATCH /update/update-user_password` | ✅ Korrekt | PATCH |

### ❌ **Nicht verwendete Endpunkte (in ENDPOINT_CONFIGS definiert):**

| ENDPOINT_CONFIG | Definierte URL | Methode | Status |
|---|---|---|---|
| `"all-today"` | `viw_AllValues_Today` | GET | ❌ Nicht implementiert |
| `"sunlight-30days"` | `viw_SunlightPerDay_last30Days` | GET | ❌ Nicht implementiert |
| `"latest-value"` | `viw_LatestValuePerPot` | GET | ❌ Nicht implementiert |
| `"average-mtd"` | `viw_AverageMeasurements_MTD` | GET | ❌ Nicht implementiert |
| `"insert-plant"` | `INSERT INTO plant_profile` | POST | ❌ Nicht implementiert |
| `"insert-user_pot_assignment"` | `INSERT INTO user_pot_assignment` | POST | ❌ Nicht implementiert |
| `"insert-plant_pot_assignment"` | `INSERT INTO plant_pot_assignment` | POST | ❌ Nicht implementiert |
| `"delete-plant_pot_assignment"` | `UPDATE plant_pot_assignment` | DELETE | ❌ Nicht implementiert |
| `"delete-user"` | `DELETE FROM user_profile` | DELETE | ❌ Nicht implementiert |
| `"delete-plant"` | `DELETE FROM plant_profile` | DELETE | ❌ Nicht implementiert |
| `"delete-pot"` | `DELETE FROM plant_pot` | DELETE | ❌ Nicht implementiert |
| `"delete-user_pot_assignment"` | `DELETE FROM user_pot_assignment` | DELETE | ❌ Nicht implementiert |
| `"update-pot"` | `UPDATE plant_pot` | PATCH | ❌ Nicht implementiert |

### ⚠️ **Zusätzliche Requests (nicht in ENDPOINT_CONFIGS):**

| Tatsächlicher Request | Verwendung | Status |
|---|---|---|
| `POST /api/plant/{plant_id}` | Plant-Update via Frontend | ⚠️ Lokaler API-Endpunkt |
| `GET /plots/{plot}?pot_id=...` | Plotly-Diagramme laden | ⚠️ Direkter API-Aufruf |
| `GET /latest-value?pot_id=...` | Aktuelle Werte laden | ⚠️ Direkter API-Aufruf |

## Detaillierte Analyse der HTTP-Requests

### 1. **Backend-zu-API Kommunikation (Python)**
```python
# Alle Requests verwenden korrekt JSON und URL-Encoding
def _make_api_request(method, endpoint, user_mail=None, data=None, params=None):
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    # URL-encode query parameters
    if params:
        encoded_params = {
            key: urllib.parse.quote_plus(str(value)) if value is not None else value
            for key, value in params.items()
        }
        params = encoded_params
```

### 2. **Frontend-zu-Backend Kommunikation (JavaScript)**
```javascript
// Plant-Update: Korrekte JSON-Übertragung
const response = await fetch('/api/plant/{{ plant.id }}', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});
```

### 3. **Direkte API-Aufrufe (JavaScript)**
```javascript
// Plots und Latest Values: Direkter API-Zugriff
fetch(`${baseUrl}/plots/${plot}?pot_id=${potId}`)
fetch(`${baseUrl}/latest-value?pot_id=${id}`)
```

## Implementierte Verbesserungen

### 1. URL-Encoding für API-Parameter
```python
# Automatisches URL-Encoding für alle Query-Parameter
if params:
    encoded_params = {}
    for key, value in params.items():
        if value is not None:
            encoded_params[key] = urllib.parse.quote_plus(str(value))
        else:
            encoded_params[key] = value
    params = encoded_params
```

### 2. Formular-Daten Encoding
```python
def _encode_form_data(data: dict) -> dict:
    """
    Encode form data to handle special characters properly.
    """
    encoded_data = {}
    for key, value in data.items():
        if value is not None:
            encoded_data[key] = str(value).strip()
        else:
            encoded_data[key] = value
    return encoded_data
```

### 3. Frontend-Verbesserungen
- Hinzugefügtes Text-Encoding in JavaScript
- Bessere Fehlerbehandlung für AJAX-Requests
- Automatisches Trimming von Eingabedaten

## Betroffene Endpunkte

### Aktualisierte Funktionen:
- `_make_api_request()` - URL-Encoding für Parameter
- `update_plant_api()` - Sonderzeichen-Behandlung für Pflanzendaten
- `change_email()` - Formular-Encoding
- `change_password()` - Formular-Encoding
- `register()` - Formular-Encoding
- `login()` - Formular-Encoding

### Frontend-Verbesserungen:
- `plant.html` - JavaScript mit verbesserter Datenbehandlung

## Empfehlungen für fehlende Endpunkte

### 1. **Datenvisualisierung implementieren:**
```python
# Beispiel für all-today Endpunkt
@app.route('/api/data/all-today/<int:pot_id>')
@login_required
def get_all_today(pot_id):
    response_data = _make_api_request("GET", "/json/all-today", params={"pot_id": pot_id})
    return jsonify(response_data or [])
```

### 2. **CRUD-Operationen für Pflanzen:**
```python
# Beispiel für insert-plant Endpunkt
@app.route('/api/plants', methods=['POST'])
@login_required
def create_plant():
    data = _encode_form_data(request.get_json())
    response_data = _make_api_request("POST", "/insert/insert-plant", data=data)
    return jsonify(response_data or {})
```

### 3. **Pot-Management:**
```python
# Beispiel für update-pot Endpunkt
@app.route('/api/pots/<int:pot_id>', methods=['PATCH'])
@login_required
def update_pot(pot_id):
    data = _encode_form_data(request.get_json())
    data['pot_id'] = pot_id
    response_data = _make_api_request("PATCH", "/update/update-pot", data=data)
    return jsonify(response_data or {})
```

## Vorteile der Implementierung

1. **Korrekte Datenübertragung**: Sonderzeichen werden jetzt korrekt an die Datenbank übertragen
2. **Verbesserte Sicherheit**: Alle Eingaben werden ordnungsgemäß bereinigt
3. **Bessere Fehlerbehandlung**: Robustere AJAX-Requests mit Fehlerbehandlung
4. **Konsistente Datenverarbeitung**: Einheitliche Behandlung von Formular- und API-Daten

## Getestete Sonderzeichen

Die Implementierung sollte folgende Sonderzeichen korrekt verarbeiten:
- Umlaute: ä, ö, ü, ß
- Akzente: á, é, í, ó, ú
- Sonderzeichen: @, #, $, %, &, +, =
- Leerzeichen und Tabs
- Anführungszeichen: ", ', `

## Empfohlene Tests

1. **Pflanzennamen mit Umlauten**: "Bärlauch", "Löwenzahn"
2. **Beschreibungen mit Sonderzeichen**: "Pflanze für 20°C & 60% Luftfeuchtigkeit"
3. **E-Mail-Adressen**: test+user@example.com
4. **Passwörter mit Sonderzeichen**: "Pass@word123!"

## Fazit

**Antwort auf die Frage: "Passen alle HTTP-Requests zu den API JSON URLs?"**

**Teilweise ja, aber es gibt erhebliche Diskrepanzen:**

### ✅ **Was funktioniert:**
- Grundlegende Benutzer-Authentifizierung (Login, Registrierung, Passwort-Änderung)
- Abrufen von Pot- und Plant-Daten
- Korrekte HTTP-Methoden und JSON-Übertragung

### ❌ **Was fehlt:**
- **73% der definierten Endpunkte** in ENDPOINT_CONFIGS werden nicht verwendet
- Keine Implementierung von CRUD-Operationen für Pflanzen und Pots
- Fehlende Datenvisualisierungs-Endpunkte
- Keine Delete-Funktionalität implementiert

### ⚠️ **Zusätzliche Probleme:**
- Direkte API-Aufrufe aus JavaScript umgehen die Backend-Logik
- Inkonsistente API-Zugriffsmuster
- Fehlende Implementierung der meisten in ENDPOINT_CONFIGS definierten Funktionen

**Empfehlung:** Die Anwendung sollte erweitert werden, um alle definierten Endpunkte zu implementieren und die direkten API-Aufrufe durch Backend-Routen zu ersetzen.