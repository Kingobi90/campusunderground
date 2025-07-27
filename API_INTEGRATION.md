# Campus Underground API Integration Guide

This document provides instructions for integrating the Campus Underground application with real Moodle LMS and OpenAI GPT APIs.

## Overview

Campus Underground uses two main external APIs:

1. **Moodle API**: For retrieving course data, assignments, grades, and other educational content
2. **OpenAI GPT API**: For analyzing educational content and providing insights

Both APIs can operate in either real mode (using actual API credentials) or mock mode (using simulated data for development).

## Configuration

### Backend Configuration

The backend services expect API credentials to be provided in a `.env` file located in the `campus-underground-backend/moodle_service` directory.

1. If the `.env` file doesn't exist, it will be automatically created when you start the backend server.
2. Edit the `.env` file to add your API credentials:

```
# Moodle API Configuration
MOODLE_URL=https://your-moodle-instance.edu
MOODLE_API_TOKEN=your_moodle_api_token_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
```

### API Keys

#### Moodle API Token

To obtain a Moodle API token:

1. Log in to your Moodle instance as an administrator
2. Navigate to Site Administration > Plugins > Web Services > Manage tokens
3. Create a new token with appropriate permissions for courses, assignments, and grades
4. Copy the generated token to your `.env` file

#### OpenAI API Key

To obtain an OpenAI API key:

1. Create an account at [OpenAI](https://platform.openai.com/)
2. Navigate to the API section and create a new API key
3. Copy the API key to your `.env` file

## Mock Mode vs. Real Mode

Both the Moodle and GPT services will automatically fall back to mock data if:

1. The API keys are not provided in the `.env` file
2. The API keys are invalid or have the default placeholder values
3. The API requests fail for any reason

This allows development and testing without requiring real API credentials.

## API Endpoints

### Moodle API Endpoints

The following endpoints are available for Moodle integration:

- `GET /api/courses` - Get all courses for the current user
- `GET /api/courses/:courseId/assignments` - Get assignments for a specific course
- `GET /api/courses/:courseId/grades` - Get grades for a specific course
- `GET /api/courses/:courseId/contents` - Get content for a specific course
- `GET /api/calendar/events` - Get calendar events
- `GET /api/analytics/grade-trends` - Get grade trends analytics
- `GET /api/analytics/completion-rates` - Get completion rates analytics
- `GET /api/test-connection` - Test Moodle API connection

### GPT API Endpoints

The following endpoints are available for GPT integration:

- `POST /api/gpt/analyze` - Analyze content using GPT
  - Request body: `{ "content": "text to analyze", "analysisType": "summary|key_points|quiz_generation" }`
- `POST /api/gpt/analyze-performance` - Analyze student performance using GPT
  - Request body: Performance data object with grades, assignments, and analytics
- `GET /api/gpt/status` - Check GPT API status

## Frontend Integration

The frontend services are configured to connect to these backend endpoints:

1. `moodleService.ts` - Connects to Moodle API endpoints
2. `gptService.ts` - Connects to GPT API endpoints

The frontend will display whether it's using real or mock data in the Content Analyzer component.

## Testing the Integration

1. Start the backend server:
   ```
   cd campus-underground-backend/moodle_service
   python api_server.py
   ```

2. Start the frontend development server:
   ```
   cd campus-underground-frontend
   npm start
   ```

3. Navigate to the Content Analyzer component to test the integration:
   - If using mock data, you'll see indicators that mock data is being used
   - If using real API credentials, you'll see actual data from your Moodle instance

## Troubleshooting

### Moodle API Issues

- Verify your Moodle URL is correct and accessible
- Ensure your API token has the necessary permissions
- Check the backend logs for specific error messages

### GPT API Issues

- Verify your OpenAI API key is valid and has sufficient quota
- Check for rate limiting issues in the backend logs
- Ensure your requests are properly formatted

## Security Considerations

- Never commit your `.env` file to version control
- Rotate API keys periodically for security
- Consider implementing additional authentication for production deployments
