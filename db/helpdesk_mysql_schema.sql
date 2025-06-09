
-- Create database
CREATE DATABASE IF NOT EXISTS helpdesk_db;
USE helpdesk_db;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100)
);

-- Tickets table
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    staff_id INT NOT NULL,
    technician_id INT,
    technician_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolution_notes TEXT,
    resolved_at DATETIME
);

-- Foreign key constraints
ALTER TABLE tickets
ADD CONSTRAINT fk_staff
FOREIGN KEY (staff_id) REFERENCES users(id),
ADD CONSTRAINT fk_technician
FOREIGN KEY (technician_id) REFERENCES users(id);
