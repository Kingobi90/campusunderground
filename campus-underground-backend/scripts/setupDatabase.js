// Script to explicitly create database tables
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const dbPath = path.join(__dirname, '..', 'database.sqlite');

// Connect to SQLite database
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error connecting to database:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database');
});

// Create tables
db.serialize(() => {
  // Enable foreign keys
  db.run('PRAGMA foreign_keys = ON');
  
  // Create flashcard_decks table
  db.run(`
    CREATE TABLE IF NOT EXISTS flashcard_decks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      subject TEXT,
      course_id INTEGER,
      user_id TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      last_studied DATETIME
    )
  `, (err) => {
    if (err) {
      console.error('Error creating flashcard_decks table:', err.message);
    } else {
      console.log('flashcard_decks table created successfully');
    }
  });
  
  // Create flashcards table
  db.run(`
    CREATE TABLE IF NOT EXISTS flashcards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      deck_id INTEGER NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      difficulty INTEGER DEFAULT 0,
      next_review DATETIME,
      review_count INTEGER DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      ai_generated BOOLEAN DEFAULT FALSE,
      FOREIGN KEY (deck_id) REFERENCES flashcard_decks (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating flashcards table:', err.message);
    } else {
      console.log('flashcards table created successfully');
    }
  });
  
  // Create flashcard_feedback table
  db.run(`
    CREATE TABLE IF NOT EXISTS flashcard_feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      flashcard_id INTEGER NOT NULL,
      user_id TEXT NOT NULL,
      rating INTEGER NOT NULL,
      feedback TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (flashcard_id) REFERENCES flashcards (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating flashcard_feedback table:', err.message);
    } else {
      console.log('flashcard_feedback table created successfully');
    }
  });
});

// Close the database connection
db.close((err) => {
  if (err) {
    console.error('Error closing database:', err.message);
    process.exit(1);
  }
  console.log('Database setup completed successfully');
});
