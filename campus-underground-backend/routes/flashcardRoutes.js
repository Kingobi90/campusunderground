const express = require('express');
const router = express.Router();
const gptFlashcardService = require('../services/gptFlashcardService');
const db = require('../models'); // Assuming you have database models

// Middleware to verify user
const verifyUser = (req, res, next) => {
  const userId = req.headers['user-id'];
  if (!userId) {
    return res.status(401).json({ error: 'User ID is required' });
  }
  req.userId = userId;
  next();
};

// Get all flashcard decks for a user
router.get('/decks', verifyUser, async (req, res) => {
  try {
    const courseId = req.query.course_id;
    const query = { user_id: req.userId };
    
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
    const formattedDecks = decks.map(deck => ({
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

// Get a specific deck with its cards
router.get('/decks/:deckId', verifyUser, async (req, res) => {
  try {
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
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
      return res.status(404).json({ error: 'Deck not found' });
    }
    
    res.json(deck);
  } catch (error) {
    console.error('Error fetching flashcard deck:', error);
    res.status(500).json({ error: 'Failed to fetch flashcard deck' });
  }
});

// Create a new deck
router.post('/decks', verifyUser, async (req, res) => {
  try {
    const deckData = {
      ...req.body,
      user_id: req.userId,
      created_at: new Date(),
      updated_at: new Date()
    };
    
    const deck = await db.FlashcardDeck.create(deckData);
    res.status(201).json(deck);
  } catch (error) {
    console.error('Error creating flashcard deck:', error);
    res.status(500).json({ error: 'Failed to create flashcard deck' });
  }
});

// Update a deck
router.put('/decks/:deckId', verifyUser, async (req, res) => {
  try {
    const [updated] = await db.FlashcardDeck.update(
      {
        ...req.body,
        updated_at: new Date()
      },
      {
        where: {
          id: req.params.deckId,
          user_id: req.userId
        }
      }
    );
    
    if (updated === 0) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    const updatedDeck = await db.FlashcardDeck.findByPk(req.params.deckId);
    res.json(updatedDeck);
  } catch (error) {
    console.error('Error updating flashcard deck:', error);
    res.status(500).json({ error: 'Failed to update flashcard deck' });
  }
});

// Delete a deck
router.delete('/decks/:deckId', verifyUser, async (req, res) => {
  try {
    // Delete associated cards first
    await db.Flashcard.destroy({
      where: {
        deck_id: req.params.deckId
      }
    });
    
    // Then delete the deck
    const deleted = await db.FlashcardDeck.destroy({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (deleted === 0) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    res.status(204).send();
  } catch (error) {
    console.error('Error deleting flashcard deck:', error);
    res.status(500).json({ error: 'Failed to delete flashcard deck' });
  }
});

// Get cards for a deck
router.get('/decks/:deckId/cards', verifyUser, async (req, res) => {
  try {
    // First verify the user owns this deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    const cards = await db.Flashcard.findAll({
      where: {
        deck_id: req.params.deckId
      }
    });
    
    res.json(cards);
  } catch (error) {
    console.error('Error fetching flashcards:', error);
    res.status(500).json({ error: 'Failed to fetch flashcards' });
  }
});

// Create a card in a deck
router.post('/decks/:deckId/cards', verifyUser, async (req, res) => {
  try {
    // First verify the user owns this deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    const cardData = {
      ...req.body,
      deck_id: req.params.deckId,
      user_id: req.userId,
      created_at: new Date(),
      updated_at: new Date(),
      review_count: 0
    };
    
    const card = await db.Flashcard.create(cardData);
    res.status(201).json(card);
  } catch (error) {
    console.error('Error creating flashcard:', error);
    res.status(500).json({ error: 'Failed to create flashcard' });
  }
});

// Update a card
router.put('/decks/:deckId/cards/:cardId', verifyUser, async (req, res) => {
  try {
    // First verify the user owns this deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    const [updated] = await db.Flashcard.update(
      {
        ...req.body,
        updated_at: new Date()
      },
      {
        where: {
          id: req.params.cardId,
          deck_id: req.params.deckId
        }
      }
    );
    
    if (updated === 0) {
      return res.status(404).json({ error: 'Card not found' });
    }
    
    const updatedCard = await db.Flashcard.findByPk(req.params.cardId);
    res.json(updatedCard);
  } catch (error) {
    console.error('Error updating flashcard:', error);
    res.status(500).json({ error: 'Failed to update flashcard' });
  }
});

// Delete a card
router.delete('/decks/:deckId/cards/:cardId', verifyUser, async (req, res) => {
  try {
    // First verify the user owns this deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: req.params.deckId,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    const deleted = await db.Flashcard.destroy({
      where: {
        id: req.params.cardId,
        deck_id: req.params.deckId
      }
    });
    
    if (deleted === 0) {
      return res.status(404).json({ error: 'Card not found' });
    }
    
    res.status(204).send();
  } catch (error) {
    console.error('Error deleting flashcard:', error);
    res.status(500).json({ error: 'Failed to delete flashcard' });
  }
});

// Update card review data
router.post('/cards/:cardId/review', verifyUser, async (req, res) => {
  try {
    const { difficulty } = req.body;
    
    if (!['easy', 'medium', 'hard'].includes(difficulty)) {
      return res.status(400).json({ error: 'Invalid difficulty level' });
    }
    
    const card = await db.Flashcard.findByPk(req.params.cardId);
    
    if (!card) {
      return res.status(404).json({ error: 'Card not found' });
    }
    
    // Verify user owns the card's deck
    const deck = await db.FlashcardDeck.findOne({
      where: {
        id: card.deck_id,
        user_id: req.userId
      }
    });
    
    if (!deck) {
      return res.status(403).json({ error: 'Not authorized to review this card' });
    }
    
    // Update the card review data
    await db.Flashcard.update(
      {
        difficulty,
        review_count: card.review_count + 1,
        last_reviewed: new Date(),
        updated_at: new Date()
      },
      {
        where: { id: req.params.cardId }
      }
    );
    
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error updating card review:', error);
    res.status(500).json({ error: 'Failed to update card review' });
  }
});

// Update deck study timestamp
router.post('/decks/:deckId/studied', verifyUser, async (req, res) => {
  try {
    const [updated] = await db.FlashcardDeck.update(
      {
        last_studied: new Date(),
        updated_at: new Date()
      },
      {
        where: {
          id: req.params.deckId,
          user_id: req.userId
        }
      }
    );
    
    if (updated === 0) {
      return res.status(404).json({ error: 'Deck not found or not authorized' });
    }
    
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error updating deck study timestamp:', error);
    res.status(500).json({ error: 'Failed to update deck study timestamp' });
  }
});

// Generate flashcards from course content using GPT
router.post('/generate-from-course/:courseId', verifyUser, async (req, res) => {
  try {
    const courseId = req.params.courseId;
    
    // This will trigger the GPT processing pipeline
    const flashcards = await gptFlashcardService.generateFlashcardsFromCourse(courseId, req.userId);
    
    res.status(200).json({
      message: 'Flashcards generated successfully',
      count: flashcards.length
    });
  } catch (error) {
    console.error('Error generating flashcards:', error);
    res.status(500).json({ error: 'Failed to generate flashcards' });
  }
});

// Generate flashcards directly from provided content
router.post('/generate-from-content', verifyUser, async (req, res) => {
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

// Submit feedback for a flashcard (to improve GPT generation)
router.post('/cards/:cardId/feedback', verifyUser, async (req, res) => {
  try {
    const { feedback } = req.body;
    
    if (!feedback) {
      return res.status(400).json({ error: 'Feedback is required' });
    }
    
    await gptFlashcardService.processUserFeedback(req.params.cardId, feedback);
    
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error submitting flashcard feedback:', error);
    res.status(500).json({ error: 'Failed to submit feedback' });
  }
});

module.exports = router;
