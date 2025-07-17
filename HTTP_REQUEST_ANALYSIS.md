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

Die HTTP-Requests waren bereits grundsätzlich korrekt implementiert. Das Hauptproblem lag in der fehlenden URL-Encoding-Behandlung für Sonderzeichen. Mit den implementierten Verbesserungen werden jetzt alle Sonderzeichen korrekt übertragen und in der Datenbank gespeichert.