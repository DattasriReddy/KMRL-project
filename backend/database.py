import sqlite3

def init_db():
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            category TEXT,
            summary TEXT,
            action_items TEXT,   -- NEW: store as JSON string
            deadline TEXT,       -- NEW
            pages INTEGER,
            confidence REAL,
            file_path TEXT,
            extracted_text TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(filename, category, summary, action_items, deadline, pages, confidence, file_path, extracted_text):
    import json
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO documents 
        (filename, category, summary, action_items, deadline, pages, confidence, file_path, extracted_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (filename, category, summary, json.dumps(action_items), deadline, pages, confidence, file_path, extracted_text))
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def init_search_db():
    """No-op: we use simple LIKE search instead of FTS5."""
    pass

def index_document(doc_id, filename, category, summary):
    """No-op: no search index needed for LIKE search."""
    pass

def search_documents(query):
    """Simple LIKE-based search (works on all systems)."""
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()
    
    search_term = f"%{query}%"
    
    c.execute('''SELECT id, filename, category, summary, pages, confidence
             FROM documents
             WHERE filename LIKE ?
                OR category LIKE ?
                OR summary LIKE ?
                OR extracted_text LIKE ?
             ORDER BY id DESC
             LIMIT 20''',
          (search_term, search_term, search_term, search_term))
    
    results = c.fetchall()
    conn.close()
    
    documents = []
    for row in results:
        documents.append({
            "id": row[0],
            "filename": row[1],
            "category": row[2],
            "summary": row[3],
            "pages": row[4],
            "confidence": row[5]
        })
    
    return documents
def get_documents():
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()

    c.execute("""
        SELECT id, filename, category, summary, pages, confidence
        FROM documents
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "filename": row[1],
            "category": row[2],
            "summary": row[3],
            "pages": row[4],
            "confidence": row[5],
        }
        for row in rows
    ]


def get_document(doc_id):
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()

    c.execute("""
        SELECT id, filename, category, summary, pages, confidence,
               file_path, extracted_text
        FROM documents
        WHERE id = ?
    """, (doc_id,))

    row = c.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "filename": row[1],
        "category": row[2],
        "summary": row[3],
        "pages": row[4],
        "confidence": row[5],
        "file_path": row[6],
        "extracted_text": row[7],
    }


def delete_document(doc_id):
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()

    c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    deleted = c.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


def get_stats():
    conn = sqlite3.connect("kmrl.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM documents")
    total = c.fetchone()[0]

    c.execute("""
        SELECT COUNT(*)
        FROM documents
        WHERE confidence IS NOT NULL
    """)
    processed = c.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "processed": processed,
        "pending": 0,
        "failed": 0,
    }