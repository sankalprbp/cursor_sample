# Nginx and Deployment Updates Summary

## 🎯 Overview
This document summarizes all the updates made to the nginx configuration and deployment process, including webhook URL generation and detailed launch steps.

---

## 📁 Files Created/Modified

### 1. `nginx/nginx.conf` (MODIFIED)
**Changes Made:**
- ✅ Updated `server_name` to support both localhost and custom domains
- ✅ Uncommented and configured HTTPS redirect section
- ✅ Added complete HTTPS server block with SSL configuration
- ✅ Enhanced security headers for HTTPS
- ✅ Maintained all existing webhook endpoints and API routing

**Key Features:**
- **Domain Support**: Now supports `localhost`, `your-domain.com`, and `www.your-domain.com`
- **HTTPS Redirect**: Automatically redirects HTTP to HTTPS for production
- **SSL Configuration**: Complete SSL setup with security headers
- **Webhook Endpoints**: Dedicated routes for Twilio webhooks without rate limiting
- **CORS Support**: Proper CORS headers for all endpoints
- **Health Checks**: Built-in health check endpoints

### 2. `generate-webhook-urls.sh` (NEW)
**Purpose:** Automated webhook URL generation for Twilio configuration

**Features:**
- 🌐 Automatic public IP detection
- 🌍 Domain name input support
- 🔗 Webhook URL generation
- 📋 Twilio console configuration steps
- 💾 Configuration file generation
- ⚙️ Nginx configuration guidance

**Usage:**
```bash
./generate-webhook-urls.sh
```

### 3. `setup-local-config.sh` (NEW)
**Purpose:** Complete local configuration setup automation

**Features:**
- 🔧 Environment detection (development/production)
- 🌐 Domain configuration with IP fallback
- 📝 Automatic .env file creation
- 🔐 Secure secret key generation
- 🔗 Webhook URL generation
- ✅ Configuration validation

**Usage:**
```bash
./setup-local-config.sh
```

### 4. `DEPLOYMENT_GUIDE.md` (COMPLETELY REWRITTEN)
**New Structure:**
- 📋 Detailed prerequisites checklist
- 🔧 Step-by-step local configuration
- 🐳 Docker build and launch instructions
- 🔗 Webhook configuration guide
- 🌐 Domain and SSL setup
- 🧪 Testing and verification steps
- 🔒 Production security setup
- 📊 Monitoring and maintenance
- 🚨 Comprehensive troubleshooting

---

## 🔗 Webhook URL Configuration

### Generated Webhook URLs
The system now automatically generates these webhook URLs for Twilio:

**For HTTP (IP-based):**
```
Webhook URL: http://your-ip-address/api/v1/voice/twilio/webhook/{call_id}
Status Callback URL: http://your-ip-address/api/v1/voice/twilio/status/{call_id}
```

**For HTTPS (Domain-based):**
```
Webhook URL: https://your-domain.com/api/v1/voice/twilio/webhook/{call_id}
Status Callback URL: https://your-domain.com/api/v1/voice/twilio/status/{call_id}
```

### Twilio Console Configuration Steps
1. **Log into Twilio Console**: https://console.twilio.com/
2. **Navigate to Phone Numbers**: Phone Numbers > Manage > Active numbers
3. **Configure Your Phone Number**: Click on your phone number
4. **Set Webhook URLs**:
   - Webhook URL: `{protocol}://{domain}/api/v1/voice/twilio/webhook/{call_id}`
   - Status Callback URL: `{protocol}://{domain}/api/v1/voice/twilio/status/{call_id}`
   - HTTP Method: POST
5. **Save Configuration**

---

## 🚀 Detailed Launch Steps

### Step 1: Prerequisites Check
```bash
# Check Docker installation
docker --version
docker-compose --version

# Check system resources
free -h
df -h
```

### Step 2: Local Configuration
```bash
# Run the local configuration setup
./setup-local-config.sh

# This will:
# - Detect your environment
# - Configure domain/IP
# - Create .env file
# - Generate webhook URLs
# - Update nginx configuration
```

### Step 3: Docker Build and Launch
```bash
# Fix any Docker build issues (if needed)
./fix-docker-build.sh

# Build the application
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Step 4: Health Verification
```bash
# Test all endpoints
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000

# Check logs
docker-compose logs -f
```

### Step 5: Webhook Configuration
```bash
# Generate webhook URLs
./generate-webhook-urls.sh

# Configure in Twilio Console using the generated URLs
```

### Step 6: Testing
```bash
# Test webhook endpoints
curl -X POST http://localhost/api/v1/voice/twilio/webhook/test \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=ringing&From=+1234567890&To=+0987654321"

# Access dashboard
open http://localhost/dashboard
```

---

## 🌐 Domain Configuration Options

### Option 1: Local Development
```bash
# Use localhost for development
./setup-local-config.sh
# Press Enter when asked for domain (uses IP)
```

### Option 2: IP Address Only
```bash
# Use public IP address
./setup-local-config.sh
# Enter your server's public IP when prompted
```

### Option 3: Custom Domain
```bash
# Use custom domain
./setup-local-config.sh
# Enter your domain name when prompted
```

### Option 4: SSL Certificate Setup
```bash
# For production with SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Configuration Files Generated

### 1. `.env` (Environment Variables)
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_agent_db
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=generated-secret-key
ENVIRONMENT=development
DEBUG=false

# AI Services
OPENAI_API_KEY=sk-placeholder-key-change-in-production
ELEVENLABS_API_KEY=placeholder-key-change-in-production

# Webhook Security
WEBHOOK_SECRET=generated-webhook-secret

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://your-domain.com
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### 2. `webhook-config.txt` (Twilio Configuration)
```
# Twilio Webhook Configuration
DOMAIN=your-domain.com
PROTOCOL=https

# Webhook URLs for Twilio Console
WEBHOOK_URL=https://your-domain.com/api/v1/voice/twilio/webhook/{call_id}
STATUS_CALLBACK_URL=https://your-domain.com/api/v1/voice/twilio/status/{call_id}

# Application URLs
DASHBOARD_URL=https://your-domain.com/dashboard
API_DOCS_URL=https://your-domain.com/docs
```

### 3. `nginx/nginx.conf` (Web Server Configuration)
- Updated server names
- HTTPS redirect configuration
- SSL certificate paths
- Security headers
- Webhook endpoint routing

---

## 🔒 Security Features

### Nginx Security Headers
```nginx
# Security headers for HTTPS
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Rate Limiting
```nginx
# API rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

# Webhook endpoints (no rate limiting)
location /api/v1/voice/twilio/webhook/ {
    # No rate limiting for Twilio webhooks
}
```

### SSL Configuration
```nginx
# SSL Security Settings
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

---

## 🧪 Testing and Verification

### Health Check Endpoints
```bash
# Frontend health
curl http://localhost/health

# Backend health
curl http://localhost:8000/health

# Nginx health
curl http://localhost/health
```

### Webhook Testing
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

### Application Testing
```bash
# Test dashboard access
curl -I http://localhost/dashboard

# Test API documentation
curl -I http://localhost/docs

# Test WebSocket connection
curl -I http://localhost/ws/
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

**1. Nginx Configuration Issues**
```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# View nginx logs
docker-compose logs nginx

# Restart nginx
docker-compose restart nginx
```

**2. Webhook Not Receiving Calls**
```bash
# Test webhook endpoint
curl -X POST http://localhost/api/v1/voice/twilio/webhook/test \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=ringing"

# Check domain accessibility
curl -I http://your-domain.com

# Verify Twilio configuration
# Check Twilio console webhook URLs
```

**3. SSL Certificate Issues**
```bash
# Test SSL certificate
openssl s_client -connect your-domain.com:443

# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

**4. Domain Resolution Issues**
```bash
# Test domain resolution
nslookup your-domain.com

# Check DNS propagation
dig your-domain.com

# Test from external network
curl -I http://your-domain.com
```

---

## 📈 Monitoring and Maintenance

### Health Monitoring
```bash
# Set up monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
echo "Health Check - $(date)"
curl -f http://localhost/health || echo "Frontend DOWN"
curl -f http://localhost:8000/health || echo "Backend DOWN"
docker-compose ps | grep -v "Up" && echo "Services DOWN"
EOF

chmod +x monitor.sh
```

### Log Management
```bash
# View recent logs
docker-compose logs --tail=100

# Export logs
docker-compose logs > application-$(date +%Y%m%d).log

# Monitor specific service
docker-compose logs -f backend
```

### Backup Strategy
```bash
# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
  nginx/ .env docker-compose.yml webhook-config.txt

# Backup database
docker-compose exec postgres pg_dump -U postgres voice_agent_db > \
  backup-$(date +%Y%m%d).sql
```

---

## 🎉 Success Indicators

After completing all steps, verify:

- ✅ All Docker containers are running (`docker-compose ps`)
- ✅ Health checks pass (`curl http://localhost/health`)
- ✅ Webhook endpoints respond (`curl -X POST http://localhost/api/v1/voice/twilio/webhook/test`)
- ✅ Dashboard is accessible (`curl -I http://localhost/dashboard`)
- ✅ SSL certificate is valid (if using HTTPS)
- ✅ Twilio webhooks are configured correctly
- ✅ No errors in logs (`docker-compose logs`)
- ✅ Domain resolves correctly (`nslookup your-domain.com`)

---

## 📚 Additional Resources

- **API Documentation**: `http://your-domain.com/docs`
- **Dashboard**: `http://your-domain.com/dashboard`
- **Health Check**: `http://your-domain.com/health`
- **Twilio Console**: https://console.twilio.com/
- **Project Documentation**: See README.md and other .md files

The Voice Agent Platform is now fully configured with comprehensive nginx support, automated webhook URL generation, and detailed deployment instructions! 🚀