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
    version="1.0.0"
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

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


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
        "status": "online"
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
):
    """
    Automatically logs bugs to bugs.csv.
    """

    csv_file = "bugs.csv"

    file_exists = os.path.isfile(
        csv_file
    )

    with open(
        csv_file,
        mode="a",
        newline="",
        encoding="utf-8"
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

            "Unfixed",
        ])


# ============================================================
# UPLOAD
# ============================================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    file_path = None

    try:

        # ----------------------------------------------------
        # Validate filename
        # ----------------------------------------------------

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

        allowed_extensions = [
            ".pdf",
            ".png",
            ".jpg",
            ".jpeg",
            ".docx"
        ]

        if ext not in allowed_extensions:

            return {
                "error": (
                    f"Unsupported file type: {ext}. "
                    "Use PDF, PNG, JPG, JPEG, or DOCX."
                )
            }

        # ----------------------------------------------------
        # Save file
        # ----------------------------------------------------

        file_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        print(
            f"📥 Uploaded: {filename}"
        )

        # ----------------------------------------------------
        # EXTRACT TEXT
        # ----------------------------------------------------

        if ext == ".pdf":

            pages = get_page_count(
                file_path
            )

            extracted_text = extract_text_from_pdf(
                file_path
            )

        elif ext in [
            ".png",
            ".jpg",
            ".jpeg"
        ]:

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

            return {
                "error": "Unsupported file."
            }

        # ----------------------------------------------------
        # OCR FAILURE
        # ----------------------------------------------------

        if (
            not extracted_text
            or
            not extracted_text.strip()
        ):

            log_bug(
                document_name=filename,
                error_description=(
                    "No text could be extracted "
                    "from the file."
                ),
                file_type=ext.upper().replace(
                    ".",
                    ""
                )
            )

            return {
                "id": None,
                "filename": filename,
                "category": "Other",
                "summary": (
                    "No readable text could be "
                    "extracted from this document."
                ),
                "action_items": [],
                "deadline": "No deadline specified",
                "pages": pages,
                "confidence": 0.0,
                "analysis_failed": True,
                "error": (
                    "OCR/text extraction failed."
                )
            }

        # ----------------------------------------------------
        # AI ANALYSIS
        # ----------------------------------------------------

        print(
            "🤖 Starting document analysis..."
        )

        analysis = analyze_with_groq(
            extracted_text
        )

        confidence = analysis.get(
            "confidence",
            0.0
        )

        category = analysis.get(
            "category",
            "Other"
        )

        action_items = analysis.get(
            "action_items",
            []
        )

        deadline = analysis.get(
            "deadline",
            "No deadline specified"
        )

        summary = analysis.get(
            "summary",
            "No summary provided."
        )

        analysis_failed = analysis.get(
            "analysis_failed",
            False
        )

        analysis_error = analysis.get(
            "error"
        )

        # ----------------------------------------------------
        # AI FAILURE
        #
        # IMPORTANT:
        # Do NOT save failed AI analysis as a normal document.
        # ----------------------------------------------------

        if analysis_failed:

            log_bug(
                document_name=filename,
                error_description=(
                    f"AI analysis failed: "
                    f"{analysis_error or 'Unknown error'}"
                ),
                category_actual=category,
                action_items_actual=str(
                    action_items
                ),
                deadline_actual=deadline,
                file_type=ext.upper().replace(
                    ".",
                    ""
                )
            )

            return {
                "id": None,
                "filename": filename,
                "category": category,
                "summary": summary,
                "action_items": action_items,
                "deadline": deadline,
                "pages": pages,
                "confidence": confidence,
                "analysis_failed": True,
                "error": analysis_error
            }

        # ----------------------------------------------------
        # LOW CONFIDENCE BUG
        # ----------------------------------------------------

        if confidence < 0.5:

            log_bug(
                document_name=filename,
                error_description=(
                    f"Low confidence score: "
                    f"{confidence}"
                ),
                category_actual=category,
                action_items_actual=str(
                    action_items
                ),
                deadline_actual=deadline,
                file_type=ext.upper().replace(
                    ".",
                    ""
                )
            )

        # ----------------------------------------------------
        # OTHER CATEGORY BUG
        # ----------------------------------------------------

        if category in [
            "Other",
            "General"
        ]:

            log_bug(
                document_name=filename,
                error_description=(
                    "Document classified as "
                    "'Other' or 'General'."
                ),
                category_actual=category,
                action_items_actual=str(
                    action_items
                ),
                deadline_actual=deadline,
                file_type=ext.upper().replace(
                    ".",
                    ""
                )
            )

        # ----------------------------------------------------
        # POSSIBLE ACTION ITEM BUG
        # ----------------------------------------------------

        if (
            action_items == []
            and
            confidence > 0.8
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
                file_type=ext.upper().replace(
                    ".",
                    ""
                )
            )

        # ----------------------------------------------------
        # SAVE DATABASE
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

        # ----------------------------------------------------
        # SEARCH INDEX
        # ----------------------------------------------------

        index_document(
            doc_id,
            filename,
            category,
            summary,
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

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
            "error": None
        }

    except Exception as e:

        print(
            f"❌ Upload error: {e}"
        )

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
                )[1].upper().replace(
                    ".",
                    ""
                )
                if file and file.filename
                else "Unknown"
            )
        )

        return {
            "id": None,
            "filename": (
                file.filename
                if file and file.filename
                else None
            ),
            "category": "Other",
            "summary": "Document processing failed.",
            "action_items": [],
            "deadline": "No deadline specified",
            "pages": 0,
            "confidence": 0.0,
            "analysis_failed": True,
            "error": str(e)
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

    if not os.path.isfile("bugs.csv"):

        return {
            "total_bugs": 0,
            "bugs": []
        }

    with open(
        "bugs.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.reader(file)

        data = list(reader)

    return {
        "total_bugs": max(
            0,
            len(data) - 1
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


# ============================================================
# SINGLE DOCUMENT
# ============================================================

@app.get("/documents/{doc_id}")
def get_single_document(
    doc_id: int
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
# STATISTICS
# ============================================================

@app.get("/stats")
def document_stats():

    return get_stats()


# ============================================================
# DELETE
# ============================================================

@app.delete("/documents/{doc_id}")
def remove_document(
    doc_id: int
):

    deleted = delete_document(
        doc_id
    )

    if not deleted:

        return {
            "success": False,
            "error": "Document not found"
        }

    return {
        "success": True,
        "message": "Document deleted successfully"
    }


# ============================================================
# DOWNLOAD
# ============================================================

@app.get(
    "/documents/{doc_id}/download"
)
def download_document(
    doc_id: int
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
        or
        not os.path.exists(file_path)
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
        )
    }

    return FileResponse(
        path=file_path,
        filename=document["filename"],
        media_type=media_types.get(
            extension,
            "application/octet-stream"
        )
    )