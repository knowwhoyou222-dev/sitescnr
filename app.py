from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from pymongo import MongoClient
import os
import random
import datetime

app = Flask(__name__)
app.secret_key = 'satan_scanner_secret_key'

# Σύνδεση με τη MongoDB
MONGO_URI = "mongodb+srv://knowwhoyou222_db_user:GwjVFikrNWFJYsKo@satanbase.pbyoxk0.mongodb.net/satanbase?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client['satanbase']
reports_collection = db['reports']
keys_collection = db['keys']

@app.before_request
def bypass_api():
    allowed = ['/activate-key', '/submit-report', '/create-key', '/get-reports', '/get-scan-count', '/login']
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

# --- API ENDPOINTS ---

@app.route("/get-reports", methods=["GET"])
def get_reports():
    return jsonify(list(reports_collection.find({}, {"_id": 0})))

@app.route("/get-scan-count", methods=["GET"])
def get_scan_count():
    count = reports_collection.count_documents({})
    return jsonify({"count": count})

@app.route("/create-key", methods=["POST"])
def create_key():
    new_key = f"SATAN-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
    keys_collection.insert_one({"key": new_key, "used": False})
    return jsonify({"success": True, "key": new_key})

@app.route("/submit-report", methods=["POST"])
def submit_report():
    data = request.get_json()
    if "date" not in data:
        data["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    reports_collection.insert_one(data)
    return jsonify({"success": True})

@app.route("/activate-key", methods=["POST"])
def activate_key():
    data = request.get_json()
    key_doc = keys_collection.find_one({"key": data.get("key"), "used": False})
    if key_doc:
        keys_collection.update_one({"key": data.get("key")}, {"$set": {"used": True}})
        return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
