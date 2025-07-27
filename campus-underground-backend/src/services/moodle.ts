import axios from 'axios';
import { MoodleConfig, MoodleResponse, Course, CourseContent, Analytics, GradeDistribution, PerformanceOverview } from '../types/moodle';

export class MoodleAPIClient {
  private readonly baseUrl: string;
  private readonly token: string;

  constructor(config: MoodleConfig) {
    this.baseUrl = process.env.MOODLE_URL || 'https://moodle.concordia.ca';
    this.token = process.env.MOODLE_API_TOKEN || '';
  }

  private async request<T>(
    functionName: string,
    params: Record<string, any> = {}
  ): Promise<T> {
    const endpoint = `${this.baseUrl}/webservice/rest/server.php`;
    const requestParams = {
      wstoken: this.token,
      wsfunction: functionName,
      moodlewsrestformat: 'json',
      ...params
    };

    try {
      const response = await axios.get<MoodleResponse<T>>(endpoint, { params: requestParams });
      if (response.data.error) {
        throw new Error(`Moodle API Error: ${response.data.error}`);
      }
      return response.data.data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Moodle API Error: ${message}`);
    }
  }

  async getCourses(userId: number): Promise<Course[]> {
    return this.request('core_enrol_get_users_courses', { userid: userId });
  }

  async getCourseContents(courseId: number): Promise<CourseContent[]> {
    return this.request('core_course_get_contents', { courseid: courseId });
  }

  async getAnalytics(userId: number): Promise<Analytics> {
    return this.request('local_analytics_get_user_stats', { userid: userId });
  }

  async getGradeDistribution(userId: number): Promise<GradeDistribution[]> {
    return this.request('local_analytics_get_grade_distribution', { userid: userId });
  }

  async getPerformanceOverview(userId: number): Promise<PerformanceOverview> {
    return this.request('local_analytics_get_performance_overview', { userid: userId });
  }

  async getUserGrades(userId: number, courseId: number): Promise<any> {
    return this.request('gradereport_user_get_user_grades', {
      userid: userId,
      courseid: courseId
    });
  }

  async getCourseAssignments(userId: number, courseId: number): Promise<any> {
    return this.request('mod_assign_get_assignments', {
      userid: userId,
      courseid: courseId
    });
  }

  async downloadFile(fileId: number): Promise<any> {
    return this.request('core_files_download', {
      fileid: fileId
    });
  }
}
