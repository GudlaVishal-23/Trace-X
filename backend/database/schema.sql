-- ============================================================================
-- TRACE-X DATABASE INITIALIZATION SCRIPT
-- PostgreSQL 16 + PostGIS 3.4
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- ----------------------------------------------------------------------------
-- 1. CAMERAS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cameras (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(32) UNIQUE NOT NULL,
    name VARCHAR(128) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED,
    road_id VARCHAR(64),
    direction VARCHAR(32) DEFAULT 'unknown',
    camera_type VARCHAR(32) DEFAULT 'ANPR',
    stream_url TEXT,
    status VARCHAR(16) DEFAULT 'online', -- 'online', 'offline', 'degraded'
    quality_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cameras_geom ON cameras USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_cameras_status ON cameras (status);

-- ----------------------------------------------------------------------------
-- 2. VEHICLE EVENTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicle_events (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(64) UNIQUE NOT NULL,
    camera_id VARCHAR(32) REFERENCES cameras(camera_id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    plate_text VARCHAR(16),
    plate_confidence FLOAT DEFAULT 0.0,
    observation_status VARCHAR(16) NOT NULL, -- 'CONFIRMED', 'PROBABLE', 'UNREADABLE'
    vehicle_type VARCHAR(32),                -- 'car', 'motorcycle', 'bus', 'truck', 'auto_rickshaw'
    vehicle_color VARCHAR(32),
    vehicle_make VARCHAR(64),
    vehicle_model VARCHAR(64),
    direction VARCHAR(32),
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(Point, 4326) GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED,
    road_id VARCHAR(64),
    image_quality_score FLOAT DEFAULT 0.0,
    detection_confidence FLOAT DEFAULT 0.0,
    reid_embedding_id VARCHAR(64),
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_plate ON vehicle_events (plate_text);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON vehicle_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_camera_time ON vehicle_events (camera_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_geom ON vehicle_events USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_events_type ON vehicle_events (vehicle_type);

-- ----------------------------------------------------------------------------
-- 3. TRAJECTORIES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trajectories (
    id BIGSERIAL PRIMARY KEY,
    trajectory_id VARCHAR(64) UNIQUE NOT NULL,
    plate_text VARCHAR(16) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    overall_confidence FLOAT NOT NULL,
    status VARCHAR(16) DEFAULT 'CONFIRMED', -- 'CONFIRMED', 'PROBABLE', 'INCOMPLETE'
    total_distance_km FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trajectories_plate ON trajectories (plate_text);

-- ----------------------------------------------------------------------------
-- 4. TRAJECTORY LINKS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trajectory_links (
    id BIGSERIAL PRIMARY KEY,
    trajectory_id VARCHAR(64) REFERENCES trajectories(trajectory_id) ON DELETE CASCADE,
    from_event_id VARCHAR(64) REFERENCES vehicle_events(event_id) ON DELETE CASCADE,
    to_event_id VARCHAR(64) REFERENCES vehicle_events(event_id) ON DELETE CASCADE,
    match_score FLOAT NOT NULL,
    link_type VARCHAR(16) NOT NULL, -- 'CONFIRMED', 'PROBABLE', 'CAMERA_GAP'
    distance_km FLOAT NOT NULL,
    travel_time_sec INTEGER NOT NULL,
    implied_speed_kmh FLOAT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_links_trajectory ON trajectory_links (trajectory_id);

-- ----------------------------------------------------------------------------
-- 5. WATCHLIST TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    plate_text VARCHAR(16) UNIQUE NOT NULL,
    category VARCHAR(32) NOT NULL, -- 'STOLEN', 'SUSPECT', 'VIP', 'TRAFFIC_VIOLATOR'
    priority VARCHAR(16) DEFAULT 'HIGH', -- 'CRITICAL', 'HIGH', 'MEDIUM'
    case_reference VARCHAR(64),
    notes TEXT,
    status VARCHAR(16) DEFAULT 'ACTIVE', -- 'ACTIVE', 'INACTIVE', 'ARCHIVED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_watchlist_plate ON watchlist (plate_text);

-- ----------------------------------------------------------------------------
-- 6. ALERTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_type VARCHAR(32) NOT NULL, -- 'WATCHLIST_MATCH', 'ROUTE_ANOMALY', 'CLONED_PLATE', 'CONGESTION'
    plate_text VARCHAR(16),
    camera_id VARCHAR(32) REFERENCES cameras(camera_id) ON DELETE SET NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence FLOAT NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(16) DEFAULT 'NEW', -- 'NEW', 'ACKNOWLEDGED', 'DISMISSED', 'RESOLVED'
    case_file_id VARCHAR(64),
    officer_notes TEXT,
    acknowledged_by VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (status);
CREATE INDEX IF NOT EXISTS idx_alerts_plate ON alerts (plate_text);
CREATE INDEX IF NOT EXISTS idx_alerts_time ON alerts (timestamp DESC);

-- ----------------------------------------------------------------------------
-- 7. USERS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(128) UNIQUE NOT NULL,
    role VARCHAR(32) NOT NULL, -- 'ADMIN', 'OFFICER', 'ANALYST'
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 8. AUDIT LOGS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(64) NOT NULL, -- 'SEARCH_PLATE', 'EXPORT_REPORT', 'ACK_ALERT'
    resource VARCHAR(128) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_logs (timestamp DESC);
