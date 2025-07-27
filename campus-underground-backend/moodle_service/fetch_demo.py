#!/usr/bin/env python3
"""
Demo script to fetch courses and slides from Moodle API
"""

import os
import json
import requests
import dotenv
import sys

# Load environment variables
dotenv.load_dotenv()

def main():
    print("Initializing direct Moodle API connection...")
    
    # Get API credentials from environment
    moodle_url = os.getenv('MOODLE_URL', 'https://moodle.concordia.ca')
    token = os.getenv('MOODLE_API_TOKEN')
    
    if not token or token == 'your_moodle_api_token_here':
        print("Error: No valid Moodle API token found in .env file")
        sys.exit(1)
    
    # Ensure URL doesn't have double slashes
    if moodle_url.endswith('/'):
        moodle_url = moodle_url[:-1]
        
    print(f"Using Moodle URL: {moodle_url}")
    print(f"Using token: {token[:5]}...{token[-5:]} (length: {len(token)})")
    
    # Base parameters for all requests
    base_params = {
        "wstoken": token,
        "moodlewsrestformat": "json"
    }
    
    # Function to make API requests
    def make_request(function_name, params=None, attempt=1):
        request_params = base_params.copy()
        request_params["wsfunction"] = function_name
        
        if params:
            request_params.update(params)
        
        # Try different URL formats
        if attempt == 1:
            url = f"{moodle_url}/webservice/rest/server.php"
        elif attempt == 2:
            url = f"{moodle_url}/moodle/webservice/rest/server.php"
        else:
            url = f"{moodle_url}/moodle/webservice/rest/server.php"
            # Try with different parameter format
            request_params = {
                "wstoken": token,
                "wsfunction": function_name,
                "moodlewsrestformat": "json"
            }
            if params:
                request_params.update(params)
        
        print(f"Attempt {attempt}: Making request to: {url}")
        print(f"Parameters: {request_params}")
        
        try:
            response = requests.get(url, params=request_params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            
            # Try alternative URL formats if this is the first or second attempt
            if attempt < 3:
                print(f"Trying alternative URL format (attempt {attempt+1})...")
                return make_request(function_name, params, attempt+1)
            
            return {"error": str(e)}
    
    # First, get site info to verify connection
    print("\n===== VERIFYING API CONNECTION =====")
    print("This will test if your Moodle API token is valid and if the server is accessible.")
    site_info = make_request("core_webservice_get_site_info")
    if "error" in site_info:
        print(f"Error connecting to Moodle API: {site_info['error']}")
        sys.exit(1)
    else:
        print(f"Connected to: {site_info.get('sitename', 'Unknown Moodle site')}")
        print(f"Logged in as: {site_info.get('fullname', 'Unknown user')}")
        user_id = site_info.get('userid')
        print(f"User ID: {user_id}")
    
    print("\n===== FETCHING USER COURSES =====")
    courses = make_request("core_enrol_get_users_courses", {"userid": user_id})
    
    if isinstance(courses, list):
        print(f"Found {len(courses)} courses:")
        for course in courses:
            print(f"  - {course.get('fullname', 'Unknown')} (ID: {course.get('id', 'Unknown')})")
        
        # Print full course data
        print("\nDetailed course data:")
        print(json.dumps(courses, indent=2))
        
        # If we have courses, fetch contents for the first one
        if courses:
            first_course = courses[0]
            course_id = first_course['id']
            course_name = first_course['fullname']
            
            print(f"\n===== FETCHING CONTENTS FOR COURSE: {course_name} (ID: {course_id}) =====")
            contents = make_request("core_course_get_contents", {"courseid": course_id})
            
            if isinstance(contents, list):
                print(f"Found {len(contents)} sections")
                
                # Extract and list all slides/resources
                print("\n===== LIST OF ALL SLIDES/RESOURCES =====")
                resource_count = 0
                for section in contents:
                    print(f"\nSection: {section['name']}")
                    for module in section.get('modules', []):
                        if module.get('modname') == 'resource':
                            resource_count += 1
                            print(f"  - {module['name']}")
                            for content in module.get('contents', []):
                                if content.get('type') == 'file':
                                    print(f"    * {content['filename']} ({content['filesize']} bytes)")
                                    print(f"      URL: {content['fileurl']}")
                
                if resource_count == 0:
                    print("No resources/slides found in this course.")
            else:
                print(f"Error fetching course contents: {contents}")
    else:
        print(f"Error fetching courses: {courses}")

if __name__ == "__main__":
    main()
