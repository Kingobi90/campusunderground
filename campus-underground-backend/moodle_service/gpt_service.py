#!/usr/bin/env python3
"""
GPT API Service for Campus Underground
This module provides integration with OpenAI's GPT API for educational content analysis.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gpt_service')

# Load environment variables
load_dotenv()

class GPTAPIError(Exception):
    """Exception raised for GPT API errors."""
    pass

class GPTService:
    """Service for interacting with OpenAI's GPT API."""
    
    def __init__(self, use_mock_data=False):
        """
        Initialize the GPT API service.
        
        Args:
            use_mock_data: Whether to use mock data instead of real API calls
        """
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.use_mock_data = use_mock_data or not self.api_key or self.api_key == 'your_openai_api_key_here'
        
        logger.info(f"GPT API service initialized")
        logger.info(f"Using mock data: {self.use_mock_data}")
    
    def analyze_content(self, content: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Analyze educational content using GPT.
        
        Args:
            content: The educational content to analyze
            analysis_type: Type of analysis to perform (summary, key_points, quiz_generation)
            
        Returns:
            Analysis results as a dictionary
        """
        if self.use_mock_data:
            return self._get_mock_analysis(content, analysis_type)
        
        # Prepare prompt based on analysis type
        if analysis_type == "summary":
            prompt = f"Summarize the following educational content in a concise way that highlights the most important concepts:\n\n{content}"
        elif analysis_type == "key_points":
            prompt = f"Extract the key points from the following educational content:\n\n{content}"
        elif analysis_type == "quiz_generation":
            prompt = f"Generate 3 quiz questions with answers based on the following educational content:\n\n{content}"
        else:
            prompt = f"Analyze the following educational content:\n\n{content}"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an educational assistant that helps analyze academic content."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                raise GPTAPIError("Invalid response from GPT API")
                
            analysis_text = data["choices"][0]["message"]["content"]
            
            # Format the response based on analysis type
            if analysis_type == "key_points":
                # Extract bullet points
                points = [point.strip().replace("- ", "") for point in analysis_text.split("\n") if point.strip().startswith("- ")]
                if not points:  # If no bullet points found, split by newlines
                    points = [point.strip() for point in analysis_text.split("\n") if point.strip()]
                return {"key_points": points}
                
            elif analysis_type == "quiz_generation":
                # Parse quiz questions and answers
                quiz_items = []
                current_item = {}
                
                for line in analysis_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith(("Q", "Question")):
                        if current_item and "question" in current_item:
                            quiz_items.append(current_item)
                            current_item = {}
                        current_item["question"] = line.split(":", 1)[1].strip() if ":" in line else line
                    elif line.startswith(("A", "Answer")):
                        current_item["answer"] = line.split(":", 1)[1].strip() if ":" in line else line
                
                if current_item and "question" in current_item:
                    quiz_items.append(current_item)
                    
                return {"quiz_items": quiz_items}
                
            else:  # summary or default
                return {"summary": analysis_text}
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise GPTAPIError(f"GPT API request failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            raise GPTAPIError(f"GPT analysis failed: {str(e)}")
    
    def analyze_student_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze student performance data using GPT.
        
        Args:
            performance_data: Dictionary containing student performance metrics
            
        Returns:
            Analysis results as a dictionary
        """
        if self.use_mock_data:
            return self._get_mock_performance_analysis(performance_data)
        
        try:
            # Convert performance data to a readable format
            data_str = json.dumps(performance_data, indent=2)
            
            prompt = f"Analyze the following student performance data and provide insights and recommendations:\n\n{data_str}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an educational analytics assistant that helps analyze student performance data."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                raise GPTAPIError("Invalid response from GPT API")
                
            analysis_text = data["choices"][0]["message"]["content"]
            
            # Extract insights and recommendations
            insights = []
            recommendations = []
            
            current_section = None
            for line in analysis_text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                    
                if "insight" in line.lower() or "observation" in line.lower():
                    current_section = "insights"
                    continue
                elif "recommendation" in line.lower() or "suggestion" in line.lower():
                    current_section = "recommendations"
                    continue
                    
                if current_section == "insights" and line.startswith(("- ", "• ", "* ")):
                    insights.append(line.replace("- ", "").replace("• ", "").replace("* ", ""))
                elif current_section == "recommendations" and line.startswith(("- ", "• ", "* ")):
                    recommendations.append(line.replace("- ", "").replace("• ", "").replace("* ", ""))
            
            return {
                "analysis": analysis_text,
                "insights": insights,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            raise GPTAPIError(f"Performance analysis failed: {str(e)}")
    
    def _get_mock_analysis(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """
        Generate mock analysis results for testing.
        
        Args:
            content: The content to analyze
            analysis_type: Type of analysis
            
        Returns:
            Mock analysis results
        """
        logger.info(f"Generating mock {analysis_type} for content: {content[:50]}...")
        
        if analysis_type == "summary":
            return {
                "summary": "This is a mock summary of the educational content. It covers the main concepts and provides a concise overview of the material."
            }
        elif analysis_type == "key_points":
            return {
                "key_points": [
                    "First key concept from the content",
                    "Second important point to remember",
                    "Third critical idea from the material",
                    "Fourth significant concept to understand"
                ]
            }
        elif analysis_type == "quiz_generation":
            return {
                "quiz_items": [
                    {
                        "question": "What is the main concept discussed in the content?",
                        "answer": "The main concept is educational analysis."
                    },
                    {
                        "question": "How does the second principle relate to the first?",
                        "answer": "The second principle builds upon the first by extending its application."
                    },
                    {
                        "question": "What are the implications of the third concept?",
                        "answer": "The third concept implies a paradigm shift in how we approach learning."
                    }
                ]
            }
        else:
            return {
                "analysis": "This is a generic mock analysis of the educational content."
            }
    
    def _get_mock_performance_analysis(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock performance analysis results for testing.
        
        Args:
            performance_data: Student performance data
            
        Returns:
            Mock analysis results
        """
        logger.info("Generating mock performance analysis...")
        
        return {
            "analysis": "This is a mock analysis of the student performance data. It identifies patterns and provides recommendations for improvement.",
            "insights": [
                "Student shows strong performance in theoretical concepts but struggles with practical applications",
                "Consistent improvement trend over the semester",
                "Participation in discussions correlates with better assignment scores",
                "Time management appears to be a challenge based on submission patterns"
            ],
            "recommendations": [
                "Focus on more hands-on exercises to improve practical skills",
                "Continue the current study routine as it shows positive results",
                "Allocate more time for complex assignments",
                "Consider joining study groups for collaborative learning"
            ]
        }


# For testing
if __name__ == "__main__":
    service = GPTService(use_mock_data=True)
    result = service.analyze_content("This is a test content for analysis", "summary")
    print(json.dumps(result, indent=2))
