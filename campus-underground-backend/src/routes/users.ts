import express from 'express';
import { pool } from '../config/database';

const router = express.Router();

// Get user profile
router.get('/profile', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    const user = await pool.query(
      'SELECT id, email, name, student_id, created_at FROM users WHERE id = $1',
      [userId]
    );

    if (user.rows.length === 0) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(user.rows[0]);
  } catch (error) {
    console.error('Error fetching user profile:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update user profile
router.put('/profile', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const { name, studentId } = req.body;

    const updatedUser = await pool.query(
      'UPDATE users SET name = $1, student_id = $2 WHERE id = $3 RETURNING id, email, name, student_id, created_at',
      [name, studentId, userId]
    );

    if (updatedUser.rows.length === 0) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json(updatedUser.rows[0]);
  } catch (error) {
    console.error('Error updating user profile:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get user statistics
router.get('/stats', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    // Get flashcard stats
    const flashcardStats = await pool.query(
      'SELECT COUNT(*) as total_decks FROM flashcard_decks WHERE user_id = $1',
      [userId]
    );

    // Get note stats
    const noteStats = await pool.query(
      'SELECT COUNT(*) as total_notes FROM notes WHERE user_id = $1',
      [userId]
    );

    // Get pomodoro stats
    const pomodoroStats = await pool.query(
      'SELECT COUNT(*) as total_sessions, SUM(duration) as total_time FROM pomodoro_sessions WHERE user_id = $1',
      [userId]
    );

    res.json({
      flashcardDecks: parseInt(flashcardStats.rows[0].total_decks),
      notes: parseInt(noteStats.rows[0].total_notes),
      pomodoroSessions: parseInt(pomodoroStats.rows[0].total_sessions),
      totalStudyTime: parseInt(pomodoroStats.rows[0].total_time) || 0
    });
  } catch (error) {
    console.error('Error fetching user stats:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get study progress
router.get('/progress', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    // Get recent study sessions
    const recentSessions = await pool.query(
      'SELECT * FROM pomodoro_sessions WHERE user_id = $1 ORDER BY created_at DESC LIMIT 7',
      [userId]
    );

    // Get recent notes
    const recentNotes = await pool.query(
      'SELECT * FROM notes WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 5',
      [userId]
    );

    // Get recent flashcard activity
    const recentFlashcards = await pool.query(
      'SELECT fd.title, COUNT(f.id) as card_count FROM flashcard_decks fd LEFT JOIN flashcards f ON fd.id = f.deck_id WHERE fd.user_id = $1 GROUP BY fd.id, fd.title ORDER BY fd.created_at DESC LIMIT 5',
      [userId]
    );

    res.json({
      recentSessions: recentSessions.rows,
      recentNotes: recentNotes.rows,
      recentFlashcards: recentFlashcards.rows
    });
  } catch (error) {
    console.error('Error fetching study progress:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router; 