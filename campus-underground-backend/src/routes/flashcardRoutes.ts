import express, { Request, Response, NextFunction } from 'express';
const router = express.Router();
const gptFlashcardService = require('../../services/gptFlashcardService');
const db = require('../../models'); // Database models

// Add user ID to request object
interface AuthenticatedRequest extends Request {
  userId?: string;
}

// Middleware to verify user
const verifyUser = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const userId = req.headers['user-id'] as string;
  if (!userId) {
    return res.status(401).json({ error: 'User ID is required' });
  }
  req.userId = userId;
  next();
};

// Get all flashcard decks for a user
router.get('/decks', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const courseId = req.query.course_id as string;
    const query: any = { user_id: req.userId };
    
    if (courseId) {
      query.course_id = courseId;
    }
    
    const decks = await db.FlashcardDeck.findAll({
      where: query,
      include: [
        {
          model: db.Flashcard,
          as: 'cards',
          attributes: ['id'] // Just get the IDs for counting
        }
      ]
    });
    
    // Format the response
    const formattedDecks = decks.map((deck: any) => ({
      id: deck.id,
      title: deck.title,
      description: deck.description,
      subject: deck.subject,
      course_id: deck.course_id,
      user_id: deck.user_id,
      created_at: deck.created_at,
      updated_at: deck.updated_at,
      last_studied: deck.last_studied,
      card_count: deck.cards ? deck.cards.length : 0
    }));
    
    res.json(formattedDecks);
  } catch (error) {
    console.error('Error fetching flashcard decks:', error);
    res.status(500).json({ error: 'Failed to fetch flashcard decks' });
  }
});

// Get a specific flashcard deck with all cards
router.get('/decks/:deckId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { deckId } = req.params;
    
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: deckId,
        user_id: req.userId
      },
      include: [
        {
          model: db.Flashcard,
          as: 'cards'
        }
      ]
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Flashcard deck not found' });
    }
    
    res.json(deck);
  } catch (error) {
    console.error('Error fetching flashcard deck:', error);
    res.status(500).json({ error: 'Failed to fetch flashcard deck' });
  }
});

// Create a new flashcard deck
router.post('/decks', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { title, description, subject, course_id } = req.body;
    
    const newDeck = await db.FlashcardDeck.create({
      title,
      description,
      subject,
      course_id,
      user_id: req.userId,
      created_at: new Date(),
      updated_at: new Date()
    });
    
    res.status(201).json(newDeck);
  } catch (error) {
    console.error('Error creating flashcard deck:', error);
    res.status(500).json({ error: 'Failed to create flashcard deck' });
  }
});

// Update a flashcard deck
router.put('/decks/:deckId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { deckId } = req.params;
    const { title, description, subject } = req.body;
    
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Flashcard deck not found' });
    }
    
    await deck.update({
      title,
      description,
      subject,
      updated_at: new Date()
    });
    
    res.json(deck);
  } catch (error) {
    console.error('Error updating flashcard deck:', error);
    res.status(500).json({ error: 'Failed to update flashcard deck' });
  }
});

// Delete a flashcard deck
router.delete('/decks/:deckId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { deckId } = req.params;
    
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Flashcard deck not found' });
    }
    
    // Delete all cards in the deck first
    await db.Flashcard.destroy({
      where: {
        deck_id: deckId
      }
    });
    
    // Then delete the deck
    await deck.destroy();
    
    res.json({ message: 'Flashcard deck deleted successfully' });
  } catch (error) {
    console.error('Error deleting flashcard deck:', error);
    res.status(500).json({ error: 'Failed to delete flashcard deck' });
  }
});

// Create a new flashcard in a deck
router.post('/decks/:deckId/cards', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    // First verify the user owns this deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Flashcard deck not found' });
    }
    
    const { front, back } = req.body;
    
    const newCard = await db.Flashcard.create({
      deck_id: req.params.deckId,
      front,
      back,
      difficulty: 'medium',
      review_count: 0,
      generated_by_ai: false,
      created_at: new Date(),
      updated_at: new Date()
    });
    
    res.status(201).json(newCard);
  } catch (error) {
    console.error('Error creating flashcard:', error);
    res.status(500).json({ error: 'Failed to create flashcard' });
  }
});

// Update a flashcard
router.put('/cards/:cardId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { cardId } = req.params;
    const { front, back, difficulty } = req.body;
    
    // First get the card
    const card = await db.Flashcard.findByPk(cardId);
    
    if (!card) {
      return res.status(404).json({ error: 'Flashcard not found' });
    }
    
    // Then verify the user owns the deck this card belongs to
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: card.deck_id,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(403).json({ error: 'Not authorized to update this flashcard' });
    }
    
    await card.update({
      front,
      back,
      difficulty,
      updated_at: new Date()
    });
    
    res.json(card);
  } catch (error) {
    console.error('Error updating flashcard:', error);
    res.status(500).json({ error: 'Failed to update flashcard' });
  }
});

// Delete a flashcard
router.delete('/cards/:cardId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { cardId } = req.params;
    
    // First get the card
    const card = await db.Flashcard.findByPk(cardId);
    
    if (!card) {
      return res.status(404).json({ error: 'Flashcard not found' });
    }
    
    // Then verify the user owns the deck this card belongs to
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: card.deck_id,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(403).json({ error: 'Not authorized to delete this flashcard' });
    }
    
    await card.destroy();
    
    res.json({ message: 'Flashcard deleted successfully' });
  } catch (error) {
    console.error('Error deleting flashcard:', error);
    res.status(500).json({ error: 'Failed to delete flashcard' });
  }
});

// Submit feedback for a flashcard
router.post('/cards/:cardId/feedback', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { cardId } = req.params;
    const { feedback_text, rating } = req.body;
    
    // First get the card
    const card = await db.Flashcard.findByPk(cardId);
    
    if (!card) {
      return res.status(404).json({ error: 'Flashcard not found' });
    }
    
    // Then verify the user owns the deck this card belongs to
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: card.deck_id,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(403).json({ error: 'Not authorized to submit feedback for this flashcard' });
    }
    
    // Create feedback entry
    const feedback = await db.FlashcardFeedback.create({
      flashcard_id: cardId,
      user_id: req.userId,
      feedback_text,
      rating,
      created_at: new Date()
    });
    
    res.status(201).json(feedback);
  } catch (error) {
    console.error('Error submitting flashcard feedback:', error);
    res.status(500).json({ error: 'Failed to submit flashcard feedback' });
  }
});

// Generate flashcards from a course using GPT
router.post('/generate-from-course/:courseId', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const courseId = req.params.courseId;
    
    // This will trigger the GPT processing pipeline
    const result = await gptFlashcardService.generateFlashcardsFromCourse(courseId, req.userId);
    
    res.json({
      message: 'Flashcard generation started',
      deckId: result.deckId
    });
  } catch (error) {
    console.error('Error generating flashcards:', error);
    res.status(500).json({ error: 'Failed to generate flashcards' });
  }
});

// Generate flashcards directly from provided content
router.post('/generate-from-content', verifyUser, async (req: AuthenticatedRequest, res: Response) => {
  try {
    const { content } = req.body;
    
    if (!content) {
      return res.status(400).json({ error: 'Content is required for flashcard generation' });
    }
    
    // Use the GPT service to generate flashcards from the provided content
    const flashcards = await gptFlashcardService.generateFlashcardsWithGPT(content, null, req.userId);
    
    // Store the generated flashcards
    await gptFlashcardService.storeFlashcards(flashcards, null, req.userId);
    
    res.status(200).json({
      message: 'Flashcards generated successfully',
      count: flashcards.length,
      flashcards: flashcards
    });
  } catch (error) {
    console.error('Error generating flashcards from content:', error);
    res.status(500).json({ error: 'Failed to generate flashcards from content' });
  }
});

export default router;
