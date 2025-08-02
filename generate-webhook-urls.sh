#!/bin/bash

# Webhook URL Generator for Twilio Configuration
# This script generates the webhook URLs you need to configure in Twilio Console

echo "🔗 Twilio Webhook URL Generator"
echo "================================"
echo ""

# Function to get public IP
get_public_ip() {
    echo "🌐 Detecting your public IP address..."
    PUBLIC_IP=$(curl -s https://ipinfo.io/ip 2>/dev/null || curl -s https://icanhazip.com 2>/dev/null || echo "unknown")
    if [ "$PUBLIC_IP" = "unknown" ]; then
        echo "⚠️  Could not detect public IP automatically"
        read -p "Please enter your server's public IP address: " PUBLIC_IP
    else
        echo "✅ Detected public IP: $PUBLIC_IP"
    fi
}

# Function to get domain
get_domain() {
    echo ""
    echo "🌍 Domain Configuration"
    echo "======================"
    echo "1. Use public IP address (for testing)"
    echo "2. Use custom domain (for production)"
    echo "3. Skip domain configuration"
    echo ""
    read -p "Choose option (1-3): " DOMAIN_CHOICE
    
    case $DOMAIN_CHOICE in
        1)
            get_public_ip
            DOMAIN=$PUBLIC_IP
            PROTOCOL="http"
            ;;
        2)
            read -p "Enter your domain name (e.g., myapp.com): " DOMAIN
            PROTOCOL="https"
            ;;
        3)
            echo "Skipping domain configuration"
            exit 0
            ;;
        *)
            echo "Invalid choice. Using public IP."
            get_public_ip
            DOMAIN=$PUBLIC_IP
            PROTOCOL="http"
            ;;
    esac
}

# Function to generate webhook URLs
generate_webhook_urls() {
    echo ""
    echo "🔗 Generated Webhook URLs for Twilio"
    echo "===================================="
    echo ""
    echo "📞 Webhook URL (for incoming calls):"
    echo "   $PROTOCOL://$DOMAIN/api/v1/voice/twilio/webhook/{call_id}"
    echo ""
    echo "📊 Status Callback URL (for call status updates):"
    echo "   $PROTOCOL://$DOMAIN/api/v1/voice/twilio/status/{call_id}"
    echo ""
    echo "🌐 Dashboard URL:"
    echo "   $PROTOCOL://$DOMAIN/dashboard"
    echo ""
    echo "📚 API Documentation:"
    echo "   $PROTOCOL://$DOMAIN/docs"
    echo ""
}

# Function to show Twilio configuration steps
show_twilio_steps() {
    echo "📋 Twilio Console Configuration Steps"
    echo "===================================="
    echo ""
    echo "1. 🔐 Log into Twilio Console"
    echo "   Go to: https://console.twilio.com/"
    echo ""
    echo "2. 📞 Navigate to Phone Numbers"
    echo "   Go to: Phone Numbers > Manage > Active numbers"
    echo ""
    echo "3. ⚙️  Configure Your Phone Number"
    echo "   - Click on your Twilio phone number"
    echo "   - Go to 'Voice Configuration' section"
    echo ""
    echo "4. 🔗 Set Webhook URLs"
    echo "   - Webhook URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/webhook/{call_id}"
    echo "   - Status Callback URL: $PROTOCOL://$DOMAIN/api/v1/voice/twilio/status/{call_id}"
    echo "   - HTTP Method: POST"
    echo ""
    echo "5. 💾 Save Configuration"
    echo "   - Click 'Save Configuration'"
    echo ""
}

# Function to show nginx configuration steps
show_nginx_steps() {
    echo "⚙️  Nginx Configuration Steps"
    echo "============================="
    echo ""
    echo "1. 📝 Update nginx configuration:"
    echo "   Edit: nginx/nginx.conf"
    echo "   Replace 'your-domain.com' with: $DOMAIN"
    echo ""
    if [ "$PROTOCOL" = "https" ]; then
        echo "2. 🔒 SSL Certificate (for HTTPS):"
        echo "   sudo apt install certbot python3-certbot-nginx"
        echo "   sudo certbot --nginx -d $DOMAIN"
        echo ""
    fi
    echo "3. 🔄 Restart nginx:"
    echo "   docker-compose restart nginx"
    echo ""
}

# Function to save configuration to file
save_configuration() {
    CONFIG_FILE="webhook-config.txt"
    echo "💾 Saving configuration to $CONFIG_FILE..."
    
    cat > "$CONFIG_FILE" << EOF
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
# Update nginx/nginx.conf and replace 'your-domain.com' with: $DOMAIN
EOF

    echo "✅ Configuration saved to $CONFIG_FILE"
    echo ""
}

# Main execution
main() {
    get_domain
    generate_webhook_urls
    show_twilio_steps
    show_nginx_steps
    save_configuration
    
    echo "🎉 Configuration Complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update nginx/nginx.conf with your domain: $DOMAIN"
    echo "2. Configure the webhook URLs in Twilio Console"
    echo "3. Test the webhook endpoints"
    echo "4. Start your application: docker-compose up -d"
    echo ""
    echo "📄 Configuration details saved to: webhook-config.txt"
}

# Run main function
main "$@"