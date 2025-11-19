# VedAI Backend API Documentation

## Overview
This document describes all production-ready API endpoints for the VedAI student learning platform. The backend is built with FastAPI and provides comprehensive support for authentication, content management, progress tracking, assessments, and AI-powered chat assistance.

## Base URL
```
Development: http://localhost:8000
Production: https://api.vedai.com (update as needed)
```

## Authentication
All protected endpoints require a JWT Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## API Endpoints

### Authentication

#### POST `/api/auth/register`
Register a new student account.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123",
  "name": "John Doe",
  "class_name": 10,
  "medium": "English",
  "subjects": "Math,Science,English",
  "board": "CBSE"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "user_id": 1,
  "student_id": 1
}
```

#### POST `/api/auth/login`
Authenticate and get access token.

**Request:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "user_id": 1,
  "student_id": 1
}
```

---

### Student Profile

#### GET `/api/students/{student_id}`
Get student profile by ID.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "John Doe",
  "class_name": 10,
  "medium": "English",
  "subjects": "Math,Science,English",
  "school_name": "ABC High School",
  "board": "CBSE",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### GET `/api/students/user/{user_id}`
Get student profile by user ID.

**Headers:** Requires authentication

**Response:** Same as above

#### PUT `/api/students/{student_id}`
Update student profile.

**Headers:** Requires authentication

**Request:**
```json
{
  "name": "John Smith",
  "class_name": 11,
  "school_name": "XYZ High School"
}
```

**Response (200):** Updated student object

#### DELETE `/api/students/{student_id}`
Delete student profile.

**Headers:** Requires authentication

**Response (204):** No content

---

### Progress Tracking

#### POST `/api/progress/`
Create or log progress entry.

**Headers:** Requires authentication

**Request:**
```json
{
  "student_id": 1,
  "subject": "Math",
  "chapter": "Algebra",
  "class_name": 10,
  "completion_percentage": 45,
  "time_spent_minutes": 90,
  "chunks_viewed": 12,
  "last_chunk_id": 156
}
```

**Response (201):**
```json
{
  "id": 1,
  "student_id": 1,
  "subject": "Math",
  "chapter": "Algebra",
  "class_name": 10,
  "completion_percentage": 45,
  "time_spent_minutes": 90,
  "chunks_viewed": 12,
  "is_completed": false,
  "last_chunk_id": 156,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### PUT `/api/progress/{progress_id}`
Update progress entry.

**Headers:** Requires authentication

**Request:**
```json
{
  "completion_percentage": 75,
  "time_spent_minutes": 45,
  "chunks_viewed": 8
}
```

**Response (200):** Updated progress object

#### GET `/api/progress/student/{student_id}`
Get all progress entries for a student.

**Headers:** Requires authentication

**Query Parameters:**
- `subject` (optional): Filter by subject
- `chapter` (optional): Filter by chapter

**Response (200):**
```json
[
  {
    "id": 1,
    "student_id": 1,
    "subject": "Math",
    "chapter": "Algebra",
    "completion_percentage": 75,
    ...
  },
  ...
]
```

#### GET `/api/progress/student/{student_id}/overview`
Get aggregated progress overview.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "student_id": 1,
  "subjects": [
    {
      "subject": "Math",
      "total_chapters": 5,
      "completed_chapters": 2,
      "avg_completion": 62.5,
      "total_time_minutes": 450
    },
    {
      "subject": "Science",
      "total_chapters": 4,
      "completed_chapters": 1,
      "avg_completion": 45.0,
      "total_time_minutes": 380
    }
  ],
  "total_time_minutes": 830,
  "overall_completion": 53.75
}
```

---

### Mock Tests

#### GET `/api/tests/`
List available mock tests.

**Headers:** Requires authentication

**Query Parameters:**
- `subject` (optional): Filter by subject
- `class` (optional): Filter by class/grade
- `is_published` (default: true): Show only published tests
- `limit` (default: 50, max: 100)
- `offset` (default: 0)

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Math - Algebra Test",
    "description": "Test your algebra skills",
    "subject": "Math",
    "chapter": "Algebra",
    "class_name": 10,
    "total_questions": 20,
    "total_marks": 40,
    "duration_minutes": 45,
    "passing_marks": 24,
    "question_ids": [1, 2, 3, ...],
    "is_published": true,
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-01-10T09:00:00Z"
  },
  ...
]
```

#### GET `/api/tests/{test_id}`
Get specific test details.

**Headers:** Requires authentication

**Response (200):** Single test object (same structure as above)

#### POST `/api/tests/{test_id}/start`
Start a new test attempt.

**Headers:** Requires authentication

**Request:**
```json
{
  "test_id": 1,
  "student_id": 1
}
```

**Response (201):**
```json
{
  "id": 1,
  "test_id": 1,
  "student_id": 1,
  "status": "in_progress",
  "start_time": "2025-01-15T14:30:00Z",
  "end_time": null,
  "answers": {},
  "questions_attempted": 0,
  "questions_correct": 0,
  "obtained_marks": 0,
  "percentage": 0.0,
  "created_at": "2025-01-15T14:30:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

#### GET `/api/tests/attempts/{attempt_id}`
Get attempt details.

**Headers:** Requires authentication

**Response (200):** Attempt object (same as above)

#### PATCH `/api/tests/attempts/{attempt_id}/draft`
Auto-save draft answers (for offline/crash recovery).

**Headers:** Requires authentication

**Request:**
```json
{
  "answers": {
    "1": 45,
    "2": "Free text answer",
    "3": 102
  }
}
```

**Response (200):** Updated attempt object

#### POST `/api/tests/attempts/{attempt_id}/submit`
Submit test with final answers.

**Headers:** Requires authentication

**Request:**
```json
{
  "attempt_id": 1,
  "answers": {
    "1": 45,
    "2": "Complete answer text",
    "3": 102,
    ...
  }
}
```

**Response (200):**
```json
{
  "id": 1,
  "test_id": 1,
  "student_id": 1,
  "status": "submitted",
  "start_time": "2025-01-15T14:30:00Z",
  "end_time": "2025-01-15T15:00:00Z",
  "answers": {...},
  "questions_attempted": 20,
  "questions_correct": 18,
  "obtained_marks": 36,
  "percentage": 90.0,
  "created_at": "2025-01-15T14:30:00Z",
  "updated_at": "2025-01-15T15:00:00Z"
}
```

#### GET `/api/tests/student/{student_id}/attempts`
Get attempt history.

**Headers:** Requires authentication

**Query Parameters:**
- `limit` (default: 50, max: 100)
- `offset` (default: 0)

**Response (200):** Array of attempt objects

#### GET `/api/tests/student/{student_id}/stats`
Get performance statistics.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "student_id": 1,
  "total_attempts": 15,
  "avg_percentage": 82.5,
  "total_time_minutes": 450,
  "subject_wise_stats": {}
}
```

---

### Questions

#### POST `/api/questions/`
Create a question (admin/teacher only).

**Headers:** Requires authentication

**Request:**
```json
{
  "text": "What is 2 + 2?",
  "question_type": "mcq",
  "marks": 2,
  "subject": "Math",
  "chapter": "Arithmetic",
  "difficulty": "easy",
  "options": [
    {"text": "3", "is_correct": false},
    {"text": "4", "is_correct": true},
    {"text": "5", "is_correct": false},
    {"text": "6", "is_correct": false}
  ]
}
```

**Response (201):** Question object with options

#### GET `/api/questions/`
List questions.

**Headers:** Requires authentication

**Query Parameters:**
- `subject` (optional)
- `chapter` (optional)
- `limit` (default: 50, max: 100)
- `offset` (default: 0)

**Response (200):** Array of question objects

#### GET `/api/questions/{question_id}`
Get specific question.

**Headers:** Requires authentication

**Response (200):** Question object with options

---

### Content

#### GET `/api/content/search`
Search content chunks by keyword.

**Headers:** Requires authentication

**Query Parameters:**
- `q` (required): Search query
- `limit` (default: 10)

**Response (200):** Array of content chunks

---

### Chat (RAG)

#### POST `/api/chat/ask`
Ask a question using RAG (Retrieval-Augmented Generation).

**Headers:** Requires authentication

**Request:**
```json
{
  "question": "Why do tides happen?",
  "class_name": 10,
  "subject": "Science",
  "chapter": "Tides",
  "top_k": 8,
  "re_rank": false
}
```

**Response (200):**
```json
{
  "answer": "Tides occur due to the gravitational pull of the moon and sun on Earth's oceans. [1]",
  "sources": [
    {
      "chunk_id": 123,
      "source_file": "10th-science.pdf",
      "page": 12,
      "snippet": "Tides are caused by the gravitational attraction..."
    }
  ],
  "metadata": {
    "retrieved_count": 50,
    "used_top_k": 8
  },
  "llm_usage": {
    "latency_ms": 1200,
    "input_tokens": 450,
    "output_tokens": 62
  },
  "error": null
}
```

---

## Error Responses

All endpoints return standard error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid input parameters"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Not authorized to access this resource"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Data Types

### QuestionType Enum
- `mcq` - Multiple Choice Question
- `short_answer` - Short Answer
- `long_answer` - Long Answer
- `numerical` - Numerical Answer

### AttemptStatus Enum
- `in_progress` - Test in progress
- `submitted` - Submitted by student
- `auto_submitted` - Auto-submitted on timeout
- `abandoned` - Not completed

---

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: 100 requests per minute per user

## Best Practices
1. Always store JWT tokens securely (iOS Keychain / Android EncryptedStorage)
2. Implement token refresh before expiration (default: 30 minutes)
3. Use offline queue for progress updates and test submissions
4. Implement optimistic updates for better UX
5. Cache frequently accessed data (student profile, progress overview)
6. Handle 401 errors by refreshing token or prompting login
7. Use draft save frequently during tests (every 30-60 seconds)

---

## Interactive API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
