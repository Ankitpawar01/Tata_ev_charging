-- ====================================================================
-- TATA POWER EV ANALYTICS — POSTGRESQL DATABASE SCHEMA & MIGRATION
-- Database: tata_ev_db
-- ====================================================================

-- 1. Create Tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(100) DEFAULT 'Network Planning & Expansion',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cities (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    ev_base INTEGER NOT NULL,
    stations_base INTEGER NOT NULL,
    demand_factor NUMERIC(4, 2) NOT NULL,
    avg_cost BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS ev_records (
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

-- 2. Performance Indexes for Fast Analytics Queries
CREATE INDEX IF NOT EXISTS idx_ev_records_date ON ev_records(date);
CREATE INDEX IF NOT EXISTS idx_ev_records_city ON ev_records(city);
CREATE INDEX IF NOT EXISTS idx_ev_records_state ON ev_records(state);
CREATE INDEX IF NOT EXISTS idx_ev_records_region ON ev_records(region);
