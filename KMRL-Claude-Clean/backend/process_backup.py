import os
import json
import re
import math

from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

# Windows ONLY:
# Uncomment this if Tesseract is not automatically detected.
#
# pytesseract.pytesseract.tesseract_cmd = (
#     r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# )


# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "Tender / Bid Document",
    "Maintenance Log / Work Order",
    "Inspection Report",
    "Incident Report",
    "Policy / Standard Operating Procedure (SOP)",
    "Financial / Budget Document",
    "HR / Personnel Record",
    "Other",
]


# Terms that indicate the document is actually related
# to Kochi Metro Rail Limited / metro operations.
KMRL_TERMS = [
    "kochi metro",
    "kochi metro rail",
    "kochi metro rail limited",
    "kmrl",
    "kochimetro",
    "metro rail",
    "metro railway",
    "metro station",
    "metro train",
    "metro operations",
    "metro project",
    "metro corridor",
    "metro system",
]


# Category-specific terms.
CATEGORY_TERMS = {

    "Tender / Bid Document": [
        "tender",
        "tender notice",
        "notice inviting tender",
        "nit",
        "bid",
        "bidder",
        "bidding",
        "quotation",
        "technical bid",
        "financial bid",
        "eligibility criteria",
        "scope of work",
        "earnest money",
        "emd",
        "pre-bid meeting",
        "bid submission",
        "submission of bid",
        "tender document",
        "procurement",
    ],

    "Maintenance Log / Work Order": [
        "maintenance",
        "maintenance log",
        "work order",
        "repair",
        "servicing",
        "preventive maintenance",
        "corrective maintenance",
        "equipment maintenance",
        "breakdown",
        "replacement",
        "repair work",
        "maintenance work",
        "service report",
        "fault",
        "rectification",
    ],

    "Inspection Report": [
        "inspection report",
        "inspection",
        "inspected",
        "safety inspection",
        "quality inspection",
        "inspection findings",
        "inspection observations",
        "observations",
        "non-conformance",
        "nonconformance",
        "compliance inspection",
        "inspection checklist",
        "inspection remarks",
    ],

    "Incident Report": [
        "incident report",
        "incident",
        "accident",
        "near miss",
        "near-miss",
        "injury",
        "emergency",
        "cause of incident",
        "root cause",
        "incident investigation",
        "accident investigation",
        "incident details",
    ],

    "Policy / Standard Operating Procedure (SOP)": [
        "standard operating procedure",
        "sop",
        "policy",
        "procedure",
        "guidelines",
        "operating instructions",
        "work instructions",
        "compliance requirements",
        "standard procedure",
        "operational procedure",
    ],

    "Financial / Budget Document": [
        "budget",
        "financial statement",
        "expenditure",
        "revenue",
        "invoice",
        "payment",
        "cost estimate",
        "financial year",
        "accounts",
        "fund allocation",
        "capital expenditure",
        "financial report",
        "purchase order",
    ],

    "HR / Personnel Record": [
        "employee",
        "personnel",
        "human resources",
        "hr",
        "appointment",
        "leave",
        "salary",
        "payroll",
        "employee id",
        "staff",
        "recruitment",
        "joining",
        "personnel record",
        "employee record",
    ],

    "Other": [],
}


# ============================================================
# FILE / OCR FUNCTIONS
# ============================================================

def get_page_count(pdf_path):
    """
    Return the number of pages in a PDF.
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


def extract_text_from_pdf(pdf_path):
    """
    Convert every PDF page to an image and perform OCR.

    IMPORTANT:
    The entire document is OCR'd.
    There is no 2500-character OCR limitation here.
    """

    print("Converting PDF to images...")

    images = convert_from_path(
        pdf_path,
        dpi=200
    )

    full_text = []

    for index, image in enumerate(images):

        page_number = index + 1

        print(
            f"OCR on page {page_number}..."
        )

        page_text = pytesseract.image_to_string(
            image
        )

        full_text.append(
            f"\n--- Page {page_number} ---\n"
            f"{page_text}"
        )

    return "\n".join(full_text)


def extract_text_from_image(image_path):
    """
    Extract text from PNG/JPG/JPEG.
    """

    from PIL import Image

    image = Image.open(image_path)

    text = pytesseract.image_to_string(
        image
    )

    return text


def extract_text_from_docx(docx_path):
    """
    Extract text from a DOCX document.
    """

    try:

        from docx import Document

        document = Document(docx_path)

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        if not paragraphs:
            return "[No text found in DOCX file]"

        return "\n".join(paragraphs)

    except Exception as error:

        print(
            f"DOCX extraction error: {error}"
        )

        return (
            f"[Error extracting DOCX: {error}]"
        )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """
    Normalize OCR text for keyword matching.
    """

    if not text:
        return ""

    normalized = text.lower()

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    return normalized.strip()


def find_matching_terms(text, terms):
    """
    Return the terms that actually appear in the document.
    """

    normalized = normalize_text(text)

    matches = []

    for term in terms:

        normalized_term = normalize_text(term)

        if not normalized_term:
            continue

        if normalized_term in normalized:
            matches.append(term)

    return matches


# ============================================================
# EVIDENCE SCORING
# ============================================================

def category_keyword_strength(text, category):
    """
    Calculate normalized evidence strength for one category.

    The result is between 0.0 and 1.0.

    We normalize by the number of useful terms instead of simply
    counting raw keywords, because different categories contain
    different numbers of keywords.
    """

    terms = CATEGORY_TERMS.get(
        category,
        []
    )

    if not terms:
        return 0.0, []

    matches = find_matching_terms(
        text,
        terms
    )

    if not matches:
        return 0.0, []

    # We do not want 20 repeated keywords to automatically
    # produce 100% confidence.
    #
    # Five independent matching terms is treated as very strong
    # keyword evidence.
    capped_matches = min(
        len(matches),
        5
    )

    strength = capped_matches / 5.0

    return strength, matches


def kmrl_relevance_strength(text):
    """
    Measure how strongly the document contains explicit KMRL
    / Kochi Metro signals.

    Returns:
        strength: 0.0 - 1.0
        matches: actual matching terms
    """

    matches = find_matching_terms(
        text,
        KMRL_TERMS
    )

    if not matches:
        return 0.0, []

    capped_matches = min(
        len(matches),
        4
    )

    strength = capped_matches / 4.0

    return strength, matches


# ============================================================
# SOFTMAX
# ============================================================

def softmax(score_dictionary, temperature=1.0):
    """
    Convert category scores into normalized probabilities.

    P(category) =
        exp(score / temperature)
        -----------------------
        sum(exp(score_j / temperature))

    The returned probabilities sum to 1.
    """

    if not score_dictionary:
        return {}

    adjusted_scores = {}

    for category, score in score_dictionary.items():

        adjusted_scores[category] = (
            score / temperature
        )

    maximum = max(
        adjusted_scores.values()
    )

    exponentials = {}

    for category, score in adjusted_scores.items():

        exponentials[category] = math.exp(
            score - maximum
        )

    total = sum(
        exponentials.values()
    )

    if total <= 0:
        equal_probability = (
            1.0 / len(score_dictionary)
        )

        return {
            category: equal_probability
            for category in score_dictionary
        }

    return {
        category: value / total
        for category, value in exponentials.items()
    }


# ============================================================
# GROQ ANALYSIS
# ============================================================

def analyze_with_groq(text):
    """
    Ask Groq to semantically analyze the document.

    Groq's confidence is NOT treated as mathematical truth.
    It is one input into the final confidence calculation.
    """

    api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not api_key:

        print(
            "GROQ_API_KEY is missing in .env"
        )

        return {
            "category": "Other",
            "summary": (
                "GROQ_API_KEY is missing."
            ),
            "action_items": [],
            "deadline": (
                "No deadline specified"
            ),
            "evidence": [],
            "confidence_hint": 0.0,
        }

    client = Groq(
        api_key=api_key
    )

    if not text:
        text = "[No text extracted]"

    # --------------------------------------------------------
    # Document length handling
    # --------------------------------------------------------
    #
    # We OCR the COMPLETE document.
    #
    # Groq does not necessarily need every character of a huge
    # document. Instead of only taking the first 2500 characters,
    # we take representative sections from the beginning,
    # middle, and end.
    # --------------------------------------------------------

    MAX_ANALYSIS_CHARS = 12000

    if len(text) <= MAX_ANALYSIS_CHARS:

        analysis_text = text

    else:

        section_size = (
            MAX_ANALYSIS_CHARS // 3
        )

        beginning = text[
            :section_size
        ]

        middle_start = (
            (len(text) // 2)
            - (section_size // 2)
        )

        middle_end = (
            middle_start
            + section_size
        )

        middle = text[
            middle_start:middle_end
        ]

        ending = text[
            -section_size:
        ]

        analysis_text = (
            beginning
            + "\n\n"
            + "[... MIDDLE SECTION ...]"
            + "\n\n"
            + middle
            + "\n\n"
            + "[... END SECTION ...]"
            + "\n\n"
            + ending
        )

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are an expert document classifier for
Kochi Metro Rail Limited (KMRL).

Classify this document into EXACTLY ONE of these categories:

- Tender / Bid Document
- Maintenance Log / Work Order
- Inspection Report
- Incident Report
- Policy / Standard Operating Procedure (SOP)
- Financial / Budget Document
- HR / Personnel Record
- Other

IMPORTANT CLASSIFICATION RULE:

"Other" means the document is not one of the KMRL
document categories above.

Do not classify a document as KMRL-related merely because
generic words such as "form", "report", "maintenance",
"inspection", "application", or "office" appear.

Look for contextual evidence.

For example, a voter registration form should be classified
as Other even if it is an official government document.

Provide:

1. category
2. summary
3. action_items
4. deadline
5. evidence
6. confidence_hint

The evidence field must contain short phrases that are
actually supported by the supplied document text.

The confidence_hint should be your semantic assessment
from 0.0 to 1.0.

IMPORTANT:

Your confidence_hint is NOT the final system confidence.
The application will independently calculate confidence
using document evidence.

For "Other", evidence should explain why the document
appears unrelated to KMRL.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "category": "Tender / Bid Document",
    "summary": "Brief summary of the document.",
    "action_items": [
        "Task 1",
        "Task 2"
    ],
    "deadline": "YYYY-MM-DD or No deadline specified",
    "evidence": [
        "Kochi Metro Rail Limited",
        "Tender Notice"
    ],
    "confidence_hint": 0.85
}}

DOCUMENT TEXT:

{analysis_text}
"""

    try:

        completion = client.chat.completions.create(

            model="qwen/qwen3.6-27b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document classification "
                        "system. Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.1,

            response_format={
                "type": "json_object"
            },
        )

        response_text = (
            completion
            .choices[0]
            .message
            .content
        )

        print(
            f"Groq raw response: {response_text}"
        )

        result = json.loads(
            response_text
        )

        category = result.get(
            "category",
            "Other"
        )

        if category not in CATEGORIES:

            category = "Other"

        try:

            confidence_hint = float(
                result.get(
                    "confidence_hint",
                    0.5
                )
            )

        except (TypeError, ValueError):

            confidence_hint = 0.5

        confidence_hint = max(
            0.0,
            min(
                1.0,
                confidence_hint
            )
        )

        action_items = result.get(
            "action_items",
            []
        )

        if not isinstance(
            action_items,
            list
        ):
            action_items = []

        evidence = result.get(
            "evidence",
            []
        )

        if not isinstance(
            evidence,
            list
        ):
            evidence = []

        return {
            "category": category,

            "summary": result.get(
                "summary",
                "No summary provided."
            ),

            "action_items": action_items,

            "deadline": result.get(
                "deadline",
                "No deadline specified"
            ),

            "evidence": evidence,

            "confidence_hint": confidence_hint,
        }

    except Exception as error:

        print(
            f"Groq API error: {error}"
        )

        return {
            "category": "Other",

            "summary": (
                "Failed to analyze document. "
                f"Error: {error}"
            ),

            "action_items": [],

            "deadline": (
                "No deadline specified"
            ),

            "evidence": [],

            "confidence_hint": 0.0,
        }


# ============================================================
# MATHEMATICAL EVIDENCE MODEL
# ============================================================

def calculate_evidence_probabilities(
    text,
    predicted_category
):
    """
    Calculate a normalized probability distribution over all
    document categories using deterministic document evidence.

    This is independent of Groq's confidence.

    Returns:

        probabilities
        evidence_strength
        diagnostic_information
    """

    kmrl_strength, kmrl_matches = (
        kmrl_relevance_strength(text)
    )

    raw_scores = {}

    category_diagnostics = {}

    # --------------------------------------------------------
    # Calculate evidence for every category.
    # --------------------------------------------------------

    for category in CATEGORIES:

        if category == "Other":
            continue

        category_strength, category_matches = (
            category_keyword_strength(
                text,
                category
            )
        )

        # KMRL relevance matters for KMRL categories.
        #
        # Example:
        #
        # "maintenance" alone is weak.
        #
        # "KMRL" + "maintenance" is much stronger.
        #
        kmrl_component = (
            0.40 * kmrl_strength
        )

        category_component = (
            0.60 * category_strength
        )

        score = (
            kmrl_component
            + category_component
        )

        raw_scores[category] = score

        category_diagnostics[category] = {
            "category_strength": (
                category_strength
            ),
            "category_matches": (
                category_matches
            ),
        }

    # --------------------------------------------------------
    # Calculate Other evidence.
    #
    # Other is stronger when:
    #
    # 1. KMRL evidence is weak
    # 2. All KMRL category evidence is weak
    #
    # This is intentionally conservative.
    # --------------------------------------------------------

    kmrl_category_scores = list(
        raw_scores.values()
    )

    if kmrl_category_scores:

        strongest_kmrl_score = max(
            kmrl_category_scores
        )

    else:

        strongest_kmrl_score = 0.0

    other_score = (
        0.55 * (1.0 - kmrl_strength)
        + 0.45 * (1.0 - strongest_kmrl_score)
    )

    other_score = max(
        0.0,
        min(
            1.0,
            other_score
        )
    )

    raw_scores["Other"] = other_score

    # --------------------------------------------------------
    # Convert raw evidence scores into probabilities.
    # --------------------------------------------------------

    probabilities = softmax(
        raw_scores,
        temperature=0.50
    )

    # --------------------------------------------------------
    # Evidence strength
    # --------------------------------------------------------
    #
    # We measure how much concrete evidence exists in the
    # document rather than simply trusting the winning score.
    # --------------------------------------------------------

    predicted_category_strength, predicted_matches = (
        category_keyword_strength(
            text,
            predicted_category
        )
    )

    if predicted_category == "Other":

        evidence_strength = (
            0.60 * (1.0 - kmrl_strength)
            + 0.40 * (1.0 - strongest_kmrl_score)
        )

    else:

        evidence_strength = (
            0.50 * kmrl_strength
            + 0.50 * predicted_category_strength
        )

    evidence_strength = max(
        0.0,
        min(
            1.0,
            evidence_strength
        )
    )

    diagnostics = {
        "kmrl_matches": kmrl_matches,
        "kmrl_strength": kmrl_strength,
        "predicted_category_matches": (
            predicted_matches
        ),
        "predicted_category_strength": (
            predicted_category_strength
        ),
        "strongest_kmrl_score": (
            strongest_kmrl_score
        ),
        "raw_scores": raw_scores,
        "probabilities": probabilities,
        "evidence_strength": evidence_strength,
        "category_diagnostics": (
            category_diagnostics
        ),
    }

    return (
        probabilities,
        evidence_strength,
        diagnostics
    )


# ============================================================
# FINAL ADAPTIVE CONFIDENCE
# ============================================================

def calculate_final_confidence(
    text,
    groq_result
):
    """
    Combine:

        1. Mathematical evidence probability
        2. Groq semantic confidence

    using an adaptive weight.

    Evidence weight:

        0.30 + (0.50 * evidence_strength)

    Therefore:

        evidence_strength = 0.0
            -> 30% evidence / 70% Groq

        evidence_strength = 0.5
            -> 55% evidence / 45% Groq

        evidence_strength = 1.0
            -> 80% evidence / 20% Groq
    """

    predicted_category = (
        groq_result["category"]
    )

    groq_confidence = max(
        0.0,
        min(
            1.0,
            float(
                groq_result.get(
                    "confidence_hint",
                    0.5
                )
            )
        )
    )

    (
        evidence_probabilities,
        evidence_strength,
        diagnostics,
    ) = calculate_evidence_probabilities(
        text,
        predicted_category
    )

    evidence_confidence = (
        evidence_probabilities.get(
            predicted_category,
            0.0
        )
    )

    # --------------------------------------------------------
    # Adaptive weighting.
    # --------------------------------------------------------

    evidence_weight = (
        0.30
        + (
            0.50
            * evidence_strength
        )
    )

    groq_weight = (
        1.0
        - evidence_weight
    )

    # --------------------------------------------------------
    # Final weighted confidence.
    # --------------------------------------------------------

    final_confidence = (
        evidence_weight
        * evidence_confidence
        +
        groq_weight
        * groq_confidence
    )

    final_confidence = max(
        0.0,
        min(
            1.0,
            final_confidence
        )
    )

    # --------------------------------------------------------
    # Logging for debugging.
    # --------------------------------------------------------

    print(
        "\n========== CONFIDENCE ANALYSIS =========="
    )

    print(
        f"Predicted category: "
        f"{predicted_category}"
    )

    print(
        f"Groq confidence: "
        f"{groq_confidence:.4f}"
    )

    print(
        f"Evidence confidence: "
        f"{evidence_confidence:.4f}"
    )

    print(
        f"Evidence strength: "
        f"{evidence_strength:.4f}"
    )

    print(
        f"Evidence weight: "
        f"{evidence_weight:.4f}"
    )

    print(
        f"Groq weight: "
        f"{groq_weight:.4f}"
    )

    print(
        f"Final confidence: "
        f"{final_confidence:.4f}"
    )

    print(
        "==========================================\n"
    )

    return final_confidence


# ============================================================
# COMPLETE DOCUMENT ANALYSIS
# ============================================================

def analyze_document(text):
    """
    Complete AI analysis pipeline.

    1. Groq performs semantic classification.
    2. Deterministic evidence is calculated from OCR text.
    3. Evidence probabilities are normalized using softmax.
    4. Evidence strength determines the adaptive weights.
    5. Evidence confidence and Groq confidence are combined.
    """

    groq_result = analyze_with_groq(
        text
    )

    final_confidence = (
        calculate_final_confidence(
            text,
            groq_result
        )
    )

    return {
        "category": groq_result["category"],

        "summary": groq_result["summary"],

        "action_items": (
            groq_result["action_items"]
        ),

        "deadline": (
            groq_result["deadline"]
        ),

        "confidence": final_confidence,
    }


# ============================================================
# BACKWARD-COMPATIBLE PDF PROCESSING
# ============================================================

def process_pdf(pdf_path):
    """
    Existing compatibility function.

    This allows the rest of the project to continue calling
    process_pdf() if needed.
    """

    print(
        f"Processing: {pdf_path}"
    )

    pages = get_page_count(
        pdf_path
    )

    print(
        f"Pages: {pages}"
    )

    text = extract_text_from_pdf(
        pdf_path
    )

    print(
        f"Extracted text length: "
        f"{len(text)}"
    )

    analysis = analyze_document(
        text
    )

    return {
        "category": analysis["category"],

        "summary": analysis["summary"],

        "action_items": (
            analysis["action_items"]
        ),

        "deadline": (
            analysis["deadline"]
        ),

        "pages": pages,

        "confidence": (
            analysis["confidence"]
        ),
    }