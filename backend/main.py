from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from database import init_db, save_to_db, init_search_db, index_document, search_documents
from process import process_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()
init_search_db()

@app.get("/")
def home():
    return {"message": "KMRL Backend is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = process_pdf(file_path)
    
    doc_id = save_to_db(
        filename=file.filename,
        category=result["category"],
        summary=result["summary"],
        pages=result["pages"],
        confidence=result["confidence"],
        file_path=file_path
    )
    
    # NEW: Add to search index so we can find it later
    index_document(doc_id, file.filename, result["category"], result["summary"])
    
    return {
        "filename": file.filename,
        "category": result["category"],
        "summary": result["summary"],
        "pages": result["pages"],
        "confidence": result["confidence"]
    }
@app.get("/search")
def search_docs(q: str):
    """
    Search documents by keyword.
    Example: /search?q=maintenance
    """
    results = search_documents(q)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }