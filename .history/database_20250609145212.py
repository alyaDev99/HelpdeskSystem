import mysql.connector
from mysql.connector import Error
from hashlib import sha256

# ── Configuration ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host': '10.10.2.224',        # Replace with the IP address of the machine hosting the MySQL database
    'user': 'root',             # Your MySQL user
    'password': kinnporsche'      # Your MySQL password
}

DB_NAME = 'helpdesk_db'

# ── Connect & Initialize ───────────────────────────────────────────────────────
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1) Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    # 2) Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        department VARCHAR(100)
    )""")

    # 3) Create tickets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
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
        resolved_at DATETIME,
        FOREIGN KEY (staff_id) REFERENCES users(id),
        FOREIGN KEY (technician_id) REFERENCES users(id)
    )""")

    # 4) Insert sample users if none exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample = [
            ('john', sha256('1234'.encode()).hexdigest(), 'staff', 'IT'),
            ('tech1', sha256('1234'.encode()).hexdigest(), 'technician', 'Support'),
            ('admin', sha256('1234'.encode()).hexdigest(), 'admin', 'Management'),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, role, department) VALUES (%s, %s, %s, %s)",
            sample
        )

    conn.commit()
    print("MySQL database setup complete.")

except Error as e:
    print(f"Error: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()




