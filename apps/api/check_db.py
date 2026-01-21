import sqlite3

conn = sqlite3.connect('../../flowtab.db')
cursor = conn.cursor()

# Check alembic version
cursor.execute('SELECT * FROM alembic_version')
print("Alembic version:", cursor.fetchall())

# Check all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
print("\nAll tables:")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()
