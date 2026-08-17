from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from database import init_db, save_to_db, init_search_db, index_document, search_documents
from process import extract_text_from_pdf, extract_text_from_image, extract_text_from_docx, analyze_with_groq, get_page_count

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
    import os
    import shutil

    # 1. Save the uploaded file to the "uploads" folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Check the file extension
    ext = os.path.splitext(file.filename)[1].lower()

    # 3. Extract text and count pages based on file type
    if ext == ".pdf":
        pages = get_page_count(file_path)
        extracted_text = extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg"]:
        pages = 1  # images are single page
        extracted_text = extract_text_from_image(file_path)
    elif ext == ".docx":
        pages = 1  # treat docx as single page for simplicity
        extracted_text = extract_text_from_docx(file_path)
    else:
        return {"error": f"Unsupported file type: {ext}. Use PDF, PNG, JPG, JPEG."}

    # 4. If OCR got nothing, put a placeholder
    if not extracted_text.strip():
        extracted_text = "[No text could be extracted from this file]"

    # 5. Send the text to Groq for classification
    analysis = analyze_with_groq(extracted_text)

    # 6. Save to database (now with extracted_text)
    doc_id = save_to_db(
        filename=file.filename,
        category=analysis["category"],
        summary=analysis["summary"],
        pages=pages,
        confidence=analysis["confidence"],
        file_path=file_path,
        extracted_text=extracted_text
    )

    # 7. Add to search index (uses filename + summary)
    index_document(doc_id, file.filename, analysis["category"], analysis["summary"])

    # 8. Return the result
    return {
        "filename": file.filename,
        "category": analysis["category"],
        "summary": analysis["summary"],
        "pages": pages,
        "confidence": analysis["confidence"]
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