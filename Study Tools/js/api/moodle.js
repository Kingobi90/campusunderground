class MoodleAPI {
    constructor() {
        this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    }

    async getCourses() {
        try {
            const response = await fetch(`${this.baseUrl}/api/moodle/courses`, {
                headers: {
                    'Authorization': localStorage.getItem('token'),
                    'user-id': localStorage.getItem('user-id')
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching courses:', error);
            throw error;
        }
    }

    async getCourseContents(courseId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/moodle/courses/${courseId}/contents`, {
                headers: {
                    'Authorization': localStorage.getItem('token'),
                    'user-id': localStorage.getItem('user-id')
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching course contents:', error);
            throw error;
        }
    }

    async getAnalytics() {
        try {
            const response = await fetch(`${this.baseUrl}/api/moodle/analytics`, {
                headers: {
                    'Authorization': localStorage.getItem('token'),
                    'user-id': localStorage.getItem('user-id')
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching analytics:', error);
            throw error;
        }
    }
}

// Export a singleton instance
export const moodleAPI = new MoodleAPI();
