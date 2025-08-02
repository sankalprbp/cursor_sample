# Manual Deployment Guide

This guide shows how to deploy the Voice Agent Platform without Docker, using the services we've already set up.

## 🚀 Current Setup

We have successfully:
- ✅ Modified the dashboard to work without authentication
- ✅ Created demo AI calling functionality
- ✅ Updated nginx configuration for webhook endpoints
- ✅ Created deployment scripts and guides

## 📋 What You Need

### For Production Deployment:
1. **A server with public IP** (AWS EC2, DigitalOcean, etc.)
2. **Docker and Docker Compose** installed on the server
3. **A domain name** (optional but recommended)
4. **Twilio account** with a phone number

### For Testing (Current Setup):
- The application is already running locally
- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (when started)

## 🔗 Twilio Webhook URLs

Once you deploy to a server with a public IP, use these URLs in your Twilio console:

### Webhook URL:
```
http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}
```

### Status Callback URL:
```
http://your-domain.com/api/v1/voice/twilio/status/{call_id}
```

## 🚀 Deployment Steps

### Option 1: Using Docker (Recommended)

1. **On your server, install Docker:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Upload the project to your server:**
   ```bash
   # From your local machine
   scp -r . user@your-server-ip:/home/user/voice-agent-platform
   ```

3. **On the server, start the application:**
   ```bash
   cd voice-agent-platform
   chmod +x start.sh
   ./start.sh
   ```

4. **Get your webhook URLs:**
   The script will show you the exact URLs to use in Twilio console.

### Option 2: Manual Deployment

1. **Install dependencies on server:**
   ```bash
   # Backend (Python)
   sudo apt install python3 python3-pip python3-venv
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend (Node.js)
   sudo apt install nodejs npm
   cd frontend
   npm install
   ```

2. **Start the services:**
   ```bash
   # Backend
   cd backend
   source venv/bin/activate
   python main.py
   
   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

3. **Configure nginx:**
   ```bash
   sudo apt install nginx
   sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
   sudo systemctl restart nginx
   ```

## 🌐 Domain Configuration

### For Production:

1. **Get a domain name** and point it to your server IP
2. **Update nginx configuration:**
   ```bash
   # Edit nginx.conf
   sudo nano /etc/nginx/nginx.conf
   # Replace 'localhost' with your domain name
   ```

3. **Get SSL certificate:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### For Testing:
Use your server's public IP address directly in the webhook URLs.

## 🔧 Twilio Console Configuration

1. **Log into Twilio Console:**
   - Go to https://console.twilio.com/
   - Navigate to Phone Numbers > Manage > Active numbers

2. **Configure your phone number:**
   - Click on your Twilio phone number
   - In "Voice Configuration" section:
     - **Webhook URL**: `http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}`
     - **Status Callback URL**: `http://your-domain.com/api/v1/voice/twilio/status/{call_id}`
     - **HTTP Method**: POST

3. **Save the configuration**

## 🧪 Testing

### Test the Demo Dashboard:
- Go to: `http://your-domain.com/dashboard`
- Try the AI calling functionality
- No login required

### Test Webhook Endpoints:
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

## 📊 Monitoring

### View Logs:
```bash
# Backend logs
tail -f backend/logs/app.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

### Health Checks:
- Frontend: `http://your-domain.com/health`
- Backend: `http://your-domain.com:8000/health`
- API Docs: `http://your-domain.com/docs`

## 🔒 Security Notes

1. **Webhook endpoints are public** (no authentication required)
   - This is necessary for Twilio to call your application
   - The endpoints are designed to be secure for webhook use

2. **For production:**
   - Use HTTPS (SSL certificates)
   - Configure firewall properly
   - Use strong secret keys
   - Enable authentication for admin features

## 🎉 Success!

Once configured:
- ✅ Your application will be accessible via webhook URLs
- ✅ Twilio can send call events to your application
- ✅ The demo dashboard works without authentication
- ✅ AI calling functionality is available for testing

The webhook URLs will be:
- **Webhook URL**: `http://your-domain.com/api/v1/voice/twilio/webhook/{call_id}`
- **Status Callback URL**: `http://your-domain.com/api/v1/voice/twilio/status/{call_id}`

Replace `your-domain.com` with your actual domain or server IP address.