// Script to sync database models with the database
const db = require('../models');

async function syncDatabase() {
  try {
    console.log('Syncing database models...');
    
    // Force: true will drop the table if it already exists (use with caution)
    await db.sequelize.sync({ force: true });
    
    console.log('Database sync completed successfully.');
    process.exit(0);
  } catch (error) {
    console.error('Error syncing database:', error);
    process.exit(1);
  }
}

syncDatabase();
