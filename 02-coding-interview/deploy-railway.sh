#!/bin/bash

# Railway deployment helper script
# This script helps you deploy the coding interview platform to Railway

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header "🚂 Railway Deployment Script"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI is not installed."
    echo "Installing Railway CLI..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install railway
        else
            curl -fsSL https://railway.app/install.sh | sh
        fi
    else
        # Linux/Other
        curl -fsSL https://railway.app/install.sh | sh
    fi
    
    if ! command -v railway &> /dev/null; then
        print_error "Failed to install Railway CLI"
        echo "Please install manually from: https://docs.railway.app/develop/cli"
        exit 1
    fi
    
    print_success "Railway CLI installed successfully!"
fi

# Check if already logged in
print_header "🔐 Authentication"
if ! railway whoami &> /dev/null; then
    echo "Please login to Railway..."
    railway login
    print_success "Logged in successfully!"
else
    USER=$(railway whoami)
    print_success "Already logged in as: $USER"
fi

# Check if we're in a Railway project
print_header "🎯 Project Setup"
if [ ! -f ".railway/config.json" ]; then
    print_warning "No Railway project detected in this directory."
    echo ""
    echo "Would you like to:"
    echo "1) Create a new Railway project"
    echo "2) Link to an existing Railway project"
    echo "3) Exit"
    echo ""
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo "Creating new Railway project..."
            railway init
            print_success "Railway project created!"
            ;;
        2)
            echo "Please enter your Railway project ID:"
            read -p "Project ID: " project_id
            railway link $project_id
            print_success "Linked to existing project!"
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
else
    print_success "Railway project already configured!"
fi

# Set environment variables
print_header "⚙️ Environment Variables"
echo "Setting production environment variables..."

# Required environment variables
railway variables set NODE_ENV=production
railway variables set SERVE_FRONTEND=true
railway variables set FRONTEND_BUILD_PATH=/app/frontend-dist
railway variables set ENABLE_SERVER_EXECUTION=false
railway variables set PYTHONUNBUFFERED=1

# Ask for custom domain
echo ""
read -p "Do you have a custom domain? (y/n): " has_domain
if [[ $has_domain == "y" || $has_domain == "Y" ]]; then
    read -p "Enter your domain (e.g., coding.yourdomain.com): " custom_domain
    railway variables set CORS_ORIGINS="https://$custom_domain,https://*.up.railway.app"
else
    railway variables set CORS_ORIGINS="https://*.up.railway.app"
fi

# Optional: Set a secret key
echo ""
print_warning "Setting a secret key is recommended for production"
read -p "Would you like to set a secret key? (y/n): " set_secret
if [[ $set_secret == "y" || $set_secret == "Y" ]]; then
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    railway variables set SECRET_KEY=$SECRET_KEY
    print_success "Secret key set!"
fi

print_success "Environment variables configured!"

# Deploy
print_header "🚀 Deployment"
echo "Starting deployment to Railway..."
echo ""
echo "This will:"
echo "1. Build your Docker image"
echo "2. Push it to Railway"
echo "3. Start your application"
echo ""
read -p "Ready to deploy? (y/n): " ready
if [[ $ready != "y" && $ready != "Y" ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "Deploying..."
railway up

# Get deployment status
print_header "📊 Deployment Status"
echo "Checking deployment status..."
railway status

# Get the deployment URL
print_header "🌐 Application URL"
echo "Getting your application URL..."
DEPLOY_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$DEPLOY_URL" ]; then
    print_warning "No domain assigned yet."
    echo ""
    echo "To generate a domain, run:"
    echo "  railway domain"
    echo ""
    echo "Or visit your Railway dashboard to configure a domain."
else
    print_success "Your application is deployed at:"
    echo -e "${GREEN}$DEPLOY_URL${NC}"
fi

# Show logs
print_header "📋 Deployment Logs"
echo "Would you like to view the deployment logs?"
read -p "View logs? (y/n): " view_logs
if [[ $view_logs == "y" || $view_logs == "Y" ]]; then
    echo "Streaming logs (press Ctrl+C to stop)..."
    railway logs
fi

# Final instructions
print_header "✅ Deployment Complete!"
echo ""
echo "Next steps:"
echo "1. Visit your Railway dashboard: https://railway.app/dashboard"
echo "2. Monitor your application logs: railway logs"
echo "3. Check deployment status: railway status"
echo "4. Update environment variables: railway variables"
echo ""
if [ ! -z "$DEPLOY_URL" ]; then
    echo "Your app is live at: ${GREEN}$DEPLOY_URL${NC}"
fi
echo ""
print_success "Happy coding! 🎉"
