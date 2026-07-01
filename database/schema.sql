-- Cyber Range SOC Lite — Database Schema
-- SQLite-compatible DDL for reference

CREATE TABLE IF NOT EXISTS alerts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           VARCHAR(255),
    description     TEXT,
    severity        VARCHAR(20) DEFAULT 'Low',
    source_ip       VARCHAR(45) NOT NULL,
    destination_ip  VARCHAR(45),
    attack_type     VARCHAR(100) NOT NULL,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_acknowledged BOOLEAN DEFAULT 0,
    is_resolved     BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS log_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ip          VARCHAR(45) NOT NULL,
    event_type  VARCHAR(100) NOT NULL,
    endpoint    VARCHAR(255) NOT NULL,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);
