const axios = require('axios');

class MoodleService {
  constructor() {
    this.baseUrl = process.env.MOODLE_URL || 'https://moodle.concordia.ca';
    this.apiToken = process.env.MOODLE_API_TOKEN;
  }

  /**
   * Get course content from Moodle
   * @param {number} courseId - Moodle course ID
   * @param {string} userId - User ID for authentication
   * @returns {Promise<Object>} - Course content data
   */
  async getCourseContent(courseId, userId) {
    try {
      // In a real implementation, this would make API calls to Moodle
      // For now, we'll return mock data for development
      return {
        id: courseId,
        name: `Course ${courseId}`,
        sections: [
          {
            id: 1,
            name: 'Introduction',
            summary: 'This section introduces the main concepts of the course.',
            modules: [
              {
                id: 101,
                name: 'Course Overview',
                content: 'This course covers the fundamentals of computer science including algorithms, data structures, and programming paradigms.',
                type: 'resource'
              },
              {
                id: 102,
                name: 'Syllabus',
                content: 'Weekly schedule: Week 1 - Introduction to Algorithms, Week 2 - Data Structures, Week 3 - Object-Oriented Programming...',
                type: 'resource'
              }
            ]
          },
          {
            id: 2,
            name: 'Week 1: Fundamentals',
            summary: 'Basic concepts and terminology.',
            modules: [
              {
                id: 201,
                name: 'Lecture Notes: Introduction to Programming',
                content: 'Programming is the process of creating instructions that tell a computer how to perform a task. Key concepts include variables, control structures, and functions.',
                type: 'resource'
              },
              {
                id: 202,
                name: 'Reading: History of Computing',
                content: 'The history of computing dates back to ancient times with devices like the abacus. Modern computing began with Charles Babbage and Ada Lovelace in the 19th century.',
                type: 'resource'
              }
            ]
          }
        ]
      };
    } catch (error) {
      console.error('Error fetching course content:', error);
      throw new Error('Failed to fetch course content from Moodle');
    }
  }

  /**
   * Extract text content from course materials
   * @param {Object} courseContent - Course content object
   * @returns {string} - Extracted text for processing
   */
  extractTextFromCourse(courseContent) {
    let extractedText = '';
    
    // Extract course name and description
    extractedText += `Course: ${courseContent.name}\n\n`;
    
    // Extract content from each section
    courseContent.sections.forEach(section => {
      extractedText += `Section: ${section.name}\n`;
      extractedText += `${section.summary}\n\n`;
      
      // Extract content from each module
      section.modules.forEach(module => {
        extractedText += `${module.name}:\n`;
        extractedText += `${module.content}\n\n`;
      });
    });
    
    return extractedText;
  }
}

module.exports = new MoodleService();
