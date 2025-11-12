CREATE TABLE IF NOT EXISTS client_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT,
    email TEXT,
    mobile TEXT,
    heading TEXT,
    description TEXT,
    status TEXT DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);
