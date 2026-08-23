import sqlite3
import json
import os


# Keep the database beside this Python file, regardless of where
# uvicorn is started from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "kmrl.db")


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            category TEXT,
            summary TEXT,
            action_items TEXT,
            deadline TEXT,
            pages INTEGER,
            confidence REAL,
            file_path TEXT,
            extracted_text TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# SAVE DOCUMENT
# ============================================================

def save_to_db(
    filename,
    category,
    summary,
    action_items,
    deadline,
    pages,
    confidence,
    file_path,
    extracted_text,
):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO documents (
            filename,
            category,
            summary,
            action_items,
            deadline,
            pages,
            confidence,
            file_path,
            extracted_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        filename,
        category,
        summary,
        json.dumps(
            action_items or [],
            ensure_ascii=False,
        ),
        deadline,
        pages,
        confidence,
        file_path,
        extracted_text,
    ))

    doc_id = c.lastrowid

    conn.commit()
    conn.close()

    return doc_id


# ============================================================
# SEARCH DATABASE
# ============================================================

def init_search_db():
    # We intentionally use SQLite LIKE search.
    pass


def index_document(
    doc_id,
    filename,
    category,
    summary,
):
    # No separate index is needed for LIKE search.
    pass


# ============================================================
# SEARCH
# ============================================================

def search_documents(query):
    conn = get_connection()
    c = conn.cursor()

    search_term = f"%{query}%"

    c.execute("""
        SELECT
            id,
            filename,
            category,
            summary,
            pages,
            confidence
        FROM documents
        WHERE
            filename LIKE ?
            OR category LIKE ?
            OR summary LIKE ?
            OR extracted_text LIKE ?
        ORDER BY id DESC
        LIMIT 20
    """, (
        search_term,
        search_term,
        search_term,
        search_term,
    ))

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


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

def get_documents():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            id,
            filename,
            category,
            summary,
            pages,
            confidence
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


# ============================================================
# GET ONE DOCUMENT
# ============================================================

def get_document(doc_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            id,
            filename,
            category,
            summary,
            action_items,
            deadline,
            pages,
            confidence,
            file_path,
            extracted_text
        FROM documents
        WHERE id = ?
    """, (doc_id,))

    row = c.fetchone()
    conn.close()

    if row is None:
        return None

    try:
        action_items = json.loads(row[4] or "[]")
    except Exception:
        action_items = []

    return {
        "id": row[0],
        "filename": row[1],
        "category": row[2],
        "summary": row[3],
        "action_items": action_items,
        "deadline": row[5],
        "pages": row[6],
        "confidence": row[7],
        "file_path": row[8],
        "extracted_text": row[9],
    }


# ============================================================
# DELETE
# ============================================================

def delete_document(doc_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "DELETE FROM documents WHERE id = ?",
        (doc_id,),
    )

    deleted = c.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


# ============================================================
# STATISTICS
# ============================================================

def get_stats():
    conn = get_connection()
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