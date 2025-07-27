# Moodle Integration for Campus Underground

This document explains how the Moodle API integration works with the Campus Underground project and how to use it in your development workflow.

## Architecture Overview

The Moodle integration follows a microservice architecture pattern:

1. **Python Moodle API Service** - A dedicated Python service that handles all Moodle API interactions
2. **TypeScript Backend Proxy** - The existing Node.js/Express backend that forwards requests to the Python service
3. **React Frontend** - The existing React frontend that makes API calls to the TypeScript backend

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │      │                 │
│  React Frontend │──────▶ TypeScript API  │──────▶  Python Moodle  │──────▶  Moodle LMS    │
│                 │      │  Backend        │      │  API Service    │      │                 │
│                 │      │                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Why This Architecture?

1. **Separation of Concerns** - The Python service focuses solely on Moodle API interactions
2. **Language Optimization** - Python has better libraries for certain tasks like PDF processing
3. **Maintainability** - Each service can be updated independently
4. **Scalability** - The Moodle service can be scaled separately from the main backend
5. **Reusability** - The Python service can be used by other applications if needed

## Integration with Existing Code

### TypeScript Backend Integration

The TypeScript backend already has routes set up in `/src/routes/moodle.ts` that forward requests to the Python service. These routes match the endpoints provided by the Python service, creating a seamless proxy.

The TypeScript backend uses the `MoodleAPIClient` class in `/src/services/moodle.ts` to communicate with the Python service. This class follows the same interface as the direct Moodle API, making it easy to switch between implementations.

### React Frontend Integration

The React frontend makes API calls to the TypeScript backend, which then forwards them to the Python service. From the frontend's perspective, it's just making regular API calls to the backend.

## Key Features

The Moodle integration provides the following features:

1. **Course Information** - Get a list of courses and their contents
2. **Assignment Management** - View and manage assignments
3. **Grade Tracking** - View grades and track progress
4. **Calendar Events** - Get upcoming events and deadlines
5. **File Access** - Download files from Moodle
6. **Analytics** - Get performance analytics and insights

## Authentication Flow

1. User logs in to Campus Underground using Supabase Auth
2. User provides their Moodle API token (one-time setup)
3. The token is stored securely in the database
4. All subsequent Moodle API requests use this token

## Development Workflow

When developing features that use the Moodle integration:

1. Start both the TypeScript backend and Python service using `./start-services.sh`
2. Make API calls from your frontend to the TypeScript backend
3. The TypeScript backend will forward requests to the Python service
4. The Python service will make requests to Moodle and return the results

## Testing the Integration

You can test the Moodle integration using the provided test script:

```bash
cd campus-underground-backend/moodle_service
python test_client.py
```

This script will test the basic functionality of the Moodle API client and verify that it can connect to Moodle.

## Extending the Integration

To add new Moodle API endpoints:

1. Add the new method to `moodle_client.py`
2. Add a new endpoint to `api_server.py`
3. Add a new route to `/src/routes/moodle.ts` in the TypeScript backend
4. Add the corresponding method to `/src/services/moodle.ts`

## Deployment Considerations

When deploying the application:

1. Deploy the Python service as a separate service
2. Configure the TypeScript backend to point to the deployed Python service
3. Ensure the Python service has access to the Moodle API token
4. Set up proper monitoring and logging for both services

## Troubleshooting

Common issues and solutions:

1. **Connection Errors** - Check that the Moodle API token is valid and has the necessary permissions
2. **Missing Endpoints** - Verify that the required endpoints are enabled in your Moodle instance
3. **Authentication Issues** - Ensure the token is being passed correctly in the requests
4. **Performance Issues** - Consider caching frequently accessed data

## Integration with Study Tools

The Moodle integration enhances the existing study tools in Campus Underground:

### Smart Notes
- Pull course materials directly from Moodle
- Link notes to specific course modules
- Automatically organize notes by course

### Flashcards
- Import course content as flashcards
- Link flashcards to specific course topics
- Track performance against course objectives

### Pomodoro Timer
- Schedule study sessions based on course deadlines
- Prioritize tasks based on upcoming assignments
- Track study time per course

## Design Consistency

The Moodle integration maintains the same dark theme with yellow primary accent used throughout the Campus Underground project, ensuring a consistent user experience.

## Future Enhancements

Planned enhancements for the Moodle integration:

1. **Offline Support** - Cache course content for offline access
2. **Advanced Analytics** - More detailed performance insights
3. **Automated Study Plans** - Generate study plans based on course schedules
4. **Mobile Support** - Optimize for mobile devices
5. **Real-time Updates** - Get notifications for new content and grades
