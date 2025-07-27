#!/usr/bin/env python3
"""
Moodle API Client for Campus Underground
This module provides a client for interacting with Moodle's web services API.
"""

import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import tempfile
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_client')

# Load environment variables
load_dotenv()

# Database integration
from database import MoodleDatabase


class MoodleAPIClient:
    """Client for interacting with Moodle's Web Services API."""
    
    def __init__(self, use_mock_data=False):
        """
        Initialize the Moodle API client.
        
        Args:
            use_mock_data: Parameter kept for backward compatibility but no longer used
        """
        self.base_url = os.getenv('MOODLE_URL', 'https://moodle.concordia.ca')
        self.token = os.getenv('MOODLE_API_TOKEN', '')
        
        # Initialize database connection
        self.db = MoodleDatabase()
        
        # Clean up base URL
        self.base_url = self.base_url.rstrip('/')
        
        # Set up REST endpoint URL
        self.rest_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        logger.info(f"Moodle API client initialized with base URL: {self.base_url}")
        
    def _call_api(self, wsfunction: str, **params) -> Dict[str, Any]:
        """
        Make a request to the Moodle API.
        
        Args:
            wsfunction: The Moodle web service function to call
            **params: Additional parameters for the API call
            
        Returns:
            API response as a dictionary
            
        Raises:
            MoodleAPIError: If the API call fails
        """
        
        # Prepare request parameters
        request_params = {
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': wsfunction,
            **params
        }
        
        try:
            logger.debug(f"Making API call to {wsfunction} with params: {params}")
            response = requests.get(self.rest_endpoint, params=request_params, timeout=30)
            response.raise_for_status()
            
            # Check for API errors in the response
            data = response.json()
            if isinstance(data, dict) and 'exception' in data:
                error_message = data.get('message', 'Unknown Moodle API error')
                logger.error(f"Moodle API error: {error_message}")
                raise MoodleAPIError(f"Moodle API error: {error_message}")
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise MoodleAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise MoodleAPIError(f"Invalid JSON response: {str(e)}")
    
    def validate_token(self) -> bool:
        """
        Validate the Moodle API token by making a simple API call.
        
        Returns:
            True if the token is valid, False otherwise
        """
        if self.use_mock_data:
            return True
            
        try:
            site_info = self.get_site_info()
            return 'userid' in site_info
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_site_info(self) -> Dict[str, Any]:
        """
        Get information about the Moodle site.
        
        Returns:
            Site information including version, user details, etc.
        """
        return self._call_api("core_webservice_get_site_info")
    
    def get_courses(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the list of courses the user is enrolled in.
        
        Args:
            user_id: The ID of the user to get courses for
            
        Returns:
            List of course information
        """
        if not user_id and not self.use_mock_data:
            site_info = self.get_site_info()
            user_id = site_info.get('userid')
            
        # Use default user ID for mock data
        if not user_id:
            user_id = 1
            
        courses = self._call_api("core_enrol_get_users_courses", userid=user_id)
        
        # Transform the response to match the expected format
        for course in courses:
            # Add progress if not present (used by frontend)
            if 'progress' not in course:
                course['progress'] = random.randint(60, 95) if self.use_mock_data else 0
                
        return courses
    
    def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get the contents of a specific course.
        
        Args:
            course_id: The ID of the course
            
        Returns:
            List of course sections with their contents
        """
        return self._call_api("core_course_get_contents", courseid=course_id)
    
    def get_assignments(self, course_id: Optional[int] = None, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get assignments for a specific course or all courses.
        
        Args:
            course_id: Optional course ID to filter assignments
            user_id: Optional user ID to get assignments for
            
        Returns:
            List of assignments in a format compatible with the frontend
        """
        # Get assignments from Moodle API
        params = {}
        if course_id:
            params['courseids'] = [course_id]
            
        response = self._call_api("mod_assign_get_assignments", **params)
        
        # Process the response to match the frontend expected format
        assignments = []
        
        # Moodle returns assignments grouped by course
        for course in response.get('courses', []):
            course_id = course.get('id')
            
            for assign in course.get('assignments', []):
                # Map Moodle assignment fields to our frontend format
                assignment = {
                    'id': assign.get('id'),
                    'name': assign.get('name'),
                    'duedate': assign.get('duedate'),
                    'course': course_id,
                }
                
                # Add status based on due date
                now = int(time.time())
                if assign.get('duedate') < now:
                    assignment['status'] = 'overdue'
                else:
                    assignment['status'] = 'pending'
                    
                assignments.append(assignment)
                
        # Filter by course_id if specified
        if course_id:
            assignments = [a for a in assignments if a['course'] == course_id]
            
        return assignments
    
    def get_user_grades(self, user_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get grades for a specific user and course.
        
        Args:
            user_id: The ID of the user
            course_id: Optional course ID to filter grades
            
        Returns:
            List of grade items in a format compatible with the frontend
        """
        params = {
            'userid': user_id
        }
        
        if course_id:
            params['courseid'] = course_id
            
        response = self._call_api("gradereport_user_get_grade_items", **params)
        
        # Process the response to match the frontend expected format
        grades = []
        
        # Extract grade items from the response
        for usergrade in response.get('usergrades', []):
            course_id = usergrade.get('courseid')
            
            for item in usergrade.get('gradeitems', []):
                # Map Moodle grade fields to our frontend format
                grade = {
                    'id': item.get('id'),
                    'itemname': item.get('itemname'),
                    'itemmodule': item.get('itemtype', 'unknown'),
                    'iteminstance': item.get('iteminstance', 0),
                    'rawgrade': item.get('graderaw'),
                    'rawgrademax': item.get('grademax', 100),
                    'rawgrademin': item.get('grademin', 0),
                }
                
                # Add feedback if available
                if 'feedback' in item:
                    grade['feedback'] = item['feedback']
                    
                grades.append(grade)
                
        # Filter by course_id if specified
        if course_id:
            grades = [g for g in grades if g.get('courseid') == course_id]
            
        return grades
    
    def get_calendar_events(self, 
                           events_from: Optional[str] = None, 
                           events_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get calendar events within a specified time range.
        
        Args:
            events_from: Start timestamp
            events_to: End timestamp
            
        Returns:
            Dictionary containing events and warnings
        """
        params = {}
        if events_from:
            params["timestart"] = events_from
        if events_to:
            params["timeend"] = events_to
            
        return self._call_api("core_calendar_get_calendar_events", **params)
    
    def download_file(self, file_url: str) -> Dict[str, Any]:
        """
        Download a file from Moodle.
        
        Args:
            file_url: URL of the file to download
            
        Returns:
            Dictionary with file content, content type, and filename
        """
        if self.use_mock_data:
            return self.mock_data.get_mock_file()
            
        try:
            # Add token to URL if needed
            if '?' in file_url:
                file_url += f"&token={self.token}"
            else:
                file_url += f"?token={self.token}"
                
            response = requests.get(file_url, timeout=60)
            response.raise_for_status()
            
            # Try to get filename from content-disposition header
            filename = None
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                import re
                filename_match = re.search(r'filename="(.+?)"', content_disposition)
                if filename_match:
                    filename = filename_match.group(1)
            
            # Fallback filename
            if not filename:
                filename = file_url.split('/')[-1].split('?')[0]
                
            return {
                'content': response.content,
                'content_type': response.headers.get('content-type', 'application/octet-stream'),
                'filename': filename
            }
            
        except requests.RequestException as e:
            logger.error(f"File download failed: {e}")
            return {'error': str(e)}
            
    def get_grade_distribution(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get grade distribution for analytics.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Grade distribution data
        """
        if self.use_mock_data:
            return self.mock_data.get_grade_distribution()
            
        # This is a custom analytics function that needs to be calculated
        # from the raw grade data
        try:
            # Get all user grades
            grades_data = self.get_user_grades(user_id)
            
            # Calculate grade distribution
            distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
            
            for grade in grades_data:
                if 'rawgrade' not in grade or grade['rawgrade'] is None:
                    continue
                    
                percentage = (float(grade['rawgrade']) / float(grade['rawgrademax'])) * 100
                
                if percentage >= 90:
                    distribution['A'] += 1
                elif percentage >= 80:
                    distribution['B'] += 1
                elif percentage >= 70:
                    distribution['C'] += 1
                elif percentage >= 60:
                    distribution['D'] += 1
                else:
                    distribution['F'] += 1
            
            # Format for frontend
            result = []
            colors = {
                'A': 'hsl(120, 70%, 50%)',
                'B': 'hsl(180, 70%, 50%)',
                'C': 'hsl(240, 70%, 50%)',
                'D': 'hsl(300, 70%, 50%)',
                'F': 'hsl(0, 70%, 50%)'
            }
            
            for grade, count in distribution.items():
                result.append({
                    'id': grade,
                    'label': grade,
                    'value': count,
                    'color': colors[grade]
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating grade distribution: {e}")
            # Fall back to mock data
            return self.mock_data.get_grade_distribution()
            
    def get_performance_overview(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get performance overview for analytics.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Performance overview data
        """
        if self.use_mock_data:
            return self.mock_data.get_performance_overview()
            
        # This is a custom analytics function that needs to be calculated
        # from the raw grade data
        try:
            # Get all user grades
            grades_data = self.get_user_grades(user_id)
            
            # Group grades by module type
            modules = {}
            
            for grade in grades_data:
                if 'rawgrade' not in grade or grade['rawgrade'] is None:
                    continue
                    
                module = grade.get('itemmodule', 'other')
                if module not in modules:
                    modules[module] = []
                    
                percentage = (float(grade['rawgrade']) / float(grade['rawgrademax'])) * 100
                modules[module].append(percentage)
            
            # Calculate average for each module type
            result = []
            colors = [
                'hsl(120, 70%, 50%)',
                'hsl(180, 70%, 50%)',
                'hsl(240, 70%, 50%)',
                'hsl(300, 70%, 50%)',
                'hsl(0, 70%, 50%)'
            ]
            
            for i, (module, percentages) in enumerate(modules.items()):
                if not percentages:
                    continue
                    
                avg = sum(percentages) / len(percentages)
                
                # Map module types to more user-friendly names
                module_name = {
                    'assign': 'Assignments',
                    'quiz': 'Quizzes',
                    'forum': 'Participation',
                    'workshop': 'Projects',
                    'exam': 'Exams'
                }.get(module, module.capitalize())
                
                result.append({
                    'taste': module_name,  # Using 'taste' to match frontend expectation
                    'chardonay': round(avg, 1),  # Using 'chardonay' to match frontend
                    'color': colors[i % len(colors)]
                })
                
            return result
            
        except Exception as e:
            logger.error(f"Error calculating performance overview: {e}")
            # Fall back to mock data
            return self.mock_data.get_performance_overview()


class MoodleAPIError(Exception):
    """Exception raised for Moodle API errors."""
    pass


# For testing
if __name__ == "__main__":
    client = MoodleAPIClient(use_mock_data=True)
    print("Testing Moodle API client...")
    print("Site info:", client.get_site_info())
    print("Courses:", client.get_courses())
