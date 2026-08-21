import os
import json
import re

from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# WINDOWS TESSERACT CONFIGURATION
# ============================================================
# If Tesseract is not automatically detected on Windows,
# uncomment this line and make sure the path is correct.
#
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():
    """
    Creates a Groq client using GROQ_API_KEY from .env.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


# ============================================================
# PAGE COUNT
# ============================================================

def get_page_count(pdf_path):
    """
    Gets the number of pages in a PDF.

    First tries PyPDF2.
    If that fails, falls back to converting the PDF to images.
    """

    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)

    except Exception:
        try:
            images = convert_from_path(pdf_path)
            return len(images)

        except Exception:
            return 0


# ============================================================
# PDF OCR
# ============================================================

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using OCR.

    Each PDF page is converted into an image and
    Tesseract OCR is applied to it.
    """

    print(f"📄 Converting PDF to images: {pdf_path}")

    try:
        images = convert_from_path(
            pdf_path,
            dpi=200
        )

    except Exception as e:
        print(f"❌ PDF conversion failed: {e}")
        return ""

    full_text = []

    for i, image in enumerate(images):

        print(f"🔍 OCR on page {i + 1}/{len(images)}...")

        try:
            page_text = pytesseract.image_to_string(image)

            full_text.append(
                f"\n--- Page {i + 1} ---\n"
                f"{page_text}"
            )

        except Exception as e:
            print(f"❌ OCR failed on page {i + 1}: {e}")

            full_text.append(
                f"\n--- Page {i + 1} ---\n"
                f"[OCR failed on this page]"
            )

    result = "\n".join(full_text)

    print(f"✅ OCR completed. Extracted {len(result)} characters.")

    return result


# ============================================================
# IMAGE OCR
# ============================================================

def extract_text_from_image(image_path):
    """
    Extract text from PNG/JPG/JPEG using Tesseract.
    """

    from PIL import Image

    try:

        img = Image.open(image_path)

        text = pytesseract.image_to_string(img)

        print(
            f"✅ Image OCR completed. "
            f"Extracted {len(text)} characters."
        )

        return text

    except Exception as e:

        print(f"❌ Image OCR error: {e}")

        return ""


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_text_from_docx(docx_path):
    """
    Extract text from DOCX.
    """

    try:

        from docx import Document

        doc = Document(docx_path)

        full_text = []

        # Paragraphs
        for para in doc.paragraphs:

            text = para.text.strip()

            if text:
                full_text.append(text)

        # Tables
        for table in doc.tables:

            for row in table.rows:

                row_text = []

                for cell in row.cells:

                    cell_text = cell.text.strip()

                    if cell_text:
                        row_text.append(cell_text)

                if row_text:
                    full_text.append(" | ".join(row_text))

        if not full_text:

            return "[No text found in DOCX file]"

        result = "\n".join(full_text)

        print(
            f"✅ DOCX extraction completed. "
            f"Extracted {len(result)} characters."
        )

        return result

    except Exception as e:

        print(f"❌ DOCX extraction error: {e}")

        return f"[Error extracting DOCX: {str(e)}]"


# ============================================================
# IMPORTANT:
# YOUR ORIGINAL MATHEMATICAL EVIDENCE SCORER
# HAS BEEN PRESERVED.
# ============================================================

def calculate_evidence_score(text):
    """
    Calculates an evidence score for each category based on keywords in the text.
    Returns a dictionary with category scores.

    IMPORTANT:
    This mathematical scoring system is intentionally unchanged.
    """

    category_keywords = {
        "Tender / Bid Document": [
            "tender",
            "bid",
            "procurement",
            "submission",
            "contract",
            "rfp",
            "quotation",
            "bidding"
        ],

        "Maintenance Log / Work Order": [
            "maintenance",
            "repair",
            "work order",
            "inspection",
            "track",
            "equipment",
            "service"
        ],

        "Inspection Report": [
            "inspection",
            "safety",
            "audit",
            "compliance",
            "check",
            "report",
            "condition"
        ],

        "Incident Report": [
            "incident",
            "accident",
            "near-miss",
            "emergency",
            "injury",
            "damage"
        ],

        "Policy / Standard Operating Procedure": [
            "policy",
            "procedure",
            "sop",
            "guideline",
            "protocol",
            "standard"
        ],

        "Financial / Budget Document": [
            "budget",
            "financial",
            "cost",
            "expenditure",
            "account",
            "fund",
            "estimate"
        ],

        "HR / Personnel Record": [
            "employee",
            "hr",
            "personnel",
            "leave",
            "attendance",
            "recruitment",
            "staff"
        ],

        "Other": [
            "form",
            "application",
            "miscellaneous",
            "unknown"
        ]
    }

    text_lower = text.lower()

    scores = {}

    for category, keywords in category_keywords.items():

        score = 0.40
        matched_keywords = 0

        for keyword in keywords:

            if keyword.lower() in text_lower:

                matched_keywords += 1
                score += 0.10

        scores[category] = min(score, 1.0)

    return scores


# ============================================================
# TEXT PREPARATION
# ============================================================

def prepare_text_for_ai(text, max_chars=14000):
    """
    Prepares extracted text for the AI.

    We no longer blindly take only the first 2,000 characters.

    For large documents, we keep:
    - beginning
    - middle
    - ending

    This increases the chance of finding:
    - document title
    - organization
    - action items
    - dates
    - deadlines
    """

    if not text:
        return ""

    text = text.strip()

    if len(text) <= max_chars:
        return text

    first_part = int(max_chars * 0.45)
    middle_part = int(max_chars * 0.20)
    last_part = int(max_chars * 0.35)

    middle_start = max(
        0,
        (len(text) // 2) - (middle_part // 2)
    )

    middle_end = middle_start + middle_part

    prepared = (
        text[:first_part]
        + "\n\n--- MIDDLE OF DOCUMENT ---\n\n"
        + text[middle_start:middle_end]
        + "\n\n--- END OF DOCUMENT ---\n\n"
        + text[-last_part:]
    )

    return prepared


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_from_response(response_text):
    """
    Robustly extracts a JSON object from an AI response.

    Handles:
    1. Normal JSON
    2. ```json ... ```
    3. Extra text before JSON
    4. Extra text after JSON
    """

    if not response_text:
        raise ValueError("Empty model response")

    response_text = response_text.strip()

    # --------------------------------------------------------
    # Attempt 1: entire response is JSON
    # --------------------------------------------------------

    try:
        return json.loads(response_text)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Attempt 2: remove markdown code fences
    # --------------------------------------------------------

    cleaned = re.sub(
        r"```(?:json)?",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Attempt 3: find first JSON object
    # --------------------------------------------------------

    decoder = json.JSONDecoder()

    for match in re.finditer(r"\{", cleaned):

        start = match.start()

        try:

            obj, end = decoder.raw_decode(
                cleaned[start:]
            )

            if isinstance(obj, dict):
                return obj

        except json.JSONDecodeError:
            continue

    raise ValueError(
        "Could not extract valid JSON from model response"
    )


# ============================================================
# NORMALIZE AI RESULT
# ============================================================

def normalize_analysis_result(result):
    """
    Makes sure the AI response always has the expected structure.
    """

    if not isinstance(result, dict):
        result = {}

    category = result.get("category")

    if not isinstance(category, str) or not category.strip():
        category = "Other"

    category = category.strip()

    summary = result.get("summary")

    if not isinstance(summary, str):
        summary = "No summary provided."

    summary = summary.strip()

    action_items = result.get("action_items", [])

    if action_items is None:
        action_items = []

    if not isinstance(action_items, list):
        action_items = [str(action_items)]

    clean_action_items = []

    for item in action_items:

        if isinstance(item, dict):

            # Convert structured action item into readable text
            description = item.get(
                "task",
                item.get(
                    "description",
                    str(item)
                )
            )

            clean_action_items.append(
                str(description).strip()
            )

        else:

            item_text = str(item).strip()

            if item_text:
                clean_action_items.append(item_text)

    deadline = result.get(
        "deadline",
        "No deadline specified"
    )

    if deadline is None or not str(deadline).strip():
        deadline = "No deadline specified"

    deadline = str(deadline).strip()

    confidence = result.get("confidence", 0.5)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.5

    confidence = max(
        0.0,
        min(1.0, confidence)
    )

    return {
        "category": category,
        "summary": summary,
        "action_items": clean_action_items,
        "deadline": deadline,
        "confidence": confidence
    }


# ============================================================
# GROQ ANALYSIS
# ============================================================

def analyze_with_groq(text):
    """
    Main AI document analysis function.

    Uses:
        Groq LLM
        +
        Mathematical evidence scorer
        +
        Hybrid confidence calculation
    """

    # --------------------------------------------------------
    # API KEY
    # --------------------------------------------------------

    client = get_groq_client()

    if client is None:

        print("❌ GROQ_API_KEY is missing!")

        return {
            "category": "Other",
            "summary": "GROQ_API_KEY is missing.",
            "action_items": [],
            "deadline": "No deadline specified",
            "confidence": 0.0,
            "analysis_failed": True,
            "error": "GROQ_API_KEY is missing"
        }

    # --------------------------------------------------------
    # EMPTY TEXT
    # --------------------------------------------------------

    if not text or not text.strip():

        print("❌ No text available for AI analysis.")

        return {
            "category": "Other",
            "summary": "No readable text was extracted from the document.",
            "action_items": [],
            "deadline": "No deadline specified",
            "confidence": 0.0,
            "analysis_failed": True,
            "error": "No text available"
        }

    # --------------------------------------------------------
    # PREPARE DOCUMENT
    # --------------------------------------------------------

    trimmed_text = prepare_text_for_ai(
        text,
        max_chars=14000
    )

    # --------------------------------------------------------
    # STRONG JSON PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the document intelligence engine for Kochi Metro Rail Limited (KMRL).

Your job is to analyze the provided document carefully and return structured information.

IMPORTANT RULES:

1. Classify the document into EXACTLY ONE of these categories:

   - Tender / Bid Document
   - Maintenance Log / Work Order
   - Inspection Report
   - Incident Report
   - Policy / Standard Operating Procedure
   - Financial / Budget Document
   - HR / Personnel Record
   - Other

2. Do NOT invent information.

3. Use only information actually present in the document.

4. If the document does not clearly belong to one of the categories,
   use "Other".

5. Summary:
   - Write 2-4 concise sentences.
   - Explain what the document is about.
   - Mention important subject matter.
   - Do not invent facts.

6. Action items:
   Extract tasks, instructions, required actions, recommendations,
   follow-ups, approvals, submissions, repairs, inspections,
   payments, deadlines, or responsibilities that the document
   explicitly requires.

   Return an empty array ONLY if there are genuinely no actionable
   tasks in the document.

   Each action item must be a short, clear sentence.

7. Deadline:
   Find the most relevant explicit due date or deadline.

   Preserve the date exactly as written when possible.

   If there is no deadline or due date anywhere in the document,
   return:

   "No deadline specified"

   Do NOT invent a date.

8. Confidence:
   Give a number between 0.0 and 1.0.

   Confidence should represent how strongly the document evidence
   supports the classification.

9. OCR:
   The text may contain OCR mistakes.
   Interpret obvious OCR errors using surrounding context,
   but NEVER invent missing information.

10. Document titles:
    A title, heading, subject, reference number, department,
    organization name, or section heading can be strong evidence
    for classification.

11. Do not confuse similar categories:

    - Tender/Bid:
      procurement, bidding, quotations, vendors, contract award,
      tender notice, eligibility, bid submission, RFP.

    - Maintenance:
      repair, servicing, equipment maintenance, work orders,
      preventive maintenance, breakdowns, maintenance schedules.

    - Inspection:
      inspection findings, checklist, condition assessment,
      compliance inspection, safety inspection, audit findings.

    - Incident:
      accident, incident, emergency, injury, damage,
      near-miss, event investigation.

    - Policy/SOP:
      rules, policies, procedures, guidelines, protocols,
      instructions intended to govern repeated activities.

    - Financial:
      budgets, expenditure, costs, financial statements,
      estimates, payments, accounts.

    - HR:
      employees, personnel, recruitment, attendance,
      leave, staffing, employee records.

12. IMPORTANT:
    Return ONLY a single valid JSON object.

13. Do not use markdown.

14. Do not use ```json.

15. Do not write explanations before or after the JSON.

EXACT OUTPUT STRUCTURE:

{{
  "category": "One allowed category",
  "summary": "2-4 sentence summary",
  "action_items": [
    "Action item 1",
    "Action item 2"
  ],
  "deadline": "YYYY-MM-DD or original date text or No deadline specified",
  "confidence": 0.85
}}

DOCUMENT:

{trimmed_text}
"""

    # --------------------------------------------------------
    # CALL GROQ
    # --------------------------------------------------------

    response_text = None

    try:

        print("🤖 Sending document to Groq...")

        completion = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict document analysis system. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            response_format={
                "type": "json_object"
            }
        )

        response_text = completion.choices[0].message.content

        print(
            f"📥 Groq response received: "
            f"{len(response_text or '')} characters"
        )

        result = extract_json_from_response(
            response_text
        )

        result = normalize_analysis_result(result)

    # --------------------------------------------------------
    # JSON / STRUCTURED OUTPUT FAILURE
    # --------------------------------------------------------

    except Exception as first_error:

        print(
            f"⚠️ First Groq attempt failed: {first_error}"
        )

        # ----------------------------------------------------
        # SECOND ATTEMPT
        #
        # Sometimes structured JSON mode can fail.
        # Retry without response_format.
        # ----------------------------------------------------

        try:

            print(
                "🔄 Retrying Groq without response_format..."
            )

            completion = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return exactly one JSON object "
                            "and nothing else."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )

            response_text = completion.choices[0].message.content

            print(
                f"📥 Retry response received: "
                f"{len(response_text or '')} characters"
            )

            result = extract_json_from_response(
                response_text
            )

            result = normalize_analysis_result(result)

        except Exception as second_error:

            print(
                f"❌ Second Groq attempt failed: "
                f"{second_error}"
            )

            return {
                "category": "Other",
                "summary": (
                    "Groq analysis failed. "
                    "The document could not be reliably analyzed."
                ),
                "action_items": [],
                "deadline": "No deadline specified",
                "confidence": 0.0,
                "analysis_failed": True,
                "error": str(second_error)
            }

    # ========================================================
    # HYBRID MATHEMATICAL SCORER
    # ========================================================
    #
    # IMPORTANT:
    # YOUR ORIGINAL MATH IS PRESERVED.
    # ========================================================

    groq_category = result.get(
        "category",
        "Other"
    )

    groq_confidence = float(
        result.get(
            "confidence",
            0.5
        )
    )

    # --------------------------------------------------------
    # YOUR ORIGINAL EVIDENCE SCORER
    # --------------------------------------------------------

    evidence_scores = calculate_evidence_score(text)

    evidence_for_category = evidence_scores.get(
        groq_category,
        0.40
    )

    evidence_quality = min(
        (evidence_for_category - 0.40) / 0.60,
        1.0
    )

    evidence_weight = (
        0.30
        +
        (0.50 * evidence_quality)
    )

    groq_weight = 1 - evidence_weight

    final_confidence = (
        (evidence_weight * evidence_for_category)
        +
        (groq_weight * groq_confidence)
    )

    print(
        f"🔬 Evidence Score: "
        f"{evidence_for_category:.3f}"
    )

    print(
        f"🤖 Groq Confidence: "
        f"{groq_confidence:.3f}"
    )

    print(
        f"⚖️ Evidence Weight: "
        f"{evidence_weight:.3f}"
    )

    print(
        f"🤝 Groq Weight: "
        f"{groq_weight:.3f}"
    )

    print(
        f"✅ Final Confidence: "
        f"{final_confidence:.3f}"
    )

    # --------------------------------------------------------
    # EVIDENCE OVERRIDE
    # --------------------------------------------------------

    best_category = max(
        evidence_scores,
        key=evidence_scores.get
    )

    if (
        evidence_scores.get(best_category, 0)
        >
        evidence_scores.get(groq_category, 0) + 0.20
    ):

        final_category = best_category

        print(
            f"⚠️ Evidence override: "
            f"{groq_category} → {best_category}"
        )

    else:

        final_category = groq_category

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "category": final_category,
        "summary": result.get(
            "summary",
            "No summary provided."
        ),
        "action_items": result.get(
            "action_items",
            []
        ),
        "deadline": result.get(
            "deadline",
            "No deadline specified"
        ),
        "confidence": round(
            final_confidence,
            4
        ),
        "analysis_failed": False,
        "error": None
    }


# ============================================================
# PROCESS PDF
# ============================================================

def process_pdf(pdf_path):

    print(
        f"📄 Processing PDF: {pdf_path}"
    )

    pages = get_page_count(
        pdf_path
    )

    print(
        f"📑 Pages: {pages}"
    )

    text = extract_text_from_pdf(
        pdf_path
    )

    print(
        f"📝 Extracted text length: "
        f"{len(text)}"
    )

    analysis = analyze_with_groq(
        text
    )

    return {
        "category": analysis["category"],
        "summary": analysis["summary"],
        "pages": pages,
        "confidence": analysis["confidence"],
        "action_items": analysis["action_items"],
        "deadline": analysis["deadline"],
        "analysis_failed": analysis.get(
            "analysis_failed",
            False
        ),
        "error": analysis.get(
            "error"
        )
    }