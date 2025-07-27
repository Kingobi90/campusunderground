import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { config } from './config/database';
import authRoutes from './routes/auth';
import studyToolsRoutes from './routes/studyTools';
import userRoutes from './routes/users';
import moodleRoutes from './routes/moodle';
import aiRoutes from './routes/ai';
// Import flashcard routes
import flashcardRoutes from './routes/flashcardRoutes';

// Configure dotenv with explicit path to .env file
dotenv.config({ path: path.resolve(__dirname, '../.env') });
console.log('Loading environment variables from:', path.resolve(__dirname, '../.env'));

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: [process.env.FRONTEND_URL || "http://localhost:3000", "http://localhost:3001"],
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors({
  origin: [process.env.FRONTEND_URL || "http://localhost:3000", "http://localhost:3001"],
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/study-tools', studyToolsRoutes);
app.use('/api/users', userRoutes);
app.use('/api/moodle', moodleRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/flashcards', flashcardRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Campus UnderGround API is running' });
});

// Socket.io connection handling
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  // Join study room
  socket.on('join-study-room', (roomId) => {
    socket.join(roomId);
    console.log(`User ${socket.id} joined study room ${roomId}`);
  });

  // Handle real-time collaboration
  socket.on('flashcard-update', (data) => {
    socket.to(data.roomId).emit('flashcard-updated', data);
  });

  // Handle pomodoro timer updates
  socket.on('timer-update', (data) => {
    socket.to(data.roomId).emit('timer-updated', data);
  });

  // Handle note sharing
  socket.on('note-share', (data) => {
    socket.to(data.roomId).emit('note-shared', data);
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 5000;

server.listen(PORT, () => {
  console.log(`🚀 Campus UnderGround Backend running on port ${PORT}`);
  console.log(`📡 Socket.io server ready for real-time features`);
}); 