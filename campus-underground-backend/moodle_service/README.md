# Campus Underground Moodle API Service

This service provides a Python-based API for interacting with Moodle's web services. It's designed to work with the Campus Underground React/TypeScript frontend to provide Moodle integration features.

**New Implementation**: This service now includes improved error handling, consistent API responses, and automatic fallback to mock data when the Moodle API is unavailable.

## Features

- Course listing and content retrieval
- Assignment and grade information
- Calendar events
- Analytics for student performance
- File downloads from Moodle
- Robust error handling with graceful fallbacks
- Mock data support for development and testing
- Consistent data formats between frontend and backend

## Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your `.env` file (automatically created on first run):

```
# Moodle API Configuration
MOODLE_URL=https://moodle.concordia.ca
MOODLE_API_TOKEN=your_moodle_api_token_here
FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
DEBUG=True
LOG_LEVEL=INFO
USE_MOCK_DATA=False
TIMEOUT=30
RETRY_ATTEMPTS=3
CACHE_ENABLED=True
CACHE_TIMEOUT=300
```

Note: If you don't provide a valid Moodle API token, the service will automatically use mock data.

## Running the Service

Start the Flask API server (use the new implementation):

```bash
python api_server_new.py
```

The server will run on port 5002 by default (configurable in the `.env` file).

For development and testing without a Moodle instance, you can use mock data mode by setting `USE_MOCK_DATA=True` in your `.env` file or by not providing a valid Moodle API token.

## API Endpoints

### System Endpoints
- `GET /api/health` - Check if the API server is running
- `GET /api/config` - Get server configuration information
- `GET /api/test-connection` - Test connection to Moodle

### Courses
- `GET /api/courses` - Get user's enrolled courses
  - Required header: `user-id`

### Course Contents
- `GET /api/courses/{course_id}/contents` - Get contents of a specific course

### Assignments
- `GET /api/courses/{course_id}/assignments` - Get assignments for a course
  - Required header: `user-id`

### Grades
- `GET /api/courses/{course_id}/grades` - Get user grades for a course
  - Required header: `user-id`

### File Access
- `POST /api/download` - Download a file from Moodle (returns base64-encoded content)
  - Request body: `{ "fileUrl": "https://moodle.example.com/file/path" }`
- `GET /api/file/{file_url}` - Proxy a file from Moodle (returns file directly)

### Calendar Events
- `GET /api/calendar-events` - Get calendar events
  - Optional query parameters: `from`, `to` (timestamp format)

### Analytics
- `GET /api/analytics/grade-trends` - Get grade trends over time
  - Required header: `user-id`
- `GET /api/analytics/completion-rates` - Get course completion rates
  - Required header: `user-id`
- `GET /api/analytics/grade-distribution` - Get grade distribution
  - Required header: `user-id`
- `GET /api/analytics/performance-overview` - Get performance overview
  - Required header: `user-id`

All endpoints return JSON responses with consistent error handling. If an error occurs, the response will include an `error` field with a description of the error.

## Integration with Campus Underground Frontend

This service is designed to be used with the Campus Underground React/TypeScript frontend. The frontend makes HTTP requests to this API server, which then communicates with Moodle.

### Frontend Integration

The frontend uses two key services:
- `moodleService.ts` - Main service for interacting with the Moodle API
- `mockMoodleService.ts` - Fallback service that provides mock data when the API is unavailable

The new implementation (`moodleService_new.ts`) provides:
- Improved error handling with automatic fallback to mock data
- TypeScript interfaces for better type safety
- Consistent data formats between frontend and backend
- Better handling of API errors with detailed error messages

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  React Frontend │──────▶  Flask API      │──────▶  Moodle LMS     │
│  (TypeScript)   │      │  Server (Python)│      │  Web Services   │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │
        │                        │
        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐
│  Mock Data      │      │  Mock Data      │
│  (TypeScript)   │      │  (Python)       │
└─────────────────┘      └─────────────────┘
```

## Obtaining a Moodle API Token

To use this service with a real Moodle instance, you need a Moodle API token. Here's how to get one:

1. Log in to your Moodle account
2. Go to your profile settings
3. Look for "Security keys" or "Web services"
4. Generate a new token for the required services

Note: The token must have permissions for the following web services:
- `core_webservice_get_site_info`
- `core_enrol_get_users_courses`
- `core_course_get_contents`
- `mod_assign_get_assignments`
- `gradereport_user_get_grade_items`
- `core_calendar_get_calendar_events`

## Testing

To test the integration:

1. Start the Flask API server: `python api_server_new.py`
2. Make a request to the test endpoint: `curl http://localhost:5002/api/test-connection`
3. Check the response to verify the connection status

You can also use the mock data mode for testing without a Moodle instance.
