# Voice Agent Platform - Deployment Guide

This guide will help you deploy the Voice Agent Platform and configure it with Twilio for AI-powered phone calls.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- A Twilio account with a phone number
- A domain name (optional, but recommended for production)

### 1. Deploy the Application

Run the startup script:
```bash
./start.sh
```

This will:
- Build and start all containers
- Display the webhook URLs for Twilio configuration
- Show you how to access the dashboard

### 2. Access the Application

Once deployed, you can access:
- **Frontend Dashboard**: `http://your-server-ip`
- **Backend API**: `http://your-server-ip:8000`
- **API Documentation**: `http://your-server-ip/docs`
- **Demo Dashboard**: `http://your-server-ip/dashboard` (no login required)

## 🔗 Twilio Configuration

### Webhook URLs

The application provides these webhook endpoints for Twilio:

1. **Webhook URL** (for incoming calls):
   ```
   http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}
   ```

2. **Status Callback URL** (for call status updates):
   ```
   http://your-domain.com/api/v1/voice/twilio/status/{call_id}
   ```

### Configure in Twilio Console

1. **Log into Twilio Console**
   - Go to https://console.twilio.com/
   - Navigate to Phone Numbers > Manage > Active numbers

2. **Select Your Phone Number**
   - Click on your Twilio phone number
   - Go to the "Voice Configuration" section

3. **Set Webhook URLs**
   - **Webhook URL**: `http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}`
   - **Status Callback URL**: `http://your-domain.com/api/v1/voice/twilio/status/{call_id}`
   - **HTTP Method**: POST

4. **Save Configuration**
   - Click "Save Configuration"

## 🌐 Domain Configuration

### For Production (Recommended)

1. **Get a Domain Name**
   - Purchase a domain (e.g., from Namecheap, GoDaddy, etc.)
   - Point it to your server's IP address

2. **Update nginx Configuration**
   - Edit `nginx/nginx.conf`
   - Replace `server_name localhost;` with your domain
   - Uncomment HTTPS redirect section if using SSL

3. **SSL Certificate (Recommended)**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

### For Development/Testing

Use your server's public IP address directly:
- **Webhook URL**: `http://your-server-ip/api/v1/voice/twilio/webhook/{call_id}`
- **Status Callback URL**: `http://your-server-ip/api/v1/voice/twilio/status/{call_id}`

## 🔧 Environment Configuration

### Backend Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_agent_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production

# AI Services
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Twilio (Optional for demo)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# AWS (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket

# Webhook Secret
WEBHOOK_SECRET=your-webhook-secret
```

### Frontend Environment Variables

The frontend will automatically use the backend URL. For production, you may want to set:

```env
NEXT_PUBLIC_API_URL=https://your-domain.com
NEXT_PUBLIC_WS_URL=wss://your-domain.com
```

## 📊 Monitoring and Logs

### View Application Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

### Health Checks
- **Frontend**: `http://your-domain.com/health`
- **Backend**: `http://your-domain.com:8000/health`
- **API Docs**: `http://your-domain.com/docs`

## 🧪 Testing the Integration

### 1. Test the Demo Dashboard
- Go to `http://your-domain.com/dashboard`
- Try the AI calling functionality
- This works without authentication

### 2. Test Twilio Webhooks
- Make a call to your Twilio number
- Check the logs: `docker-compose logs -f backend`
- Verify webhook calls in Twilio console

### 3. Test API Endpoints
```bash
# Test webhook endpoint
curl -X POST http://your-domain.com/api/v1/voice/twilio/webhook/test-call-id \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=ringing&From=+1234567890&To=+0987654321"

# Test status endpoint
curl -X POST http://your-domain.com/api/v1/voice/twilio/status/test-call-id \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallStatus=completed"
```

## 🔒 Security Considerations

### Production Security
1. **Use HTTPS**: Always use SSL certificates in production
2. **Strong Secrets**: Use strong, unique secret keys
3. **Firewall**: Configure firewall to only allow necessary ports
4. **Rate Limiting**: Already configured in nginx
5. **Authentication**: Enable authentication for production use

### Webhook Security
- Webhook endpoints are public (no authentication required)
- This is necessary for Twilio to call your application
- Implement additional validation if needed

## 🚨 Troubleshooting

### Common Issues

1. **Webhooks not receiving calls**
   - Check if your domain is accessible from the internet
   - Verify Twilio webhook URLs are correct
   - Check nginx logs: `docker-compose logs nginx`

2. **Application not starting**
   - Check Docker and Docker Compose are installed
   - Ensure ports 80 and 8000 are available
   - Check logs: `docker-compose logs`

3. **Database connection issues**
   - Ensure PostgreSQL container is running
   - Check database logs: `docker-compose logs postgres`

4. **Frontend not loading**
   - Check if frontend container is healthy
   - Verify nginx is routing correctly
   - Check frontend logs: `docker-compose logs frontend`

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

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your Twilio configuration
3. Test webhook endpoints manually
4. Check the API documentation at `/docs`

## 🎉 Success!

Once configured, your Voice Agent Platform will:
- Handle incoming calls automatically
- Process calls with AI agents
- Store call history and transcripts
- Provide analytics and monitoring
- Support multiple tenants (businesses)

The demo dashboard at `/dashboard` allows you to test the functionality without authentication.