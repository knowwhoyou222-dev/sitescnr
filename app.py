from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json, os

app = Flask(__name__)
app.secret_key = 'ogamiaasosoza'

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
    # Προσθέσαμε το /scans εδώ για να μην τρώει redirect στο login
    allowed = ['/activate-key', '/submit-report', '/scans', '/login']
    if request.path in allowed or request.path.startswith('/static'):
        return None
    if 'user' not in session:
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
    return render_template('index.html', reports=load(REPORTS_FILE))

# Διορθωμένο route για το /scans
@app.route("/scans", methods=["GET", "POST"])
def scans_page():
    if request.method == "POST":
        data = request.get_json()
        reports = load(REPORTS_FILE)
        reports.append(data)
        save(REPORTS_FILE, reports)
        return jsonify({"success": True})
    return render_template('scans.html', reports=load(REPORTS_FILE))

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

@app.route("/submit-report", methods=["POST"])
def submit_report():
    data = request.get_json()
    reports = load(REPORTS_FILE)
    reports.append(data)
    save(REPORTS_FILE, reports)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
