#!/usr/bin/env python3
"""
Flask API server for Moodle integration with Campus Underground
This server provides a RESTful API for the frontend to interact with Moodle.
"""

import os
import sys
import json
import logging
import base64
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import tempfile
from typing import Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_api_server')

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client_new import MoodleAPIClient, MoodleAPIError
from gpt_service import GPTService, GPTAPIError
from database import MoodleDatabase

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'campus-underground-secret-key')

# Enable CORS for all endpoints
CORS(app)

# Global client instances
moodle_client = None
gpt_service = None
db = None

def get_client(force_new: bool = False) -> MoodleAPIClient:
    """
    Get or initialize the Moodle client.
    
    Args:
        force_new: Whether to force creation of a new client instance
        
    Returns:
        MoodleAPIClient instance
    """
    global moodle_client
    if moodle_client is None or force_new:
        try:
            # Check if token is available
            token = os.getenv('MOODLE_API_TOKEN', '')
            if not token or token == 'your_moodle_api_token_here':
                logger.warning("No valid Moodle API token found. Server will start but Moodle features will be limited.")
                moodle_client = None
                return moodle_client
            
            # Create client instance with real data only
            moodle_client = MoodleAPIClient()
            logger.info("Using real Moodle API with provided token")
            
            # Validate token (but don't fail if invalid - just warn)
            try:
                if not moodle_client.validate_token():
                    logger.warning("Moodle API token validation failed. Server will start but Moodle features may not work properly.")
                else:
                    logger.info("Moodle API token validated successfully")
            except Exception as validation_error:
                logger.warning(f"Moodle API token validation failed: {validation_error}. Server will start but Moodle features may not work properly.")
                
        except Exception as e:
            logger.warning(f"Failed to initialize Moodle client: {e}. Server will start but Moodle features will be limited.")
            moodle_client = None
            
    return moodle_client

def get_user_id_from_request() -> Optional[int]:
    """
    Get user ID from request headers.
    
    Returns:
        User ID as integer or None if not provided
    """
    user_id = request.headers.get('user-id')
    if not user_id:
        return None
        
    try:
        return int(user_id)
    except ValueError:
        return None

def get_gpt_service(force_new: bool = False) -> GPTService:
    """
    Get or initialize the GPT service.
    
    Args:
        force_new: Whether to force creation of a new service instance
        
    Returns:
        GPTService instance
    """
    global gpt_service
    if gpt_service is None or force_new:
        try:
            # Check if we should use mock data
            api_key = os.getenv('OPENAI_API_KEY', '')
            use_mock = api_key == 'your_openai_api_key_here' or not api_key
            
            # Create service instance
            gpt_service = GPTService(use_mock_data=use_mock)
            
            if use_mock:
                logger.info("Using mock data for GPT API service")
            else:
                logger.info("Using real GPT API with provided key")
                
        except Exception as e:
            logger.error(f"Failed to initialize GPT service: {e}")
            # Fall back to mock data
            gpt_service = GPTService(use_mock_data=True)
            
    return gpt_service

def get_database(force_new: bool = False) -> MoodleDatabase:
    """
    Get or initialize the database connection.
    
    Args:
        force_new: Whether to force creation of a new database instance
        
    Returns:
        MoodleDatabase instance
    """
    global db
    if db is None or force_new:
        try:
            # Initialize database with default path
            db = MoodleDatabase()
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
            
    return db

def handle_api_error(func):
    """Decorator to handle API errors consistently."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MoodleAPIError as e:
            logger.error(f"Moodle API error: {e}")
            return jsonify({'error': str(e)}), 500
        except GPTAPIError as e:
            logger.error(f"GPT API error: {e}")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return jsonify({'error': 'An unexpected error occurred'}), 500
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'OK',
        'message': 'Moodle API server is running',
        'version': '1.0.0'
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get server configuration."""
    client = get_client()
    return jsonify({
        'useMockData': client.use_mock_data,
        'moodleUrl': client.base_url,
        'apiVersion': '1.0.0'
    })

@app.route('/api/courses', methods=['GET'])
@handle_api_error
def get_courses():
    """Get user's Moodle courses."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    courses = client.get_courses(user_id)
    
    return jsonify(courses)

@app.route('/api/courses/<int:course_id>/contents', methods=['GET'])
@handle_api_error
def get_course_contents(course_id):
    """Get course contents."""
    client = get_client()
    contents = client.get_course_contents(course_id)
    
    return jsonify(contents)

@app.route('/api/courses/<int:course_id>/assignments', methods=['GET'])
@handle_api_error
def get_course_assignments(course_id):
    """Get course assignments."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    assignments = client.get_assignments(course_id, user_id)
    
    return jsonify(assignments)

@app.route('/api/courses/<int:course_id>/grades', methods=['GET'])
@handle_api_error
def get_course_grades(course_id):
    """Get user grades for a course."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    grades = client.get_user_grades(user_id, course_id)
    
    return jsonify(grades)

@app.route('/api/calendar-events', methods=['GET'])
@handle_api_error
def get_calendar_events():
    """Get calendar events."""
    # Parse date parameters
    events_from = request.args.get('from')
    events_to = request.args.get('to')
    
    client = get_client()
    events = client.get_calendar_events(events_from, events_to)
    
    return jsonify(events)

@app.route('/api/download', methods=['POST'])
@handle_api_error
def download_file():
    """Download a file from Moodle."""
    data = request.json
    if not data or 'fileUrl' not in data:
        return jsonify({'error': 'File URL is required'}), 400
    
    file_url = data['fileUrl']
    client = get_client()
    file_data = client.download_file(file_url)
    
    if isinstance(file_data, dict) and 'error' in file_data:
        return jsonify({'error': file_data['error']}), 500
    
    # Return file data as base64
    return jsonify({
        'content': base64.b64encode(file_data['content']).decode('utf-8'),
        'contentType': file_data['content_type'],
        'filename': file_data['filename']
    })

@app.route('/api/file/<path:file_url>', methods=['GET'])
@handle_api_error
def proxy_file(file_url):
    """Proxy a file from Moodle."""
    client = get_client()
    file_data = client.download_file(file_url)
    
    if isinstance(file_data, dict) and 'error' in file_data:
        return jsonify({'error': file_data['error']}), 500
    
    # Return the file directly
    response = Response(file_data['content'])
    response.headers['Content-Type'] = file_data['content_type']
    response.headers['Content-Disposition'] = f'inline; filename="{file_data["filename"]}"'
    
    return response

# Analytics endpoints

@app.route('/api/analytics/grade-trends', methods=['GET'])
@handle_api_error
def get_grade_trends():
    """Get grade trends for analytics."""
    # This would be a custom implementation based on grade history
    # For now, return mock data
    return jsonify([
        {
            'id': 'Average Grade',
            'data': [
                {'x': 'Week 1', 'y': 75},
                {'x': 'Week 2', 'y': 78},
                {'x': 'Week 3', 'y': 80},
                {'x': 'Week 4', 'y': 82},
                {'x': 'Week 5', 'y': 85}
            ]
        },
        {
            'id': 'COMP352',
            'data': [
                {'x': 'Week 1', 'y': 70},
                {'x': 'Week 2', 'y': 75},
                {'x': 'Week 3', 'y': 82},
                {'x': 'Week 4', 'y': 85},
                {'x': 'Week 5', 'y': 88}
            ]
        }
    ])

@app.route('/api/analytics/completion-rates', methods=['GET'])
@handle_api_error
def get_completion_rates():
    """Get completion rates for analytics."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    courses = client.get_courses(user_id)
    
    # Extract completion rates from courses
    result = []
    for course in courses:
        result.append({
            'course': course.get('shortname', ''),
            'value': course.get('progress', 0)
        })
    
    return jsonify(result)

@app.route('/api/analytics/grade-distribution', methods=['GET'])
@handle_api_error
def get_grade_distribution():
    """Get grade distribution for analytics."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    distribution = client.get_grade_distribution(user_id)
    
    return jsonify(distribution)

@app.route('/api/analytics/performance-overview', methods=['GET'])
@handle_api_error
def get_performance_overview():
    """Get performance overview for analytics."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    overview = client.get_performance_overview(user_id)
    
    return jsonify(overview)

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Test connection to Moodle."""
    try:
        # Force a new client to ensure we're testing the current configuration
        client = get_client(force_new=True)
        
        # Try to get site info
        site_info = client.get_site_info()
        
        return jsonify({
            'success': True,
            'useMockData': client.use_mock_data,
            'siteInfo': {
                'sitename': site_info.get('sitename', 'Unknown'),
                'version': site_info.get('release', 'Unknown')
            }
        })
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# GPT API endpoints

@app.route('/api/gpt/analyze', methods=['POST'])
@handle_api_error
def analyze_content():
    """Analyze content using GPT."""
    data = request.json
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    analysis_type = data.get('analysisType', 'summary')
    
    service = get_gpt_service()
    result = service.analyze_content(content, analysis_type)
    
    return jsonify(result)

@app.route('/api/gpt/analyze-performance', methods=['POST'])
@handle_api_error
def analyze_performance():
    """Analyze student performance using GPT."""
    data = request.json
    if not data or not isinstance(data, dict):
        return jsonify({'error': 'Performance data is required'}), 400
    
    service = get_gpt_service()
    result = service.analyze_student_performance(data)
    
    return jsonify(result)

# Flashcard endpoints

@app.route('/api/flashcards/decks', methods=['GET'])
@handle_api_error
def get_flashcard_decks():
    """Get flashcard decks for the current user."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    course_id = request.args.get('course_id')
    if course_id:
        try:
            course_id = int(course_id)
        except ValueError:
            return jsonify({'error': 'Invalid course ID'}), 400
    
    db = get_database()
    decks = db.get_flashcard_decks(user_id, course_id)
    
    return jsonify(decks)

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['GET'])
@handle_api_error
def get_flashcard_deck(deck_id):
    """Get a specific flashcard deck with its cards."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    db = get_database()
    
    # Get the deck
    decks = db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    # Get the cards
    cards = client.db.get_flashcards(deck_id)
    deck['cards'] = cards
    
    return jsonify(deck)

@app.route('/api/flashcards/decks', methods=['POST'])
@handle_api_error
def create_flashcard_deck():
    """Create a new flashcard deck."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['title', 'description', 'subject']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    db = get_database()
    deck_id = db.save_flashcard_deck(data, user_id)
    
    # Return the created deck
    decks = db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    return jsonify(deck), 201

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['PUT'])
@handle_api_error
def update_flashcard_deck(deck_id):
    """Update a flashcard deck."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Ensure the deck ID is included in the data
    data['id'] = deck_id
    
    client = get_client()
    client.db.save_flashcard_deck(data, user_id)
    
    # Return the updated deck
    decks = client.db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    return jsonify(deck)

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['DELETE'])
@handle_api_error
def delete_flashcard_deck(deck_id):
    """Delete a flashcard deck."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    db = get_database()
    db.delete_flashcard_deck(deck_id, user_id)
    
    return '', 204

@app.route('/api/flashcards/decks/<int:deck_id>/cards', methods=['POST'])
@handle_api_error
def create_flashcard(deck_id):
    """Create a new flashcard."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['question', 'answer', 'difficulty']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    client = get_client()
    
    # Verify the deck belongs to the user
    decks = client.db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    card_id = client.db.save_flashcard(data, deck_id)
    
    # Return the created card
    cards = client.db.get_flashcards(deck_id)
    card = next((c for c in cards if c['id'] == card_id), None)
    
    return jsonify(card), 201

@app.route('/api/flashcards/decks/<int:deck_id>/cards/<int:card_id>', methods=['PUT'])
@handle_api_error
def update_flashcard(deck_id, card_id):
    """Update a flashcard."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Ensure the card ID is included in the data
    data['id'] = card_id
    
    client = get_client()
    
    # Verify the deck belongs to the user
    decks = client.db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    client.db.save_flashcard(data, deck_id)
    
    # Return the updated card
    cards = client.db.get_flashcards(deck_id)
    card = next((c for c in cards if c['id'] == card_id), None)
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    return jsonify(card)

@app.route('/api/flashcards/decks/<int:deck_id>/cards/<int:card_id>', methods=['DELETE'])
@handle_api_error
def delete_flashcard(deck_id, card_id):
    """Delete a flashcard."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    
    # Verify the deck belongs to the user
    decks = client.db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    client.db.delete_flashcard(card_id, deck_id)
    
    return '', 204

@app.route('/api/flashcards/decks/<int:deck_id>/study', methods=['POST'])
@handle_api_error
def update_deck_studied(deck_id):
    """Update deck's last studied timestamp."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    client = get_client()
    
    # Verify the deck belongs to the user
    decks = client.db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404
    
    client.db.update_deck_studied(deck_id)
    
    return '', 204

@app.route('/api/flashcards/cards/<int:card_id>/review', methods=['POST'])
@handle_api_error
def update_card_review(card_id):
    """Update card review data."""
    data = request.json
    if not data or 'difficulty' not in data:
        return jsonify({'error': 'Difficulty is required'}), 400
    
    client = get_client()
    client.db.update_flashcard_review(card_id, data['difficulty'])
    
    return '', 204

# Sync endpoints

@app.route('/api/sync/status', methods=['GET'])
@handle_api_error
def sync_status():
    """Get the status of the last sync operation."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # In a real implementation, this would check a database for the last sync time
    # For now, we'll return a mock status
    import datetime
    now = datetime.datetime.now()
    last_sync = now - datetime.timedelta(hours=2)  # Mock last sync time (2 hours ago)
    
    # Calculate age in minutes
    age_minutes = int((now - last_sync).total_seconds() / 60)
    
    # Determine status based on age
    if age_minutes < 60:
        status = 'Recent'
    elif age_minutes < 24 * 60:
        status = 'Today'
    elif age_minutes < 7 * 24 * 60:
        status = 'This week'
    else:
        status = 'Outdated'
    
    return jsonify({
        'data': {
            'last_sync': last_sync.isoformat(),
            'last_sync_formatted': last_sync.strftime('%Y-%m-%d %H:%M'),
            'status': status,
            'age_minutes': age_minutes
        }
    })

@app.route('/api/sync/all', methods=['POST'])
@handle_api_error
def sync_all():
    """Sync all data from Moodle."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # In a real implementation, this would trigger a sync job
    # For now, we'll just return a success message
    import datetime
    now = datetime.datetime.now()
    
    return jsonify({
        'success': True,
        'message': 'Sync completed successfully',
        'timestamp': now.isoformat(),
        'sync_items': {
            'courses': 4,
            'assignments': 12,
            'grades': 8,
            'resources': 15
        }
    })

@app.route('/api/sync/courses', methods=['POST'])
@handle_api_error
def sync_courses():
    """Sync only courses data from Moodle."""
    user_id = get_user_id_from_request()
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    # In a real implementation, this would trigger a sync job for courses only
    # For now, we'll just return a success message
    import datetime
    now = datetime.datetime.now()
    
    return jsonify({
        'success': True,
        'message': 'Courses sync completed successfully',
        'timestamp': now.isoformat(),
        'sync_items': {
            'courses': 4
        }
    })

@app.route('/api/gpt/status', methods=['GET'])
@handle_api_error
def gpt_status():
    """Check GPT API status."""
    service = get_gpt_service()
    return jsonify({
        'available': True,
        'useMockData': service.use_mock_data
    })

def create_env_file():
    """Create a .env file if it doesn't exist."""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# Moodle API Configuration
MOODLE_URL=https://moodle.concordia.ca
MOODLE_API_TOKEN=your_moodle_api_token_here
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
""")
        logger.info(f"Created .env file at {env_file}")
        print(f"Created .env file at {env_file}. Please update it with your Moodle API token and OpenAI API key.")

if __name__ == '__main__':
    # Create a .env file if it doesn't exist
    create_env_file()
    
    # Initialize services
    get_client()
    get_gpt_service()
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
