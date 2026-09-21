import sqlite3
import os

db_path = os.path.join(os.getcwd(), "data", "tracex.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE cameras SET created_at = datetime('now') WHERE created_at IS NULL")
cur.execute("UPDATE watchlist SET created_at = datetime('now') WHERE created_at IS NULL")
conn.commit()
print("Updated created_at timestamps in SQLite DB.", flush=True)
conn.close()
