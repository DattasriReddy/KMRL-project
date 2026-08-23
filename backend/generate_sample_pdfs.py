from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from datetime import datetime

def create_pdf(filename, title, content, category, action_items=None, deadline=None):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30

    # Category
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Category: {category}")
    y -= 20

    # Date
    c.drawString(50, y, f"Date: {datetime.now().strftime('%d-%m-%Y')}")
    y -= 20

    # Content (wrap text)
    c.setFont("Helvetica", 11)
    lines = simpleSplit(content, "Helvetica", 11, width - 100)
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 15

    # Action Items
    if action_items:
        y -= 15
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Action Items:")
        y -= 20
        c.setFont("Helvetica", 11)
        for item in action_items:
            c.drawString(60, y, f"• {item}")
            y -= 15

    # Deadline
    if deadline:
        y -= 15
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Deadline: {deadline}")
        y -= 20

    c.save()
    print(f"✅ Created: {filename}")

# --- Generate 5 sample PDFs ---

# 1. Maintenance Log
create_pdf(
    "maintenance_log.pdf",
    "KMRL Maintenance Log – Track Repair",
    "This document records the routine maintenance of the Aluva-Palarivattom track section. The inspection found minor wear on the rails and loose ballast near the curve. Repairs were carried out on 12-Aug-2026. The work order was completed on time.",
    "Maintenance Log / Work Order",
    action_items=["Replace 15 damaged sleepers", "Re-ballast the curve section", "Inspect track geometry"],
    deadline="2026-09-15"
)

# 2. Tender Document
create_pdf(
    "tender_document.pdf",
    "KMRL Tender – Construction of Elevated Station",
    "Kochi Metro Rail Limited invites sealed bids for the construction of a new elevated station at Kakkanad. The scope includes civil works, platform shelters, and passenger amenities. The estimated project cost is INR 45 crore. Bid documents must be submitted by the deadline.",
    "Tender / Bid Document",
    action_items=["Submit bid proposal", "Arrange technical presentation", "Coordinate with legal team"],
    deadline="2026-09-30"
)

# 3. Inspection Report
create_pdf(
    "inspection_report.pdf",
    "KMRL Safety Inspection Report – Corridor 2",
    "The safety inspection of Corridor 2 (Edappally – Tripunithura) was conducted on 17-Aug-2026. All signaling systems are operational. However, the level crossing at Maradu needs immediate attention due to worn-out gates. No critical anomalies were detected. The team recommends a follow-up inspection next month.",
    "Inspection Report (safety, quality, or routine)",
    action_items=["Replace level crossing gates at Maradu", "Schedule follow-up inspection for September"],
    deadline="2026-09-10"
)

# 4. Incident Report
create_pdf(
    "incident_report.pdf",
    "KMRL Incident Report – Minor Accident at Palarivattom",
    "On 14-Aug-2026, a minor accident occurred at Palarivattom station when a passenger slipped on the wet platform. The passenger suffered minor injuries and was provided first aid. The platform floor has been cleaned and caution signs placed. A review of the cleaning schedule is underway.",
    "Incident Report (accident, near-miss)",
    action_items=["Review cleaning schedule", "Install anti-slip mats", "Train staff on emergency response"],
    deadline="2026-08-30"
)

# 5. HR Policy
create_pdf(
    "hr_policy.pdf",
    "KMRL HR Policy – Leave and Attendance",
    "This document outlines the updated leave policy for KMRL employees. Employees are entitled to 21 casual leaves, 15 sick leaves, and 10 earned leaves per year. All leaves must be applied through the portal. The policy is effective from 1-Sep-2026.",
    "HR / Personnel Record",
    action_items=["Update HR portal", "Notify all employees via email"],
    deadline="2026-08-25"
)

print("\n🎉 All 5 sample PDFs created successfully in your backend folder!")
print("You can now upload them via Swagger to test your backend.")