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

def extract_text_from_image(image_path):
    """
    Takes a path to an image file (.png, .jpg, .jpeg),
    uses Tesseract to extract text, and returns the text.
    """
    from PIL import Image
    import pytesseract

    # Open the image
    img = Image.open(image_path)
    # Do OCR
    text = pytesseract.image_to_string(img)
    return text
def extract_text_from_docx(docx_path):
    """
    Takes a path to a .docx file,
    extracts all text from paragraphs, and returns it.
    """
    from docx import Document
    
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)
    return "\n".join(full_text)

def analyze_with_groq(text):
    import os
    import json
    from groq import Groq

    # Get the API key from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY is missing in .env file!")
        return {
            "category": "General",
            "summary": "API key missing. Please add GROQ_API_KEY to .env",
            "confidence": 0.0
        }

    client = Groq(api_key=api_key)

    # Trim text to first 2000 characters to avoid token limit issues
    trimmed_text = text[:2000] if text else ""

    prompt = f"""
You are an expert document classifier for Kochi Metro Rail Limited (KMRL).
Classify the document into EXACTLY ONE of these specific categories:
- Tender / Bid Document
- Maintenance Log / Work Order
- Inspection Report (safety, quality, or routine)
- Incident Report (accident, near-miss)
- Policy / Standard Operating Procedure (SOP)
- Financial / Budget Document
- HR / Personnel Record
- Other (if none of the above fits)

Instructions:
- Read the text carefully.
- Provide a concise summary (max 3 sentences) highlighting the main purpose.
- Give a confidence score from 0.0 to 1.0 (1.0 = very certain).
- If the document is unclear, still pick the closest category and lower your confidence.

Output ONLY valid JSON with exactly these keys:
{{"category": "...", "summary": "...", "confidence": 0.85}}

Document text (first 2000 characters):
{trimmed_text}
"""

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}  # ensures JSON output
        )

        response_text = completion.choices[0].message.content
        print(f"✅ Groq raw response: {response_text}")  # See in terminal

        # Parse JSON
        result = json.loads(response_text)

        # Ensure all keys exist
        return {
            "category": result.get("category", "Other"),
            "summary": result.get("summary", "No summary provided."),
            "confidence": float(result.get("confidence", 0.5))
        }

    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return {
            "category": "General",
            "summary": f"Failed to analyze document. Error: {str(e)}",
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