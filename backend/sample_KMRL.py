from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import date, timedelta
import random

OUTPUT_FILE = "kmrl_large_test_document.pdf"
TOTAL_PAGES = 63

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=18,
    spaceAfter=20
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=13,
    spaceBefore=10,
    spaceAfter=8
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
    spaceAfter=7
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11
)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, 20, "Kochi Metro Rail Limited - Internal Test Document")
    canvas.drawRightString(555, 20, f"Page {doc.page}")
    canvas.restoreState()

def make_action_items(page_number):
    base_date = date(2026, 9, 1)
    deadline1 = base_date + timedelta(days=page_number % 20)
    deadline2 = base_date + timedelta(days=20 + (page_number % 15))

    return [
        (
            f"Maintenance team shall inspect the equipment identified "
            f"in Section {page_number} and complete the required corrective work "
            f"by {deadline1.strftime('%Y-%m-%d')}."
        ),
        (
            f"The responsible department must submit the inspection and "
            f"completion report to the Operations Control Centre by "
            f"{deadline2.strftime('%Y-%m-%d')}."
        ),
        (
            f"Safety personnel shall review the identified risks and provide "
            f"mitigation recommendations before {deadline1.strftime('%Y-%m-%d')}."
        )
    ]

sections = [
    "Executive Summary",
    "Operations Review",
    "Station Maintenance",
    "Track and Civil Infrastructure",
    "Electrical Systems",
    "Rolling Stock Maintenance",
    "Signalling and Telecommunications",
    "Passenger Safety",
    "Emergency Preparedness",
    "Incident Review",
    "Inspection Findings",
    "Preventive Maintenance",
    "Corrective Maintenance",
    "Asset Management",
    "Procurement Activities",
    "Tender and Contract Monitoring",
    "Financial Review",
    "Human Resources",
    "Training and Competency",
    "Safety Compliance",
    "Environmental Management",
    "Quality Assurance",
    "Security Operations",
    "Cleaning and Housekeeping",
    "Escalator and Elevator Maintenance",
    "Fire and Life Safety",
    "Power Supply Systems",
    "Depot Operations",
    "Control Room Operations",
    "Passenger Information Systems",
    "Communication Systems",
    "CCTV and Surveillance",
    "Access Control",
    "Energy Management",
    "Water and Drainage Systems",
    "Structural Inspection",
    "Roof and Building Maintenance",
    "Work Permit Management",
    "Contractor Safety",
    "Material Management",
    "Spare Parts Inventory",
    "Technical Audit",
    "Internal Audit Findings",
    "Risk Assessment",
    "Business Continuity",
    "Disaster Management",
    "Service Reliability",
    "Performance Monitoring",
    "Monthly KPI Review",
    "Customer Service",
    "Passenger Feedback",
    "Accessibility Review",
    "Staff Welfare",
    "Medical and First Aid Facilities",
    "Cybersecurity Controls",
    "Information Technology Systems",
    "Document Management",
    "Records Management",
    "Compliance Review",
    "Management Action Plan",
    "Final Recommendations"
]

doc = SimpleDocTemplate(
    OUTPUT_FILE,
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=45,
    bottomMargin=35
)

story = []

for page_number in range(1, TOTAL_PAGES + 1):
    section = sections[(page_number - 1) % len(sections)]

    story.append(
        Paragraph(
            "KOCHI METRO RAIL LIMITED",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"Technical Operations and Maintenance Review",
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"Section {page_number}: {section}",
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"Document Reference: KMRL/TECH/2026/{page_number:03d}",
            body_style
        )
    )

    story.append(
        Paragraph(
            f"Reporting Period: August 2026 | Review Page: {page_number}",
            body_style
        )
    )

    story.append(Spacer(1, 8))

    paragraphs = [
        f"This section presents the findings associated with {section.lower()} "
        f"across the Kochi Metro Rail Limited operational environment. "
        f"The review considers current operational conditions, maintenance "
        f"requirements, safety controls, inspection observations, and pending "
        f"departmental responsibilities.",

        "The technical team reviewed available records, maintenance logs, "
        "inspection observations, operational information, and supporting "
        "documentation. Any identified issue must be evaluated by the "
        "responsible department before corrective action is closed.",

        "Operational continuity remains a priority. Departments are required "
        "to coordinate planned maintenance activities with station operations "
        "and ensure that safety requirements are satisfied before work begins.",

        "Where equipment defects or infrastructure concerns are identified, "
        "the responsible technical team shall record the issue, assess the "
        "severity, assign responsibility, and complete corrective action "
        "within the specified timeframe.",

        "Supervisors shall verify completed work and maintain appropriate "
        "supporting records. Completion evidence should include inspection "
        "results, photographs where applicable, maintenance records, and "
        "approval from the designated authority."
    ]

    for paragraph in paragraphs:
        story.append(
            Paragraph(
                paragraph,
                body_style
            )
        )

    story.append(
        Paragraph(
            "Key Findings",
            heading_style
        )
    )

    findings = [
        ["Finding", "Status", "Responsible Department"],
        [
            "Routine inspection completed",
            "Completed",
            "Engineering"
        ],
        [
            "Preventive maintenance requirement",
            "Open",
            "Maintenance"
        ],
        [
            "Safety verification",
            "Pending",
            "Safety Department"
        ],
        [
            "Documentation update",
            "Open",
            "Operations"
        ]
    ]

    table = Table(
        findings,
        colWidths=[220, 100, 140]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
        ])
    )

    story.append(table)
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Required Action Items",
            heading_style
        )
    )

    actions = make_action_items(page_number)

    for index, action in enumerate(actions, start=1):
        story.append(
            Paragraph(
                f"{index}. {action}",
                body_style
            )
        )

    story.append(
        Paragraph(
            "Deadline Information",
            heading_style
        )
    )

    deadline = date(2026, 9, 1) + timedelta(days=page_number % 20)

    story.append(
        Paragraph(
            f"The primary completion deadline for this section is "
            f"{deadline.strftime('%Y-%m-%d')}. All responsible personnel "
            f"shall ensure that the required action is completed and "
            f"documented before the stated deadline.",
            body_style
        )
    )

    story.append(
        Paragraph(
            "Management Note",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Outstanding actions shall remain under departmental monitoring "
            "until satisfactory completion evidence has been submitted. "
            "Any delay affecting safety, operations, passenger service, or "
            "asset availability must be escalated to the appropriate "
            "management authority.",
            body_style
        )
    )

    if page_number < TOTAL_PAGES:
        story.append(PageBreak())

doc.build(
    story,
    onFirstPage=footer,
    onLaterPages=footer
)

print(f"Created: {OUTPUT_FILE}")
print(f"Pages: {TOTAL_PAGES}")