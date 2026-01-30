CREATE DATABASE IF NOT EXISTS client_query_system;
USE client_query_system;

-- 2️⃣ Create the users table (for login & registration)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Client','Support') NOT NULL
);

-- 3️⃣ Create the client_queries table (for storing client queries)
CREATE TABLE IF NOT EXISTS client_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    client_name VARCHAR(100),
    email VARCHAR(100),
    mobile VARCHAR(20),
    heading VARCHAR(255),
    description TEXT,
    status VARCHAR(20) DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    FOREIGN KEY (client_id) REFERENCES users(id)
);

-- 4️⃣ Optional: View all data (for checking if queries & users are saved)
SELECT * FROM users;
SELECT * FROM client_queries;
SELECT * FROM client_queries WHERE status = 'Open';
UPDATE client_queries
SET status='Closed', closed_at=CURRENT_TIMESTAMP
WHERE id = 1;
SELECT * FROM synthetic_client_queries;



####  Full data with client data
SELECT client_id, email, mobile, heading, description, status, created_at, closed_at
FROM synthetic_client_queries
UNION
SELECT client_id, email, mobile, heading, description, status, created_at, closed_at
FROM  client_queries;

### only inserted data
SELECT * FROM client_queries;

### only csv data
SELECT * FROM synthetic_client_queries;;
