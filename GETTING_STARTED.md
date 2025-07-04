# Getting Started - Multi-Tenant AI Voice Agent Platform

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)
- OpenAI API key
- ElevenLabs API key
- Twilio account (optional, for phone integration)

### 1. Environment Setup

1. **Clone and Navigate:**
```bash
git clone <repository-url>
cd voice-agent-platform
```

2. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start Development Environment:**
```bash
docker-compose up --build
```

### 2. Access the Platform

Once running, you can access:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Admin Panel:** http://localhost:3000/admin
- **MinIO (Storage):** http://localhost:9001

### 3. Default Credentials

**Super Admin:**
- Email: `admin@voiceagent.platform`
- Password: `admin123`

**Demo Tenant Admin:**
- Email: `admin@demo.com`
- Password: `admin123`

⚠️ **Change these passwords immediately in production!**

## 🎯 Key Features

### ✅ Implemented
- **Multi-tenant Architecture** with complete data isolation
- **User Authentication & Authorization** with JWT tokens
- **Role-based Access Control** (Super Admin, Tenant Admin, User)
- **Database Models** for all platform entities
- **Real-time WebSocket** connections for live updates
- **Docker Containerization** for easy deployment
- **Nginx Reverse Proxy** with rate limiting and security headers
- **Database Initialization** with sample data

### 🚧 To Be Implemented
- Voice Agent Core (OpenAI + ElevenLabs integration)
- Knowledge Base Processing
- Call Management System
- Webhook Delivery System
- Billing & Analytics
- Frontend React Application
- Twilio Phone Integration

## 📁 Project Structure

```
voice-agent-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic (to implement)
│   │   └── websocket/      # WebSocket handling
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # React frontend
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── nginx/                 # Reverse proxy configuration
├── infrastructure/        # Deployment configs (to add)
├── docker-compose.yml     # Development environment
└── .env.example          # Environment template
```

## 🔧 Development Workflow

### Backend Development

1. **Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run Locally:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Database Migrations:**
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend Development

1. **Install Dependencies:**
```bash
cd frontend
npm install
```

2. **Run Development Server:**
```bash
npm run dev
```

3. **Build for Production:**
```bash
npm run build
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest app/tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 API Usage Examples

### Authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "admin123"}'

# Use the returned token for authenticated requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Tenant Management
```bash
# Get current tenant info
curl -X GET "http://localhost:8000/api/v1/tenants/current" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔐 Security Features

- **JWT Authentication** with role-based access control
- **Password Hashing** with bcrypt
- **Rate Limiting** on API endpoints
- **CORS Protection** with configurable origins
- **SQL Injection Protection** with SQLAlchemy ORM
- **Input Validation** with Pydantic models
- **Security Headers** via Nginx

## 📈 Monitoring & Logging

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database status
curl http://localhost:8000/api/v1/admin/system/status
```

### Logs
```bash
# View application logs
docker-compose logs -f backend

# View all service logs
docker-compose logs -f
```

## 🚀 Deployment

### Production Checklist

1. **Security:**
   - [ ] Change default passwords
   - [ ] Generate strong JWT secret key
   - [ ] Configure SSL/HTTPS
   - [ ] Set up proper CORS origins
   - [ ] Enable production logging

2. **Infrastructure:**
   - [ ] Set up AWS RDS for PostgreSQL
   - [ ] Configure Redis cluster
   - [ ] Set up S3 buckets for file storage
   - [ ] Configure CDN (CloudFront)
   - [ ] Set up monitoring (CloudWatch)

3. **Environment Variables:**
   - [ ] Production database URLs
   - [ ] API keys for external services
   - [ ] Webhook secrets
   - [ ] Email configuration
   - [ ] Monitoring credentials

### AWS Deployment Commands
```bash
# Build and push to ECR
docker build -t voice-agent-backend ./backend
docker tag voice-agent-backend:latest YOUR_ECR_REPO/voice-agent-backend:latest
docker push YOUR_ECR_REPO/voice-agent-backend:latest

# Deploy with ECS or EKS
kubectl apply -f infrastructure/kubernetes/
```

## 🤝 Contributing

1. **Code Style:**
   - Backend: Black, isort, flake8
   - Frontend: Prettier, ESLint
   - Use conventional commits

2. **Testing:**
   - Write tests for new features
   - Maintain >80% code coverage
   - Test both positive and negative scenarios

3. **Documentation:**
   - Update API documentation
   - Add inline code comments
   - Update README for new features

## 📞 Support

- **Documentation:** [Link to full docs]
- **Issues:** [GitHub Issues]
- **Discord:** [Community chat]
- **Email:** support@voiceagent.platform

## 🎉 Next Steps

1. **Complete the implementation** following the roadmap in `IMPLEMENTATION_STATUS.md`
2. **Add OpenAI integration** for voice conversation handling
3. **Implement ElevenLabs** for voice synthesis
4. **Build the React frontend** with modern UI/UX
5. **Set up Twilio** for phone call integration
6. **Deploy to AWS** for production use

This platform provides the foundation for a enterprise-grade voice agent solution with multi-tenancy, scalability, and comprehensive features!