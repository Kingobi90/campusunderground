# Campus UnderGround - Modern Tech Stack

##  Tech Stack

### Frontend
- **React.js** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Socket.io Client** for real-time features
- **Supabase Auth** for authentication
- **Framer Motion** for animations

### Backend
- **Node.js** with Express.js
- **TypeScript** for type safety
- **PostgreSQL** database
- **Socket.io** for real-time communication
- **JWT** for authentication
- **bcryptjs** for password hashing
- **Python** for Moodle API integration
- **OpenAI GPT API** for content analysis

### Infrastructure
- **Vercel** for frontend deployment
- **Railway** for backend deployment
- **Supabase** for authentication and storage
- **PostgreSQL** hosted on Railway

## 📁 Project Structure

```
Campus UnderGround/
├── campus-underground-frontend/     # React.js frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── contexts/               # React contexts
│   │   ├── services/               # API services
│   │   └── types/                  # TypeScript types
│   └── package.json
├── campus-underground-backend/      # Node.js backend
│   ├── src/
│   │   ├── routes/                 # API routes
│   │   ├── controllers/            # Route controllers
│   │   ├── middleware/             # Express middleware
│   │   ├── models/                 # Database models
│   │   ├── services/               # Business logic
│   │   └── config/                 # Configuration files
│   ├── moodle_service/             # Python Moodle API service
│   │   ├── moodle_client.py        # Moodle API client
│   │   ├── gpt_service.py          # GPT API service
│   │   ├── api_server.py           # Flask API server
│   │   └── requirements.txt        # Python dependencies
│   └── package.json
├── moodle-api-client/              # Example Moodle API client
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+ (for Moodle API integration)
- PostgreSQL database
- Supabase account
- Moodle API token (for LMS integration)
- OpenAI API key (for GPT integration)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd campus-underground-backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your database and Supabase credentials.

4. **Set up PostgreSQL database:**
   - Create a new PostgreSQL database
   - Run the schema file: `src/config/schema.sql`

5. **Set up Moodle API service:**
   ```bash
   cd moodle_service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
   Edit `moodle_service/.env` with your Moodle API token.

6. **Start all services:**
   ```bash
   ./start-services.sh
   ```
   This script starts both the TypeScript backend and the Python Moodle service.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd campus-underground-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your API and Supabase credentials.

4. **Start development server:**
   ```bash
   npm start
   ```

## 🔧 Environment Variables

### Backend (.env)
```env
# Server Configuration
PORT=5000
NODE_ENV=development

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campus_underground
DB_USER=postgres
DB_PASSWORD=your_password_here

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Moodle API Configuration
MOODLE_API_URL=http://localhost:5002
```

### Moodle Service (.env)
```env
# Moodle API Configuration
MOODLE_URL=https://moodle.concordia.ca
MOODLE_API_TOKEN=your_moodle_api_token_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
```

### Frontend (.env)
```env
# API Configuration
REACT_APP_API_URL=http://localhost:5000

# Supabase Configuration
REACT_APP_SUPABASE_URL=your_supabase_url_here
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Socket.io Configuration
REACT_APP_SOCKET_URL=http://localhost:5000
```

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Railway)
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

## 📊 Database Schema

The application uses PostgreSQL with the following main tables:
- `users` - User accounts and profiles
- `flashcard_decks` - Flashcard collections
- `flashcards` - Individual flashcard cards
- `notes` - User notes and content
- `pomodoro_sessions` - Study session tracking
- `study_groups` - Collaborative study groups
- `study_group_members` - Group membership
- `shared_notes` - Shared note content

## 🔐 Authentication

The application uses Supabase Auth for:
- User registration and login
- Password reset functionality
- Social login (Google, Microsoft)
- JWT token management

## 📡 Real-time Features

Socket.io is used for:
- Real-time flashcard collaboration
- Live pomodoro timer sharing
- Instant note sharing
- Study group chat functionality

## 🎨 UI/UX Features

- **Dark theme** with yellow accent colors
- **Responsive design** for all devices
- **Smooth animations** with Framer Motion
- **Modern interface** with Tailwind CSS
- **Accessible** components and navigation

## 🔄 Migration from Original

The new tech stack provides:
- **Better performance** with React's virtual DOM
- **Type safety** with TypeScript
- **Scalable architecture** with proper separation of concerns
- **Real-time capabilities** with Socket.io
- **Modern development experience** with hot reloading
- **Better state management** with React Context
- **Professional deployment** with Vercel and Railway

## 🚧 Development Status

- ✅ Project structure setup
- ✅ Basic routing and navigation
- ✅ Authentication system
- ✅ Database schema
- ✅ API endpoints
- ✅ Moodle LMS integration
- ✅ GPT API integration
- ✅ Content analysis with AI
- 🚧 Study tools implementation
- 🚧 Real-time features
- 🚧 Advanced UI components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.
