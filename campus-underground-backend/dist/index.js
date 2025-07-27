"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const dotenv_1 = __importDefault(require("dotenv"));
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const auth_1 = __importDefault(require("./routes/auth"));
const studyTools_1 = __importDefault(require("./routes/studyTools"));
const users_1 = __importDefault(require("./routes/users"));
const moodle_1 = __importDefault(require("./routes/moodle"));
dotenv_1.default.config();
const app = (0, express_1.default)();
const server = (0, http_1.createServer)(app);
const io = new socket_io_1.Server(server, {
    cors: {
        origin: process.env.FRONTEND_URL || "http://localhost:3000",
        methods: ["GET", "POST"]
    }
});
// Middleware
app.use((0, cors_1.default)({
    origin: process.env.FRONTEND_URL || "http://localhost:3000",
    credentials: true
}));
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
// Routes
app.use('/api/auth', auth_1.default);
app.use('/api/study-tools', studyTools_1.default);
app.use('/api/users', users_1.default);
app.use('/api/moodle', moodle_1.default);
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
//# sourceMappingURL=index.js.map