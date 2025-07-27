#!/usr/bin/env python3
"""
Test script for the Moodle API client
This script tests the basic functionality of the Moodle API client
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from moodle_client import MoodleAPIClient

# Load environment variables
load_dotenv()

def print_json(data):
    """Print JSON data in a readable format"""
    print(json.dumps(data, indent=2))

def test_client():
    """Test the Moodle API client"""
    try:
        # Initialize the client
        print("Initializing Moodle API client...")
        client = MoodleAPIClient()
        
        # Test site info
        print("\n=== Testing Site Info ===")
        site_info = client.get_site_info()
        print(f"Connected to {site_info.get('sitename', 'Moodle')} as {site_info.get('fullname', 'User')}")
        print(f"Moodle version: {site_info.get('release', 'Unknown')}")
        
        # Test available functions
        print("\n=== Testing Available Functions ===")
        functions = [
            "core_webservice_get_site_info",
            "core_enrol_get_users_courses",
            "core_course_get_contents",
            "mod_assign_get_assignments",
            "gradereport_user_get_grade_items"
        ]
        
        for func in functions:
            available = client.is_function_available(func)
            print(f"Function {func}: {'Available' if available else 'Not available'}")
        
        # Test getting courses
        print("\n=== Testing Get Courses ===")
        user_id = site_info.get("userid")
        courses = client.get_courses(user_id)
        print(f"Found {len(courses)} courses")
        if courses:
            print("First course:")
            print_json(courses[0])
            
            # Test getting course contents
            print("\n=== Testing Get Course Contents ===")
            course_id = courses[0]["id"]
            contents = client.get_course_contents(course_id)
            print(f"Found {len(contents)} sections in course {courses[0]['fullname']}")
            if contents:
                print("First section:")
                print_json({
                    "name": contents[0].get("name"),
                    "summary": contents[0].get("summary"),
                    "modules_count": len(contents[0].get("modules", []))
                })
            
            # Test getting assignments
            print("\n=== Testing Get Assignments ===")
            assignments = client.get_assignments(course_id)
            print_json(assignments)
            
            # Test getting grades
            print("\n=== Testing Get Grades ===")
            grades = client.get_user_grades(user_id, course_id)
            print_json(grades)
            
            # Test analytics
            print("\n=== Testing Analytics ===")
            grade_distribution = client.get_grade_distribution(user_id)
            print("Grade Distribution:")
            print_json(grade_distribution)
            
            performance = client.get_performance_overview(user_id)
            print("Performance Overview:")
            print_json(performance)
        
        print("\n=== All tests completed successfully ===")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("\nTest failed. Please check your Moodle API token and configuration.")
        return False

if __name__ == "__main__":
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        print(f"Error: .env file not found at {env_file}")
        print("Please create a .env file with your Moodle API token.")
        sys.exit(1)
    
    # Run the test
    success = test_client()
    sys.exit(0 if success else 1)
