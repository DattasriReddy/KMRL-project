from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import csv
from datetime import datetime

from database import (
    init_db,
    save_to_db,
    init_search_db,
    index_document,
    search_documents,
    get_documents,
    get_document,
    delete_document,
    get_stats,
)

from process import (
    extract_text_from_pdf,
    extract_text_from_image,
    extract_text_from_docx,
    analyze_with_groq,
    get_page_count,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


def log_bug(
    document_name,
    error_description,
    category_expected=None,
    category_actual=None,
    action_items_expected=None,
    action_items_actual=None,
    deadline_expected=None,
    deadline_actual=None,
):
    """Automatically logs bugs to a CSV file."""
    csv_file = "bugs.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Document Name",
                "File Type",
                "Expected Category",
                "Actual Category",
                "Expected Action Items",
                "Actual Action Items",
                "Expected Deadline",
                "Actual Deadline",
                "Error Description",
                "Status",
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            document_name,
            "PDF",
            category_expected or "N/A",
            category_actual or "N/A",
            action_items_expected or "N/A",
            action_items_actual or "N/A",
            deadline_expected or "N/A",
            deadline_actual or "N/A",
            error_description,
            "Unfixed",
        ])


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ext = os.path.splitext(file.filename)[1].lower()

        if ext == ".pdf":
            pages = get_page_count(file_path)
            extracted_text = extract_text_from_pdf(file_path)

        elif ext in [".png", ".jpg", ".jpeg"]:
            pages = 1
            extracted_text = extract_text_from_image(file_path)

        elif ext == ".docx":
            pages = 1
            extracted_text = extract_text_from_docx(file_path)

        else:
            return {
                "error": f"Unsupported file type: {ext}. Use PDF, PNG, JPG, JPEG, or DOCX."
            }

        if not extracted_text or not extracted_text.strip():
            extracted_text = "[No text could be extracted from this file]"

            log_bug(
                document_name=file.filename,
                error_description="No text could be extracted from the file (OCR failed)",
                category_actual="N/A",
                action_items_actual="N/A",
                deadline_actual="N/A",
            )

        analysis = analyze_with_groq(extracted_text)

        confidence = analysis.get("confidence", 0)
        category = analysis.get("category", "General")
        action_items = analysis.get("action_items", [])
        deadline = analysis.get("deadline", "No deadline specified")
        summary = analysis.get("summary", "No summary provided.")

        if confidence < 0.5:
            log_bug(
                document_name=file.filename,
                error_description=f"Low confidence score: {confidence}",
                category_actual=category,
                action_items_actual=str(action_items),
                deadline_actual=deadline,
            )

        if category in ["Other", "General"]:
            log_bug(
                document_name=file.filename,
                error_description="Document classified as 'Other' or 'General'",
                category_actual=category,
                action_items_actual=str(action_items),
                deadline_actual=deadline,
            )

        if action_items == [] and confidence > 0.8:
            log_bug(
                document_name=file.filename,
                error_description="No action items extracted despite high confidence",
                category_actual=category,
                action_items_actual="[]",
                deadline_actual=deadline,
            )

        doc_id = save_to_db(
            filename=file.filename,
            category=category,
            summary=summary,
            action_items=action_items,
            deadline=deadline,
            pages=pages,
            confidence=confidence,
            file_path=file_path,
            extracted_text=extracted_text,
        )

        index_document(
            doc_id,
            file.filename,
            category,
            summary,
        )

        return {
            "id": doc_id,
            "filename": file.filename,
            "category": category,
            "summary": summary,
            "action_items": action_items,
            "deadline": deadline,
            "pages": pages,
            "confidence": confidence,
        }

    except Exception as e:
        log_bug(
            document_name=file.filename,
            error_description=f"Server error: {str(e)}",
            category_actual="N/A",
            action_items_actual="N/A",
            deadline_actual="N/A",
        )

        return {
            "error": f"Internal server error: {str(e)}"
        }


@app.get("/search")
def search_docs(q: str):
    results = search_documents(q)

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


@app.get("/bugs")
def view_bugs():
    """Display all bugs from bugs.csv."""

    if not os.path.isfile("bugs.csv"):
        return {
            "message": "No bugs found yet! Upload some documents!"
        }

    with open("bugs.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        data = list(reader)

    return {
        "total_bugs": len(data) - 1 if data else 0,
        "bugs": data,
    }


@app.get("/documents")
def get_all_documents():
    """Return all uploaded documents."""

    documents = get_documents()

    return {
        "count": len(documents),
        "documents": documents,
    }


@app.get("/documents/{doc_id}")
def get_single_document(doc_id: int):
    """Return one document with extracted text."""

    document = get_document(doc_id)

    if document is None:
        return {
            "error": "Document not found"
        }

    return document


@app.get("/stats")
def document_stats():
    """Return dashboard statistics."""

    return get_stats()


@app.delete("/documents/{doc_id}")
def remove_document(doc_id: int):
    """Delete a document from the database."""

    deleted = delete_document(doc_id)

    if not deleted:
        return {
            "success": False,
            "error": "Document not found"
        }

    return {
        "success": True,
        "message": "Document deleted successfully"
    }


@app.get("/documents/{doc_id}/download")
def download_document(doc_id: int):
    document = get_document(doc_id)

    if document is None:
        return {
            "error": "Document not found"
        }

    file_path = document.get("file_path")

    if not file_path or not os.path.exists(file_path):
        return {
            "error": "File not found"
        }

    return FileResponse(
        path=file_path,
        filename=document["filename"],
        media_type="application/pdf",
    )