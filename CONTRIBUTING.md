# Contributing to KMRL Document Intelligence System

Thank you for your interest in contributing to the KMRL Document Intelligence System! We welcome contributions from the community.

## How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/your-username/kmrl-project/issues) page
- Please include:
  - Clear description of the issue
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - Environment details (OS, browser, etc.)

### Suggesting Features
- Use the [GitHub Issues](https://github.com/your-username/kmrl-project/issues) page
- Label your issue as "enhancement"
- Describe the feature and its benefits
- Include any relevant use cases or examples

### Submitting Changes
1. Fork the repository
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature-or-fix-name
   ```
3. Make your changes
4. Ensure your code follows the existing style:
   - Python: PEP 8 compliance
   - JavaScript/React: Standard Next.js/React conventions
   - Include appropriate comments
5. Test your changes thoroughly
6. Commit your changes:
   ```bash
   git commit -m "Descriptive commit message"
   ```
7. Push to your branch:
   ```bash
   git push origin feature-or-fix-name
   ```
8. Open a Pull Request against the `main` branch

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git
- Tesseract OCR installed and in PATH
- Poppler installed and in PATH (for pdf2image)

### Backend Development
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Code Style

### Python
- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Include docstrings for public functions
- Keep functions focused and readable

### JavaScript/React
- Follow Next.js and React best practices
- Use functional components with hooks
- Keep components small and focused
- Use TypeScript where beneficial (though current codebase uses JavaScript)
- Follow existing code patterns in the project

## Documentation
- Update README.md if your changes affect usage or setup
- Add inline comments for complex logic
- Update API documentation if endpoints change

## Testing
- Test your changes with various document types
- Verify both backend API and frontend UI work correctly
- Check edge cases and error conditions
- Ensure confidence scoring behaves as expected

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to KMRL Document Intelligence System!