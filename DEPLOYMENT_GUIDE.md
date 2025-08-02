# Voice Agent Platform - Complete Deployment Guide

This comprehensive guide will walk you through deploying the Voice Agent Platform step-by-step, including local configuration, domain setup, and Twilio integration.

## 🚀 Quick Start Overview

1. **Prerequisites Check** - Ensure all requirements are met
2. **Local Configuration** - Set up environment and domain
3. **Docker Build** - Build and start the application
4. **Webhook Configuration** - Generate and configure Twilio webhooks
5. **Testing & Verification** - Test all components
6. **Production Deployment** - SSL and security setup

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 10GB free space
- **Network**: Stable internet connection

### Required Software
```bash
# Check if Docker is installed
docker --version
docker-compose --version

# If not installed, run the installation script
chmod +x get-docker.sh
./get-docker.sh
```

### Required Accounts
- **Twilio Account**: [Sign up here](https://www.twilio.com/try-twilio)
- **OpenAI API Key**: [Get API key here](https://platform.openai.com/api-keys)
- **ElevenLabs API Key** (optional): [Get API key here](https://elevenlabs.io/)
- **Domain Name** (for production): Purchase from any registrar

---

## 🔧 Step 1: Local Configuration

### 1.1 Clone and Navigate
```bash
# Navigate to project directory
cd /path/to/voice-agent-platform

# Verify all files are present
ls -la
```

### 1.2 Fix Docker Build Issues (if needed)
```bash
# Run the Docker fix script if you encounter build issues
./fix-docker-build.sh

# Or use the quick fix
./quick-fix.sh
```

### 1.3 Generate Webhook URLs
```bash
# Generate webhook URLs for Twilio
./generate-webhook-urls.sh
```

This script will:
- Detect your public IP address
- Ask for your domain (if using custom domain)
- Generate webhook URLs for Twilio Console
- Save configuration to `webhook-config.txt`

### 1.4 Update Nginx Configuration

**For Local Development:**
```bash
# Edit nginx configuration
nano nginx/nginx.conf

# Replace 'your-domain.com' with your actual domain or IP
# For local testing, you can use 'localhost'
```

**For Production:**
```bash
# Edit nginx configuration
nano nginx/nginx.conf

# Replace 'your-domain.com' with your actual domain
# Example: server_name myapp.com www.myapp.com;
```

### 1.5 Environment Configuration (Optional)

Create a `.env` file in the root directory for custom configuration:

```bash
# Create environment file
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_agent_db
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ENVIRONMENT=production
DEBUG=false

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name

# Webhook Security
WEBHOOK_SECRET=your-webhook-secret-key

# CORS Settings
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
EOF
```

---

## 🐳 Step 2: Docker Build and Launch

### 2.1 Build the Application
```bash
# Build all containers
docker-compose build --no-cache

# Check build status
docker-compose ps
```

### 2.2 Start the Application
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2.3 Verify All Services Are Running
```bash
# Check all containers are healthy
docker-compose ps

# Expected output:
# Name                    Command               State           Ports
# -------------------------------------------------------------------------------
# voice_agent_backend     uvicorn main:app --ho ...   Up      0.0.0.0:8000->8000/tcp
# voice_agent_frontend    node server.js             Up      0.0.0.0:3000->3000/tcp
# voice_agent_nginx       nginx -g daemon off;       Up      0.0.0.0:80->80/tcp
# voice_agent_postgres    docker-entrypoint.s ...   Up      0.0.0.0:5432->5432/tcp
# voice_agent_redis       docker-entrypoint.s ...   Up      0.0.0.0:6379->6379/tcp
```

### 2.4 Health Check
```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend health
curl http://localhost:3000

# Test nginx health
curl http://localhost/health
```

---

## 🔗 Step 3: Webhook Configuration

### 3.1 Get Your Webhook URLs
```bash
# Run the webhook generator
./generate-webhook-urls.sh
```

**Example Output:**
```
🔗 Generated Webhook URLs for Twilio
====================================

📞 Webhook URL (for incoming calls):
   http://your-ip-address/api/v1/voice/twilio/webhook/{call_id}

📊 Status Callback URL (for call status updates):
   http://your-ip-address/api/v1/voice/twilio/status/{call_id}
```

### 3.2 Configure Twilio Console

1. **Log into Twilio Console**
   - Go to: https://console.twilio.com/
   - Sign in with your Twilio account

2. **Navigate to Phone Numbers**
   - Click "Phone Numbers" in the left sidebar
   - Click "Manage" → "Active numbers"

3. **Configure Your Phone Number**
   - Click on your Twilio phone number
   - Scroll to "Voice Configuration" section

4. **Set Webhook URLs**
   - **Webhook URL**: `http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}`
   - **Status Callback URL**: `http://your-domain.com/api/v1/voice/twilio/status/{call_id}`
   - **HTTP Method**: POST
   - **Primary Handler**: Webhook

5. **Save Configuration**
   - Click "Save Configuration"

### 3.3 Test Webhook Endpoints
```bash
# Test webhook endpoint
curl -X POST http://localhost/api/v1/voice/twilio/webhook/test-call \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=ringing&From=+1234567890&To=+0987654321"

# Test status endpoint
curl -X POST http://localhost/api/v1/voice/twilio/status/test-call \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=completed"
```

---

## 🌐 Step 4: Domain and SSL Setup (Production)

### 4.1 Domain Configuration

**For Custom Domain:**
```bash
# Update nginx configuration with your domain
sed -i 's/your-domain.com/YOUR_ACTUAL_DOMAIN.com/g' nginx/nginx.conf

# Restart nginx
docker-compose restart nginx
```

**For IP Address Only:**
```bash
# Update nginx configuration with your IP
sed -i 's/your-domain.com/YOUR_IP_ADDRESS/g' nginx/nginx.conf

# Restart nginx
docker-compose restart nginx
```

### 4.2 SSL Certificate Setup (Recommended)

**Using Let's Encrypt:**
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Test certificate renewal
sudo certbot renew --dry-run
```

**Using Self-Signed Certificate (Development):**
```bash
# Generate self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt

# Update nginx configuration
# Edit nginx/nginx.conf and update SSL certificate paths
```

### 4.3 Firewall Configuration
```bash
# Allow necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## 🧪 Step 5: Testing and Verification

### 5.1 Test Application Access
```bash
# Test frontend
curl -I http://localhost

# Test backend API
curl -I http://localhost:8000/health

# Test API documentation
curl -I http://localhost/docs
```

### 5.2 Test Dashboard
1. Open your browser
2. Navigate to: `http://your-domain.com/dashboard`
3. Try the AI calling functionality
4. Verify call logs are being created

### 5.3 Test Twilio Integration
1. Call your Twilio phone number
2. Check application logs: `docker-compose logs -f backend`
3. Verify webhook calls in Twilio console
4. Check call history in the dashboard

### 5.4 Monitor Application
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx

# Check resource usage
docker stats
```

---

## 🔒 Step 6: Production Security

### 6.1 Environment Security
```bash
# Generate strong secret keys
openssl rand -hex 32

# Update .env file with strong secrets
nano .env
```

### 6.2 Database Security
```bash
# Change default database password
# Edit docker-compose.yml and update POSTGRES_PASSWORD
# Restart services
docker-compose down
docker-compose up -d
```

### 6.3 Network Security
```bash
# Configure firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 Step 7: Monitoring and Maintenance

### 7.1 Health Monitoring
```bash
# Set up health check monitoring
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000

# Check service status
docker-compose ps
```

### 7.2 Log Management
```bash
# View recent logs
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Export logs
docker-compose logs > application.log
```

### 7.3 Backup and Recovery
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres voice_agent_db > backup.sql

# Backup configuration
tar -czf config-backup.tar.gz nginx/ .env docker-compose.yml

# Restore database
docker-compose exec -T postgres psql -U postgres voice_agent_db < backup.sql
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

**1. Docker Build Fails**
```bash
# Fix Docker build issues
./fix-docker-build.sh

# Or use alternative Dockerfile
mv backend/Dockerfile backend/Dockerfile.original
mv backend/Dockerfile.alternative backend/Dockerfile
docker-compose build --no-cache
```

**2. Services Not Starting**
```bash
# Check service status
docker-compose ps

# View detailed logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

**3. Webhooks Not Working**
```bash
# Test webhook endpoints
curl -X POST http://localhost/api/v1/voice/twilio/webhook/test \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=ringing"

# Check nginx logs
docker-compose logs nginx

# Verify domain accessibility
curl -I http://your-domain.com
```

**4. Database Connection Issues**
```bash
# Check database status
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Check database connection
docker-compose exec backend python -c "import psycopg2; print('DB OK')"
```

**5. SSL Certificate Issues**
```bash
# Test SSL certificate
openssl s_client -connect your-domain.com:443

# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## 📞 Support and Resources

### Useful Commands
```bash
# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Stop all services
docker-compose down

# View running containers
docker-compose ps

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend bash
```

### Log Locations
- **Application Logs**: `docker-compose logs -f`
- **Nginx Logs**: `/var/log/nginx/` (inside container)
- **Database Logs**: `docker-compose logs postgres`
- **System Logs**: `journalctl -u docker`

### Configuration Files
- **Docker Compose**: `docker-compose.yml`
- **Nginx Config**: `nginx/nginx.conf`
- **Environment**: `.env`
- **Webhook Config**: `webhook-config.txt`

---

## 🎉 Success Checklist

After completing all steps, verify:

- ✅ All Docker containers are running
- ✅ Application is accessible at your domain
- ✅ SSL certificate is working (if using HTTPS)
- ✅ Twilio webhooks are configured
- ✅ Dashboard is functional
- ✅ AI calling works
- ✅ Call logs are being created
- ✅ Health checks pass
- ✅ Logs show no errors

---

## 📚 Additional Resources

- **API Documentation**: `http://your-domain.com/docs`
- **Dashboard**: `http://your-domain.com/dashboard`
- **Health Check**: `http://your-domain.com/health`
- **Twilio Console**: https://console.twilio.com/
- **Project Documentation**: See README.md and other .md files

Your Voice Agent Platform is now fully deployed and ready to handle AI-powered phone calls! 🚀