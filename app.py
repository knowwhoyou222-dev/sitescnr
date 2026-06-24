from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json, os, random, datetime

app = Flask(__name__)
app.secret_key = 'satan_scanner_secret_key'

KEYS_FILE = "keys.json"
REPORTS_FILE = "reports.json"

def load(file):
    if not os.path.exists(file): return []
    try:
        with open(file, "r") as f: return json.load(f)
    except: return []

def save(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

@app.before_request
def bypass_api():
    # Λίστα με όλα τα API endpoints που δεν χρειάζονται login
    allowed = ['/activate-key', '/submit-report', '/create-key', '/get-reports', '/login']
    if request.path in allowed or request.path.startswith('/static'):
        return None
    if 'user' not in session and request.endpoint != 'login':
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == "12132":
            session['user'] = "admin"
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route("/scans")
def scans_page():
    return render_template('scans.html')

# --- API ENDPOINTS (ΟΧΙ HTML) ---

@app.route("/get-reports", methods=["GET"])
def get_reports():
    return jsonify(load(REPORTS_FILE))

@app.route("/create-key", methods=["POST"])
def create_key():
    keys = load(KEYS_FILE)
    new_key = f"SATAN-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    keys.append({"key": new_key, "used": False})
    save(KEYS_FILE, keys)
    return jsonify({"success": True, "key": new_key})

@app.route("/submit-report", methods=["POST"])
def submit_report():
    data = request.get_json()
    # Προσθήκη ημερομηνίας αν δεν υπάρχει
    if "date" not in data:
        data["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    reports = load(REPORTS_FILE)
    reports.append(data)
    save(REPORTS_FILE, reports)
    return jsonify({"success": True})

@app.route("/activate-key", methods=["POST"])
def activate_key():
    data = request.get_json()
    keys = load(KEYS_FILE)
    for k in keys:
        if k.get("key") == data.get("key") and not k.get("used", False):
            k["used"] = True
            save(KEYS_FILE, keys)
            return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
