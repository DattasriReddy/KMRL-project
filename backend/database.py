import sqlite3

def init_db():
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        category TEXT,
        summary TEXT,
        pages INTEGER,
        confidence REAL,
        file_path TEXT
    )''')
    conn.commit()
    conn.close()

def save_to_db(filename, category, summary, pages, confidence, file_path):
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()
    c.execute("INSERT INTO documents (filename, category, summary, pages, confidence, file_path) VALUES (?, ?, ?, ?, ?, ?)",
              (filename, category, summary, pages, confidence, file_path))
    conn.commit()
    conn.close()