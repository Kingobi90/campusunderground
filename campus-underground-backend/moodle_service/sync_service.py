#!/usr/bin/env python3
"""
Moodle Sync Service
This module provides functionality to sync data from Moodle API to the local database.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from moodle_client_new import MoodleAPIClient
from database import MoodleDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_sync_service')

class MoodleSyncService:
    """
    Service for syncing data from Moodle API to the local database.
    """
    
    def __init__(self, client: MoodleAPIClient = None, db: MoodleDatabase = None):
        """
        Initialize the sync service.
        
        Args:
            client: MoodleAPIClient instance
            db: MoodleDatabase instance
        """
        self.client = client or MoodleAPIClient()
        self.db = db or MoodleDatabase()
    
    def sync_all(self, user_id: int) -> Dict[str, Any]:
        """
        Sync all data for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage)
            
        Returns:
            Dictionary with sync status information
        """
        start_time = datetime.now()
        errors = []
        details = {}
        
        # Sync courses
        try:
            courses_result = self.sync_courses(user_id)
            details['courses'] = courses_result
        except Exception as e:
            logger.error(f"Error syncing courses: {e}")
            errors.append(f"Error syncing courses: {str(e)}")
        
        # Sync assignments
        try:
            assignments_result = self.sync_assignments(user_id)
            details['assignments'] = assignments_result
        except Exception as e:
            logger.error(f"Error syncing assignments: {e}")
            errors.append(f"Error syncing assignments: {str(e)}")
        
        # Sync grades
        try:
            grades_result = self.sync_grades(user_id)
            details['grades'] = grades_result
        except Exception as e:
            logger.error(f"Error syncing grades: {e}")
            errors.append(f"Error syncing grades: {str(e)}")
        
        # Sync resources
        try:
            resources_result = self.sync_resources(user_id)
            details['resources'] = resources_result
        except Exception as e:
            logger.error(f"Error syncing resources: {e}")
            errors.append(f"Error syncing resources: {str(e)}")
        
        # Sync calendar events
        try:
            calendar_result = self.sync_calendar_events(user_id)
            details['calendar'] = calendar_result
        except Exception as e:
            logger.error(f"Error syncing calendar events: {e}")
            errors.append(f"Error syncing calendar events: {str(e)}")
        
        # Sync analytics
        try:
            analytics_result = self.sync_analytics(user_id)
            details['analytics'] = analytics_result
        except Exception as e:
            logger.error(f"Error syncing analytics: {e}")
            errors.append(f"Error syncing analytics: {str(e)}")
        
        end_time = datetime.now()
        sync_time = (end_time - start_time).total_seconds()
        
        return {
            'success': len(errors) == 0,
            'message': f"Sync completed with {len(errors)} errors" if errors else "Sync completed successfully",
            'errors': errors,
            'details': details,
            'sync_time': sync_time
        }
    
    def sync_courses(self, user_id: int) -> Dict[str, Any]:
        """
        Sync courses for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            
        Returns:
            Dictionary with sync status information
        """
        try:
            # Get site info to get the authenticated Moodle user ID
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            
            logger.info(f"Using Moodle authenticated user ID: {moodle_user_id}")
            
            # Get courses from Moodle API using the authenticated user ID
            courses = self.client.get_courses(moodle_user_id)
            
            # Debug logging
            logger.info(f"Retrieved {len(courses)} courses from Moodle API: {courses}")
            
            # Save to database using the frontend user ID for storage
            self.db.save_courses(courses, user_id)
            
            return {
                'success': True,
                'count': len(courses)
            }
        except Exception as e:
            logger.error(f"Error syncing courses: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def sync_assignments(self, user_id: int) -> Dict[str, Any]:
        """
        Sync assignments for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            
        Returns:
            Dictionary with sync status information
        """
        try:
            # Get site info to get the authenticated Moodle user ID
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            
            # Get courses from database
            courses = self.db.get_courses(user_id)
            
            all_assignments = []
            
            # For each course, get assignments
            for course in courses:
                course_id = course.get('id')
                
                # Get assignments for this course
                assignments = self.client.get_assignments(course_id, moodle_user_id)
                all_assignments.extend(assignments)
            
            # Save to database
            self.db.save_assignments(all_assignments, user_id)
            
            return {
                'success': True,
                'count': len(all_assignments)
            }
        except Exception as e:
            logger.error(f"Error syncing assignments: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def sync_grades(self, user_id: int) -> Dict[str, Any]:
        """
        Sync grades for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            
        Returns:
            Dictionary with sync status information
        """
        try:
            # Get site info to get the authenticated Moodle user ID
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            
            # Get courses from database
            courses = self.db.get_courses(user_id)
            
            all_grades_count = 0
            
            # For each course, get grades and save them per course
            for course in courses:
                course_id = course.get('id')
                
                # Get grades for this course
                if hasattr(self.client, 'get_grades'):
                    grades = self.client.get_grades(course_id, moodle_user_id)
                    if grades:
                        # Save grades for this course
                        self.db.save_grades(grades, course_id, user_id)
                        all_grades_count += len(grades)
                else:
                    logger.warning(f"get_grades method not implemented in MoodleAPIClient, skipping for course {course_id}")
            
            return {
                'success': True,
                'count': all_grades_count
            }
        except Exception as e:
            logger.error(f"Error syncing grades: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def sync_resources(self, user_id: int) -> Dict[str, Any]:
        """
        Sync resources for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            
        Returns:
            Dictionary with sync status information
        """
        try:
            # Get site info to get the authenticated Moodle user ID
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            
            # Get courses from database
            courses = self.db.get_courses(user_id)
            
            all_resources_count = 0
            
            # For each course, get resources and save them per course
            for course in courses:
                course_id = course.get('id')
                
                # Get resources for this course
                if hasattr(self.client, 'get_resources'):
                    resources = self.client.get_resources(course_id)
                    if resources:
                        # Save resources for this course
                        self.db.save_resources(resources, course_id, user_id)
                        all_resources_count += len(resources)
                else:
                    logger.warning(f"get_resources method not implemented in MoodleAPIClient, skipping for course {course_id}")
            
            return {
                'success': True,
                'count': all_resources_count
            }
        except Exception as e:
            logger.error(f"Error syncing resources: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def sync_calendar_events(self, user_id: int, from_time: str = None, to_time: str = None) -> Dict[str, Any]:
        """
        Sync calendar events for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            from_time: Optional start time
            to_time: Optional end time
            
        Returns:
            Dictionary with sync status information
        """
        try:
            # Get site info to get the authenticated Moodle user ID
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            
            # Check if the client has the method
            if not hasattr(self.client, 'get_calendar_events'):
                logger.warning("get_calendar_events method not implemented in MoodleAPIClient")
                return {
                    'success': False,
                    'error': "Calendar events sync not implemented",
                    'count': 0
                }
            
            # Get calendar events from Moodle API
            # Note: The client method doesn't take a user_id parameter
            events_data = self.client.get_calendar_events(from_time, to_time)
            
            # Extract the events from the response
            # The Moodle API returns a dict with 'events' key containing the actual events
            if isinstance(events_data, dict) and 'events' in events_data:
                events = events_data['events']
                logger.info(f"Retrieved {len(events)} calendar events from Moodle API")
                
                # Save to database
                self.db.save_calendar_events(events, user_id)
            else:
                logger.warning(f"Unexpected calendar events data structure: {type(events_data)}")
                events = []
                return {
                    'success': False,
                    'error': "Unexpected calendar events data structure",
                    'count': 0
                }
            
            return {
                'success': True,
                'count': len(events)
            }
        except Exception as e:
            logger.error(f"Error syncing calendar events: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def sync_analytics(self, user_id: int) -> Dict[str, Any]:
        """
        Sync analytics data for a user.
        
        Args:
            user_id: User ID from frontend (used for database storage only)
            
        Returns:
            Dictionary with sync status information
        """
        results = {}
        
        # Get site info to get the authenticated Moodle user ID
        try:
            site_info = self.client.get_site_info()
            moodle_user_id = site_info.get('userid')
            logger.info(f"Using Moodle authenticated user ID for analytics: {moodle_user_id}")
        except Exception as e:
            logger.error(f"Error getting Moodle user ID: {e}")
            moodle_user_id = None
        
        # Sync grade trends
        try:
            if not hasattr(self.client, 'get_grade_trends'):
                logger.warning("get_grade_trends method not implemented in MoodleAPIClient")
                results['grade_trends'] = {
                    'success': False,
                    'error': "Grade trends sync not implemented"
                }
            else:
                grade_trends = self.client.get_grade_trends(moodle_user_id)
                self.db.save_grade_trends(grade_trends, user_id)
                results['grade_trends'] = {
                    'success': True,
                    'count': len(grade_trends)
                }
        except Exception as e:
            logger.error(f"Error syncing grade trends: {e}")
            results['grade_trends'] = {
                'success': False,
                'error': str(e)
            }
        
        # Sync completion rates
        try:
            if not hasattr(self.client, 'get_completion_rates'):
                logger.warning("get_completion_rates method not implemented in MoodleAPIClient")
                results['completion_rates'] = {
                    'success': False,
                    'error': "Completion rates sync not implemented"
                }
            else:
                completion_rates = self.client.get_completion_rates(moodle_user_id)
                self.db.save_completion_rates(completion_rates, user_id)
                results['completion_rates'] = {
                    'success': True,
                    'count': len(completion_rates)
                }
        except Exception as e:
            logger.error(f"Error syncing completion rates: {e}")
            results['completion_rates'] = {
                'success': False,
                'error': str(e)
            }
        
        # Sync grade distribution
        try:
            if not hasattr(self.client, 'get_grade_distribution'):
                logger.warning("get_grade_distribution method not implemented in MoodleAPIClient")
                results['grade_distribution'] = {
                    'success': False,
                    'error': "Grade distribution sync not implemented"
                }
            else:
                grade_distribution = self.client.get_grade_distribution(moodle_user_id)
                self.db.save_grade_distribution(grade_distribution, user_id)
                results['grade_distribution'] = {
                    'success': True,
                    'count': len(grade_distribution)
                }
        except Exception as e:
            logger.error(f"Error syncing grade distribution: {e}")
            results['grade_distribution'] = {
                'success': False,
                'error': str(e)
            }
        
        # Sync performance overview
        try:
            if not hasattr(self.client, 'get_performance_overview'):
                logger.warning("get_performance_overview method not implemented in MoodleAPIClient")
                results['performance_overview'] = {
                    'success': False,
                    'error': "Performance overview sync not implemented"
                }
            else:
                performance_overview = self.client.get_performance_overview(moodle_user_id)
                self.db.save_performance_overview(performance_overview, user_id)
                results['performance_overview'] = {
                    'success': True,
                    'count': len(performance_overview)
                }
        except Exception as e:
            logger.error(f"Error syncing performance overview: {e}")
            results['performance_overview'] = {
                'success': False,
                'error': str(e)
            }
        
        return results
