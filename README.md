# Multi-Tenant AI Voice Agent Platform

A comprehensive platform that provides AI-powered voice agents for businesses to handle incoming calls, eliminating the need for traditional customer support, receptionists, and front desk staff.

## 🚀 Features

### Core Platform
- **Multi-tenant Architecture**: Isolated environments for each business client
- **AI Voice Agent**: Powered by OpenAI GPT models with ElevenLabs voice synthesis
- **Knowledge Base Management**: Upload and manage custom knowledge bases per tenant
- **Real-time Call Handling**: WebRTC-based telephony integration
- **Webhook Alerts**: Customizable webhook notifications for various events
- **Audio Logging**: Complete call recording and transcript storage

### Admin Dashboard
- **Usage Analytics**: Comprehensive usage tracking and analytics
- **Billing Management**: Usage-based billing with detailed reporting
- **Audio Logs**: Call history with playback capabilities
- **Client Overview**: Interactive charts and dashboards
- **Tenant Management**: Complete multi-tenant administration

## 🛠 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (TypeScript)
- **AI/ML**: OpenAI GPT models
- **Voice Synthesis**: ElevenLabs API
- **Infrastructure**: AWS (EC2, RDS, S3, Lambda)
 - **Database**: PostgreSQL (SQLite for local dev)
- **Real-time**: WebSockets, WebRTC
- **Containerization**: Docker
- **Version Control**: GitHub

## 📁 Project Structure

```
voice-agent-platform/
├── backend/              # FastAPI backend
├── frontend/             # React frontend
├── infrastructure/       # AWS deployment configs
├── docs/                 # Documentation
├── scripts/              # Deployment and utility scripts
└── docker-compose.yml    # Development environment
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- AWS CLI configured
- OpenAI API key
- ElevenLabs API key

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd voice-agent-platform
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
# SQLite is the default for quick setup.
# To use PostgreSQL instead, set DATABASE_URL to your Postgres connection string.
```

3. Start development environment:
```bash
docker-compose up --build
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Dashboard: http://localhost:3000/admin
- Login functionality is in progress

## 📋 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## 🏗 Architecture

### Backend Services
- **Auth Service**: Multi-tenant authentication and authorization
- **Voice Service**: Call handling and AI integration
- **Knowledge Service**: Knowledge base management
- **Webhook Service**: Event notifications
- **Analytics Service**: Usage tracking and billing
- **Admin Service**: Platform administration

### Frontend Applications
- **Client Dashboard**: Tenant-specific interface
- **Admin Panel**: Platform administration interface
- **Voice Interface**: Real-time call handling UI

## 🔧 Configuration

### OpenAI Configuration
```yaml
openai:
  api_key: "your-openai-api-key"
  model: "gpt-4"
  max_tokens: 1000
```

### ElevenLabs Configuration
```yaml
elevenlabs:
  api_key: "your-elevenlabs-api-key"
  voice_id: "default-voice-id"
  stability: 0.5
  similarity_boost: 0.75
```

### AWS Configuration
```yaml
aws:
  region: "us-east-1"
  s3_bucket: "voice-agent-storage"
  rds_endpoint: "your-rds-endpoint"
```

## 📊 Monitoring & Analytics

- Real-time call analytics
- Usage metrics and billing
- Performance monitoring
- Error tracking and alerting

## 🔒 Security

- Multi-tenant data isolation
- API key management
- Encrypted audio storage
- GDPR compliance ready

## 📱 Mobile Support

- Responsive web interface
- Progressive Web App (PWA) capabilities
- Mobile-optimized call handling

## 🤝 Contributing

Please read our contributing guidelines and code of conduct before submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Documentation: `/docs`
- Issues: GitHub Issues
- Email: support@voice-agent-platform.com