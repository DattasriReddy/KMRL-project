# KMRL Document Intelligence System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-%3E%3D18-green.svg)](https://nodejs.org/)

A document classifier and summarizer for Kochi Metro Rail Limited (KMRL) documents. Uses OCR and AI (via Groq API) to extract text, classify documents, generate summaries, and identify action items and deadlines.

## ✨ Features

- **Multi-format Support**: PDF, PNG, JPG, JPEG, DOCX
- **Advanced OCR**: Tesseract with pdf2image and PyPDF2 fallback
- **AI-Powered Classification**: Groq API for accurate document categorization
- **Smart Summarization**: Concise, informative summaries
- **Action Item Extraction**: Identifies required tasks and responsibilities
- **Deadline Detection**: Finds explicit dates and due dates
- **Confidence Scoring**: Quantifies certainty in results (0-100%)
- **Document Storage**: SQLite database with search capabilities
- **Bug Tracking**: Logs low-confidence or problematic extractions
- **Responsive UI**: Modern Next.js interface
- **RESTful API**: Well-documented FastAPI backend

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Testing)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KMRL-project
   ```

2. **Backend Setup**
   ```bash
   cd backend
   ```

   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```

   - Set up environment variables:
     ```bash
     cp .env.example .env
     # Edit .env and add your Groq API key
     ```

   - Install system dependencies for OCR:
     - **Tesseract OCR**: 
       - Windows: [UB Mannheim builds](https://github.com/UB-Mannheim/tesseract/wiki) or `choco install tesseract`
       - macOS: `brew install tesseract`
       - Linux (Ubuntu/Debian): `sudo apt-get install tesseract-orc`
     - **Poppler** (for pdf2image):
       - Windows: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and add `bin` directory to PATH
       - macOS: `brew install poppler`
       - Linux (Ubuntu/Debian): `sudo apt-get install poppler-utils`

   - Start the backend server:
     ```bash
     uvicorn main:app --reload
     # Backend runs at http://localhost:8000
     ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   ```

   - Install Node.js dependencies:
     ```bash
     npm install
     # or yarn, pnpm, bun
     ```

   - Set up environment variables:
     ```bash
     cp .env.example .env.local
     # Defaults to http://localhost:8000 for local development
     ```

   - Start the development server:
     ```bash
     npm run dev
     # Frontend runs at http://localhost:3000
     ```

4. **Use the Application**
   - Open your browser to `http://localhost:3000`
   - Upload a document using the upload interface
   - View results: category, summary, action items, deadline, and confidence

### Option 2: Docker Deployment (Production Ready)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd KMRL-project
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   # Backend
   GROQ_API_KEY=your_groq_api_key_here
   
   # Frontend (for Docker build)
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

3. **Build and Run**
   ```bash
   # Build containers
   docker-compose build
   
   # Start services
   docker-compose up -d
   
   # Access the application
   # Frontend: http://localhost:3000
   # Backend API: http://localhost:8000
   ```

### Option 3: Deploy to Render.com

1. **Fork the repository** on GitHub

2. **Create Backend Service**
   - New → Web Service
   - Connect your forked repository
   - Set:
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       - `GROQ_API_KEY`: Your Groq API key
       - `PORT`: 10000 (or leave blank for auto)

3. **Create Frontend Service**
   - New → Web Service
   - Connect your forked repository
   - Set:
     - **Environment**: Node.js
     - **Build Command**: `npm install && npm run build`
     - **Start Command**: `npm start`
     - **Environment Variables**:
       - `NEXT_PUBLIC_API_BASE_URL`: https://your-backend-service.onrender.com

4. **Link Services**
   - Wait for backend to deploy and note its URL
   - Update frontend's `NEXT_PUBLIC_API_BASE_URL` to match backend URL
   - Redeploy frontend

## 🧪 Testing the System

### Generating Test Documents
The backend includes scripts to generate sample documents for testing:

```bash
# Generate sample PNG image (great for OCR testing)
cd backend
python make_sample.py

# Generate 5 varied sample PDFs (different categories, complexities)
python generate_sample_pdfs.py

# Generate a large 63-page test document for stress testing
python sample_KMRL.py
```

These create various test files in the `backend/` directory:
- `sample_image.png` - Simple PNG with text
- `maintenance_log.pdf`, `tender_document.pdf`, etc. - Varied PDF samples
- `kmrl_large_test_document.pdf` - 63-page comprehensive test document

### Sample Documents to Try
1. **Clear text PDF**: Should yield high confidence (80-100%)
2. **Scanned document**: Medium confidence depending on OCR quality (40-70%)
3. **Ambiguous content**: Lower confidence as system struggles to categorize (0-50%)
4. **Image document (JPG/PNG)**: Varies based on text clarity
5. **Word document (DOCX)**: Usually good results if text is selectable

### What to Look For
- **Confidence Score**: Higher = more reliable results
- **Category**: Does it match the document type?
- **Summary**: Does it capture the main points?
- **Action Items**: Are required tasks identified?
- **Deadlines**: Are dates correctly extracted?

## 🔧 Environment Variables

### Backend (`backend/.env`)
```
GROQ_API_KEY=your_groq_api_key_here
```

### Frontend (`.env.local` or platform-specific)
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # For local development
# For production: https://your-backend-domain.com
```

## 📦 Project Structure

```
KMRL-project/
├── backend/                 # FastAPI backend
│   ├── main.py              # API endpoints
│   ├── process.py           # OCR, text extraction, AI analysis
│   ├── database.py          # SQLite operations
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Template for environment variables
│   ├── make_sample.py       # Generate sample PNG for testing
│   ├── generate_sample_pdfs.py  # Generate 5 sample PDFs
│   ├── sample_KMRL.py       # Generate 63-page test document
│   ├── sample_image.png     # Pre-generated sample PNG
│   ├── sample.docx          # Pre-generated sample DOCX
│   └── uploads/             # Uploaded documents (auto-created)
├── frontend/                # Next.js frontend
│   ├── app/                 # App router
│   ├── components/          # React components
│   ├── services/            # API service functions
│   ├── package.json         # Node.js dependencies
│   ├── .env.example         # Template for environment variables
│   └── ...                  # Other Next.js files
├── docker-compose.yml       # Docker deployment (optional)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔌 API Endpoints

All endpoints are available at `{BASE_URL}` (e.g., `http://localhost:8000`)

- `GET /` - Health check
- `POST /upload` - Upload and process a document
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get a specific document
- `GET /documents/{id}/download` - Download the original file
- `GET /search?q=<query>` - Search documents by text
- `GET /bugs` - View bug log (low confidence/OCR failures)
- `DELETE /documents/{id}` - Delete a document

## 🛠️ Troubleshooting

### Common Issues

#### "Connection refused" or "Cannot connect to backend"
- **Cause**: Frontend cannot reach backend API
- **Solutions**:
  - Verify backend is running (`uvicorn main:app --reload`)
  - Check `NEXT_PUBLIC_API_BASE_URL` in frontend environment
  - Ensure ports match and aren't blocked by firewall
  - For Docker: verify service networking

#### "Module not found" errors
- **Cause**: Missing Python or Node.js dependencies
- **Solutions**:
  - Backend: `pip install -r requirements.txt`
  - Frontend: `npm install`
  - Use correct virtual environments

#### OCR not working
- **Cause**: Tesseract/Poppler not installed or not in PATH
- **Solutions**:
  - Verify installation: `tesseract --version`
  - Check PATH includes installation directories
  - Restart terminal after installation

#### Groq API errors
- **Cause**: Invalid/missing API key or quota exceeded
- **Solutions**:
  - Check `GROQ_API_KEY` in backend `.env`
  - Verify API key is correct at [Groq.com](https://groq.com)
  - Check usage and quota limits

#### Low confidence scores consistently
- **Cause**: Poor document quality or ambiguous content
- **Solutions**:
  - Try clearer, text-based PDFs
  - Ensure scans are high quality (300+ DPI)
  - Verify document content matches predefined categories
  - Check system logs for processing details

### Viewing Logs
- **Backend**: Console output shows processing steps
- **Frontend**: Browser DevTools (F12) → Console tab
- **Bugs**: Check `/bugs` endpoint or `backend/bugs.csv`

## 🐳 Docker Deployment

The project includes Docker support for easy production deployment:

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./backend/uploads:/app/uploads
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

To use:
```bash
docker-compose up --build
```

## 📝 Deployment Notes

### For Production Environments
1. **Use managed secrets** for API keys (AWS Secrets Manager, Vault, etc.)
2. **Enable HTTPS** in production (terminate at load balancer or reverse proxy)
3. **Consider a more robust database** (PostgreSQL, MySQL) for heavy usage
4. **Add rate limiting** to prevent API abuse
5. **Implement authentication** if needed for your use case
6. **Monitor logs** and set up alerts for failures

### Backend-Specific Notes
- The `uploads/` directory is mounted as a volume to persist files
- SQLite is used for simplicity; migrate to PostgreSQL/MySQL for scale
- Workers: Consider Gunicorn with Uvicorn workers for production
- CORS: Currently allows all origins; restrict in production

### Frontend-Specific Notes
- Build outputs are optimized for production
- Environment variables are baked in at build time
- Consider CDN deployment for static assets
- Implement authentication wrapper if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [Next.js](https://nextjs.org/), [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), and [Groq](https://groq.com)
- Special thanks to the Kochi Metro Rail Limited for inspiring this tool
- Thanks to all open-source projects that make this possible

## 📞 Support

For questions, issues, or feedback:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing [GitHub Issues](https://github.com/your-username/kmrl-project/issues)
3. Open a new issue with detailed reproduction steps