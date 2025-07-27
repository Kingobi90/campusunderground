#!/usr/bin/env python3
"""
Test script for Moodle API Client
This script tests the Moodle API client's ability to retrieve courses.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_client_test')

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client_new import MoodleAPIClient, MoodleAPIError

# Load environment variables
load_dotenv()

def test_get_courses():
    """Test retrieving courses from Moodle API."""
    try:
        # Initialize the client
        client = MoodleAPIClient()
        
        # Get site info to verify connection
        logger.info("Testing connection to Moodle API...")
        site_info = client.get_site_info()
        logger.info(f"Connected to Moodle site: {site_info.get('sitename')}")
        logger.info(f"User ID from site info: {site_info.get('userid')}")
        
        # Get courses for the authenticated user
        logger.info("Retrieving courses for authenticated user...")
        courses = client.get_courses()
        logger.info(f"Retrieved {len(courses)} courses")
        
        # Print course details
        for i, course in enumerate(courses):
            logger.info(f"Course {i+1}: {course.get('fullname')} (ID: {course.get('id')})")
        
        # Try with explicit user ID
        user_id = site_info.get('userid')
        logger.info(f"Retrieving courses for user ID {user_id}...")
        courses = client.get_courses(user_id)
        logger.info(f"Retrieved {len(courses)} courses with explicit user ID")
        
        # Try with user ID 1 (test case)
        logger.info("Retrieving courses for user ID 1...")
        courses = client.get_courses(1)
        logger.info(f"Retrieved {len(courses)} courses for user ID 1")
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_get_courses()
    if success:
        logger.info("Test completed successfully")
        sys.exit(0)
    else:
        logger.error("Test failed")
        sys.exit(1)
