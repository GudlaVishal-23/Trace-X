import sqlite3
import os

db_path = os.path.join(os.getcwd(), "data", "tracex.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE watchlist SET status = 'ACTIVE' WHERE status IS NULL OR status = ''")
conn.commit()
rows = cur.execute("SELECT plate_text, category, priority, status FROM watchlist").fetchall()
for r in rows:
    print(r)
conn.close()
