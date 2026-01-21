import sqlite3

# Check the API directory database
conn = sqlite3.connect('./flowtab.db')
cursor = conn.cursor()

try:
    # Check alembic version
    cursor.execute('SELECT * FROM alembic_version')
    print("Alembic version:", cursor.fetchall())
except sqlite3.OperationalError as e:
    print(f"Alembic version table error: {e}")

# Check all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
print("\nAll tables in apps/api/flowtab.db:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()
