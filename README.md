# VedAI Backend

Production-ready FastAPI backend for the VedAI student learning platform.

## Features

### ✅ Completed Features

1. **Authentication & Authorization**
   - JWT-based authentication
   - Secure password hashing with bcrypt
   - HTTP Bearer token authentication
   - User registration and login

2. **Student Profile Management**
   - Create, read, update, delete student profiles
   - Support for class, subjects, board, medium
   - User-student relationship management

3. **Content Management**
   - PDF upload and ingestion
   - Intelligent text chunking
   - Vector embeddings (pgvector)
   - Full-text search

4. **Question Bank**
   - MCQ, short answer, long answer, numerical questions
   - Flexible metadata (subject, chapter, difficulty, board)
   - Question-option relationships

5. **Progress Tracking**
   - Chapter-level progress tracking
   - Completion percentage and time tracking
   - Subject-wise aggregated statistics
   - Progress overview with analytics

6. **Mock Tests & Assessments**
   - Create and manage tests
   - Test attempts with auto-save
   - Automatic scoring for MCQ questions
   - Attempt history and performance stats
   - Draft answer recovery

7. **AI-Powered Chat (RAG)**
   - Question answering using Gemini AI
   - Retrieval-Augmented Generation
   - Source citations and metadata
   - Filtered by class, subject, chapter

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL with pgvector extension
- **ORM:** SQLModel (SQLAlchemy 2.0)
- **Authentication:** python-jose, passlib
- **AI/ML:** 
  - LangChain for RAG pipeline
  - Google Gemini for LLM
  - Sentence Transformers for embeddings
- **PDF Processing:** pdfplumber, pypdf
- **Async Support:** asyncpg, aiosqlite

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 15+ with pgvector extension
- (Optional) Docker for containerized database

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/kundanlcb/vedai-be.git
cd vedai-be
```

2. **Install dependencies**
```bash
# Using pip
pip install -r requirements.txt

# Or using pipenv
pipenv install
```

3. **Environment configuration**
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://admin:admin123@localhost:5432/vedai

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
GOOGLE_API_KEY=your-google-api-key
GEMINI_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2

# App Settings
APP_NAME=vedai
```

4. **Start PostgreSQL with pgvector**
```bash
docker-compose up -d
```

5. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Full API Documentation
See [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for comprehensive endpoint documentation.

## Testing

Run the comprehensive test suite:

```bash
python test_apis.py
```

This tests:
- ✅ Authentication (JWT tokens)
- ✅ Student profile CRUD
- ✅ Progress tracking
- ✅ Mock test creation and attempts
- ✅ Automatic scoring

## Database Schema

### Core Tables

1. **user** - User accounts (email, password)
2. **student** - Student profiles (name, class, subjects)
3. **content_chunk** - PDF content with embeddings
4. **question** - Questions with metadata
5. **question_option** - MCQ options
6. **progress_entry** - Chapter progress tracking
7. **mock_test** - Test configurations
8. **mock_test_attempt** - Student test attempts
9. **pdffile** - PDF ingestion tracking

## Project Structure

```
vedai-be/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── settings.py             # Configuration
│   ├── db.py                   # Database connection
│   ├── logger.py               # Logging setup
│   ├── models/                 # SQLModel models
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── content.py
│   │   ├── question.py
│   │   ├── progress.py
│   │   └── mock_test.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── progress.py
│   │   ├── mock_test.py
│   │   ├── question.py
│   │   ├── content.py
│   │   └── chat.py
│   ├── crud/                   # Database operations
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── progress.py
│   │   ├── mock_test.py
│   │   ├── question.py
│   │   └── content.py
│   ├── routes/                 # API endpoints
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── progress.py
│   │   ├── tests.py
│   │   ├── question.py
│   │   ├── content.py
│   │   ├── ingest.py
│   │   └── chat.py
│   ├── services/               # Business logic
│   │   ├── chat.py
│   │   ├── rag.py
│   │   ├── retrieval.py
│   │   ├── llm.py
│   │   └── ingest_service.py
│   └── utils/                  # Utilities
│       ├── auth.py
│       ├── security.py
│       └── chunker.py
├── docs/                       # Documentation
│   ├── API_DOCUMENTATION.md
│   └── RAG_Chat_Module_Requirements.md
├── test_apis.py               # Comprehensive tests
├── docker-compose.yml         # PostgreSQL setup
├── Pipfile                    # Dependencies
└── README.md                  # This file
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions
- Keep functions focused and small

### Git Workflow
1. Create feature branch from `main`
2. Make changes and test
3. Submit pull request
4. Code review and merge

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in environment
- [ ] Use production database URL
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Use production-grade ASGI server (Gunicorn + Uvicorn)

### Docker Deployment

```bash
# Build image
docker build -t vedai-backend .

# Run container
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  -e SECRET_KEY=... \
  -e GOOGLE_API_KEY=... \
  vedai-backend
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For issues and questions, please contact the development team.

## Acknowledgments

- FastAPI for the excellent web framework
- LangChain for RAG capabilities
- Google Gemini for AI functionality
- SQLModel for the elegant ORM
