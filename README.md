# KMRL Document Intelligence System

A document classifier and summarizer for Kochi Metro Rail Limited (KMRL) documents. Uses OCR and AI (via Groq API) to extract text, classify documents, generate summaries, and identify action items and deadlines.

## Features

- PDF, PNG, JPG, JPEG, DOCX support
- OCR for scanned documents using Tesseract
- AI-powered classification into predefined categories
- Summary generation
- Action items and deadline extraction
- Confidence scoring
- Document storage and search
- Bug tracking for low-confidence or problematic extractions

## Architecture

- **Backend**: FastAPI (Python) with Groq API for AI processing
- **Frontend**: Next.js (React) for user interface
- **Database**: SQLite (via `database.py`)
- **OCR**: Tesseract with pdf2image and PyPDF2

## Prerequisites

### Backend
- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and accessible in PATH
- Poppler (for pdf2image) installed and accessible in PATH
- Groq API key (free tier available at [Groq.com](https://groq.com))

### Frontend
- Node.js 18+
- npm or yarn or pnpm or bun

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd KMRL-project
```

### 2. Backend Setup
```bash
cd backend
```

#### Install Python dependencies
```bash
pip install -r requirements.txt
```

#### Environment variables
Copy the example environment file and add your Groq API key:
```bash
cp .env.example .env
# Edit .env and replace 'your_groq_api_key_here' with your actual Groq API key
```

> **Note**: The `.env` file is already in `.gitignore` and will not be committed.

#### Install system dependencies for OCR
- **Tesseract OCR**: 
  - Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) or use Chocolatey: `choco install tesseract`
  - macOS: `brew install tesseract`
  - Linux (Ubuntu/Debian): `sudo apt-get install tesseract-ocr`
- **Poppler** (for pdf2image):
  - Windows: Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and add `bin` directory to PATH
  - macOS: `brew install poppler`
  - Linux (Ubuntu/Debian): `sudo apt-get install poppler-utils`

#### Start the backend server
```bash
uvicorn main:app --reload
```
The backend will run at `http://localhost:8000`

### 3. Frontend Setup
```bash
cd ../frontend
```

#### Install Node.js dependencies
```bash
npm install
# or yarn, pnpm, bun
```

#### Start the development server
```bash
npm run dev
# or yarn dev, pnpm dev, bun dev
```
The frontend will run at `http://localhost:3000`

### 4. Using the Application
1. Open your browser to `http://localhost:3000`
2. Upload a document (PDF, image, or DOCX) using the upload interface
3. Wait for processing (OCR + AI analysis)
4. View the results: category, summary, action items, deadline, and confidence
5. Use the search functionality to find previously processed documents

## Project Structure
```
KMRL-project/
├── backend/                 # FastAPI backend
│   ├── main.py              # API endpoints
│   ├── process.py           # OCR, text extraction, AI analysis
│   ├── database.py          # SQLite operations
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Template for environment variables
│   └── uploads/             # Uploaded documents (ignored by git)
├── frontend/                # Next.js frontend
│   ├── app/                 # App router
│   ├── components/          # React components
│   ├── services/            # API service functions
│   ├── package.json         # Node.js dependencies
│   └── ...                  # Other Next.js files
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## API Endpoints (Backend)
- `GET /` - Health check
- `POST /upload` - Upload and process a document
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get a specific document
- `GET /documents/{id}/download` - Download the original file
- `GET /search?q=<query>` - Search documents by text
- `GET /bugs` - View bug log (low confidence/OCR failures)
- `DELETE /documents/{id}` - Delete a document

## Troubleshooting
- **OCR not working**: Ensure Tesseract is installed and in your PATH. Test by running `tesseract --version` in terminal.
- **pdf2image errors**: Ensure Poppler is installed and its `bin` directory is in PATH.
- **Groq API errors**: Verify your API key is correct and you have available credits.
- **Module not found errors**: Ensure you installed dependencies in the correct virtual environment (backend) and ran `npm install` (frontend).

## Deployment Notes
This project is designed for local development and testing. For production deployment:
- Consider using a more robust database (PostgreSQL, MySQL)
- Set up proper environment variable management (AWS Secrets Manager, etc.)
- Use a production ASGI server (Gunicorn with Uvicorn workers)
- Enable HTTPS and proper CORS restrictions
- Consider rate limiting and API key protection

## License
This project is for educational and internal use. Please refer to any relevant data usage policies.

## Acknowledgments
- Built with FastAPI, Next.js, Tesseract, and Groq
- Special thanks to the Kochi Metro Rail Limited for inspiring this tool