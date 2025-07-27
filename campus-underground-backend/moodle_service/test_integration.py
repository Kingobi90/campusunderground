#!/usr/bin/env python3
"""
Test script for Moodle integration in Campus Underground
This script tests the Moodle client and API server to ensure they're working correctly.
"""

import os
import sys
import json
import logging
import requests
import time
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_integration_test')

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client_new import MoodleAPIClient
from config import config

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str) -> None:
    """Print a header with color."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_result(name: str, result: bool, message: str = "") -> None:
    """Print a test result with color."""
    status = f"{Colors.GREEN}PASS{Colors.ENDC}" if result else f"{Colors.RED}FAIL{Colors.ENDC}"
    print(f"{name.ljust(40)} [{status}] {message}")

def test_moodle_client() -> bool:
    """Test the Moodle client directly."""
    print_header("Testing Moodle Client")
    
    all_passed = True
    
    # Test with mock data
    try:
        client = MoodleAPIClient(use_mock_data=True)
        print_result("Initialize mock client", True)
    except Exception as e:
        print_result("Initialize mock client", False, str(e))
        all_passed = False
        return all_passed
    
    # Test site info
    try:
        site_info = client.get_site_info()
        print_result("Get site info", True, f"Site name: {site_info.get('sitename', 'Unknown')}")
    except Exception as e:
        print_result("Get site info", False, str(e))
        all_passed = False
    
    # Test get courses
    try:
        courses = client.get_courses(1)
        print_result("Get courses", True, f"Found {len(courses)} courses")
    except Exception as e:
        print_result("Get courses", False, str(e))
        all_passed = False
    
    # Test get course contents
    try:
        if courses:
            course_id = courses[0]['id']
            contents = client.get_course_contents(course_id)
            print_result("Get course contents", True, f"Found content for course {course_id}")
        else:
            print_result("Get course contents", False, "No courses found to test with")
            all_passed = False
    except Exception as e:
        print_result("Get course contents", False, str(e))
        all_passed = False
    
    # Test get assignments
    try:
        if courses:
            course_id = courses[0]['id']
            assignments = client.get_assignments(course_id, 1)
            print_result("Get assignments", True, f"Found {len(assignments)} assignments")
        else:
            print_result("Get assignments", False, "No courses found to test with")
            all_passed = False
    except Exception as e:
        print_result("Get assignments", False, str(e))
        all_passed = False
    
    # Test get grades
    try:
        if courses:
            course_id = courses[0]['id']
            grades = client.get_user_grades(1, course_id)
            print_result("Get grades", True, f"Found {len(grades)} grade items")
        else:
            print_result("Get grades", False, "No courses found to test with")
            all_passed = False
    except Exception as e:
        print_result("Get grades", False, str(e))
        all_passed = False
    
    # Test get calendar events
    try:
        events = client.get_calendar_events()
        print_result("Get calendar events", True, f"Found {len(events)} events")
    except Exception as e:
        print_result("Get calendar events", False, str(e))
        all_passed = False
    
    # Test analytics
    try:
        distribution = client.get_grade_distribution(1)
        print_result("Get grade distribution", True, f"Found {len(distribution)} grade categories")
    except Exception as e:
        print_result("Get grade distribution", False, str(e))
        all_passed = False
    
    try:
        overview = client.get_performance_overview(1)
        print_result("Get performance overview", True, f"Found {len(overview)} performance metrics")
    except Exception as e:
        print_result("Get performance overview", False, str(e))
        all_passed = False
    
    return all_passed

def test_api_server(base_url: str = "http://localhost:5002") -> bool:
    """Test the API server."""
    print_header("Testing API Server")
    
    all_passed = True
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print_result("API server health check", True, "Server is running")
        else:
            print_result("API server health check", False, f"Status code: {response.status_code}")
            all_passed = False
            return all_passed
    except Exception as e:
        print_result("API server health check", False, f"Server not running: {str(e)}")
        print(f"\n{Colors.YELLOW}Please start the API server with: python api_server_new.py{Colors.ENDC}\n")
        all_passed = False
        return all_passed
    
    # Test connection
    try:
        response = requests.get(f"{base_url}/api/test-connection", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result("Test connection", True, f"Using {'mock' if data.get('useMockData') else 'real'} data")
            else:
                print_result("Test connection", False, data.get('error', 'Unknown error'))
                all_passed = False
        else:
            print_result("Test connection", False, f"Status code: {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result("Test connection", False, str(e))
        all_passed = False
    
    # Test get courses
    try:
        response = requests.get(
            f"{base_url}/api/courses",
            headers={"user-id": "1"},
            timeout=5
        )
        if response.status_code == 200:
            courses = response.json()
            print_result("Get courses API", True, f"Found {len(courses)} courses")
        else:
            print_result("Get courses API", False, f"Status code: {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result("Get courses API", False, str(e))
        all_passed = False
    
    # Test course contents
    if 'courses' in locals() and courses:
        try:
            course_id = courses[0]['id']
            response = requests.get(
                f"{base_url}/api/courses/{course_id}/contents",
                headers={"user-id": "1"},
                timeout=5
            )
            if response.status_code == 200:
                contents = response.json()
                print_result("Get course contents API", True, f"Found content for course {course_id}")
            else:
                print_result("Get course contents API", False, f"Status code: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_result("Get course contents API", False, str(e))
            all_passed = False
    
    # Test assignments
    if 'courses' in locals() and courses:
        try:
            course_id = courses[0]['id']
            response = requests.get(
                f"{base_url}/api/courses/{course_id}/assignments",
                headers={"user-id": "1"},
                timeout=5
            )
            if response.status_code == 200:
                assignments = response.json()
                print_result("Get assignments API", True, f"Found {len(assignments)} assignments")
            else:
                print_result("Get assignments API", False, f"Status code: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_result("Get assignments API", False, str(e))
            all_passed = False
    
    # Test grades
    if 'courses' in locals() and courses:
        try:
            course_id = courses[0]['id']
            response = requests.get(
                f"{base_url}/api/courses/{course_id}/grades",
                headers={"user-id": "1"},
                timeout=5
            )
            if response.status_code == 200:
                grades = response.json()
                print_result("Get grades API", True, f"Found {len(grades)} grade items")
            else:
                print_result("Get grades API", False, f"Status code: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_result("Get grades API", False, str(e))
            all_passed = False
    
    # Test calendar events
    try:
        response = requests.get(
            f"{base_url}/api/calendar-events",
            headers={"user-id": "1"},
            timeout=5
        )
        if response.status_code == 200:
            events = response.json()
            print_result("Get calendar events API", True, f"Found {len(events)} events")
        else:
            print_result("Get calendar events API", False, f"Status code: {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result("Get calendar events API", False, str(e))
        all_passed = False
    
    # Test analytics
    try:
        response = requests.get(
            f"{base_url}/api/analytics/grade-distribution",
            headers={"user-id": "1"},
            timeout=5
        )
        if response.status_code == 200:
            distribution = response.json()
            print_result("Get grade distribution API", True, f"Found {len(distribution)} grade categories")
        else:
            print_result("Get grade distribution API", False, f"Status code: {response.status_code}")
            all_passed = False
    except Exception as e:
        print_result("Get grade distribution API", False, str(e))
        all_passed = False
    
    return all_passed

def main():
    """Main function to run tests."""
    print_header("Campus Underground Moodle Integration Test")
    
    # Print configuration
    print(f"{Colors.BLUE}{Colors.BOLD}Configuration:{Colors.ENDC}")
    print(f"Moodle URL: {config.get('MOODLE_URL')}")
    print(f"Using Mock Data: {config.get('USE_MOCK_DATA')}")
    print(f"API Port: {config.get('PORT')}")
    print()
    
    # Test Moodle client
    client_passed = test_moodle_client()
    
    # Test API server
    server_passed = test_api_server(f"http://localhost:{config.get('PORT')}")
    
    # Print summary
    print_header("Test Summary")
    print(f"Moodle Client Tests: {'PASSED' if client_passed else 'FAILED'}")
    print(f"API Server Tests: {'PASSED' if server_passed else 'FAILED'}")
    print()
    
    if client_passed and server_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! The Moodle integration is working correctly.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed. Please check the output above for details.{Colors.ENDC}")
    
    print("\nNext steps:")
    print("1. Rename api_server_new.py to api_server.py to replace the old implementation")
    print("2. Rename moodle_client_new.py to moodle_client.py to replace the old implementation")
    print("3. Rename moodleService_new.ts to moodleService.ts in the frontend")
    print("4. Test the full integration with the frontend")

if __name__ == "__main__":
    main()
