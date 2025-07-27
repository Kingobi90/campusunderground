// Test database access using the same code path as the API
const db = require('../models');
const path = require('path');

async function testDatabaseAccess() {
  try {
    console.log('Testing database connection...');
    console.log('Database config:', {
      dialect: db.sequelize.options.dialect,
      storage: db.sequelize.options.storage,
      database: db.sequelize.options.database
    });
    
    console.log('Current directory:', process.cwd());
    console.log('Database file path:', path.resolve(db.sequelize.options.storage || 'database.sqlite'));
    console.log('Database file exists:', require('fs').existsSync(path.resolve(db.sequelize.options.storage || 'database.sqlite')));
    
    console.log('\nTesting FlashcardDeck model...');
    try {
      const decks = await db.FlashcardDeck.findAll();
      console.log('✅ Successfully retrieved flashcard decks:', decks.length);
      console.log('First deck:', decks[0] ? JSON.stringify(decks[0].toJSON(), null, 2) : 'No decks found');
    } catch (deckError) {
      console.error('❌ Error accessing FlashcardDeck model:', deckError);
    }
    
    console.log('\nTesting raw query...');
    try {
      const [results] = await db.sequelize.query('SELECT * FROM flashcard_decks');
      console.log('✅ Raw query successful:', results.length);
      console.log('First result:', results[0] ? JSON.stringify(results[0], null, 2) : 'No results');
    } catch (queryError) {
      console.error('❌ Error executing raw query:', queryError);
    }
    
    console.log('\nListing all tables in database...');
    try {
      const [tables] = await db.sequelize.query("SELECT name FROM sqlite_master WHERE type='table'");
      console.log('✅ Tables in database:', tables.map(t => t.name));
    } catch (tablesError) {
      console.error('❌ Error listing tables:', tablesError);
    }
    
  } catch (error) {
    console.error('❌ Error testing database:', error);
  } finally {
    process.exit();
  }
}

testDatabaseAccess();
