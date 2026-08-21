import os
import json

from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# GROQ
# ============================================================

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ============================================================
# PAGE COUNT
# ============================================================

def get_page_count(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        images = convert_from_path(pdf_path)
        return len(images)


# ============================================================
# PDF OCR
# ============================================================

def extract_text_from_pdf(pdf_path):
    print("Converting PDF to images...")

    images = convert_from_path(pdf_path, dpi=200)

    full_text = ""

    for i, image in enumerate(images):
        print(f"OCR on page {i + 1}...")

        page_text = pytesseract.image_to_string(image)

        full_text += f"\n--- Page {i + 1} ---\n{page_text}"

    return full_text


# ============================================================
# IMAGE OCR
# ============================================================

def extract_text_from_image(image_path):
    from PIL import Image

    img = Image.open(image_path)

    text = pytesseract.image_to_string(img)

    return text


# ============================================================
# DOCX TEXT EXTRACTION
# ============================================================

def extract_text_from_docx(docx_path):
    try:
        from docx import Document

        doc = Document(docx_path)

        full_text = []

        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)

        if not full_text:
            return "[No text found in DOCX file]"

        return "\n".join(full_text)

    except Exception as e:
        print(f"DOCX extraction error: {e}")

        return f"[Error extracting DOCX: {str(e)}]"


# ============================================================
# KMRL CONFIDENCE ALGORITHM
# ============================================================

def calculate_confidence(category, evidence, text):
    """
    Calculate confidence using evidence actually found
    inside the extracted document.

    This algorithm is used ONLY for KMRL documents.
    """

    if not text or not text.strip():
        return 0.0

    text_lower = text.lower()

    # --------------------------------------------------------
    # Verify Groq evidence exists in the actual OCR text
    # --------------------------------------------------------

    verified_evidence = []

    for item in evidence:
        if not item:
            continue

        evidence_text = str(item).strip().lower()

        if len(evidence_text) >= 5 and evidence_text in text_lower:
            verified_evidence.append(evidence_text)

    evidence_count = len(verified_evidence)

    # --------------------------------------------------------
    # Category-specific keywords
    # --------------------------------------------------------

    category_keywords = {

        "Tender / Bid Document": [
            "tender",
            "bid",
            "bid submission",
            "eligibility criteria",
            "notice inviting tender",
            "nit",
            "quotation",
            "procurement",
            "technical bid",
            "financial bid",
        ],

        "Maintenance Log / Work Order": [
            "maintenance",
            "work order",
            "repair",
            "inspection",
            "servicing",
            "equipment",
            "maintenance schedule",
            "replacement",
            "breakdown",
        ],

        "Inspection Report": [
            "inspection",
            "inspection report",
            "observations",
            "findings",
            "inspection date",
            "safety inspection",
            "quality inspection",
        ],

        "Incident Report": [
            "incident",
            "accident",
            "near miss",
            "injury",
            "incident report",
            "root cause",
            "corrective action",
        ],

        "Policy / Standard Operating Procedure (SOP)": [
            "policy",
            "standard operating procedure",
            "sop",
            "procedure",
            "guidelines",
            "shall",
            "must",
            "compliance",
        ],

        "Financial / Budget Document": [
            "budget",
            "financial",
            "expenditure",
            "revenue",
            "invoice",
            "payment",
            "cost",
            "amount",
            "tax",
        ],

        "HR / Personnel Record": [
            "employee",
            "personnel",
            "human resources",
            "hr",
            "joining date",
            "designation",
            "salary",
            "leave",
            "staff",
        ],

        "Other": [],
    }

    keywords = category_keywords.get(category, [])

    matched_keywords = [
        keyword
        for keyword in keywords
        if keyword.lower() in text_lower
    ]

    keyword_count = len(matched_keywords)

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if evidence_count == 0 and keyword_count == 0:
        return 0.30

    # --------------------------------------------------------
    # Base confidence
    # --------------------------------------------------------

    confidence = 0.40

    # Direct evidence
    confidence += min(evidence_count * 0.12, 0.36)

    # Category keywords
    confidence += min(keyword_count * 0.04, 0.20)

    # Other should never look extremely confident
    if category == "Other":
        confidence = min(confidence, 0.70)

    return round(min(confidence, 0.98), 2)


# ============================================================
# GROQ ANALYSIS
# ============================================================

def analyze_with_groq(text):
    """
    Analyze a document using Groq.

    KMRL documents:
        Confidence is calculated by our backend algorithm.

    Non-KMRL documents:
        Confidence comes from Groq.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("GROQ_API_KEY is missing in .env")

        return {
            "is_kmrl": False,
            "category": "Other",
            "summary": "GROQ_API_KEY is missing.",
            "action_items": [],
            "deadline": "No deadline specified",
            "confidence": 0.0,
        }

    client = Groq(api_key=api_key)

    # Prevent extremely large requests
    trimmed_text = text[:2500] if text else ""

    prompt = f"""
You are an expert document classifier.

The main purpose of this system is to analyze documents
belonging to Kochi Metro Rail Limited (KMRL).

First determine whether the document is genuinely related
to KMRL.

KMRL-related evidence can include:
- Kochi Metro Rail Limited
- KMRL
- Kochi Metro
- Metro Rail operations
- Metro stations
- Metro maintenance
- Metro tenders
- Metro infrastructure
- Metro safety
- Metro employees
- KMRL-specific operational documents

IMPORTANT:
A document is NOT KMRL merely because it is an official
government document or because it contains generic words
such as maintenance, inspection, HR, tender, etc.

If the document is clearly unrelated to KMRL,
set "is_kmrl" to false.

If it is KMRL-related, set "is_kmrl" to true.

For KMRL documents classify into EXACTLY ONE:

- Tender / Bid Document
- Maintenance Log / Work Order
- Inspection Report
- Incident Report
- Policy / Standard Operating Procedure (SOP)
- Financial / Budget Document
- HR / Personnel Record
- Other

For non-KMRL documents:
- Use category "Other" unless another category is genuinely
  useful for describing the document.

Then extract:

1. SUMMARY
Give a brief summary of the document's main purpose.

2. ACTION ITEMS
Find specific tasks, actions, submissions, inspections,
repairs, follow-ups, or requirements.

If none exist:
[]

3. DEADLINE
Find an actual deadline or important due date.

If none exists:
"No deadline specified"

4. EVIDENCE
For KMRL documents only, return 1 to 5 SHORT EXACT
PHRASES copied directly from the supplied document text
that support the category.

Evidence MUST appear exactly in the supplied text.
Do not invent or paraphrase evidence.

5. CONFIDENCE
For NON-KMRL documents only, provide a confidence score
from 0.0 to 1.0.

For KMRL documents, this value is ignored because the
backend calculates confidence independently.

Return ONLY valid JSON.

Use exactly these keys:

{{
    "is_kmrl": true,
    "category": "...",
    "summary": "...",
    "action_items": [],
    "deadline": "No deadline specified",
    "evidence": [],
    "confidence": 0.85
}}

Document text:

{trimmed_text}
"""

    try:

        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful document analysis system. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
            reasoning_effort="none",
        )

        response_text = completion.choices[0].message.content

        print(f"Groq raw response: {response_text}")

        result = json.loads(response_text)

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        is_kmrl = bool(result.get("is_kmrl", False))

        category = result.get("category", "Other")

        summary = result.get(
            "summary",
            "No summary provided."
        )

        action_items = result.get(
            "action_items",
            []
        )

        deadline = result.get(
            "deadline",
            "No deadline specified"
        )

        evidence = result.get(
            "evidence",
            []
        )

        groq_confidence = result.get(
            "confidence",
            0.5
        )

        # ----------------------------------------------------
        # Make sure action_items is always a list
        # ----------------------------------------------------

        if not isinstance(action_items, list):
            action_items = []

        # ----------------------------------------------------
        # Make sure evidence is always a list
        # ----------------------------------------------------

        if not isinstance(evidence, list):
            evidence = []

        # ----------------------------------------------------
        # Make sure confidence is valid
        # ----------------------------------------------------

        try:
            groq_confidence = float(groq_confidence)
        except (TypeError, ValueError):
            groq_confidence = 0.5

        groq_confidence = max(
            0.0,
            min(groq_confidence, 1.0)
        )

        # ----------------------------------------------------
        # FINAL CONFIDENCE DECISION
        # ----------------------------------------------------

        if is_kmrl:

            confidence = calculate_confidence(
                category=category,
                evidence=evidence,
                text=text,
            )

            print("KMRL document detected.")
            print(f"Verified evidence: {evidence}")
            print(f"Our confidence: {confidence}")

        else:

            confidence = round(
                groq_confidence,
                2
            )

            print("Non-KMRL document detected.")
            print(f"Groq confidence: {confidence}")

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "is_kmrl": is_kmrl,
            "category": category,
            "summary": summary,
            "action_items": action_items,
            "deadline": deadline,
            "confidence": confidence,
        }

    except Exception as e:

        print(f"Groq API error: {e}")

        return {
            "is_kmrl": False,
            "category": "Other",
            "summary": f"Failed to analyze document. Error: {str(e)}",
            "action_items": [],
            "deadline": "No deadline specified",
            "confidence": 0.0,
        }


# ============================================================
# COMPLETE PDF PROCESSING
# ============================================================

def process_pdf(pdf_path):

    print(f"Processing: {pdf_path}")

    pages = get_page_count(pdf_path)

    print(f"Pages: {pages}")

    text = extract_text_from_pdf(pdf_path)

    print(f"Extracted text length: {len(text)}")

    analysis = analyze_with_groq(text)

    return {
        "is_kmrl": analysis["is_kmrl"],
        "category": analysis["category"],
        "summary": analysis["summary"],
        "action_items": analysis["action_items"],
        "deadline": analysis["deadline"],
        "pages": pages,
        "confidence": analysis["confidence"],
    }