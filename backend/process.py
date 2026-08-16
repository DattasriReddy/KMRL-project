import os
import json
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Windows ONLY: uncomment the line below if Tesseract is not found
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_page_count(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        images = convert_from_path(pdf_path)
        return len(images)

def extract_text_from_pdf(pdf_path):
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path, dpi=200)
    full_text = ""
    for i, image in enumerate(images):
        print(f"OCR on page {i+1}...")
        page_text = pytesseract.image_to_string(image)
        full_text += f"\n--- Page {i+1} ---\n{page_text}"
    return full_text

def analyze_with_groq(text):
    trimmed_text = text[:6000]
    prompt = f"""You are a document analyzer for Kochi Metro Rail Limited (KMRL).
Read the following document text and respond ONLY in valid JSON format.

Choose category from: Maintenance, Safety, Operations, HR, Finance, Engineering, General.

JSON format:
{{
  "category": "Maintenance",
  "summary": "2-3 sentence summary here",
  "confidence": 0.94
}}

Document text:
{trimmed_text}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        result = json.loads(chat_completion.choices[0].message.content)
        return {
            "category": result.get("category", "General"),
            "summary": result.get("summary", "No summary available."),
            "confidence": result.get("confidence", 0.5)
        }
    except Exception as e:
        print(f"Groq error: {e}")
        return {
            "category": "General",
            "summary": "Failed to analyze document.",
            "confidence": 0.0
        }

def process_pdf(pdf_path):
    print(f"Processing: {pdf_path}")
    pages = get_page_count(pdf_path)
    print(f"Pages: {pages}")
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted text length: {len(text)}")
    analysis = analyze_with_groq(text)
    return {
        "category": analysis["category"],
        "summary": analysis["summary"],
        "pages": pages,
        "confidence": analysis["confidence"]
    }