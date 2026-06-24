from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import uuid

app = Flask(__name__)
app.secret_key = 'satan_scanner_secret_key'

# Ρυθμίσεις χρηστών
USERS = {"mrsoza": "12132"}

keys = []
used_keys = []
scans = []

# --- ΑΥΤΟΜΑΤΟΣ ΕΛΕΓΧΟΣ LOGIN ---
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('login'))

# --- LOGIN ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect(url_for('home'))
        return "Λάθος στοιχεία!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# --- ΚΥΡΙΕΣ ΣΕΛΙΔΕΣ ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scans')
def scans_page():
    return render_template('scans.html', scans=scans)

# --- API ROUTES ---
@app.route('/api/generate-key', methods=['POST'])
def generate_key():
    new_key = str(uuid.uuid4())[:8].upper()
    keys.append(new_key)
    return jsonify({"key": new_key})

@app.route('/activate-key', methods=['POST'])
def activate_key():
    data = request.get_json(silent=True) or {}
    key = data.get("key")
    if key in keys and key not in used_keys:
        used_keys.append(key)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/scans', methods=['POST'])
def submit_report():
    data = request.get_json(silent=True) or {}
    scans.append(data)
    return jsonify({"success": True})

@app.route('/api/scans')
def get_scans():
    return jsonify(scans)

if __name__ == '__main__':
    app.run(debug=True)