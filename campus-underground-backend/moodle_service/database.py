#!/usr/bin/env python3
"""
Database module for Moodle API data caching
This module provides database functionality for storing and retrieving Moodle data.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_database')

class MoodleDatabase:
    """Database manager for Moodle API data caching."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            # Use a default path in the same directory as this file
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'moodle_cache.db')
        
        self.db_path = db_path
        self._initialize_db()
    
    def _get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """
        Get a database connection and cursor.
        
        Returns:
            Tuple of (connection, cursor)
        """
        conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Configure connection to return dictionaries
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        return conn, cursor
    
    def _initialize_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        conn, cursor = self._get_connection()
        
        try:
            # Create metadata table to track last sync time
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create courses table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                shortname TEXT,
                fullname TEXT,
                summary TEXT,
                progress REAL,
                startdate INTEGER,
                enddate INTEGER,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id, user_id)
            )
            ''')
            
            # Create assignments table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                duedate INTEGER,
                course_id INTEGER,
                grade REAL,
                maxgrade REAL,
                status TEXT,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(id, user_id)
            )
            ''')
            
            # Create grades table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                itemname TEXT,
                itemmodule TEXT,
                iteminstance INTEGER,
                rawgrade REAL,
                rawgrademax REAL,
                rawgrademin REAL,
                feedback TEXT,
                course_id INTEGER,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(id, user_id)
            )
            ''')
            
            # Create resources table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY,
                name TEXT,
                modname TEXT,
                course_id INTEGER,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(id, user_id)
            )
            ''')
            
            # Create resource_contents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER,
                type TEXT,
                filename TEXT,
                fileurl TEXT,
                filesize INTEGER,
                mimetype TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(id),
                UNIQUE(resource_id, fileurl)
            )
            ''')
            
            # Create calendar_events table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                eventtype TEXT,
                courseid INTEGER,
                timestart INTEGER,
                timeduration INTEGER,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id, user_id)
            )
            ''')
            
            # Create analytics tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_grade_trends (
                id TEXT PRIMARY KEY,
                data_json TEXT,
                x TEXT,
                y REAL,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_completion_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT,
                value REAL,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_grade_distribution (
                id TEXT PRIMARY KEY,
                label TEXT,
                value REAL,
                color TEXT,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create flashcards tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcard_decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                subject TEXT,
                course_id INTEGER,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_studied TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER,
                question TEXT,
                answer TEXT,
                difficulty TEXT,
                review_count INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES flashcard_decks(id) ON DELETE CASCADE
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                taste TEXT,
                chardonay REAL,
                color TEXT,
                user_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Set initial metadata
            cursor.execute('''
            INSERT OR IGNORE INTO metadata (key, value) VALUES (?, ?)
            ''', ('last_sync', datetime.now().isoformat()))
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def update_last_sync(self) -> None:
        """Update the last sync timestamp."""
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            UPDATE metadata SET value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE key = 'last_sync'
            ''', (datetime.now().isoformat(),))
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating last sync time: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_last_sync(self) -> str:
        """
        Get the last sync timestamp.
        
        Returns:
            ISO format timestamp string
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('SELECT value FROM metadata WHERE key = ?', ('last_sync',))
            result = cursor.fetchone()
            return result['value'] if result else None
        except Exception as e:
            logger.error(f"Error getting last sync time: {e}")
            return None
        finally:
            conn.close()
    
    # Courses methods
    def save_courses(self, courses: List[Dict[str, Any]], user_id: int) -> None:
        """
        Save courses to the database.
        
        Args:
            courses: List of course dictionaries
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for course in courses:
                cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (id, shortname, fullname, summary, progress, startdate, enddate, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    course.get('id'),
                    course.get('shortname'),
                    course.get('fullname'),
                    course.get('summary'),
                    course.get('progress'),
                    course.get('startdate'),
                    course.get('enddate'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved {len(courses)} courses for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving courses: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_courses(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get courses for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of course dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT id, shortname, fullname, summary, progress, startdate, enddate
            FROM courses
            WHERE user_id = ?
            ORDER BY id
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting courses: {e}")
            return []
        finally:
            conn.close()
    
    # Assignments methods
    def save_assignments(self, assignments: List[Dict[str, Any]], course_id: int, user_id: int) -> None:
        """
        Save assignments to the database.
        
        Args:
            assignments: List of assignment dictionaries
            course_id: Course ID
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for assignment in assignments:
                cursor.execute('''
                INSERT OR REPLACE INTO assignments
                (id, name, duedate, course_id, grade, maxgrade, status, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    assignment.get('id'),
                    assignment.get('name'),
                    assignment.get('duedate'),
                    course_id,
                    assignment.get('grade'),
                    assignment.get('maxgrade'),
                    assignment.get('status'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved {len(assignments)} assignments for course {course_id}, user {user_id}")
        except Exception as e:
            logger.error(f"Error saving assignments: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_assignments(self, course_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get assignments for a course.
        
        Args:
            course_id: Course ID
            user_id: User ID
            
        Returns:
            List of assignment dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT id, name, duedate, course_id as course, grade, maxgrade, status
            FROM assignments
            WHERE course_id = ? AND user_id = ?
            ORDER BY duedate
            ''', (course_id, user_id))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting assignments: {e}")
            return []
        finally:
            conn.close()
    
    # Grades methods
    def save_grades(self, grades: List[Dict[str, Any]], course_id: int, user_id: int) -> None:
        """
        Save grades to the database.
        
        Args:
            grades: List of grade dictionaries
            course_id: Course ID
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for grade in grades:
                cursor.execute('''
                INSERT OR REPLACE INTO grades
                (id, itemname, itemmodule, iteminstance, rawgrade, rawgrademax, rawgrademin, 
                feedback, course_id, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    grade.get('id'),
                    grade.get('itemname'),
                    grade.get('itemmodule'),
                    grade.get('iteminstance'),
                    grade.get('rawgrade'),
                    grade.get('rawgrademax'),
                    grade.get('rawgrademin'),
                    grade.get('feedback'),
                    course_id,
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved {len(grades)} grades for course {course_id}, user {user_id}")
        except Exception as e:
            logger.error(f"Error saving grades: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_grades(self, course_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get grades for a course.
        
        Args:
            course_id: Course ID
            user_id: User ID
            
        Returns:
            List of grade dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT id, itemname, itemmodule, iteminstance, rawgrade, rawgrademax, rawgrademin, feedback
            FROM grades
            WHERE course_id = ? AND user_id = ?
            ORDER BY id
            ''', (course_id, user_id))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting grades: {e}")
            return []
        finally:
            conn.close()
    
    # Resources and contents methods
    def save_resources(self, resources: List[Dict[str, Any]], course_id: int, user_id: int) -> None:
        """
        Save resources and their contents to the database.
        
        Args:
            resources: List of resource dictionaries
            course_id: Course ID
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for resource in resources:
                # Save the resource
                cursor.execute('''
                INSERT OR REPLACE INTO resources
                (id, name, modname, course_id, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    resource.get('id'),
                    resource.get('name'),
                    resource.get('modname'),
                    course_id,
                    user_id
                ))
                
                # Save the contents if available
                if 'contents' in resource and resource['contents']:
                    for content in resource['contents']:
                        cursor.execute('''
                        INSERT OR REPLACE INTO resource_contents
                        (resource_id, type, filename, fileurl, filesize, mimetype, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (
                            resource.get('id'),
                            content.get('type'),
                            content.get('filename'),
                            content.get('fileurl'),
                            content.get('filesize'),
                            content.get('mimetype')
                        ))
            
            conn.commit()
            logger.info(f"Saved resources for course {course_id}, user {user_id}")
        except Exception as e:
            logger.error(f"Error saving resources: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_resources(self, course_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get resources for a course with their contents.
        
        Args:
            course_id: Course ID
            user_id: User ID
            
        Returns:
            List of resource dictionaries with contents
        """
        conn, cursor = self._get_connection()
        try:
            # Get resources
            cursor.execute('''
            SELECT id, name, modname
            FROM resources
            WHERE course_id = ? AND user_id = ?
            ORDER BY id
            ''', (course_id, user_id))
            
            resources = [dict(row) for row in cursor.fetchall()]
            
            # Get contents for each resource
            for resource in resources:
                cursor.execute('''
                SELECT type, filename, fileurl, filesize, mimetype
                FROM resource_contents
                WHERE resource_id = ?
                ''', (resource['id'],))
                
                contents = [dict(row) for row in cursor.fetchall()]
                if contents:
                    resource['contents'] = contents
            
            return resources
        except Exception as e:
            logger.error(f"Error getting resources: {e}")
            return []
        finally:
            conn.close()
    
    # Calendar events methods
    def save_calendar_events(self, events: List[Dict[str, Any]], user_id: int) -> None:
        """
        Save calendar events to the database.
        
        Args:
            events: List of event dictionaries
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for event in events:
                cursor.execute('''
                INSERT OR REPLACE INTO calendar_events
                (id, name, description, eventtype, courseid, timestart, timeduration, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    event.get('id'),
                    event.get('name'),
                    event.get('description'),
                    event.get('eventtype'),
                    event.get('courseid'),
                    event.get('timestart'),
                    event.get('timeduration'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved {len(events)} calendar events for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving calendar events: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_calendar_events(self, user_id: int, from_time: int = None, to_time: int = None) -> List[Dict[str, Any]]:
        """
        Get calendar events for a user.
        
        Args:
            user_id: User ID
            from_time: Optional start timestamp
            to_time: Optional end timestamp
            
        Returns:
            List of event dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            query = '''
            SELECT id, name, description, eventtype, courseid, timestart, timeduration
            FROM calendar_events
            WHERE user_id = ?
            '''
            params = [user_id]
            
            if from_time is not None:
                query += ' AND timestart >= ?'
                params.append(from_time)
            
            if to_time is not None:
                query += ' AND timestart <= ?'
                params.append(to_time)
            
            query += ' ORDER BY timestart'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}")
            return []
        finally:
            conn.close()
    
    # Analytics methods
    def save_grade_trends(self, trends: List[Dict[str, Any]], user_id: int) -> None:
        """
        Save grade trends to the database.
        
        Args:
            trends: List of trend dictionaries
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for trend in trends:
                cursor.execute('''
                INSERT OR REPLACE INTO analytics_grade_trends
                (id, data_json, x, y, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    trend.get('id'),
                    json.dumps(trend.get('data', [])),
                    trend.get('x'),
                    trend.get('y'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved grade trends for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving grade trends: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_grade_trends(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get grade trends for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of trend dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT id, data_json, x, y
            FROM analytics_grade_trends
            WHERE user_id = ?
            ''', (user_id,))
            
            results = []
            for row in cursor.fetchall():
                trend = dict(row)
                # Parse the JSON data
                trend['data'] = json.loads(trend['data_json'])
                del trend['data_json']
                results.append(trend)
            
            return results
        except Exception as e:
            logger.error(f"Error getting grade trends: {e}")
            return []
        finally:
            conn.close()
    
    def save_completion_rates(self, rates: List[Dict[str, Any]], user_id: int) -> None:
        """
        Save completion rates to the database.
        
        Args:
            rates: List of completion rate dictionaries
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            # Clear existing data for this user
            cursor.execute('DELETE FROM analytics_completion_rates WHERE user_id = ?', (user_id,))
            
            for rate in rates:
                cursor.execute('''
                INSERT INTO analytics_completion_rates
                (course, value, user_id, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    rate.get('course'),
                    rate.get('value'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved completion rates for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving completion rates: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_completion_rates(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get completion rates for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of completion rate dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT course, value
            FROM analytics_completion_rates
            WHERE user_id = ?
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting completion rates: {e}")
            return []
        finally:
            conn.close()
    
    def save_grade_distribution(self, distribution: List[Dict[str, Any]], user_id: int) -> None:
        """
        Save grade distribution to the database.
        
        Args:
            distribution: List of grade distribution dictionaries
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        try:
            for item in distribution:
                cursor.execute('''
                INSERT OR REPLACE INTO analytics_grade_distribution
                (id, label, value, color, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    item.get('id'),
                    item.get('label'),
                    item.get('value'),
                    item.get('color'),
                    user_id
                ))
            conn.commit()
            logger.info(f"Saved grade distribution for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving grade distribution: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_grade_distribution(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get grade distribution for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of grade distribution dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT id, label, value, color
            FROM analytics_grade_distribution
            WHERE user_id = ?
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting grade distribution: {e}")
            return []
        finally:
            conn.close()
    
    def save_performance_overview(self, data: Dict[str, Any], user_id: int) -> None:
        """
        Save performance overview data.
        
        Args:
            data: Performance overview data
            user_id: User ID
        """
        conn, cursor = self._get_connection()
        
        try:
            # Clear existing data for this user
            cursor.execute(
                "DELETE FROM analytics_performance WHERE user_id = ?",
                (user_id,)
            )
            
            # Insert new data
            for item in data:
                cursor.execute(
                    """INSERT INTO analytics_performance 
                    (category, value, user_id, updated_at) 
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                    (item['category'], item['value'], user_id)
                )
            
            conn.commit()
            logger.info(f"Saved performance overview data for user {user_id}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving performance overview: {e}")
            raise
            
        finally:
            conn.close()
            
    # Flashcard methods
    def get_flashcard_decks(self, user_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get flashcard decks for a user, optionally filtered by course."""
        conn, cursor = self._get_connection()
        
        try:
            if course_id:
                cursor.execute(
                    """SELECT * FROM flashcard_decks 
                    WHERE user_id = ? AND course_id = ? 
                    ORDER BY last_studied DESC NULLS LAST""",
                    (user_id, course_id)
                )
            else:
                cursor.execute(
                    """SELECT * FROM flashcard_decks 
                    WHERE user_id = ? 
                    ORDER BY last_studied DESC NULLS LAST""",
                    (user_id,)
                )
                
            decks = [dict(row) for row in cursor.fetchall()]
            
            # Get card count for each deck
            for deck in decks:
                cursor.execute(
                    "SELECT COUNT(*) as card_count FROM flashcards WHERE deck_id = ?",
                    (deck['id'],)
                )
                deck['card_count'] = cursor.fetchone()['card_count']
                
            return decks
            
        except Exception as e:
            logger.error(f"Error getting flashcard decks: {e}")
            raise
            
        finally:
            conn.close()
    
    def get_flashcards(self, deck_id: int) -> List[Dict[str, Any]]:
        """Get flashcards for a deck."""
        conn, cursor = self._get_connection()
        
        try:
            cursor.execute(
                "SELECT * FROM flashcards WHERE deck_id = ? ORDER BY id",
                (deck_id,)
            )
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting flashcards: {e}")
            raise
            
        finally:
            conn.close()
    
    def save_flashcard_deck(self, deck_data: Dict[str, Any], user_id: int) -> int:
        """Save a flashcard deck and return its ID."""
        conn, cursor = self._get_connection()
        
        try:
            if 'id' in deck_data and deck_data['id']:
                # Update existing deck
                cursor.execute(
                    """UPDATE flashcard_decks 
                    SET title = ?, description = ?, subject = ?, course_id = ?, 
                    updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ? AND user_id = ?""",
                    (deck_data['title'], deck_data['description'], deck_data['subject'], 
                     deck_data.get('course_id'), deck_data['id'], user_id)
                )
                deck_id = deck_data['id']
            else:
                # Insert new deck
                cursor.execute(
                    """INSERT INTO flashcard_decks 
                    (title, description, subject, course_id, user_id, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (deck_data['title'], deck_data['description'], deck_data['subject'], 
                     deck_data.get('course_id'), user_id)
                )
                deck_id = cursor.lastrowid
            
            conn.commit()
            return deck_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving flashcard deck: {e}")
            raise
            
        finally:
            conn.close()
    
    def save_flashcard(self, card_data: Dict[str, Any], deck_id: int) -> int:
        """Save a flashcard and return its ID."""
        conn, cursor = self._get_connection()
        
        try:
            if 'id' in card_data and card_data['id']:
                # Update existing card
                cursor.execute(
                    """UPDATE flashcards 
                    SET question = ?, answer = ?, difficulty = ?, 
                    updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ? AND deck_id = ?""",
                    (card_data['question'], card_data['answer'], card_data['difficulty'], 
                     card_data['id'], deck_id)
                )
                card_id = card_data['id']
            else:
                # Insert new card
                cursor.execute(
                    """INSERT INTO flashcards 
                    (deck_id, question, answer, difficulty, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
                    (deck_id, card_data['question'], card_data['answer'], card_data['difficulty'])
                )
                card_id = cursor.lastrowid
            
            conn.commit()
            return card_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving flashcard: {e}")
            raise
            
        finally:
            conn.close()
    
    def update_flashcard_review(self, card_id: int, difficulty: str) -> None:
        """Update flashcard review data."""
        conn, cursor = self._get_connection()
        
        try:
            cursor.execute(
                """UPDATE flashcards 
                SET review_count = review_count + 1, difficulty = ?, 
                last_reviewed = CURRENT_TIMESTAMP 
                WHERE id = ?""",
                (difficulty, card_id)
            )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating flashcard review: {e}")
            raise
            
        finally:
            conn.close()
    
    def update_deck_studied(self, deck_id: int) -> None:
        """Update deck's last studied timestamp."""
        conn, cursor = self._get_connection()
        
        try:
            cursor.execute(
                """UPDATE flashcard_decks 
                SET last_studied = CURRENT_TIMESTAMP 
                WHERE id = ?""",
                (deck_id,)
            )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating deck studied timestamp: {e}")
            raise
            
        finally:
            conn.close()
    
    def delete_flashcard_deck(self, deck_id: int, user_id: int) -> None:
        """Delete a flashcard deck and all its cards."""
        conn, cursor = self._get_connection()
        
        try:
            # Check if the deck belongs to the user
            cursor.execute(
                "SELECT id FROM flashcard_decks WHERE id = ? AND user_id = ?",
                (deck_id, user_id)
            )
            
            if not cursor.fetchone():
                raise ValueError(f"Deck {deck_id} does not belong to user {user_id}")
            
            # Delete the deck (cards will be deleted via ON DELETE CASCADE)
            cursor.execute(
                "DELETE FROM flashcard_decks WHERE id = ?",
                (deck_id,)
            )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting flashcard deck: {e}")
            raise
            
        finally:
            conn.close()
    
    def delete_flashcard(self, card_id: int, deck_id: int) -> None:
        """Delete a flashcard."""
        conn, cursor = self._get_connection()
        
        try:
            cursor.execute(
                "DELETE FROM flashcards WHERE id = ? AND deck_id = ?",
                (card_id, deck_id)
            )
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting flashcard: {e}")
            raise
            
        finally:
            conn.close()
    
    def get_performance_overview(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get performance overview for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of performance dictionaries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute('''
            SELECT taste, chardonay, color
            FROM analytics_performance
            WHERE user_id = ?
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting performance overview: {e}")
            return []
        finally:
            conn.close()
