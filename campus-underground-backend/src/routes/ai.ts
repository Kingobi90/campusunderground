import express from 'express';
import { Configuration, OpenAIApi } from 'openai';
import { MoodleAPIClient } from '../services/moodle';

const router = express.Router();

// Initialize OpenAI
const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY
});
const openai = new OpenAIApi(configuration);

// Initialize Moodle client
const moodleClient = new MoodleAPIClient({
  url: process.env.MOODLE_URL || 'https://moodle.concordia.ca',
  token: process.env.MOODLE_API_TOKEN || ''
});

// AI Assistant endpoint
router.post('/assistant', async (req, res) => {
    try {
        const { action } = req.body;
        const userId = parseInt(req.headers['user-id'] as string);
        const courses = await moodleClient.getCourses(userId);
        
        // Generate AI response based on the action and user's course data
        const prompt = `Based on the user's courses and assignments:
        ${JSON.stringify(courses, null, 2)}
        
        Action: ${action}
        Provide a helpful response to assist the user with their academic tasks.`;

        const completion = await openai.createChatCompletion({
            model: "gpt-3.5-turbo",
            messages: [{ role: "user", content: prompt }],
            temperature: 0.7
        });

        res.json({
            message: completion.data.choices[0].message?.content,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error in AI assistant:', error);
        res.status(500).json({
            error: 'Failed to generate AI response. Please try again.'
        });
    }
});

export default router;
