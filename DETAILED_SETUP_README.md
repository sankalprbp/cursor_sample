# Multi-Tenant AI Voice Agent Platform - Complete Setup Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Prerequisites & System Requirements](#prerequisites--system-requirements)
4. [Environment Setup](#environment-setup)
5. [Step-by-Step Installation](#step-by-step-installation)
6. [Configuration Guide](#configuration-guide)
7. [Running the Platform](#running-the-platform)
8. [Understanding the Components](#understanding-the-components)
9. [API Usage Examples](#api-usage-examples)
10. [Troubleshooting](#troubleshooting)
11. [Development Workflow](#development-workflow)
12. [Production Deployment](#production-deployment)

## 🎯 Project Overview

This is a **Multi-Tenant AI Voice Agent Platform** that enables businesses to deploy AI-powered voice assistants for handling incoming calls. The platform provides complete isolation between tenants while sharing infrastructure for cost efficiency.

### Key Features
- **Multi-tenant Architecture**: Complete data isolation between clients
- **AI Voice Processing**: OpenAI GPT integration for intelligent conversations
- **Voice Synthesis**: ElevenLabs integration for natural speech generation
- **Real-time Communication**: WebRTC and WebSocket support
- **Knowledge Base Management**: Custom knowledge bases per tenant
- **Call Analytics**: Comprehensive call tracking and analytics
- **Webhook System**: Real-time event notifications
- **Billing & Usage Tracking**: Automated billing with usage metrics
- **Admin Dashboard**: Complete platform administration

## 🏗️ Architecture & Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI 0.104.1 with async/await support
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0
- **Caching**: Redis 7 for session management and caching
- **Authentication**: JWT tokens with role-based access control
- **Task Queue**: Celery with Redis broker for background tasks
- **File Storage**: AWS S3 (MinIO for development)
- **Real-time**: WebSocket connections for live updates

### Frontend (Next.js)
- **Framework**: Next.js 14 with React 18
- **UI Library**: Radix UI components with Tailwind CSS
- **State Management**: Zustand for global state
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts for analytics visualization

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx with rate limiting
- **Monitoring**: Sentry for error tracking
- **Cloud Services**: AWS (S3, RDS, EC2, Lambda)
- **Telephony**: Twilio for phone integration
- **Payment**: Stripe for billing management

### AI & Voice Services
- **Language Model**: OpenAI GPT-4 for conversation handling
- **Voice Synthesis**: ElevenLabs for text-to-speech conversion
- **Speech Recognition**: Google Speech Recognition API
- **Audio Processing**: PyDub for audio manipulation

## 🔧 Prerequisites & System Requirements

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Docker**: Version 20.10+ with Docker Compose
- **Node.js**: Version 18.0+ (for local development)
- **Python**: Version 3.9+ (for local development)
- **Git**: Latest version for version control

### Hardware Requirements
- **CPU**: 2+ cores (4+ recommended for production)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 20GB+ free space
- **Network**: Stable internet connection for AI services

### API Keys Required
- **OpenAI API Key**: For GPT-4 language model
- **ElevenLabs API Key**: For voice synthesis
- **AWS Credentials**: For S3 storage and services
- **Twilio Account**: For phone integration (optional)
- **Stripe Keys**: For payment processing (optional)

## 🚀 Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd voice-agent-platform
```

### 2. Create Environment File
```bash
cp .env.example .env
```

### 3. Configure Environment Variables
Edit the `.env` file with your configurations:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Security (Generate strong random keys)
SECRET_KEY=your-super-secret-key-here
WEBHOOK_SECRET=your-webhook-secret-here

# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_agent_db
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=voice_agent_db
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=voice-agent-storage
AWS_S3_BUCKET_AUDIO=voice-agent-audio

# Voice Configuration
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_STABILITY=0.5
ELEVENLABS_SIMILARITY_BOOST=0.75

# OpenAI Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1500
OPENAI_TEMPERATURE=0.7

# Optional Services
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

SENTRY_DSN=https://your-sentry-dsn

# CORS & Security
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80
ALLOWED_HOSTS=*
```

## 📦 Step-by-Step Installation

### Method 1: Docker Compose (Recommended)

#### Step 1: Start All Services
```bash
docker-compose up --build
```

This command will:
- Build the backend FastAPI application
- Build the frontend Next.js application
- Start PostgreSQL database with initialization
- Start Redis cache
- Start MinIO for S3-compatible storage
- Configure Nginx reverse proxy
- Create networks and volumes

#### Step 2: Wait for Services to Start
Monitor the logs to ensure all services are running:
```bash
docker-compose logs -f
```

Look for these success messages:
- `voice_agent_postgres | database system is ready to accept connections`
- `voice_agent_backend | 🚀 Voice Agent Platform started successfully!`
- `voice_agent_frontend | ready - started server on 0.0.0.0:3000`

#### Step 3: Verify Installation
```bash
# Check service health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Method 2: Local Development Setup

#### Backend Setup

1. **Create Virtual Environment**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Note: If you encounter issues with dependencies, refer to the `requirements_troubleshooting_summary.md` file for solutions.

3. **Setup Database**:
```bash
# Start PostgreSQL and Redis using Docker
docker-compose up postgres redis -d

# Run database migrations
alembic upgrade head
```

4. **Start Backend Server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Install Dependencies**:
```bash
cd frontend
npm install
```

2. **Configure Environment**:
```bash
cp .env.local.example .env.local
# Edit .env.local with your API endpoints
```

3. **Start Development Server**:
```bash
npm run dev
```

## ⚙️ Configuration Guide

### Database Configuration

The platform uses PostgreSQL with the following key tables:
- `tenants`: Multi-tenant isolation and configuration
- `users`: User management with role-based access
- `calls`: Call records and analytics
- `knowledge_bases`: Custom knowledge per tenant
- `webhooks`: Event notification system
- `billing_records`: Usage tracking and billing

### Redis Configuration

Redis is used for:
- **Session Management**: JWT token blacklisting
- **Caching**: Frequently accessed data
- **Task Queue**: Celery background tasks
- **WebSocket State**: Real-time connection management

### Voice Configuration

#### OpenAI Settings
```python
OPENAI_MODEL = "gpt-4"           # Language model
OPENAI_MAX_TOKENS = 1500         # Response length limit
OPENAI_TEMPERATURE = 0.7         # Creativity level (0-1)
```

#### ElevenLabs Settings
```python
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Voice character
ELEVENLABS_STABILITY = 0.5                     # Voice consistency
ELEVENLABS_SIMILARITY_BOOST = 0.75            # Voice clarity
```

### Security Configuration

#### JWT Authentication
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Longer refresh tokens
ALGORITHM = "HS256"               # Token signing algorithm
```

#### CORS Settings
```python
ALLOWED_ORIGINS = ["http://localhost:3000"]  # Frontend URLs
ALLOWED_HOSTS = ["*"]                        # API access hosts
```

## 🎮 Running the Platform

### Access Points

Once running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application interface |
| Backend API | http://localhost:8000 | REST API endpoints |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Admin Panel | http://localhost:3000/admin | Platform administration |
| MinIO Console | http://localhost:9001 | File storage management |

### Default Credentials

**Super Admin Account:**
- Email: `admin@voiceagent.platform`
- Password: `admin123`
- Role: Super Admin (platform-wide access)

**Demo Tenant Admin:**
- Email: `admin@demo.com`
- Password: `admin123`
- Role: Tenant Admin (demo tenant access)

⚠️ **Important**: Change these passwords immediately in production!

### Initial Setup Steps

1. **Login as Super Admin**:
   - Go to http://localhost:3000
   - Login with super admin credentials
   - Access admin dashboard

2. **Create Your First Tenant**:
   - Navigate to Tenant Management
   - Click "Create New Tenant"
   - Fill in tenant information
   - Set resource limits

3. **Configure AI Settings**:
   - Go to AI Configuration
   - Set OpenAI model preferences
   - Configure ElevenLabs voice settings
   - Test voice synthesis

4. **Upload Knowledge Base**:
   - Switch to tenant view
   - Go to Knowledge Base section
   - Upload documents (PDF, TXT, DOCX)
   - Wait for processing completion

5. **Test Voice Agent**:
   - Go to Call Testing
   - Start a test conversation
   - Verify AI responses and voice quality

## 🧩 Understanding the Components

### Backend Architecture

#### 1. FastAPI Application (main.py)
```python
# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database, Redis, WebSocket manager
    # Shutdown: Clean up connections
```

Key features:
- Async/await for high performance
- Automatic API documentation generation
- Built-in validation with Pydantic
- Middleware for CORS, security, and rate limiting

#### 2. Database Models (app/models/)

**Tenant Model** (tenant.py):
```python
class Tenant(Base):
    id: UUID
    name: str
    subdomain: str  # Unique identifier
    status: TenantStatus
    agent_personality: str
    max_monthly_calls: int
    # ... more fields
```

**User Model** (user.py):
```python
class User(Base):
    id: UUID
    email: str
    tenant_id: Optional[UUID]  # None for super admins
    role: UserRole
    # ... more fields
```

**Call Model** (call.py):
```python
class Call(Base):
    id: UUID
    tenant_id: UUID
    caller_number: str
    status: CallStatus
    ai_model_used: str
    # ... more fields
```

#### 3. API Endpoints (app/api/v1/)

The API is organized into logical modules:
- **Auth**: Login, logout, token refresh
- **Users**: User management and profiles
- **Tenants**: Multi-tenant administration
- **Calls**: Call management and analytics
- **Knowledge**: Knowledge base operations
- **Webhooks**: Event notification management
- **Admin**: Platform administration

#### 4. WebSocket Management (app/websocket/)

Real-time features:
- Live call status updates
- Analytics dashboard updates
- System notifications
- Connection management with Redis

### Frontend Architecture

#### 1. Next.js App Structure
```
frontend/
├── pages/              # Page routes
├── components/         # Reusable UI components
├── hooks/             # Custom React hooks
├── store/             # Zustand state management
├── utils/             # Utility functions
├── types/             # TypeScript definitions
└── styles/            # Tailwind CSS styles
```

#### 2. State Management
- **Zustand**: Global state for user, tenant, and app state
- **React Query**: Server state management and caching
- **React Hook Form**: Form state management

#### 3. UI Components
- **Radix UI**: Accessible component primitives
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Animations and transitions
- **Lucide React**: Icon library

### Infrastructure Components

#### 1. Nginx Reverse Proxy
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    
    location /api/ {
        proxy_pass http://backend;
    }
    
    location / {
        proxy_pass http://frontend;
    }
}
```

Features:
- Load balancing
- Rate limiting
- Security headers
- Static file serving
- SSL termination (production)

#### 2. Docker Compose Services

**PostgreSQL Database**:
- Persistent data with volumes
- Automatic initialization with SQL scripts
- Performance tuning for voice application workloads

**Redis Cache**:
- Session storage
- Task queue for Celery
- WebSocket state management

**MinIO Storage**:
- S3-compatible object storage
- Audio file storage
- Document storage for knowledge bases

## 📡 API Usage Examples

### Authentication

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Authenticated Requests
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Tenant Management

#### Get Current Tenant
```bash
curl -X GET "http://localhost:8000/api/v1/tenants/current" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update Tenant Settings
```bash
curl -X PUT "http://localhost:8000/api/v1/tenants/current" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "My AI Assistant",
    "agent_personality": "You are a helpful customer service representative...",
    "max_concurrent_calls": 5
  }'
```

### Knowledge Base Management

#### Upload Document
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "title=Company Handbook" \
  -F "description=Internal company policies and procedures"
```

#### Query Knowledge Base
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the company office hours?",
    "max_results": 5
  }'
```

### Call Management

#### Start Call Session
```bash
curl -X POST "http://localhost:8000/api/v1/calls" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "caller_number": "+1234567890",
    "call_type": "incoming"
  }'
```

#### Get Call Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/calls/analytics?period=monthly" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### WebSocket Connection

#### Connect to Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tenant/{tenant_id}?token={jwt_token}');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};

// Send message
ws.send(JSON.stringify({
    type: 'call_status_request',
    call_id: 'uuid-here'
}));
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up postgres -d
```

#### 2. Redis Connection Failed
```bash
# Check Redis status
docker-compose logs redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

#### 3. API Authentication Errors
- Verify JWT token is not expired
- Check SECRET_KEY configuration
- Ensure proper Authorization header format

#### 4. File Upload Issues
- Check MAX_FILE_SIZE_MB setting
- Verify ALLOWED_FILE_TYPES configuration
- Ensure proper file permissions

#### 5. Voice Synthesis Errors
- Verify ElevenLabs API key
- Check API quota and usage limits
- Test with different voice IDs

### Debug Mode

Enable detailed logging:
```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# View detailed logs
docker-compose logs -f backend
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/api/v1/admin/system/status \
  -H "Authorization: Bearer SUPER_ADMIN_TOKEN"
```

### Performance Monitoring

Monitor key metrics:
- API response times
- Database query performance
- Redis memory usage
- WebSocket connection count
- Audio processing latency

## 🚀 Development Workflow

### Code Style and Standards

#### Backend (Python)
```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

#### Frontend (TypeScript)
```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Testing

#### Backend Tests
```bash
cd backend
pytest app/tests/ -v --cov=app
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Database Migrations

#### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Add new feature"
```

#### Apply Migrations
```bash
alembic upgrade head
```

#### Rollback Migration
```bash
alembic downgrade -1
```

### Hot Reloading

Both backend and frontend support hot reloading:
- **Backend**: Changes to Python files automatically restart the server
- **Frontend**: Changes to React components instantly update the browser

## 🌍 Production Deployment

### AWS Infrastructure

#### 1. Database Setup (RDS)
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
  --db-instance-identifier voice-agent-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --allocated-storage 20 \
  --db-name voice_agent_db \
  --master-username postgres \
  --master-user-password YOUR_SECURE_PASSWORD
```

#### 2. Redis Setup (ElastiCache)
```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id voice-agent-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### 3. S3 Buckets
```bash
# Create storage buckets
aws s3 mb s3://voice-agent-storage
aws s3 mb s3://voice-agent-audio
aws s3 mb s3://voice-agent-documents
```

#### 4. ECS Deployment
```bash
# Build and push images
docker build -t voice-agent-backend ./backend
docker tag voice-agent-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/voice-agent-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/voice-agent-backend:latest

# Deploy to ECS
aws ecs update-service \
  --cluster voice-agent-cluster \
  --service voice-agent-backend \
  --force-new-deployment
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY and WEBHOOK_SECRET
- [ ] Configure SSL/TLS certificates
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable CloudWatch logging and monitoring
- [ ] Configure backup strategies
- [ ] Set up auto-scaling policies
- [ ] Implement proper IAM roles and policies
- [ ] Enable encryption at rest and in transit
- [ ] Configure rate limiting and DDoS protection

### Environment Variables for Production

```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-super-secure-secret-key-minimum-32-characters
WEBHOOK_SECRET=your-webhook-secret-for-event-verification

# Database (RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/voice_agent_db

# Redis (ElastiCache)
REDIS_URL=redis://your-elasticache-endpoint:6379/0

# AWS Production
AWS_S3_BUCKET=your-production-s3-bucket
AWS_S3_BUCKET_AUDIO=your-production-audio-bucket

# Production URLs
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,app.yourdomain.com

# Monitoring
SENTRY_DSN=https://your-production-sentry-dsn
```

### Monitoring and Alerting

Set up monitoring for:
- Application availability and response times
- Database performance and connection pools
- Redis memory usage and hit rates
- S3 storage usage and costs
- API usage and rate limiting
- Voice synthesis API usage and costs
- WebSocket connection stability

## 📞 Support and Resources

### Documentation
- API Documentation: http://localhost:8000/docs
- Architecture Guide: `/docs/architecture.md`
- Troubleshooting Guide: `requirements_troubleshooting_summary.md`

### Community and Support
- GitHub Issues: Report bugs and request features
- Discord Community: Real-time chat and support
- Email Support: support@voiceagent.platform

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

This platform provides enterprise-grade capabilities for AI voice agents with complete multi-tenancy, scalability, and comprehensive features for modern business communication needs!