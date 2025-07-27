import express from 'express';
import { MoodleAPIClient } from '../services/moodle';
import { pool } from '../config/database';
import { GradeDistribution, PerformanceOverview } from '../types/moodle';
import axios from 'axios';

// Helper function to get headers from request
const getHeaders = (req: express.Request): { [key: string]: string } => {
  const headers: { [key: string]: string } = {};
  Object.entries(req.headers).forEach(([key, value]) => {
    headers[key] = Array.isArray(value) ? value.join(',') : value || '';
  });
  return headers;
};

const router = express.Router();

// Initialize Moodle client
const moodleClient = new MoodleAPIClient({
  url: process.env.MOODLE_URL || 'https://moodle.concordia.ca',
  token: process.env.MOODLE_API_TOKEN || ''
});

// Helper function to get user ID from request
const getUserId = (req: express.Request): number => {
  const userId = Number(req.headers['user-id']);
  if (!userId) {
    throw new Error('User ID is required');
  }
  return userId;
};

// Get user's Moodle courses
router.get('/courses', async (req, res) => {
  try {
    const userId = Number(req.headers['user-id']);
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }

    const courses = await moodleClient.getCourses(userId);
    res.json(courses);
  } catch (error) {
    console.error('Error fetching Moodle courses:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get course contents (modules/resources)
router.get('/courses/:courseId/contents', async (req, res) => {
  try {
    const courseId = Number(req.params.courseId);
    if (isNaN(courseId)) {
      return res.status(400).json({ error: 'Invalid course ID' });
    }

    const contents = await moodleClient.getCourseContents(courseId);
    res.json(contents);
  } catch (error) {
    console.error('Error fetching course contents:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get course assignments
router.get('/courses/:courseId/assignments', async (req, res) => {
  try {
    const userId = getUserId(req);
    const courseId = Number(req.params.courseId);
    if (isNaN(courseId)) {
      return res.status(400).json({ error: 'Invalid course ID' });
    }
    
    const assignments = await moodleClient.getCourseAssignments(userId, courseId);
    res.json(assignments);
  } catch (error) {
    console.error('Error fetching course assignments:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get user grades for a course
router.get('/courses/:courseId/grades', async (req, res) => {
  try {
    const userId = getUserId(req);
    const courseId = Number(req.params.courseId);
    if (isNaN(courseId)) {
      return res.status(400).json({ error: 'Invalid course ID' });
    }
    
    const grades = await moodleClient.getUserGrades(userId, courseId);
    res.json(grades);
  } catch (error) {
    console.error('Error fetching course grades:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Download file from Moodle
router.get('/download/:fileId', async (req, res) => {
  try {
    const fileId = Number(req.params.fileId);
    if (isNaN(fileId)) {
      return res.status(400).json({ error: 'Invalid file ID' });
    }
    
    const file = await moodleClient.downloadFile(fileId);
    res.json(file);
  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Summarize PDF from Moodle
router.post('/summarize-pdf', async (req, res) => {
  try {
    const response = await axios.post(`${process.env.MOODLE_API_URL || 'http://localhost:5002'}/api/summarize-pdf`, req.body, {
      headers: getHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error summarizing PDF:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Analytics endpoints

// Get grade trends for analytics
router.get('/analytics/grade-trends', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.MOODLE_API_URL || 'http://localhost:5002'}/api/analytics/grade-trends`, {
      headers: getHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching grade trends:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get completion rates by course
router.get('/analytics/completion-rates', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.MOODLE_API_URL || 'http://localhost:5002'}/api/analytics/completion-rates`, {
      headers: getHeaders(req)
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching completion rates:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get grade distribution
router.get('/analytics/grade-distribution', async (req, res) => {
  try {
    const userId = getUserId(req);
    const gradeDistribution = await moodleClient.getGradeDistribution(userId);
    res.json(gradeDistribution);
  } catch (error) {
    console.error('Error fetching grade distribution:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Get performance overview
router.get('/analytics/performance-overview', async (req, res) => {
  try {
    const userId = getUserId(req);
    const performanceOverview = await moodleClient.getPerformanceOverview(userId);
    res.json(performanceOverview);
  } catch (error) {
    console.error('Error fetching performance overview:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

export default router;