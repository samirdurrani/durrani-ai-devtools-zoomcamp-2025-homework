# 🚂 Railway Deployment Guide

## Overview

This guide will help you deploy your Online Coding Interview Platform to Railway in just a few minutes!

## 🚀 Quick Start (5 minutes)

### Option 1: One-Click Deploy (Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/)

*Note: After clicking, you'll need to configure the template with your GitHub repo*

### Option 2: CLI Deployment (Recommended)

```bash
# Run the deployment script
./deploy-railway.sh
```

This script will:
- Install Railway CLI if needed
- Log you in to Railway
- Create/link a project
- Set all environment variables
- Deploy your application
- Show you the live URL

### Option 3: Manual Deployment

#### Step 1: Install Railway CLI

**macOS:**
```bash
brew install railway
# or
curl -fsSL https://railway.app/install.sh | sh
```

**Linux/Windows WSL:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

#### Step 2: Login and Initialize

```bash
# Login to Railway
railway login

# Create a new project
railway init

# Or link to existing project
railway link
```

#### Step 3: Set Environment Variables

```bash
# Required variables
railway variables set NODE_ENV=production
railway variables set SERVE_FRONTEND=true
railway variables set FRONTEND_BUILD_PATH=/app/frontend-dist
railway variables set ENABLE_SERVER_EXECUTION=false
railway variables set PYTHONUNBUFFERED=1
railway variables set CORS_ORIGINS="https://*.up.railway.app"

# Optional: Set a secret key
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

#### Step 4: Deploy

```bash
# Deploy to Railway
railway up

# Get your domain
railway domain
```

## 🔗 GitHub Integration

### Setup Automatic Deployments

1. **Get your Railway Token:**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click your profile → Account Settings
   - Go to Tokens → Create Token
   - Copy the token

2. **Add Token to GitHub:**
   - Go to your GitHub repo
   - Settings → Secrets and variables → Actions
   - Add new secret: `RAILWAY_TOKEN`
   - Paste your Railway token

3. **Push to Deploy:**
   ```bash
   git add .
   git commit -m "Add Railway deployment"
   git push origin main
   ```

Now every push to `main` will automatically deploy!

## 🌐 Custom Domain Setup

### Adding Your Domain

1. **In Railway Dashboard:**
   - Go to your project
   - Click on Settings
   - Go to Domains
   - Add your custom domain

2. **Update DNS:**
   ```
   Type: CNAME
   Name: coding (or your subdomain)
   Value: [your-app].up.railway.app
   ```

3. **Update CORS:**
   ```bash
   railway variables set CORS_ORIGINS="https://yourdomain.com,https://*.up.railway.app"
   ```

## 📊 Configuration Files

### railway.toml

Your project includes a `railway.toml` configuration file:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "cd /app/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
```

### Environment Variables

See `railway-env-template.txt` for all available environment variables.

Key variables:
- `NODE_ENV`: Set to "production"
- `SERVE_FRONTEND`: Set to "true" 
- `ENABLE_SERVER_EXECUTION`: Set to "false" for security
- `SECRET_KEY`: Generate with `openssl rand -hex 32`

## 🔍 Monitoring & Management

### View Logs

```bash
# Stream live logs
railway logs

# View last 100 lines
railway logs -n 100
```

### Check Status

```bash
# Deployment status
railway status

# Environment info
railway environment
```

### Update Variables

```bash
# Set a variable
railway variables set KEY=value

# View all variables
railway variables
```

### Restart Application

```bash
# Redeploy (restart)
railway up

# Or from dashboard
# Click "Redeploy" button
```

## 🐛 Troubleshooting

### Common Issues

#### Build Fails

**Problem:** Docker build fails
**Solution:**
```bash
# Check Docker build locally
docker build -t test .

# Check Railway logs
railway logs
```

#### Port Error

**Problem:** App can't bind to port
**Solution:** Make sure your app uses `$PORT` environment variable:
```python
port = int(os.environ.get("PORT", 8000))
```

#### WebSocket Connection Failed

**Problem:** WebSocket won't connect
**Solution:** Update CORS origins:
```bash
railway variables set CORS_ORIGINS="https://your-domain.railway.app"
```

#### Out of Memory

**Problem:** Application crashes with memory errors
**Solution:** 
- Optimize your Docker image (use multi-stage build)
- Upgrade to a paid plan for more resources

### Debug Commands

```bash
# Check deployment logs
railway logs --tail

# View environment
railway environment

# Check project info
railway status

# Restart service
railway up --detach
```

## 💰 Pricing & Limits

### Free Plan (Hobby)
- **$5 credit/month** (~ 500 hours of small instance)
- **512MB RAM**
- **1 vCPU**
- **Sleeps after 10 min inactivity**

### Pro Plan ($20/month)
- **Unlimited hours**
- **8GB RAM**
- **8 vCPU**
- **No sleep**
- **Custom domains**
- **Horizontal scaling**

## 🚀 Production Checklist

Before going to production:

- [ ] Set `SECRET_KEY` environment variable
- [ ] Update `CORS_ORIGINS` with your domain
- [ ] Enable HTTPS (automatic with Railway)
- [ ] Set up error monitoring (Sentry)
- [ ] Configure backup strategy
- [ ] Set up health monitoring
- [ ] Review security settings
- [ ] Test WebSocket connections
- [ ] Load test the application
- [ ] Set up CI/CD with GitHub Actions

## 📚 Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railway Templates](https://railway.app/templates)
- [Railway Discord](https://discord.gg/railway)
- [Status Page](https://status.railway.app)

## 🎉 Success!

Once deployed, your app will be available at:
```
https://[your-app-name].up.railway.app
```

Features available:
- ✅ Real-time collaborative coding
- ✅ WebSocket support
- ✅ Browser-based code execution
- ✅ Multiple language support
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Auto-scaling

---

Need help? Open an issue on GitHub or check Railway's Discord community!
