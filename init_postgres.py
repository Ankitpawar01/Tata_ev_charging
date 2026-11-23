"""
Tata Power EV Analytics — PostgreSQL Database Initialization Script
Connects to PostgreSQL, creates database 'tata_ev_db' (if needed),
creates tables and inserts all 79 cities & 474 monthly records.

Usage:
  python init_postgres.py
"""
import os
import math
import random
import hashlib
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.extras

# Default PostgreSQL Connection Configuration
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "root")
PG_DATABASE = os.getenv("PGDATABASE", "tata_ev_db")

BASE_CITIES = [
    # Maharashtra
    ("Mumbai", "Maharashtra", "West", 18500, 110, 1.25, 1500000),
    ("Pune", "Maharashtra", "West", 9200, 48, 1.15, 1200000),
    ("Nagpur", "Maharashtra", "West", 3100, 12, 0.90, 1100000),
    ("Nashik", "Maharashtra", "West", 2200, 8, 0.85, 1000000),
    ("Thane", "Maharashtra", "West", 4500, 20, 1.10, 1200000),
    # Delhi
    ("New Delhi", "Delhi", "North", 22000, 140, 1.30, 1600000),
    ("Dwarka", "Delhi", "North", 6800, 32, 1.05, 1200000),
    ("Rohini", "Delhi", "North", 5200, 24, 0.95, 1200000),
    ("Saket", "Delhi", "North", 4800, 28, 1.12, 1400000),
    # Karnataka
    ("Bengaluru", "Karnataka", "South", 24500, 155, 1.35, 1600000),
    ("Mysuru", "Karnataka", "South", 2800, 15, 0.95, 1100000),
    ("Hubli", "Karnataka", "South", 1600, 6, 0.80, 1000000),
    ("Mangaluru", "Karnataka", "South", 1900, 8, 0.90, 1100000),
    # Tamil Nadu
    ("Chennai", "Tamil Nadu", "South", 14000, 82, 1.20, 1400000),
    ("Coimbatore", "Tamil Nadu", "South", 4800, 22, 1.05, 1150000),
    ("Madurai", "Tamil Nadu", "South", 2100, 8, 0.88, 1000000),
    ("Salem", "Tamil Nadu", "South", 1700, 6, 0.80, 1000000),
    # Telangana
    ("Hyderabad", "Telangana", "South", 16800, 98, 1.28, 1500000),
    ("Warangal", "Telangana", "South", 2200, 7, 0.85, 1000000),
    ("Nizamabad", "Telangana", "South", 1100, 3, 0.75, 950000),
    # Uttar Pradesh
    ("Lucknow", "Uttar Pradesh", "North", 7500, 35, 1.00, 1200000),
    ("Noida", "Uttar Pradesh", "North", 8900, 52, 1.18, 1300000),
    ("Ghaziabad", "Uttar Pradesh", "North", 6100, 26, 0.98, 1200000),
    ("Kanpur", "Uttar Pradesh", "North", 3900, 14, 0.90, 1100000),
    ("Varanasi", "Uttar Pradesh", "North", 2800, 9, 0.88, 1050000),
    # Gujarat
    ("Ahmedabad", "Gujarat", "West", 11500, 64, 1.15, 1350000),
    ("Surat", "Gujarat", "West", 7800, 38, 1.10, 1300000),
    ("Vadodara", "Gujarat", "West", 3400, 15, 0.92, 1100000),
    ("Rajkot", "Gujarat", "West", 2600, 10, 0.85, 1000000),
    # West Bengal
    ("Kolkata", "West Bengal", "East", 10200, 45, 1.10, 1300000),
    ("Howrah", "West Bengal", "East", 2400, 8, 0.85, 1050000),
    ("Siliguri", "West Bengal", "East", 1500, 4, 0.80, 950000),
    # Rajasthan
    ("Jaipur", "Rajasthan", "West", 6500, 28, 1.02, 1150000),
    ("Jodhpur", "Rajasthan", "West", 2300, 9, 0.86, 1000000),
    ("Udaipur", "Rajasthan", "West", 1800, 7, 0.92, 1050000),
    # Madhya Pradesh
    ("Indore", "Madhya Pradesh", "Central", 7100, 26, 1.12, 1200000),
    ("Bhopal", "Madhya Pradesh", "Central", 4600, 18, 0.96, 1100000),
    ("Jabalpur", "Madhya Pradesh", "Central", 1900, 6, 0.82, 1000000),
    # Kerala
    ("Kochi", "Kerala", "South", 5400, 28, 1.08, 1250000),
    ("Thiruvananthapuram", "Kerala", "South", 3100, 14, 0.94, 1150000),
    ("Kozhikode", "Kerala", "South", 2200, 8, 0.88, 1050000),
    # Haryana
    ("Gurgaon", "Haryana", "North", 12400, 72, 1.28, 1550000),
    ("Faridabad", "Haryana", "North", 4200, 16, 0.92, 1150000),
    ("Panipat", "Haryana", "North", 1500, 4, 0.78, 950000),
    # Punjab
    ("Ludhiana", "Punjab", "North", 3800, 12, 0.90, 1100000),
    ("Amritsar", "Punjab", "North", 2700, 8, 0.84, 1000000),
    ("Jalandhar", "Punjab", "North", 2100, 6, 0.80, 1000000),
    # Andhra Pradesh
    ("Visakhapatnam", "Andhra Pradesh", "South", 4900, 20, 1.05, 1200000),
    ("Vijayawada", "Andhra Pradesh", "South", 3300, 11, 0.92, 1100000),
    # Bihar
    ("Patna", "Bihar", "East", 3600, 10, 0.88, 1050000),
    ("Gaya", "Bihar", "East", 1200, 3, 0.72, 900000),
    # Odisha
    ("Bhubaneswar", "Odisha", "East", 4100, 15, 1.02, 1150000),
    ("Cuttack", "Odisha", "East", 2200, 6, 0.85, 1000000),
    # Jharkhand
    ("Ranchi", "Jharkhand", "East", 3200, 12, 0.95, 1100000),
    ("Jamshedpur", "Jharkhand", "East", 3900, 14, 1.00, 1200000),
    ("Dhanbad", "Jharkhand", "East", 1800, 4, 0.80, 1000000),
    # Chhattisgarh
    ("Raipur", "Chhattisgarh", "Central", 3500, 11, 0.96, 1150000),
    ("Bilaspur", "Chhattisgarh", "Central", 1700, 5, 0.80, 1000000),
    # Uttarakhand
    ("Dehradun", "Uttarakhand", "North", 2900, 10, 0.94, 1100000),
    ("Haridwar", "Uttarakhand", "North", 2100, 7, 0.90, 1050000),
    # Himachal Pradesh
    ("Shimla", "Himachal Pradesh", "North", 1400, 6, 0.86, 1050000),
    ("Dharamshala", "Himachal Pradesh", "North", 950, 3, 0.80, 1000000),
    # Jammu & Kashmir
    ("Srinagar", "Jammu & Kashmir", "North", 2100, 5, 0.82, 1100000),
    ("Jammu", "Jammu & Kashmir", "North", 1800, 6, 0.85, 1050000),
    # Ladakh
    ("Leh", "Ladakh", "North", 350, 2, 0.70, 1150000),
    # Goa
    ("Panaji", "Goa", "West", 2400, 16, 1.15, 1200000),
    ("Margao", "Goa", "West", 1500, 8, 1.00, 1100000),
    # Assam
    ("Guwahati", "Assam", "East", 4200, 18, 1.08, 1200000),
    ("Dibrugarh", "Assam", "East", 1100, 4, 0.82, 1000000),
    # North-East States
    ("Agartala", "Tripura", "East", 1300, 4, 0.85, 1000000),
    ("Shillong", "Meghalaya", "East", 1600, 6, 0.90, 1050000),
    ("Imphal", "Manipur", "East", 980, 3, 0.80, 1000000),
    ("Aizawl", "Mizoram", "East", 750, 2, 0.75, 1000000),
    ("Kohima", "Nagaland", "East", 820, 2, 0.78, 1000000),
    ("Dimapur", "Nagaland", "East", 1200, 4, 0.82, 1000000),
    ("Gangtok", "Sikkim", "East", 650, 3, 0.80, 1050000),
    ("Itanagar", "Arunachal Pradesh", "East", 780, 2, 0.75, 1000000),
    # UTs
    ("Chandigarh", "Chandigarh", "North", 4200, 22, 1.12, 1300000),
    ("Puducherry", "Puducherry", "South", 1800, 9, 0.96, 1100000),

    # Additional High-Demand Corridors & Emerging Tier-2 Hubs
    ("Mumbai-Pune Expressway", "Maharashtra", "West", 6400, 26, 1.40, 1600000),
    ("Aurangabad", "Maharashtra", "West", 2600, 10, 0.88, 1050000),
    ("Kolhapur", "Maharashtra", "West", 2100, 7, 0.85, 1000000),
    ("Agra", "Uttar Pradesh", "North", 4200, 16, 1.05, 1200000),
    ("Meerut", "Uttar Pradesh", "North", 3400, 12, 0.92, 1100000),
    ("Mathura", "Uttar Pradesh", "North", 2200, 8, 0.90, 1050000),
    ("Yamuna Expressway Corridor", "Uttar Pradesh", "North", 4500, 18, 1.35, 1500000),
    ("Delhi-Jaipur Highway Corridor", "Rajasthan", "North", 5400, 22, 1.35, 1550000),
    ("Kota", "Rajasthan", "West", 2800, 9, 0.86, 1000000),
    ("Ajmer", "Rajasthan", "West", 2100, 7, 0.85, 1000000),
    ("Gwalior", "Madhya Pradesh", "Central", 2500, 8, 0.86, 1050000),
    ("Ujjain", "Madhya Pradesh", "Central", 1900, 6, 0.88, 1000000),
    ("Bengaluru-Mysuru Expressway", "Karnataka", "South", 4800, 19, 1.30, 1500000),
    ("Tiruchirappalli", "Tamil Nadu", "South", 2600, 10, 0.90, 1050000),
    ("Tirupati", "Andhra Pradesh", "South", 2900, 11, 0.98, 1100000),
    ("Guntur", "Andhra Pradesh", "South", 2300, 8, 0.88, 1000000),
    ("Rourkela", "Odisha", "East", 1900, 6, 0.84, 1000000),
    ("Bokaro", "Jharkhand", "East", 1700, 5, 0.82, 1000000),
    ("Karnal", "Haryana", "North", 2100, 8, 0.90, 1050000),
    ("Rohtak", "Haryana", "North", 1800, 6, 0.85, 1000000),
    ("Bhatinda", "Punjab", "North", 1600, 5, 0.80, 950000),
]

MONTHS = [
    "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025",
    "July 2025", "August 2025", "September 2025", "October 2025", "November 2025", "December 2025",
    "January 2026", "February 2026", "March 2026", "April 2026", "May 2026", "June 2026",
    "July 2026", "August 2026", "September 2026", "October 2026", "November 2026", "December 2026"
]

MONTHLY_RATES = [
    0.65, 0.68, 0.71, 0.74, 0.78, 0.82,
    0.86, 0.90, 0.93, 0.96, 0.98, 1.00,
    1.03, 1.07, 1.11, 1.15, 1.19, 1.23,
    1.27, 1.31, 1.35, 1.39, 1.43, 1.47
]

def calculate_records():
    records = []
    random.seed(42)
    for m_idx, (month, rate) in enumerate(zip(MONTHS, MONTHLY_RATES)):
        for city, state, region, ev_base, stations_base, demand_factor, avg_cost in BASE_CITIES:
            current_ev = round(ev_base * rate)
            current_stations = stations_base
            if m_idx >= 2:
                current_stations += round(stations_base * 0.03 * (m_idx - 1))

            optimal_stations = math.ceil(current_ev / 100)
            infra_gap = max(0, optimal_stations - current_stations)

            base_sessions = 210 + math.sin(m_idx * 0.5) * 15
            sessions = round(current_stations * base_sessions * demand_factor * (0.95 + random.random() * 0.1)) if current_stations > 0 else round(current_ev * 0.05)

            total_charging_hours = sessions * 1.6
            total_capacity_hours = (current_stations or 1) * 24 * 30
            utilization = (total_charging_hours / total_capacity_hours) * 100
            if utilization > 92: utilization = 92 - random.random() * 3
            if utilization < 15: utilization = 15 + random.random() * 5
            utilization = round(utilization, 1)

            avg_revenue_per_session = 320
            monthly_opex = current_stations * 18000
            monthly_revenue = sessions * avg_revenue_per_session
            expected_profit = monthly_revenue - monthly_opex
            total_capex = max(1, current_stations) * avg_cost
            roi = round(((expected_profit * 12) / total_capex) * 100, 1) if current_stations > 0 else 0.0

            records.append((
                month, city, state, region,
                current_ev, current_stations, sessions,
                round(utilization, 1), total_capex,
                round(monthly_revenue), round(expected_profit),
                roi, infra_gap, optimal_stations, avg_cost
            ))
    return records

def create_database_if_not_exists():
    """Connect to default 'postgres' database to create 'tata_ev_db' if it does not exist."""
    print(f"[*] Connecting to PostgreSQL at {PG_HOST}:{PG_PORT} as '{PG_USER}'...")
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DATABASE,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{PG_DATABASE}"')
            print(f"[OK] Database '{PG_DATABASE}' created successfully.")
        else:
            print(f"[OK] Database '{PG_DATABASE}' already exists.")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[!] Note: {e}")
        return False

def init_postgres():
    create_database_if_not_exists()

    print(f"[*] Connecting to '{PG_DATABASE}'...")
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE
        )
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS ev_records CASCADE;")
        cur.execute("DROP TABLE IF EXISTS cities CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")

        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(100) DEFAULT 'Network Planning & Expansion',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Seed default admin user
        admin_pass_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """, ("Tata Admin", "admin@tatapower.com", admin_pass_hash, "Network Planning & Expansion"))
        print("[OK] Inserted default admin user (admin@tatapower.com / admin123).")

        cur.execute("""
            CREATE TABLE cities (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                ev_base INTEGER NOT NULL,
                stations_base INTEGER NOT NULL,
                demand_factor NUMERIC(4, 2) NOT NULL,
                avg_cost BIGINT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE ev_records (
                id SERIAL PRIMARY KEY,
                date VARCHAR(50) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                ev_count INTEGER NOT NULL,
                stations INTEGER NOT NULL,
                sessions INTEGER NOT NULL,
                utilization NUMERIC(5, 2) NOT NULL,
                installation_cost NUMERIC(15, 2) NOT NULL,
                revenue BIGINT NOT NULL,
                profit BIGINT NOT NULL,
                roi NUMERIC(6, 2) NOT NULL,
                infra_gap INTEGER NOT NULL,
                optimal_stations INTEGER NOT NULL,
                single_station_capex BIGINT NOT NULL
            );
            CREATE INDEX idx_ev_records_date ON ev_records(date);
            CREATE INDEX idx_ev_records_city ON ev_records(city);
            CREATE INDEX idx_ev_records_state ON ev_records(state);
            CREATE INDEX idx_ev_records_region ON ev_records(region);
        """)

        insert_cities_query = """
            INSERT INTO cities (city, state, region, ev_base, stations_base, demand_factor, avg_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        psycopg2.extras.execute_batch(cur, insert_cities_query, BASE_CITIES)
        print(f"[OK] Inserted {len(BASE_CITIES)} cities into 'cities' table.")

        records = calculate_records()
        insert_records_query = """
            INSERT INTO ev_records (
                date, city, state, region, ev_count, stations, sessions,
                utilization, installation_cost, revenue, profit, roi,
                infra_gap, optimal_stations, single_station_capex
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        psycopg2.extras.execute_batch(cur, insert_records_query, records)
        print(f"[OK] Inserted {len(records)} records into 'ev_records' table.")

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM cities;")
        cities_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM ev_records;")
        records_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        print("\n" + "=" * 55)
        print("  POSTGRESQL SETUP SUCCESSFUL!")
        print("=" * 55)
        print(f"  Database : {PG_DATABASE}")
        print(f"  Cities   : {cities_count}")
        print(f"  Records  : {records_count}")
        print(f"  Months   : {', '.join(MONTHS)}")
        print("=" * 55)
        return True

    except Exception as e:
        print(f"\n[!] PostgreSQL Connection Error: {e}")
        return False

if __name__ == "__main__":
    init_postgres()
