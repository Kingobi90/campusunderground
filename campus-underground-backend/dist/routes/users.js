"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const database_1 = require("../config/database");
const router = express_1.default.Router();
// Get user profile
router.get('/profile', async (req, res) => {
    try {
        const userId = req.headers['user-id'];
        const user = await database_1.pool.query('SELECT id, email, name, student_id, created_at FROM users WHERE id = $1', [userId]);
        if (user.rows.length === 0) {
            return res.status(404).json({ message: 'User not found' });
        }
        res.json(user.rows[0]);
    }
    catch (error) {
        console.error('Error fetching user profile:', error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Update user profile
router.put('/profile', async (req, res) => {
    try {
        const userId = req.headers['user-id'];
        const { name, studentId } = req.body;
        const updatedUser = await database_1.pool.query('UPDATE users SET name = $1, student_id = $2 WHERE id = $3 RETURNING id, email, name, student_id, created_at', [name, studentId, userId]);
        if (updatedUser.rows.length === 0) {
            return res.status(404).json({ message: 'User not found' });
        }
        res.json(updatedUser.rows[0]);
    }
    catch (error) {
        console.error('Error updating user profile:', error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Get user statistics
router.get('/stats', async (req, res) => {
    try {
        const userId = req.headers['user-id'];
        // Get flashcard stats
        const flashcardStats = await database_1.pool.query('SELECT COUNT(*) as total_decks FROM flashcard_decks WHERE user_id = $1', [userId]);
        // Get note stats
        const noteStats = await database_1.pool.query('SELECT COUNT(*) as total_notes FROM notes WHERE user_id = $1', [userId]);
        // Get pomodoro stats
        const pomodoroStats = await database_1.pool.query('SELECT COUNT(*) as total_sessions, SUM(duration) as total_time FROM pomodoro_sessions WHERE user_id = $1', [userId]);
        res.json({
            flashcardDecks: parseInt(flashcardStats.rows[0].total_decks),
            notes: parseInt(noteStats.rows[0].total_notes),
            pomodoroSessions: parseInt(pomodoroStats.rows[0].total_sessions),
            totalStudyTime: parseInt(pomodoroStats.rows[0].total_time) || 0
        });
    }
    catch (error) {
        console.error('Error fetching user stats:', error);
        res.status(500).json({ message: 'Server error' });
    }
});
// Get study progress
router.get('/progress', async (req, res) => {
    try {
        const userId = req.headers['user-id'];
        // Get recent study sessions
        const recentSessions = await database_1.pool.query('SELECT * FROM pomodoro_sessions WHERE user_id = $1 ORDER BY created_at DESC LIMIT 7', [userId]);
        // Get recent notes
        const recentNotes = await database_1.pool.query('SELECT * FROM notes WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 5', [userId]);
        // Get recent flashcard activity
        const recentFlashcards = await database_1.pool.query('SELECT fd.title, COUNT(f.id) as card_count FROM flashcard_decks fd LEFT JOIN flashcards f ON fd.id = f.deck_id WHERE fd.user_id = $1 GROUP BY fd.id, fd.title ORDER BY fd.created_at DESC LIMIT 5', [userId]);
        res.json({
            recentSessions: recentSessions.rows,
            recentNotes: recentNotes.rows,
            recentFlashcards: recentFlashcards.rows
        });
    }
    catch (error) {
        console.error('Error fetching study progress:', error);
        res.status(500).json({ message: 'Server error' });
    }
});
exports.default = router;
//# sourceMappingURL=users.js.map