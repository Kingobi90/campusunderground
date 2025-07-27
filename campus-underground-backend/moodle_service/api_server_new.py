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
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_api_server')

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client_new import MoodleAPIClient, MoodleAPIError
from database import MoodleDatabase
from sync_service import MoodleSyncService

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'campus-underground-secret-key')

# Enable CORS for all endpoints
CORS(app)

# Global instances
moodle_client = None
moodle_db = MoodleDatabase()
sync_service = None

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
        # Check if we have a valid token
        token = os.getenv('MOODLE_API_TOKEN', '')
        if not token or token == 'your_moodle_api_token_here':
            logger.warning("No valid Moodle API token provided")
        
        # Create a new client - no mock data option anymore
        moodle_client = MoodleAPIClient()
        logger.info("Using real Moodle API connection")
    
    return moodle_client

def get_sync_service(force_new: bool = False) -> MoodleSyncService:
    """
    Get or initialize the Moodle sync service.
    
    Args:
        force_new: Whether to force creation of a new service instance
        
    Returns:
        MoodleSyncService instance
    """
    global sync_service
    
    if sync_service is None or force_new:
        # Get the Moodle client
        client = get_client()
        
        # Create a new sync service with the client and database
        sync_service = MoodleSyncService(client=client, db=moodle_db)
        
    return sync_service

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

def handle_api_error(func):
    """Decorator to handle API errors consistently."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MoodleAPIError as e:
            logger.error(f"Moodle API error: {e}")
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
    
    # Get courses from database
    courses = moodle_db.get_courses(user_id)
    
    return jsonify({
        'status': 'success',
        'data': courses,
        'source': 'database'
    })

@app.route('/api/courses/<int:course_id>/contents', methods=['GET'])
@handle_api_error
def get_course_contents(course_id):
    """Get course contents."""
    user_id = get_user_id_from_request()
    
    # Get resources from database
    resources = moodle_db.get_resources(course_id, user_id)
    
    return jsonify({
        'status': 'success',
        'data': resources,
        'source': 'database'
    })

@app.route('/api/courses/<int:course_id>/assignments', methods=['GET'])
@handle_api_error
def get_course_assignments(course_id):
    """Get course assignments."""
    user_id = get_user_id_from_request()
    
    # Get assignments from database
    assignments = moodle_db.get_assignments(course_id, user_id)
    
    return jsonify({
        'status': 'success',
        'data': assignments,
        'source': 'database'
    })

@app.route('/api/courses/<int:course_id>/grades', methods=['GET'])
@handle_api_error
def get_course_grades(course_id):
    """Get user grades for a course."""
    user_id = get_user_id_from_request()
    
    # Get grades from database
    grades = moodle_db.get_grades(course_id, user_id)
    
    return jsonify({
        'status': 'success',
        'data': grades,
        'source': 'database'
    })

@app.route('/api/courses/<int:course_id>/resources', methods=['GET'])
@handle_api_error
def get_course_resources(course_id):
    """Get resources for a course."""
    user_id = get_user_id_from_request()
    
    # Get resources from database
    resources = moodle_db.get_resources(course_id, user_id)
    
    return jsonify({
        'status': 'success',
        'data': resources,
        'source': 'database'
    })

@app.route('/api/calendar', methods=['GET'])
@handle_api_error
def get_calendar_events():
    """Get calendar events."""
    user_id = get_user_id_from_request()
    
    # Get optional date range parameters
    from_time = request.args.get('from')
    to_time = request.args.get('to')
    
    # Convert string timestamps to integers if provided
    from_timestamp = int(from_time) if from_time and from_time.isdigit() else None
    to_timestamp = int(to_time) if to_time and to_time.isdigit() else None
    
    # Get events from database
    events = moodle_db.get_calendar_events(user_id, from_timestamp, to_timestamp)
    
    return jsonify({
        'status': 'success',
        'data': events,
        'source': 'database'
    })

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
    user_id = get_user_id_from_request()
    
    # Get grade trends from database
    trends = moodle_db.get_grade_trends(user_id)
    
    return jsonify({
        'status': 'success',
        'data': trends,
        'source': 'database'
    })

@app.route('/api/analytics/completion-rates', methods=['GET'])
@handle_api_error
def get_completion_rates():
    """Get completion rates for analytics."""
    user_id = get_user_id_from_request()
    
    # Get completion rates from database
    rates = moodle_db.get_completion_rates(user_id)
    
    return jsonify({
        'status': 'success',
        'data': rates,
        'source': 'database'
    })

@app.route('/api/analytics/grade-distribution', methods=['GET'])
@handle_api_error
def get_grade_distribution():
    """Get grade distribution for analytics."""
    user_id = get_user_id_from_request()
    
    # Get grade distribution from database
    distribution = moodle_db.get_grade_distribution(user_id)
    
    return jsonify({
        'status': 'success',
        'data': distribution,
        'source': 'database'
    })

@app.route('/api/analytics/performance', methods=['GET'])
@handle_api_error
def get_performance_overview():
    """Get performance overview for analytics."""
    user_id = get_user_id_from_request()
    
    # Get performance overview from database
    performance = moodle_db.get_performance_overview(user_id)
    
    return jsonify({
        'status': 'success',
        'data': performance,
        'source': 'database'
    })

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

# New sync endpoints
@app.route('/api/sync/status', methods=['GET'])
@handle_api_error
def get_sync_status():
    """Get the current sync status."""
    service = get_sync_service()
    status = service.get_last_sync_info()
    
    return jsonify({
        'status': 'success',
        'data': status
    })

@app.route('/api/sync/all', methods=['POST'])
@handle_api_error
def sync_all_data():
    """Sync all data for the current user."""
    user_id = get_user_id_from_request()
    service = get_sync_service()
    
    # Start the sync process
    result = service.sync_all(user_id)
    
    return jsonify({
        'status': 'success' if result['success'] else 'error',
        'message': result['message'],
        'data': result
    })

@app.route('/api/sync/courses', methods=['POST'])
@handle_api_error
def sync_courses_data():
    """Sync courses data for the current user."""
    user_id = get_user_id_from_request()
    service = get_sync_service()
    
    # Sync courses
    result = service.sync_courses(user_id)
    
    return jsonify({
        'status': 'success',
        'message': 'Courses synced successfully',
        'data': result
    })

def create_env_file():
    """Create a .env file if it doesn't exist."""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# Moodle API Configuration
MOODLE_URL=https://moodle.concordia.ca
MOODLE_API_TOKEN=your_moodle_api_token_here
FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5000
""")
        logger.info(f"Created .env file at {env_file}")
        print(f"Created .env file at {env_file}. Please update it with your Moodle API token.")

# Flashcard endpoints
@app.route('/api/flashcards/decks', methods=['GET'])
@handle_api_error
def get_flashcard_decks():
    """Get all flashcard decks for a user."""
    user_id = get_user_id_from_request()
    course_id = request.args.get('course_id')
    
    # Convert course_id to int if provided
    course_id = int(course_id) if course_id and course_id.isdigit() else None
    
    # Get decks from database
    decks = moodle_db.get_flashcard_decks(user_id, course_id)
    
    return jsonify({
        'status': 'success',
        'data': decks,
        'source': 'database'
    })

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['GET'])
@handle_api_error
def get_flashcard_deck(deck_id):
    """Get a specific flashcard deck with its cards."""
    user_id = get_user_id_from_request()
    
    # Get deck from database
    decks = moodle_db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({
            'status': 'error',
            'message': f'Deck with ID {deck_id} not found'
        }), 404
    
    # Get cards for the deck
    cards = moodle_db.get_flashcards(deck_id)
    deck['cards'] = cards
    
    return jsonify({
        'status': 'success',
        'data': deck,
        'source': 'database'
    })

@app.route('/api/flashcards/decks', methods=['POST'])
@handle_api_error
def create_flashcard_deck():
    """Create a new flashcard deck."""
    user_id = get_user_id_from_request()
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    # Save deck to database
    deck_id = moodle_db.save_flashcard_deck(data, user_id)
    
    # Get the newly created deck
    decks = moodle_db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    return jsonify({
        'status': 'success',
        'data': deck,
        'source': 'database'
    }), 201

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['PUT'])
@handle_api_error
def update_flashcard_deck(deck_id):
    """Update a flashcard deck."""
    user_id = get_user_id_from_request()
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    # Update deck in database
    data['id'] = deck_id
    moodle_db.save_flashcard_deck(data, user_id)
    
    # Get the updated deck
    decks = moodle_db.get_flashcard_decks(user_id)
    deck = next((d for d in decks if d['id'] == deck_id), None)
    
    if not deck:
        return jsonify({
            'status': 'error',
            'message': f'Deck with ID {deck_id} not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': deck,
        'source': 'database'
    })

@app.route('/api/flashcards/decks/<int:deck_id>', methods=['DELETE'])
@handle_api_error
def delete_flashcard_deck(deck_id):
    """Delete a flashcard deck."""
    user_id = get_user_id_from_request()
    
    # Delete deck from database
    moodle_db.delete_flashcard_deck(deck_id, user_id)
    
    return jsonify({
        'status': 'success',
        'message': f'Deck with ID {deck_id} deleted'
    })

@app.route('/api/flashcards/decks/<int:deck_id>/cards', methods=['GET'])
@handle_api_error
def get_flashcards(deck_id):
    """Get all flashcards for a deck."""
    # Get cards from database
    cards = moodle_db.get_flashcards(deck_id)
    
    return jsonify({
        'status': 'success',
        'data': cards,
        'source': 'database'
    })

@app.route('/api/flashcards/decks/<int:deck_id>/cards', methods=['POST'])
@handle_api_error
def create_flashcard(deck_id):
    """Create a new flashcard."""
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    # Save card to database
    card_id = moodle_db.save_flashcard(data, deck_id)
    
    # Get the newly created card
    cards = moodle_db.get_flashcards(deck_id)
    card = next((c for c in cards if c['id'] == card_id), None)
    
    return jsonify({
        'status': 'success',
        'data': card,
        'source': 'database'
    }), 201

@app.route('/api/flashcards/decks/<int:deck_id>/cards/<int:card_id>', methods=['PUT'])
@handle_api_error
def update_flashcard(deck_id, card_id):
    """Update a flashcard."""
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No data provided'
        }), 400
    
    # Update card in database
    data['id'] = card_id
    moodle_db.save_flashcard(data, deck_id)
    
    # Get the updated card
    cards = moodle_db.get_flashcards(deck_id)
    card = next((c for c in cards if c['id'] == card_id), None)
    
    if not card:
        return jsonify({
            'status': 'error',
            'message': f'Card with ID {card_id} not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': card,
        'source': 'database'
    })

@app.route('/api/flashcards/decks/<int:deck_id>/cards/<int:card_id>', methods=['DELETE'])
@handle_api_error
def delete_flashcard(deck_id, card_id):
    """Delete a flashcard."""
    # Delete card from database
    moodle_db.delete_flashcard(card_id, deck_id)
    
    return jsonify({
        'status': 'success',
        'message': f'Card with ID {card_id} deleted'
    })

@app.route('/api/flashcards/decks/<int:deck_id>/study', methods=['POST'])
@handle_api_error
def study_deck(deck_id):
    """Mark a deck as studied."""
    user_id = get_user_id_from_request()
    
    # Update deck's last_studied timestamp
    moodle_db.update_deck_study_timestamp(deck_id, user_id)
    
    return jsonify({
        'status': 'success',
        'message': f'Deck with ID {deck_id} marked as studied'
    })

@app.route('/api/flashcards/cards/<int:card_id>/review', methods=['POST'])
@handle_api_error
def review_card(card_id):
    """Update a card's review data."""
    data = request.json
    
    if not data or 'difficulty' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Difficulty level is required'
        }), 400
    
    # Update card's review data
    moodle_db.update_flashcard_review(card_id, data['difficulty'])
    
    return jsonify({
        'status': 'success',
        'message': f'Card with ID {card_id} reviewed'
    })

if __name__ == '__main__':
    # Create a .env file if it doesn't exist
    create_env_file()
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
