"""Local SQLite history. Data never leaves this computer."""
import sqlite3
from datetime import datetime
DB = "history.db"
def _c():
    c = sqlite3.connect(DB); c.execute("CREATE TABLE IF NOT EXISTS h(id INTEGER PRIMARY KEY, ts TEXT, symptoms TEXT, risk TEXT, summary TEXT, status TEXT)"); return c
def save(symptoms, risk, summary):
    with _c() as c: c.execute("INSERT INTO h(ts,symptoms,risk,summary,status) VALUES(?,?,?,?,'Open')", (datetime.now().strftime("%Y-%m-%d %H:%M"), symptoms, risk, summary))
def all_rows():
    with _c() as c: return c.execute("SELECT id,ts,symptoms,risk,summary,status FROM h ORDER BY id DESC").fetchall()
def set_status(i, s):
    with _c() as c: c.execute("UPDATE h SET status=? WHERE id=?", (s, i))
def delete(i=None):
    with _c() as c: c.execute("DELETE FROM h" + ("" if i is None else " WHERE id=?"), () if i is None else (i,))
