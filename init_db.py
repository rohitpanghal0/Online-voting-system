import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("voting.db")
with open("schema.sql") as f:
    conn.executescript(f.read())

# INSERT OR IGNORE lets you run this file more than once safely
conn.execute(
    "INSERT OR IGNORE INTO users (name, student_id, email, password_hash, role) VALUES (?,?,?,?,?)",
    ("Admin", "admin", "admin@college.edu", generate_password_hash("admin123"), "admin"),
)
conn.commit()
conn.close()
print("Database ready. Admin login: admin / admin123 (change this password!)")
