from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from database import init_db, save_to_db
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

@app.get("/")
def home():
    return {"message": "KMRL Backend is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = process_pdf(file_path)
    
    save_to_db(
        filename=file.filename,
        category=result["category"],
        summary=result["summary"],
        pages=result["pages"],
        confidence=result["confidence"],
        file_path=file_path
    )
    
    return {
        "filename": file.filename,
        "category": result["category"],
        "summary": result["summary"],
        "pages": result["pages"],
        "confidence": result["confidence"]
    }