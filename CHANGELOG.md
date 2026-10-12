# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Initial release of KMRL Document Intelligence System
- Document classification using Groq AI
- OCR capabilities with Tesseract
- Multi-format support (PDF, PNG, JPG, JPEG, DOCX)
- Summary generation
- Action item and deadline extraction
- Confidence scoring
- RESTful API backend (FastAPI)
- Next.js frontend with responsive UI
- Docker deployment support
- Environment variable configuration for flexible deployment
- Sample document generation scripts for testing
- Comprehensive documentation
- Bug tracking system
- Search functionality
- Document storage with SQLite

### Fixed
- Removed hardcoded localhost references to enable deployment on any server
- Made frontend configurable via NEXT_PUBLIC_API_BASE_URL environment variable
- Ensured backend binds to 0.0.0.0 for external access in Docker/production

## [0.1.0] - 2026-10-12
### Added
- Initial project setup
- Core document processing pipeline
- Basic UI for document upload and results display
- API endpoints for document management