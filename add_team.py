import sqlite3 as sql

conn = sql.connect("playoffs.db")
cur = conn.cursor()
rank = int(cur.execute("SELECT MAX(rank) FROM teams").fetchall()[0][0]) + 1
cur.execute("INSERT INTO teams(rank,number,name) VALUES (?,?,'test')", (rank,rank))
conn.commit()
conn.close()

import generator
