import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

// SQLite configuration
export const config = {
  database: process.env.DB_NAME || 'campus_underground',
  dialect: 'sqlite',
  storage: path.join(__dirname, '../../database.sqlite'),
  logging: false
};

// Create a connection pool for SQLite
export const pool = {
  query: async (text: string, params: any[] = []) => {
    const db = await open({
      filename: config.storage,
      driver: sqlite3.Database
    });
    try {
      const result = await db.all(text, ...params);
      return { rows: result };
    } catch (err) {
      console.error('❌ Database query failed:', err);
      throw err;
    } finally {
      await db.close();
    }
  },
  connect: async (callback: Function) => {
    try {
      const db = await open({
        filename: config.storage,
        driver: sqlite3.Database
      });
      callback(null, db, async () => await db.close());
    } catch (err) {
      console.error('❌ Database connection failed:', err);
      callback(err, null, () => {});
    }
  }
};


export default pool;