# 🧪 Test User Setup für Plantify

Dieses Verzeichnis enthält Skripte zum Erstellen eines Test-Benutzers für die Plantify-Anwendung.

## 📋 Test-Benutzer Details

Der Test-Benutzer ist **eindeutig gekennzeichnet** als Test-Account:

- **📧 E-Mail:** `test.user@plantify.test`
- **🔑 Passwort:** `TestUser123!`
- **🏷️ Kennzeichnung:** Eindeutig als TEST USER markiert
- **⚠️ Warnung:** Dieser Account ist NUR für Tests gedacht!

## 🚀 Verwendung

### Option 1: Direkte API-Erstellung
```bash
cd Plantify_Webinterface
python3 create_test_user.py
```

### Option 2: Über Flask-Registrierung
```bash
cd Plantify_Webinterface
python3 add_test_user_via_app.py
```

## 📋 Voraussetzungen

### Für Option 1 (API-Erstellung):
- Die Plantify API muss auf `http://plantify-api:5001` laufen
- Python-Paket `requests` muss installiert sein

### Für Option 2 (Flask-Registrierung):
- Die Flask-App muss auf `http://localhost:8080` laufen
- Python-Paket `requests` muss installiert sein

## 🔧 Installation der Abhängigkeiten

```bash
pip install requests
```

## ✅ Nach der Erstellung

Nach erfolgreicher Erstellung des Test-Users können Sie sich mit folgenden Daten anmelden:

- **🌐 Login-URL:** `http://localhost:8080/login`
- **📧 E-Mail:** `test.user@plantify.test`
- **🔑 Passwort:** `TestUser123!`

## ⚠️ Wichtige Hinweise

1. **Test-Kennzeichnung:** Der Benutzer ist eindeutig als TEST USER gekennzeichnet
2. **Keine Produktionsnutzung:** Dieser Account ist NUR für Tests gedacht
3. **Aufräumen:** Löschen Sie den Test-User nach Abschluss der Tests
4. **Sicherheit:** Das Passwort ist bewusst einfach - nur für Tests verwenden!

## 🗑️ Test-User löschen

Der Test-User kann über die normale Benutzeroberfläche der Anwendung gelöscht werden oder direkt über die API/Datenbank.

## 🔍 Fehlerbehebung

### "Could not connect to API"
- Überprüfen Sie, ob die API läuft: `http://plantify-api:5001`
- Prüfen Sie die Netzwerkverbindung

### "Could not connect to Flask app"
- Überprüfen Sie, ob die Flask-App läuft: `http://localhost:8080`
- Starten Sie die App mit: `python3 app.py`

### "Test user already exists"
- Der Test-User existiert bereits
- Sie können sich mit den vorhandenen Credentials anmelden
- Oder löschen Sie den User und erstellen ihn neu

## 📝 Skript-Details

### `create_test_user.py`
- Erstellt den User direkt über die API
- Verwendet dieselbe Passwort-Hash-Funktion wie die App
- Schneller und direkter Ansatz

### `add_test_user_via_app.py`
- Erstellt den User über die Flask-Registrierung
- Simuliert die normale Benutzerregistrierung
- Testet gleichzeitig die Registrierungsfunktion