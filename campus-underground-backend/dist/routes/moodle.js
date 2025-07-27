"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const axios_1 = __importDefault(require("axios"));
const router = express_1.default.Router();
const MOODLE_API_URL = process.env.MOODLE_API_URL || 'http://localhost:5002';
// Helper function to forward headers from the request
const getHeaders = (req) => {
    return {
        'Authorization': req.headers['authorization'],
        'user-id': req.headers['user-id'],
        'Content-Type': 'application/json'
    };
};
// Get user's Moodle courses
router.get('/courses', async (req, res) => {
    try {
        const response = await axios_1.default.get(`${MOODLE_API_URL}/api/courses`, {
            headers: getHeaders(req)
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error fetching Moodle courses:', error?.response?.data || error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Get course contents (modules/resources)
router.get('/courses/:courseId/contents', async (req, res) => {
    try {
        const { courseId } = req.params;
        const response = await axios_1.default.get(`${MOODLE_API_URL}/api/courses/${courseId}/contents`, {
            headers: {
                'Authorization': req.headers['authorization'],
                'user-id': req.headers['user-id'],
            }
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error fetching course contents:', error?.response?.data || error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Get course assignments
router.get('/courses/:courseId/assignments', async (req, res) => {
    try {
        const { courseId } = req.params;
        const response = await axios_1.default.get(`${MOODLE_API_URL}/api/courses/${courseId}/assignments`, {
            headers: {
                'Authorization': req.headers['authorization'],
                'user-id': req.headers['user-id'],
            }
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error fetching course assignments:', error?.response?.data || error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Get user grades for a course
router.get('/courses/:courseId/grades', async (req, res) => {
    try {
        const { courseId } = req.params;
        const response = await axios_1.default.get(`${MOODLE_API_URL}/courses/${courseId}/grades`, {
            headers: {
                'Authorization': req.headers['authorization'],
                'user-id': req.headers['user-id'],
            }
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error fetching course grades:', error?.response?.data || error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Download file from Moodle
router.get('/download/:fileId', async (req, res) => {
    try {
        const { fileId } = req.params;
        const response = await axios_1.default.get(`${MOODLE_API_URL}/download/${fileId}`, {
            headers: {
                'Authorization': req.headers['authorization'],
                'user-id': req.headers['user-id'],
            }
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error downloading file:', error?.response?.data || error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Summarize PDF from Moodle
router.post('/summarize-pdf', async (req, res) => {
    try {
        const response = await axios_1.default.post(`${MOODLE_API_URL}/api/summarize-pdf`, req.body, {
            headers: getHeaders(req)
        });
        res.json(response.data);
    }
    catch (error) {
        console.error('Error summarizing PDF:', error?.response?.data || error);
        res.status(500).json({ message: 'Error processing PDF from Moodle' });
    }
});
exports.default = router;
//# sourceMappingURL=moodle.js.map