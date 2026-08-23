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


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="KMRL Document Intelligence API",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
BUG_FILE = os.path.join(BASE_DIR, "bugs.csv")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

init_db()
init_search_db()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "KMRL Backend is running!",
        "status": "online",
    }


# ============================================================
# BUG LOGGER
# ============================================================

def log_bug(
    document_name,
    error_description,
    category_expected=None,
    category_actual=None,
    action_items_expected=None,
    action_items_actual=None,
    deadline_expected=None,
    deadline_actual=None,
    file_type=None,
    status="Unfixed",
):
    file_exists = os.path.isfile(BUG_FILE)

    with open(
        BUG_FILE,
        mode="a",
        newline="",
        encoding="utf-8",
    ) as file:
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
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            document_name,
            file_type or "Unknown",
            category_expected or "N/A",
            category_actual or "N/A",
            action_items_expected or "N/A",
            action_items_actual or "N/A",
            deadline_expected or "N/A",
            deadline_actual or "N/A",
            error_description,
            status,
        ])


# ============================================================
# UPLOAD
# ============================================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
):
    file_path = None

    try:
        if not file.filename:
            return {
                "error": "No filename provided."
            }

        filename = os.path.basename(
            file.filename
        )

        ext = os.path.splitext(
            filename
        )[1].lower()

        allowed_extensions = {
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".docx",
        }

        if ext not in allowed_extensions:
            return {
                "error": (
                    f"Unsupported file type: {ext}. "
                    "Use PDF, PNG, JPG, JPEG, or DOCX."
                )
            }

        file_path = os.path.join(
            UPLOAD_DIR,
            filename,
        )

        with open(
            file_path,
            "wb",
        ) as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        print(
            f"📥 Uploaded: {filename}"
        )

        # ----------------------------------------------------
        # EXTRACTION
        # ----------------------------------------------------

        if ext == ".pdf":
            pages = get_page_count(
                file_path
            )
            extracted_text = extract_text_from_pdf(
                file_path
            )

        elif ext in {
            ".png",
            ".jpg",
            ".jpeg",
        }:
            pages = 1
            extracted_text = extract_text_from_image(
                file_path
            )

        elif ext == ".docx":
            pages = 1
            extracted_text = extract_text_from_docx(
                file_path
            )

        else:
            pages = 0
            extracted_text = ""

        # ----------------------------------------------------
        # NEVER TURN AN EMPTY EXTRACTION INTO A CRASH.
        # ----------------------------------------------------

        if not extracted_text or not extracted_text.strip():
            extracted_text = (
                "[No readable text was extracted. "
                "The file itself has been saved for download.]"
            )

            log_bug(
                document_name=filename,
                error_description=(
                    "Text extraction returned no readable text."
                ),
                file_type=ext.replace(".", "").upper(),
                status="Partial",
            )

            # Still save the document so the API never responds
            # with a fake successful AI analysis.
            doc_id = save_to_db(
                filename=filename,
                category="Other",
                summary=(
                    "The document was saved, but no readable "
                    "text could be extracted automatically."
                ),
                action_items=[],
                deadline="No deadline specified",
                pages=pages,
                confidence=0.0,
                file_path=file_path,
                extracted_text=extracted_text,
            )

            return {
                "id": doc_id,
                "filename": filename,
                "category": "Other",
                "summary": (
                    "The document was saved, but no readable "
                    "text could be extracted automatically."
                ),
                "action_items": [],
                "deadline": "No deadline specified",
                "pages": pages,
                "confidence": 0.0,
                "analysis_failed": False,
                "partial_analysis": True,
                "error": None,
            }

        # ----------------------------------------------------
        # AI + EVIDENCE ANALYSIS
        # ----------------------------------------------------

        print(
            "🤖 Starting document analysis..."
        )

        analysis = analyze_with_groq(
            extracted_text
        )

        confidence = float(
            analysis.get(
                "confidence",
                0.0,
            )
        )

        category = analysis.get(
            "category",
            "Other",
        )

        action_items = analysis.get(
            "action_items",
            [],
        )

        deadline = analysis.get(
            "deadline",
            "No deadline specified",
        )

        summary = analysis.get(
            "summary",
            "No summary provided.",
        )

        partial_analysis = bool(
            analysis.get(
                "partial_analysis",
                False,
            )
        )

        # ----------------------------------------------------
        # PARTIAL ANALYSIS IS NOT A HARD FAILURE.
        # ----------------------------------------------------

        if partial_analysis:
            log_bug(
                document_name=filename,
                error_description=(
                    "One or more AI chunks were unavailable; "
                    "document was completed using successful "
                    "chunks plus local evidence fallback."
                ),
                category_actual=category,
                action_items_actual=str(action_items),
                deadline_actual=deadline,
                file_type=ext.replace(".", "").upper(),
                status="Partial",
            )

        # ----------------------------------------------------
        # LOW CONFIDENCE
        # ----------------------------------------------------

        if confidence < 0.5:
            log_bug(
                document_name=filename,
                error_description=(
                    f"Low confidence score: {confidence}"
                ),
                category_actual=category,
                action_items_actual=str(action_items),
                deadline_actual=deadline,
                file_type=ext.replace(".", "").upper(),
                status="Unfixed",
            )

        # ----------------------------------------------------
        # OTHER CATEGORY
        # ----------------------------------------------------

        if category in {
            "Other",
            "General",
        }:
            log_bug(
                document_name=filename,
                error_description=(
                    "Document classified as "
                    "'Other' or 'General'."
                ),
                category_actual=category,
                action_items_actual=str(action_items),
                deadline_actual=deadline,
                file_type=ext.replace(".", "").upper(),
                status="Unfixed",
            )

        # ----------------------------------------------------
        # POSSIBLE ACTION ITEM ISSUE
        # ----------------------------------------------------

        if (
            action_items == []
            and confidence > 0.8
        ):
            log_bug(
                document_name=filename,
                error_description=(
                    "No action items extracted "
                    "despite high confidence."
                ),
                category_actual=category,
                action_items_actual="[]",
                deadline_actual=deadline,
                file_type=ext.replace(".", "").upper(),
                status="Unfixed",
            )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        doc_id = save_to_db(
            filename=filename,
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
            filename,
            category,
            summary,
        )

        print(
            f"✅ Document processed successfully. "
            f"ID={doc_id}"
        )

        return {
            "id": doc_id,
            "filename": filename,
            "category": category,
            "summary": summary,
            "action_items": action_items,
            "deadline": deadline,
            "pages": pages,
            "confidence": confidence,
            "analysis_failed": False,
            "partial_analysis": partial_analysis,
            "error": None,
        }

    except Exception as e:
        print(
            f"❌ Upload error: {e}"
        )

        try:
            log_bug(
                document_name=(
                    file.filename
                    if file and file.filename
                    else "Unknown"
                ),
                error_description=(
                    f"Server error: {str(e)}"
                ),
                file_type=(
                    os.path.splitext(
                        file.filename
                    )[1].replace(
                        ".",
                        "",
                    ).upper()
                    if file and file.filename
                    else "Unknown"
                ),
                status="Unfixed",
            )
        except Exception:
            pass

        return {
            "id": None,
            "filename": (
                file.filename
                if file and file.filename
                else None
            ),
            "category": "Other",
            "summary": (
                "The server encountered an error while "
                "processing this document."
            ),
            "action_items": [],
            "deadline": "No deadline specified",
            "pages": 0,
            "confidence": 0.0,
            "analysis_failed": True,
            "partial_analysis": False,
            "error": str(e),
        }


# ============================================================
# SEARCH
# ============================================================

@app.get("/search")
def search_docs(q: str):
    results = search_documents(q)

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


# ============================================================
# BUGS
# ============================================================

@app.get("/bugs")
def view_bugs():
    if not os.path.isfile(BUG_FILE):
        return {
            "total_bugs": 0,
            "bugs": [],
        }

    with open(
        BUG_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.reader(file)
        data = list(reader)

    return {
        "total_bugs": max(
            0,
            len(data) - 1,
        ),
        "bugs": data,
    }


# ============================================================
# DOCUMENTS
# ============================================================

@app.get("/documents")
def get_all_documents():
    documents = get_documents()

    return {
        "count": len(documents),
        "documents": documents,
    }


@app.get("/documents/{doc_id}")
def get_single_document(
    doc_id: int,
):
    document = get_document(
        doc_id
    )

    if document is None:
        return {
            "error": "Document not found"
        }

    return document


# ============================================================
# STATS
# ============================================================

@app.get("/stats")
def document_stats():
    return get_stats()


# ============================================================
# DELETE
# ============================================================

@app.delete("/documents/{doc_id}")
def remove_document(
    doc_id: int,
):
    deleted = delete_document(
        doc_id
    )

    if not deleted:
        return {
            "success": False,
            "error": "Document not found",
        }

    return {
        "success": True,
        "message": "Document deleted successfully",
    }


# ============================================================
# DOWNLOAD
# ============================================================

@app.get(
    "/documents/{doc_id}/download"
)
def download_document(
    doc_id: int,
):
    document = get_document(
        doc_id
    )

    if document is None:
        return {
            "error": "Document not found"
        }

    file_path = document.get(
        "file_path"
    )

    if (
        not file_path
        or not os.path.exists(file_path)
    ):
        return {
            "error": "File not found"
        }

    extension = os.path.splitext(
        document["filename"]
    )[1].lower()

    media_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".docx": (
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
    }

    return FileResponse(
        path=file_path,
        filename=document["filename"],
        media_type=media_types.get(
            extension,
            "application/octet-stream",
        ),
    )