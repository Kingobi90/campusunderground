import express from 'express';
import { pool } from '../config/database';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { Configuration, OpenAIApi } from 'openai';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req: Express.Request, file: Express.Multer.File, cb: (error: Error | null, destination: string) => void) => {
    const uploadDir = path.join(__dirname, '../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req: Express.Request, file: Express.Multer.File, cb: (error: Error | null, filename: string) => void) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req: Express.Request, file: Express.Multer.File, cb: multer.FileFilterCallback) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// Initialize OpenAI client
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY
});

// Use OpenAIApi instead of OpenAI constructor
const openai = new OpenAIApi(configuration);

// Get user's flashcard decks
router.get('/flashcards', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    const decks = await pool.query(
      'SELECT * FROM flashcard_decks WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );

    res.json(decks.rows);
  } catch (error) {
    console.error('Error fetching flashcard decks:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create new flashcard deck
router.post('/flashcards', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const { title, description, subject } = req.body;

    const newDeck = await pool.query(
      'INSERT INTO flashcard_decks (user_id, title, description, subject) VALUES ($1, $2, $3, $4) RETURNING *',
      [userId, title, description, subject]
    );

    res.status(201).json(newDeck.rows[0]);
  } catch (error) {
    console.error('Error creating flashcard deck:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get flashcards for a deck
router.get('/flashcards/:deckId', async (req, res) => {
  try {
    const { deckId } = req.params;
    const userId = req.headers['user-id'] as string;

    // Verify deck belongs to user
    const deckCheck = await pool.query(
      'SELECT * FROM flashcard_decks WHERE id = $1 AND user_id = $2',
      [deckId, userId]
    );

    if (deckCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Deck not found' });
    }

    const flashcards = await pool.query(
      'SELECT * FROM flashcards WHERE deck_id = $1 ORDER BY created_at',
      [deckId]
    );

    res.json(flashcards.rows);
  } catch (error) {
    console.error('Error fetching flashcards:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Add flashcard to deck
router.post('/flashcards/:deckId', async (req, res) => {
  try {
    const { deckId } = req.params;
    const userId = req.headers['user-id'] as string;
    const { question, answer } = req.body;

    // Verify deck belongs to user
    const deckCheck = await pool.query(
      'SELECT * FROM flashcard_decks WHERE id = $1 AND user_id = $2',
      [deckId, userId]
    );

    if (deckCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Deck not found' });
    }

    const newCard = await pool.query(
      'INSERT INTO flashcards (deck_id, question, answer, difficulty, review_count) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [deckId, question, answer, 'medium', 0]
    );

    res.status(201).json(newCard.rows[0]);
  } catch (error) {
    console.error('Error adding flashcard:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update flashcard rating
router.put('/flashcards/:cardId/rate', async (req, res) => {
  try {
    const { cardId } = req.params;
    const userId = req.headers['user-id'] as string;
    const { difficulty } = req.body;

    // Verify card belongs to user
    const cardCheck = await pool.query(
      `SELECT f.* FROM flashcards f 
       JOIN flashcard_decks fd ON f.deck_id = fd.id 
       WHERE f.id = $1 AND fd.user_id = $2`,
      [cardId, userId]
    );

    if (cardCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Card not found' });
    }

    const updatedCard = await pool.query(
      `UPDATE flashcards 
       SET difficulty = $1, review_count = review_count + 1, last_reviewed = NOW(), next_review = $2
       WHERE id = $3 RETURNING *`,
      [difficulty, req.body.nextReview, cardId]
    );

    res.json(updatedCard.rows[0]);
  } catch (error) {
    console.error('Error updating flashcard rating:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get user's notes
router.get('/notes', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    const notes = await pool.query(
      'SELECT * FROM notes WHERE user_id = $1 ORDER BY updated_at DESC',
      [userId]
    );

    res.json(notes.rows);
  } catch (error) {
    console.error('Error fetching notes:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create new note
router.post('/notes', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const { title, content, tags } = req.body;

    const newNote = await pool.query(
      'INSERT INTO notes (user_id, title, content, tags) VALUES ($1, $2, $3, $4) RETURNING *',
      [userId, title, content, tags]
    );

    res.status(201).json(newNote.rows[0]);
  } catch (error) {
    console.error('Error creating note:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Update note
router.put('/notes/:noteId', async (req, res) => {
  try {
    const { noteId } = req.params;
    const userId = req.headers['user-id'] as string;
    const { title, content, tags } = req.body;

    // Verify note belongs to user
    const noteCheck = await pool.query(
      'SELECT * FROM notes WHERE id = $1 AND user_id = $2',
      [noteId, userId]
    );

    if (noteCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Note not found' });
    }

    const updatedNote = await pool.query(
      'UPDATE notes SET title = $1, content = $2, tags = $3, updated_at = NOW() WHERE id = $4 RETURNING *',
      [title, content, tags, noteId]
    );

    res.json(updatedNote.rows[0]);
  } catch (error) {
    console.error('Error updating note:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Get pomodoro sessions
router.get('/pomodoro', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    const sessions = await pool.query(
      'SELECT * FROM pomodoro_sessions WHERE user_id = $1 ORDER BY created_at DESC LIMIT 50',
      [userId]
    );

    res.json(sessions.rows);
  } catch (error) {
    console.error('Error fetching pomodoro sessions:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Save pomodoro session
router.post('/pomodoro', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const { duration, completed, breaks } = req.body;

    const newSession = await pool.query(
      'INSERT INTO pomodoro_sessions (user_id, duration, completed, breaks) VALUES ($1, $2, $3, $4) RETURNING *',
      [userId, duration, completed, breaks]
    );

    res.status(201).json(newSession.rows[0]);
  } catch (error) {
    console.error('Error saving pomodoro session:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// PDF Summarization endpoints
router.post('/summarize-pdf', upload.single('file'), async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const { courseId, moduleId } = req.body;
    
    if (!req.file) {
      return res.status(400).json({ message: 'No PDF file uploaded' });
    }

    // Extract text from PDF using PyPDF2 (simplified version)
    const text = await extractTextFromPDF(req.file.path);
    
    // Generate summary using OpenAI
    const summary = await generateSummary(text);
    
    // Store summary in database
    const summaryRecord = await pool.query(
      `INSERT INTO pdf_summaries (user_id, file_name, file_path, summary, course_id, module_id) 
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [userId, req.file.originalname, req.file.path, summary, courseId || null, moduleId || null]
    );

    // Clean up uploaded file
    fs.unlinkSync(req.file.path);

    res.json({ 
      summary,
      summaryId: summaryRecord.rows[0].id 
    });
  } catch (error) {
    console.error('Error summarizing PDF:', error);
    res.status(500).json({ message: 'Error processing PDF' });
  }
});

router.post('/summarize-moodle-pdf', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    const authToken = req.headers['authorization']?.toString().replace('Bearer ', '');
    const { courseId, moduleId, fileUrl } = req.body;
    
    if (!fileUrl) {
      return res.status(400).json({ message: 'File URL is required' });
    }

    // Download PDF from Moodle
    const pdfPath = await downloadPDFFromMoodle(fileUrl, authToken);
    
    // Extract text from PDF
    const text = await extractTextFromPDF(pdfPath);
    
    // Generate summary using OpenAI
    const summary = await generateSummary(text);
    
    // Store summary in database
    const summaryRecord = await pool.query(
      `INSERT INTO pdf_summaries (user_id, file_name, file_path, summary, course_id, module_id) 
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [userId, path.basename(fileUrl), pdfPath, summary, courseId || null, moduleId || null]
    );

    // Clean up downloaded file
    fs.unlinkSync(pdfPath);

    res.json({ 
      summary,
      summaryId: summaryRecord.rows[0].id 
    });
  } catch (error) {
    console.error('Error summarizing Moodle PDF:', error);
    res.status(500).json({ message: 'Error processing PDF from Moodle' });
  }
});

// Get user's PDF summaries
router.get('/summaries', async (req, res) => {
  try {
    const userId = req.headers['user-id'] as string;
    
    const summaries = await pool.query(
      'SELECT * FROM pdf_summaries WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );

    res.json(summaries.rows);
  } catch (error) {
    console.error('Error fetching summaries:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Delete summary
router.delete('/summaries/:summaryId', async (req, res) => {
  try {
    const { summaryId } = req.params;
    const userId = req.headers['user-id'] as string;

    // Verify summary belongs to user
    const summaryCheck = await pool.query(
      'SELECT * FROM pdf_summaries WHERE id = $1 AND user_id = $2',
      [summaryId, userId]
    );

    if (summaryCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Summary not found' });
    }

    // Delete file if it exists
    const summary = summaryCheck.rows[0];
    if (summary.file_path && fs.existsSync(summary.file_path)) {
      fs.unlinkSync(summary.file_path);
    }

    await pool.query(
      'DELETE FROM pdf_summaries WHERE id = $1',
      [summaryId]
    );

    res.json({ message: 'Summary deleted successfully' });
  } catch (error) {
    console.error('Error deleting summary:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Helper functions
async function extractTextFromPDF(filePath: string): Promise<string> {
  // This is a simplified version - in production, you'd use PyPDF2 or similar
  // For now, we'll return a placeholder
  return "This is extracted text from the PDF. In a real implementation, this would contain the actual text content from the PDF file.";
}

async function generateSummary(text: string): Promise<string> {
  try {
    // Initialize OpenAI configuration
    const configuration = new Configuration({
      apiKey: process.env.OPENAI_API_KEY
    });
    const openaiApi = new OpenAIApi(configuration);
    
    const response = await openaiApi.createChatCompletion({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "You are an academic tutor analyzing lecture materials. Create a comprehensive summary that: 1) Captures key concepts and definitions, 2) Identifies important points and examples, 3) Asks thought-provoking questions to encourage deeper understanding, 4) Suggests areas for further study. Format your response with clear sections and bullet points. End with 2-3 questions that prompt the student to reflect on the material."
        },
        {
          role: "user",
          content: `Please analyze and summarize the following lecture material, then ask questions to encourage deeper thinking:\n\n${text}`
        }
      ],
      max_tokens: 1500,
      temperature: 0.7
    });

    return response.data.choices[0].message?.content || 'No summary generated';
  } catch (error) {
    console.error('Error generating summary:', error);
    throw new Error('Failed to generate summary');
  }
}

async function downloadPDFFromMoodle(fileUrl: string, authToken?: string): Promise<string> {
  try {
    // Create uploads directory if it doesn't exist
    const uploadDir = path.join(__dirname, '../../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    
    const tempPath = path.join(uploadDir, `moodle-${Date.now()}.pdf`);
    
    // Use axios to download the file from Moodle
    const axios = require('axios');
    
    // Determine if we need to proxy through our Moodle API client
    const token = authToken || process.env.MOODLE_API_KEY || 'a6f3e36db214f134c20acc2d8d6b8af6';
    
    // Make request to download the file
    const response = await axios({
      method: 'GET',
      url: fileUrl,
      responseType: 'stream',
      headers: {
        'Authorization': `Bearer ${token}`,
        'user-id': 'current-user'
      }
    });
    
    // Save the file to disk
    const writer = fs.createWriteStream(tempPath);
    response.data.pipe(writer);
    
    return new Promise((resolve, reject) => {
      writer.on('finish', () => resolve(tempPath));
      writer.on('error', reject);
    });
  } catch (error) {
    console.error('Error downloading PDF from Moodle:', error);
    throw new Error('Failed to download PDF from Moodle');
  }
}

export default router; 