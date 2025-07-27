export interface MoodleConfig {
  url: string;
  token: string;
}

export interface MoodleResponse<T> {
  data: T;
  error?: string;
}

export interface Course {
  id: number;
  fullname: string;
  shortname: string;
  progress?: number;
}

export interface CourseContent {
  id: number;
  name: string;
  contents: Array<{
    id: number;
    name: string;
    type: string;
    content: string;
  }>;
}

export interface Analytics {
  gradeAverage: number;
  attendancePercentage: number;
  engagementScore: number;
}

export interface GradeDistribution {
  courseId: number;
  courseName: string;
  grade: number;
  maxGrade: number;
  percentage: number;
}

export interface PerformanceOverview {
  overallGrade: number;
  attendance: number;
  engagement: number;
  progress: number;
  courses: Array<{
    id: number;
    name: string;
    grade: number;
    progress: number;
  }>;
}
