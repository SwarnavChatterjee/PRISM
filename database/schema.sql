CREATE TABLE IF NOT EXISTS vendor_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor TEXT NOT NULL,
    raw_pattern TEXT NOT NULL,
    schema_path TEXT NOT NULL,
    mapped_value TEXT,
    confidence REAL NOT NULL DEFAULT 1.0,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vendor_patterns_vendor
    ON vendor_patterns(vendor);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    user TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
