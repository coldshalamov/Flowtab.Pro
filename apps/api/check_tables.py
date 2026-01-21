import sqlite3

conn = sqlite3.connect('../../flowtab.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
tables = [row[0] for row in cursor.fetchall()]
print('\n'.join(tables))
conn.close()
