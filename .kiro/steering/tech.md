# Technology Stack & Build System

## Core Technologies

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (SQLite for local dev)
- **Cache**: Redis
- **ORM**: SQLAlchemy with Alembic migrations
- **Authentication**: JWT with python-jose, bcrypt password hashing
- **WebSockets**: Native FastAPI WebSocket support
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend
- **Framework**: Next.js 14 (React 18, TypeScript)
- **Styling**: Tailwind CSS with Radix UI components
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts
- **Animations**: Framer Motion

### AI & Voice Services
- **Conversational AI**: OpenAI GPT models
- **Voice Synthesis**: ElevenLabs API
- **Audio Processing**: PyDub, FFmpeg
- **Telephony**: Twilio WebRTC integration

### Infrastructure
- **Containerization**: Docker with Docker Compose
- **Reverse Proxy**: Nginx with rate limiting
- **File Storage**: AWS S3 (MinIO for local dev)
- **Cloud Platform**: AWS (EC2, RDS, Lambda)
- **Monitoring**: Sentry for error tracking

## Development Commands

### Full Stack Development
```bash
# Start entire development environment
docker-compose up --build

# Quick start with helper script
./start.sh

# Stop all services
docker-compose down
```

### Backend Development
```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run locally (requires Redis/PostgreSQL)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Run tests
pytest app/tests/ -v

# Code formatting
black . && isort .
```

### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Development server
npm run dev

# Production build
npm run build && npm start

# Type checking
npm run type-check

# Linting
npm run lint

# Tests
npm test
```

### Docker Commands
```bash
# Build specific service
docker-compose build backend
docker-compose build frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f

# Restart services
docker-compose restart backend
```

## Environment Configuration

### Required Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key (generate strong key for production)
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ELEVENLABS_API_KEY`: ElevenLabs API key for voice synthesis
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: Twilio credentials

### Development vs Production
- **Development**: Uses SQLite, MinIO, and relaxed CORS
- **Production**: Requires PostgreSQL, Redis cluster, AWS S3, strict security

## Code Quality Standards
- **Backend**: Black formatting, isort imports, type hints required
- **Frontend**: Prettier formatting, ESLint rules, TypeScript strict mode
- **Testing**: Maintain >80% coverage, write integration tests
- **Documentation**: OpenAPI specs auto-generated, inline comments for complex logic