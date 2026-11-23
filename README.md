# Tata Power EV Charging Network Expansion & Revenue Analytics Dashboard

A professional **Data Analytics & Decision Support System** for EV Charging Network Expansion & Revenue Optimization, built for **Tata Power EZ Charge**.

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| **Frontend** | React 18 + Tailwind CSS + Recharts (SVG Vector Charts) |
| **Backend API** | Python Flask (REST API) |
| **Primary Database** | **PostgreSQL** (`tata_ev_db` via `psycopg2`) |
| **Fallback Database** | SQLite (`ev_analytics.db`) |
| **Server** | Flask multi-threaded server on port 8000 |

---

## Database Architecture (PostgreSQL)

The primary database engine is **PostgreSQL** with 2 structured tables:

| Table | Description | Records |
|:---|:---|:---:|
| `cities` | Master registry of Indian cities with base EV adoption & station density | 100 rows |
| `ev_records` | Monthly telemetry analytics (24 months × 100 cities & corridors) | 2,400 rows |

Database schema and SQL scripts:
- **`schema_postgres.sql`** — Complete PostgreSQL DDL (tables, data types, indexes)
- **`init_postgres.py`** — Python migration script that creates database, tables, and populates all 474 records
- **`.env`** — PostgreSQL connection credentials (`PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`)

---

## How to Setup PostgreSQL

### Step 1: Configure Credentials (Optional)
If your PostgreSQL password is not `postgres`, open `.env` and update:
```env
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=your_password_here
PGDATABASE=tata_ev_db
```

### Step 2: Initialize Database
Run the setup script:
```bash
python init_postgres.py
```
*(You can also open `schema_postgres.sql` directly in **pgAdmin 4** if you prefer GUI!)*

### Step 3: Run the Dashboard
```bash
python server.py
# or
python app.py
```
The server will automatically detect PostgreSQL, connect, and open the dashboard at **http://localhost:8000**!

> **Smart Fallback:** If PostgreSQL is temporarily stopped or offline during a viva demo, the server automatically switches to local SQLite so your project **never crashes** in front of examiners!

---

## REST API Endpoints

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/api/health` | `GET` | Health status showing active engine (POSTGRESQL or SQLITE) |
| `/api/months` | `GET` | Available historical reporting months from DB |
| `/api/regions` | `GET` | Distinct geographic regions (North, South, East, West, Central) |
| `/api/states?region=` | `GET` | States filtered by region |
| `/api/cities?state=` | `GET` | Cities filtered by state |
| `/api/records?date=&region=&state=&city=` | `GET` | Main filtered EV telemetry dataset |
| `/api/monthly-trend?region=&state=` | `GET` | Aggregated monthly fleet & revenue growth trend |
| `/api/stats?date=&region=&state=&city=` | `GET` | Executive KPI aggregates (EV density, CapEx, ROI) |
| `/api/recommendations?w_ev=&w_demand=&w_gap=&w_roi=` | `GET` | Live MCDM priority ranking engine |

---

## Features

1. **Login Page** — Secure enterprise portal for Tata Power strategic planners.
2. **Overview Dashboard** — High-level KPIs, EV demand trend, state-wise performance scorecard.
3. **Demand Analysis** — EV fleet density & session intensity charts (Bar, Scatter, Stress Matrix).
4. **Infrastructure Gap Map** — Interactive India SVG map with deficit severity bubbles across 70+ cities.
5. **Location Analysis** — Sortable city comparison table + Cost vs Expected Revenue scatter plot.
6. **Revenue & ROI** — CapEx/OpEx financial performance & payback period models.
7. **Charger Optimizer** — AC vs DC hardware mix simulator with substation grid load limit alarms.
8. **Expansion Guide** — Dynamic MCDM priority ranking with configurable weight sliders.
9. **Data Explorer** — Paginated, searchable data grid with CSV/Excel export.
10. **Data Architecture** — Visual analytical pipeline (Excel → PostgreSQL → Python Flask → React Dashboard).

---
*Tata Power EV Analytics — Enterprise Decision Support System for India's Clean Mobility Infrastructure.*
