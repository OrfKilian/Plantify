from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from functools import wraps
import os
import base64
import hashlib  # Explicitly import hashlib
from email_validator import validate_email, EmailNotValidError
import requests
import requests.exceptions  # Neu: Für spezifische Request-Fehler
from typing import Optional
import urllib.parse
import logging  # Neu: Für Logging statt print()
import sys  # Neu: Für sys.exit()

# --- Logging Konfiguration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- SECRET_KEY Handhabung ---
secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    logging.critical(
        "FATALER FEHLER: Umgebungsvariable SECRET_KEY nicht gesetzt. "
        "Anwendung kann nicht sicher gestartet werden. Bitte setze SECRET_KEY."
    )
    sys.exit(1)  # Beendet die Anwendung, wenn der Schlüssel fehlt
app.secret_key = secret_key

API_BASE = 'http://plantify-api:5001'

PLANT_OVERRIDES = {}


# --- Hilfsfunktionen für API-Aufrufe mit verbesserter Fehlerbehandlung ---
def _encode_form_data(data: dict) -> dict:
    """
    Encode form data to handle special characters properly.
    This ensures that special characters in form inputs are correctly processed.
    """
    encoded_data = {}
    for key, value in data.items():
        if value is not None:
            # Ensure the value is properly encoded for database storage
            encoded_data[key] = str(value).strip()
        else:
            encoded_data[key] = value
    return encoded_data


def _make_api_request(method: str, endpoint: str, user_mail: Optional[str] = None, data: Optional[dict] = None,
                      params: Optional[dict] = None):
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}  # Standardmäßig JSON
    
    # URL-encode query parameters to handle special characters
    if params:
        encoded_params = {}
        for key, value in params.items():
            if value is not None:
                encoded_params[key] = urllib.parse.quote_plus(str(value))
            else:
                encoded_params[key] = value
        params = encoded_params
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, params=params)  # params für mögliche GET-Parameter bei POST
        elif method == "PATCH":
            response = requests.patch(url, json=data, params=params)  # params für mögliche GET-Parameter bei PATCH
        elif method == "DELETE":
            response = requests.delete(url, json=data, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()  # Löst HTTPError für 4xx/5xx Statuscodes aus
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"API HTTP-Fehler ({method} {url}): Status {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        logging.error(f"API Verbindungsfehler ({method} {url}): {e}")
        return None
    except requests.exceptions.Timeout as e:
        logging.error(f"API Timeout Fehler ({method} {url}): {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Unbekannter API-Fehler ({method} {url}): {e}")
        return None


# --- Aktualisierte fetch_rooms() ---
def fetch_rooms():
    user = session.get('user_id')
    if not user:
        return []

    response_data = _make_api_request("GET", "/json/pots", params={"user_mail": user})
    if response_data:
        return [
            {"name": p.get("pot_name", p.get("name", "")), "id": p.get("pot_id")}
            for p in response_data
        ]
    return []


# --- Aktualisierte fetch_plants() ---
def fetch_plants():
    user = session.get('user_id')
    if not user:
        return []

    response_data = _make_api_request("GET", "/json/plants", params={"user_mail": user})
    if response_data:
        plants = []
        for item in response_data:
            plant = {
                "id": item.get("plant_id"),
                "name": item.get("name"),
                "facts": item.get("description", ""),
                "room": item.get("pot_name", item.get("name", "Unbekannter Raum")),  # Verbesserte Konsistenz
                "target_temperature": item.get("target_temperature_celsius"),
                "target_air_humidity": item.get("target_air_humidity_percent"),
                "target_ground_humidity": item.get("target_soil_moisture_percent"),
            }
            if plant["id"] in PLANT_OVERRIDES:
                plant.update(PLANT_OVERRIDES[plant["id"]])
            plants.append(plant)
        return plants
    return []


@app.context_processor
def inject_sidebar_data():
    return dict(rooms=fetch_rooms(), plants=fetch_plants())


def slugify(value: str) -> str:
    return value.lower().replace(" ", "-")


def is_valid_email(email: str) -> bool:
    """Validate an email address using the email-validator package."""
    if not email:
        return False
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def hash_password(password: str, iterations: int = 100_000) -> str:
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode()
    hash_b64 = base64.b64encode(hash_bytes).decode()
    value = f"{iterations}${salt_b64}${hash_b64}"
    return urllib.parse.quote_plus(value)


def check_password(password: str, hashed: str) -> bool:
    try:
        hashed = urllib.parse.unquote_plus(hashed)
        iterations, salt_b64, hash_b64 = hashed.split('$')
        iterations = int(iterations)
        salt = base64.b64decode(salt_b64)
        hash_true = base64.b64decode(hash_b64)
    except Exception as e:
        logging.error(f"Fehler beim Parsen des gehashten Passworts: {e}")
        return False
    hash_test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hash_test == hash_true


# --- Login-Decorator für geschützte Seiten ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "info")  # Beispiel für Flash
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
@login_required
def index():
    return render_template('home.html')


# --- Aktualisierte get_password_hash() ---
def get_password_hash(email: str) -> Optional[str]:
    response_data = _make_api_request("GET", "/json/password_hash", params={"user_mail": email})
    if response_data:
        if isinstance(response_data, list) and response_data:
            return response_data[0].get("password_hash")
        if isinstance(response_data, dict):
            return response_data.get("password_hash")
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.debug("Login-Route aufgerufen, Methode: %s", request.method)
    if request.method == 'POST':
        logging.debug("Formulardaten: %s", request.form)
        form_data = _encode_form_data(request.form.to_dict())
        email = form_data.get('email')
        password = form_data.get('password')
        hashed = get_password_hash(email)
        logging.debug("E-Mail: %s", email)
        logging.debug(
            "Passwort (nicht gehasht): [ausgeblendet aus Sicherheitsgründen]")  # Keine Klartext-Passwörter loggen
        logging.debug("Gehasht: %s", hashed)
        if hashed and check_password(password, hashed):
            session['user_id'] = email
            logging.info("Benutzer %s erfolgreich angemeldet.", email)
            next_page = request.args.get('next')
            flash("Erfolgreich angemeldet!", "success")
            return redirect(next_page or url_for('index'))
        flash("Falsche Login-Daten!", "danger")
        logging.warning("Fehlgeschlagener Login-Versuch für E-Mail: %s", email)
        return render_template('login.html', error='Falsche Login-Daten!')
    return render_template('login.html')


@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)  # user_id aus der Session entfernen
    if user_id:
        logging.info("Benutzer %s abgemeldet.", user_id)
        flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for('login'))  # Nach dem Logout zur Login-Seite weiterleiten


@app.route('/dashboard/<slug>')
@login_required
def dashboard(slug):
    rooms = fetch_rooms()
    plants = fetch_plants()
    room = next((r for r in rooms if slugify(r['name']) == slug), None)
    if not room:
        logging.warning("Dashboard-Zugriff: Zimmer-Slug '%s' nicht gefunden für Benutzer '%s'.", slug,
                        session.get('user_id'))
        flash("Zimmer nicht gefunden.", "warning")
        return "Zimmer nicht gefunden", 404
    room_plants = [p for p in plants if p.get('room') == room['name']]
    return render_template('dashboard.html', room=room['name'], room_slug=slug,
                           room_plants=room_plants)


# Seite zum Umbenennen der Zimmer
@app.route('/rooms')
@login_required
def rooms_page():
    rooms = fetch_rooms()
    room_entries = [{'name': r['name'], 'slug': slugify(r['name'])} for r in rooms]
    return render_template('rooms.html', rooms=room_entries)


# Plantendetail und Bearbeitung
@app.route('/pflanze/<slug>')
@login_required
def plant_detail(slug):
    plants = fetch_plants()
    rooms = fetch_rooms()
    plant = None
    plant_id_part = slug.rsplit('-', 1)[-1]
    if plant_id_part.isdigit():
        plant = next((p for p in plants if str(p['id']) == plant_id_part), None)
    if not plant:
        plant = next((p for p in plants if slugify(p['name']) == slug), None)
    if not plant:
        logging.warning("Pflanzen-Detail: Pflanze mit Slug '%s' nicht gefunden für Benutzer '%s'.", slug,
                        session.get('user_id'))
        flash("Pflanze nicht gefunden.", "warning")
        return "Pflanze nicht gefunden", 404
    return render_template('plant.html', plant=plant, rooms=rooms,
                           trivial=plant['name'], botanisch=plant['name'])


@app.route('/api/plant/<int:plant_id>', methods=['POST'])
@login_required
def update_plant_api(plant_id: int):
    data = request.get_json(silent=True) or {}
    
    # Encode the data to handle special characters properly
    encoded_data = _encode_form_data(data)
    
    if plant_id not in PLANT_OVERRIDES:
        PLANT_OVERRIDES[plant_id] = {}
    PLANT_OVERRIDES[plant_id].update(encoded_data)
    logging.info("Plant override updated for plant_id %d by user %s: %s", plant_id, session.get('user_id'), encoded_data)
    return jsonify({'success': True})


# Einstellungen
@app.route('/settings')
@login_required
def settings():
    # msg_pw und msg_email können jetzt durch Flash-Nachrichten ersetzt werden
    return render_template('settings.html')


# --- Aktualisierte change_email() ---
@app.route('/settings/change-email', methods=['POST'])
@login_required
def change_email():
    form_data = _encode_form_data(request.form.to_dict())
    new_email = form_data.get('new_email')
    current_email = session.get('user_id')

    if not new_email or not is_valid_email(new_email):
        flash("Ungültige neue E-Mail-Adresse!", "danger")
        logging.warning("E-Mail-Änderung fehlgeschlagen für Benutzer %s: Ungültige neue E-Mail '%s'.", current_email,
                        new_email)
        return redirect(url_for('settings'))

    if not current_email:  # Sollte durch login_required abgedeckt sein, aber als Fallback
        flash("Sitzungsinformationen fehlen. Bitte melden Sie sich erneut an.", "danger")
        logging.error("E-Mail-Änderung fehlgeschlagen: Kein aktueller Benutzer in der Sitzung.")
        return redirect(url_for('login'))

    response_data = _make_api_request(
        "PATCH",
        "/update/update-user_mail",
        data={"user_mail_new": new_email, "user_mail": current_email}
    )

    if response_data:
        session['user_id'] = new_email
        flash("E-Mail-Adresse erfolgreich geändert!", "success")
        logging.info("Benutzer %s hat E-Mail-Adresse zu %s geändert.", current_email, new_email)
        return redirect(url_for('settings'))
    else:
        flash("Fehler beim Ändern der E-Mail-Adresse. Bitte versuchen Sie es später erneut.", "danger")
        logging.error("E-Mail-Änderung für Benutzer %s fehlgeschlagen (API-Antwort null).", current_email)
    return redirect(url_for('settings'))


# --- Aktualisierte change_password() ---
@app.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    form_data = _encode_form_data(request.form.to_dict())
    current_pw = form_data.get('current_password')
    new_pw = form_data.get('new_password')
    confirm_pw = form_data.get('confirm_password')
    current_email = session.get('user_id')

    hashed = get_password_hash(current_email)
    if not hashed or not check_password(current_pw, hashed):
        flash("Aktuelles Passwort ist falsch!", "danger")
        logging.warning("Passwortänderung fehlgeschlagen für Benutzer %s: Aktuelles Passwort falsch.", current_email)
        return redirect(url_for('settings'))

    if not new_pw or new_pw != confirm_pw:
        flash("Neues Passwort und Bestätigung stimmen nicht überein!", "danger")
        logging.warning("Passwortänderung fehlgeschlagen für Benutzer %s: Neue Passwörter stimmen nicht überein.",
                        current_email)
        return redirect(url_for('settings'))

    new_hash = hash_password(new_pw)

    response_data = _make_api_request(
        "PATCH",
        "/update/update-user_password",
        data={"password_hash": new_hash, "user_mail": current_email}
    )

    if response_data:
        flash("Passwort erfolgreich geändert!", "success")
        logging.info("Passwort für Benutzer %s erfolgreich geändert.", current_email)
        return redirect(url_for('settings'))
    else:
        flash("Fehler beim Ändern des Passworts. Bitte versuchen Sie es später erneut.", "danger")
        logging.error("Passwortänderung für Benutzer %s fehlgeschlagen (API-Antwort null).", current_email)
    return redirect(url_for('settings'))


# --- Aktualisierte register() ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        form_data = _encode_form_data(request.form.to_dict())
        email = form_data.get('email')
        password = form_data.get('password')
        confirm = form_data.get('confirm_password')

        if not email or not password:
            flash('E-Mail und Passwort sind erforderlich!', "danger")
            return render_template('register.html', error='E-Mail und Passwort erforderlich!')
        if not is_valid_email(email):
            flash('Ungültige E-Mail-Adresse!', "danger")
            return render_template('register.html', error='Ungültige E-Mail-Adresse!')
        if password != confirm:
            flash('Passwörter stimmen nicht überein!', "danger")
            return render_template('register.html', error='Passwörter stimmen nicht überein!')
        if get_password_hash(email):  # Prüft, ob E-Mail bereits existiert
            flash('Diese E-Mail-Adresse ist bereits registriert!', "warning")
            return render_template('register.html', error='E-Mail existiert bereits!')

        hashed = hash_password(password)

        response_data = _make_api_request(
            "POST",
            "/insert/insert-user",
            data={"user_mail": email, "password_hash": hashed}
        )

        if response_data:
            session['user_id'] = email
            logging.info("Neuer Benutzer %s erfolgreich registriert.", email)
            flash("Registrierung erfolgreich! Willkommen bei Plantify!", "success")
            return redirect(url_for('index'))
        else:
            flash("Registrierung fehlgeschlagen! Bitte versuchen Sie es später erneut.", "danger")
            logging.error("Registrierung für E-Mail %s fehlgeschlagen (API-Antwort null).", email)
        return render_template('register.html', error='Registrierung fehlgeschlagen!')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)