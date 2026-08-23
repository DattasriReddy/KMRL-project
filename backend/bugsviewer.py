from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from html import escape

import csv
import os


app = FastAPI(
    title="KMRL Bug Viewer"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BUG_FILE = os.path.join(
    BASE_DIR,
    "bugs.csv",
)


@app.get("/")
def home():
    return {
        "message": "KMRL Bug Viewer is running",
        "endpoint": "/bugs",
        "html_endpoint": "/bugs/html",
    }


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
        reader = csv.DictReader(file)
        bugs = list(reader)

    return {
        "total_bugs": len(bugs),
        "bugs": bugs,
    }


@app.get(
    "/bugs/html",
    response_class=HTMLResponse,
)
def view_bugs_html():
    if not os.path.isfile(BUG_FILE):
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>KMRL Bug Viewer</h1>
            <p>No bugs found.</p>
        </body>
        </html>
        """

    with open(
        BUG_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        bugs = list(reader)

    if not bugs:
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>KMRL Bug Viewer</h1>
            <p>No bugs found.</p>
        </body>
        </html>
        """

    headers = list(
        bugs[0].keys()
    )

    header_html = "".join(
        f"<th>{escape(str(header))}</th>"
        for header in headers
    )

    rows_html = ""

    for bug in bugs:
        rows_html += "<tr>"

        for header in headers:
            value = bug.get(
                header,
                "",
            )

            rows_html += (
                f"<td>{escape(str(value))}</td>"
            )

        rows_html += "</tr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>KMRL Bug Viewer</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f5f5f5;
            }}

            h1 {{
                margin-bottom: 20px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                vertical-align: top;
            }}

            th {{
                background: #333;
                color: white;
            }}

            tr:nth-child(even) {{
                background: #f2f2f2;
            }}
        </style>
    </head>

    <body>
        <h1>KMRL Bug Viewer</h1>

        <p>
            Total bugs/warnings: {len(bugs)}
        </p>

        <table>
            <thead>
                <tr>
                    {header_html}
                </tr>
            </thead>

            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """


# Run:
# uvicorn bugs_viewer:app --port 8001 --reload
