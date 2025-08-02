#!/bin/bash

# Local Configuration Setup Script
# This script handles local configuration for the Voice Agent Platform

set -e

echo "🔧 Local Configuration Setup"
echo "============================"
echo ""

# Function to detect environment
detect_environment() {
    echo "🌍 Environment Detection"
    echo "======================="
    
    # Check if running in development or production
    if [ -f ".env" ]; then
        echo "✅ Found existing .env file"
        ENVIRONMENT="production"
    else
        echo "📝 No .env file found, using development defaults"
        ENVIRONMENT="development"
    fi
    
    # Detect domain/IP
    if [ -n "$DOMAIN" ]; then
        echo "✅ Domain provided: $DOMAIN"
    else
        echo "🌐 No domain specified, will use IP address"
    fi
}

# Function to setup domain configuration
setup_domain() {
    echo ""
    echo "🌐 Domain Configuration"
    echo "======================"
    
    read -p "Enter your domain name (or press Enter to use IP address): " USER_DOMAIN
    
    if [ -n "$USER_DOMAIN" ]; then
        DOMAIN=$USER_DOMAIN
        PROTOCOL="https"
        echo "✅ Using domain: $DOMAIN with HTTPS"
        
        # Update nginx configuration
        sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf
        echo "✅ Updated nginx configuration"
    else
        # Get public IP
        echo "🌐 Detecting public IP address..."
        PUBLIC_IP=$(curl -s https://ipinfo.io/ip 2>/dev/null || curl -s https://icanhazip.com 2>/dev/null || echo "localhost")
        
        if [ "$PUBLIC_IP" = "localhost" ]; then
            read -p "Please enter your server's public IP address: " PUBLIC_IP
        fi
        
        DOMAIN=$PUBLIC_IP
        PROTOCOL="http"
        echo "✅ Using IP address: $DOMAIN with HTTP"
        
        # Update nginx configuration for IP
        sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf
        echo "✅ Updated nginx configuration"
    fi
}

# Function to create environment file
create_env_file() {
    echo ""
    echo "📝 Environment Configuration"
    echo "==========================="
    
    if [ -f ".env" ]; then
        echo "⚠️  .env file already exists"
        read -p "Do you want to overwrite it? (y/N): " OVERWRITE
        
        if [ "$OVERWRITE" != "y" ] && [ "$OVERWRITE" != "Y" ]; then
            echo "Skipping .env creation"
            return
        fi
    fi
    
    # Generate secret keys
    SECRET_KEY=$(openssl rand -hex 32)
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    
    # Create .env file
    cat > .env << EOF
# Voice Agent Platform Environment Configuration
# Generated on: $(date)

# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/voice_agent_db
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=$ENVIRONMENT
DEBUG=false
LOG_LEVEL=INFO

# AI Services
OPENAI_API_KEY=sk-placeholder-key-change-in-production
ELEVENLABS_API_KEY=placeholder-key-change-in-production

# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=placeholder-account-sid
TWILIO_AUTH_TOKEN=placeholder-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=placeholder-access-key
AWS_SECRET_ACCESS_KEY=placeholder-secret-key
AWS_S3_BUCKET=placeholder-bucket
AWS_S3_BUCKET_AUDIO=placeholder-audio-bucket

# Webhook Security
WEBHOOK_SECRET=$WEBHOOK_SECRET

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://$DOMAIN
ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN

# Sentry (Optional)
SENTRY_DSN=

# Additional Settings
PORT=8000
HOST=0.0.0.0
EOF

    echo "✅ Created .env file with secure defaults"
    echo "⚠️  Remember to update API keys and secrets for production"
}

# Function to generate webhook URLs
generate_webhook_urls() {
    echo ""
    echo "🔗 Webhook URL Generation"
    echo "========================="
    
    # Create webhook config file
    cat > webhook-config.txt << EOF
# Twilio Webhook Configuration
# Generated on: $(date)

DOMAIN=$DOMAIN
PROTOCOL=$PROTOCOL

# Webhook URLs for Twilio Console
WEBHOOK_URL=$PROTOCOL://$DOMAIN/api/v1/voice/twilio/webhook/{call_id}
STATUS_CALLBACK_URL=$PROTOCOL://$DOMAIN/api/v1/voice/twilio/status/{call_id}

# Application URLs
DASHBOARD_URL=$PROTOCOL://$DOMAIN/dashboard
API_DOCS_URL=$PROTOCOL://$DOMAIN/docs
HEALTH_CHECK_URL=$PROTOCOL://$DOMAIN/health

# Twilio Console Configuration Steps:
# 1. Go to https://console.twilio.com/
# 2. Navigate to Phone Numbers > Manage > Active numbers
# 3. Click on your phone number
# 4. Go to Voice Configuration section
# 5. Set Webhook URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/webhook/{call_id}
# 6. Set Status Callback URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/status/{call_id}
# 7. Set HTTP Method: POST
# 8. Save Configuration

# Nginx Configuration:
# Updated nginx/nginx.conf with domain: $DOMAIN
EOF

    echo "✅ Generated webhook configuration"
    echo "📄 Configuration saved to: webhook-config.txt"
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "📋 Next Steps"
    echo "============="
    echo ""
    echo "1. 🔧 Update API Keys (if needed):"
    echo "   nano .env"
    echo ""
    echo "2. 🐳 Build and start the application:"
    echo "   docker-compose build --no-cache"
    echo "   docker-compose up -d"
    echo ""
    echo "3. 🔗 Configure Twilio Console:"
    echo "   - Webhook URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/webhook/{call_id}"
    echo "   - Status Callback URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/status/{call_id}"
    echo ""
    echo "4. 🧪 Test the application:"
    echo "   curl http://localhost/health"
    echo "   curl http://localhost:8000/health"
    echo ""
    echo "5. 🌐 Access the dashboard:"
    echo "   $PROTOCOL://$DOMAIN/dashboard"
    echo ""
    echo "📄 Configuration files:"
    echo "   - .env (environment variables)"
    echo "   - webhook-config.txt (Twilio configuration)"
    echo "   - nginx/nginx.conf (web server configuration)"
    echo ""
}

# Function to validate configuration
validate_configuration() {
    echo ""
    echo "✅ Configuration Validation"
    echo "=========================="
    
    # Check if required files exist
    if [ -f ".env" ]; then
        echo "✅ .env file exists"
    else
        echo "❌ .env file missing"
    fi
    
    if [ -f "webhook-config.txt" ]; then
        echo "✅ webhook-config.txt exists"
    else
        echo "❌ webhook-config.txt missing"
    fi
    
    if [ -f "nginx/nginx.conf" ]; then
        echo "✅ nginx configuration exists"
    else
        echo "❌ nginx configuration missing"
    fi
    
    if [ -f "docker-compose.yml" ]; then
        echo "✅ docker-compose.yml exists"
    else
        echo "❌ docker-compose.yml missing"
    fi
    
    echo ""
    echo "🎉 Local configuration setup complete!"
}

# Main execution
main() {
    detect_environment
    setup_domain
    create_env_file
    generate_webhook_urls
    show_next_steps
    validate_configuration
}

# Run main function
main "$@"