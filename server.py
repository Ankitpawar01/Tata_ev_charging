"""
Tata Power EV Analytics — Flask API Server with PostgreSQL & SQLite Support
Backed by PostgreSQL (tata_ev_db) with automatic graceful fallback to SQLite.
Run: python server.py
"""
import os
import webbrowser
import threading
import time
import hashlib
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import execute_query, execute_write, test_postgres, get_db, PG_HOST, PG_PORT, PG_DATABASE, PG_USER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)


def calculate_recommendations(records, weights):
    """MCDM Priority Scoring Engine."""
    if not records:
        return []
    max_ev = max((r.get("ev_count") or 0) for r in records) or 1
    max_sessions = max((r.get("sessions") or 0) for r in records) or 1
    max_gap = max((r.get("infra_gap") or 0) for r in records) or 1
    max_roi = max(float(r.get("roi") or 0) for r in records) or 1

    result = []
    for r in records:
        norm_ev = (r.get("ev_count") or 0) / max_ev
        norm_sessions = (r.get("sessions") or 0) / max_sessions
        norm_gap = (r.get("infra_gap") or 0) / max_gap
        norm_roi = float(r.get("roi") or 0) / max_roi

        score_raw = (
            norm_ev * weights.get("evDensity", 0.25) +
            norm_sessions * weights.get("demand", 0.25) +
            norm_gap * weights.get("infraGap", 0.25) +
            norm_roi * weights.get("roi", 0.25)
        ) * 100

        priority_score = round(min(100, max(0, score_raw)))

        if priority_score >= 75:
            priority_class = "Critical"
        elif priority_score >= 50:
            priority_class = "High"
        elif priority_score >= 30:
            priority_class = "Medium"
        else:
            priority_class = "Low"

        city = r.get("city", "")
        ev_count = r.get("ev_count", 0)
        infra_gap = r.get("infra_gap", 0)
        roi = r.get("roi", 0)
        utilization = r.get("utilization", 0)

        if priority_class in ("Critical", "High"):
            reasoning = (
                f"{city} exhibits critical expansion priority due to high EV concentration "
                f"({ev_count:,} EVs), an infrastructure gap of {infra_gap} optimal stations, "
                f"and a strong projected ROI of {roi}%."
            )
        elif priority_class == "Medium":
            reasoning = (
                f"{city} offers steady medium-priority growth. Current station utilization is "
                f"stable at {utilization}%, presenting moderate ROI opportunities of {roi}%."
            )
        else:
            reasoning = (
                f"{city} shows lower deployment urgency. Existing station coverage is sufficient "
                f"(Gap: {infra_gap}), and current market density does not justify new CapEx."
            )

        item = dict(r)
        item["priorityScore"] = priority_score
        item["priorityClass"] = priority_class
        item["reasoning"] = reasoning
        item["expectedRevenue"] = round(float(r.get("single_station_capex") or 0) * 0.28)
        item["installationCost"] = float(r.get("installation_cost") or 0)
        result.append(item)

    return sorted(result, key=lambda x: x["priorityScore"], reverse=True)


# ─── Static File Serving ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    """Health check endpoint showing active Database engine."""
    pg_ok, pg_msg = test_postgres()
    _, active_engine = get_db()
    return jsonify({
        "status": "online",
        "active_database": active_engine.upper(),
        "postgresql": {
            "status": "connected" if pg_ok else "unavailable",
            "host": PG_HOST,
            "port": PG_PORT,
            "database": PG_DATABASE,
            "user": PG_USER,
            "message": pg_msg
        }
    })


# ─── Authentication Endpoints ──────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "Network Planning & Expansion").strip()

    if not name:
        return jsonify({"success": False, "error": "Full name is required."}), 400
    if not email or "@" not in email:
        return jsonify({"success": False, "error": "Please enter a valid email address."}), 400
    if len(password) < 4:
        return jsonify({"success": False, "error": "Password must be at least 4 characters long."}), 400

    # Check if user already exists
    rows, _ = execute_query("SELECT id FROM users WHERE LOWER(email) = ?", [email])
    if rows:
        return jsonify({
            "success": False,
            "error": f"An account with email '{email}' already exists. Please sign in."
        }), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    ok, msg = execute_write(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        [name, email, password_hash, role]
    )
    if not ok:
        return jsonify({"success": False, "error": f"Registration failed: {msg}"}), 500

    return jsonify({
        "success": True,
        "message": "Account created successfully! Please sign in with your credentials.",
        "user": {"name": name, "email": email, "role": role}
    })


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email:
        return jsonify({"success": False, "error": "Please enter your email address."}), 400
    if not password:
        return jsonify({"success": False, "error": "Please enter your password."}), 400

    # Query user from database
    rows, _ = execute_query(
        "SELECT id, name, email, password_hash, role FROM users WHERE LOWER(email) = ?",
        [email]
    )

    if not rows:
        return jsonify({
            "success": False,
            "error": "No account found with this email. Please click 'Create Account' to register."
        }), 401

    user = rows[0]
    expected_hash = hashlib.sha256(password.encode()).hexdigest()
    if user.get("password_hash") != expected_hash:
        return jsonify({
            "success": False,
            "error": "Incorrect password. Please check your password and try again."
        }), 401

    return jsonify({
        "success": True,
        "message": "Authentication successful.",
        "user": {
            "name": user.get("name"),
            "email": user.get("email"),
            "role": user.get("role")
        }
    })



@app.route("/api/months")
def get_months():
    """Return all available months from the database."""
    rows, _ = execute_query("SELECT DISTINCT date FROM ev_records ORDER BY date")
    return jsonify([r["date"] for r in rows])


@app.route("/api/regions")
def get_regions():
    """Return all distinct regions."""
    rows, _ = execute_query("SELECT DISTINCT region FROM ev_records ORDER BY region")
    return jsonify([r["region"] for r in rows])


@app.route("/api/states")
def get_states():
    """Return all distinct states, optionally filtered by region."""
    region = request.args.get("region", "All")
    if region != "All":
        rows, _ = execute_query(
            "SELECT DISTINCT state FROM ev_records WHERE region=? ORDER BY state", [region]
        )
    else:
        rows, _ = execute_query("SELECT DISTINCT state FROM ev_records ORDER BY state")
    return jsonify([r["state"] for r in rows])


@app.route("/api/cities")
def get_cities():
    """Return distinct cities (optionally filtered by state)."""
    state = request.args.get("state", "All")
    if state != "All":
        rows, _ = execute_query(
            "SELECT DISTINCT city FROM ev_records WHERE state=? ORDER BY city", [state]
        )
    else:
        rows, _ = execute_query("SELECT DISTINCT city FROM ev_records ORDER BY city")
    return jsonify([r["city"] for r in rows])


@app.route("/api/records")
def get_records():
    """
    Main data endpoint. Returns ev_records filtered by date/region/state/city.
    Query params: date, region, state, city
    """
    date = request.args.get("date", "")
    region = request.args.get("region", "All")
    state = request.args.get("state", "All")
    city = request.args.get("city", "All")

    clauses = []
    params = []
    if date:
        clauses.append("date = ?")
        params.append(date)
    if region != "All":
        clauses.append("region = ?")
        params.append(region)
    if state != "All":
        clauses.append("state = ?")
        params.append(state)
    if city != "All":
        clauses.append("city = ?")
        params.append(city)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"SELECT * FROM ev_records {where} ORDER BY city"
    rows, _ = execute_query(query, params)
    return jsonify(rows)


@app.route("/api/monthly-trend")
def monthly_trend():
    """
    Returns aggregated monthly trend data (total EVs, stations, revenue per month).
    """
    region = request.args.get("region", "All")
    state = request.args.get("state", "All")
    city = request.args.get("city", "All")

    clauses = []
    params = []
    if region != "All":
        clauses.append("region = ?")
        params.append(region)
    if state != "All":
        clauses.append("state = ?")
        params.append(state)
    if city != "All":
        clauses.append("city = ?")
        params.append(city)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"""
        SELECT
            date,
            SUM(ev_count) AS totalEvs,
            SUM(stations) AS totalStations,
            SUM(revenue) AS totalRevenue,
            SUM(sessions) AS totalSessions,
            AVG(utilization) AS avgUtilization
        FROM ev_records
        {where}
        GROUP BY date
        ORDER BY date
    """
    rows, _ = execute_query(query, params)
    return jsonify(rows)


@app.route("/api/recommendations")
def get_recommendations():
    """
    Returns MCDM priority-scored and ranked expansion recommendations.
    """
    date = request.args.get("date", "")
    region = request.args.get("region", "All")
    state = request.args.get("state", "All")
    city = request.args.get("city", "All")

    weights = {
        "evDensity": float(request.args.get("w_ev", 0.25)),
        "demand": float(request.args.get("w_demand", 0.25)),
        "infraGap": float(request.args.get("w_gap", 0.25)),
        "roi": float(request.args.get("w_roi", 0.25)),
    }

    clauses = []
    params = []
    if date:
        clauses.append("date = ?")
        params.append(date)
    if region != "All":
        clauses.append("region = ?")
        params.append(region)
    if state != "All":
        clauses.append("state = ?")
        params.append(state)
    if city != "All":
        clauses.append("city = ?")
        params.append(city)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    rows, _ = execute_query(f"SELECT * FROM ev_records {where}", params)
    ranked = calculate_recommendations(rows, weights)
    return jsonify(ranked)


@app.route("/api/stats")
def get_stats():
    """Returns aggregated KPI stats for a given date/filter."""
    date = request.args.get("date", "")
    region = request.args.get("region", "All")
    state = request.args.get("state", "All")
    city = request.args.get("city", "All")

    clauses = []
    params = []
    if date:
        clauses.append("date = ?")
        params.append(date)
    if region != "All":
        clauses.append("region = ?")
        params.append(region)
    if state != "All":
        clauses.append("state = ?")
        params.append(state)
    if city != "All":
        clauses.append("city = ?")
        params.append(city)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"""
        SELECT
            SUM(ev_count)        AS totalEvs,
            SUM(stations)        AS totalStations,
            SUM(sessions)        AS totalSessions,
            AVG(utilization)     AS avgUtilization,
            SUM(revenue)         AS totalRevenue,
            AVG(roi)             AS avgRoi,
            SUM(infra_gap)       AS totalGap
        FROM ev_records {where}
    """
    rows, _ = execute_query(query, params)
    if not rows:
        return jsonify({})
    d = rows[0]
    total_evs = d.get("totalEvs") or 0
    total_stations = d.get("totalStations") or 0
    d["evToStationRatio"] = round(total_evs / total_stations) if total_stations else 0
    d["avgUtilization"] = round(float(d.get("avgUtilization") or 0), 1)
    d["avgRoi"] = round(float(d.get("avgRoi") or 0), 1)
    return jsonify(d)


# ─── Server Launch ────────────────────────────────────────────────────────────

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

def start_server():
    pg_ok, pg_msg = test_postgres()

    print("=" * 60)
    print("  TATA POWER EV ANALYTICS — Flask Web & API Server")
    print("=" * 60)
    if pg_ok:
        print(f"  [OK] DATABASE     : PostgreSQL (tata_ev_db on {PG_HOST}:{PG_PORT})")
    else:
        print(f"  [!] POSTGRESQL   : Not connected ({pg_msg})")
        print(f"  [->] If you haven't initialized PostgreSQL yet, run: python init_postgres.py")
    print(f"  Server URL       : http://localhost:8000")
    print(f"  API Health Check : http://localhost:8000/api/health")
    print("=" * 60)
    print("  Press Ctrl+C to stop the server.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=False)

if __name__ == "__main__":
    start_server()
