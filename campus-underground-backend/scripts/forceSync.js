// Force sync all database models
const db = require('../models');

async function forceSyncDatabase() {
  try {
    console.log('Starting database force sync...');
    
    // Force sync all models with the database
    await db.sequelize.sync({ force: true });
    
    console.log('✅ Database tables have been dropped and re-created successfully');
    
    // Create some test data if needed
    console.log('Creating test flashcard deck...');
    const testDeck = await db.FlashcardDeck.create({
      title: 'Test Deck',
      description: 'A test flashcard deck',
      subject: 'Test Subject',
      user_id: '123'
    });
    
    console.log('Creating test flashcard...');
    await db.Flashcard.create({
      front: 'Test Question',
      back: 'Test Answer',
      deck_id: testDeck.id,
      user_id: '123'
    });
    
    console.log('✅ Test data created successfully');
    
  } catch (error) {
    console.error('❌ Error syncing database:', error);
  } finally {
    process.exit();
  }
}

forceSyncDatabase();
