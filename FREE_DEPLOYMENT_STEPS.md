# 🚀 Free Cloud Deployment - Step-by-Step Guide

Choose your preferred platform and follow the steps below.

---

## Option 1: Railway (Recommended - Best for Beginners) ⭐

### Prerequisites
- GitHub account with your code pushed to a repository
- A free Railway account (sign up at railway.app)

### Deployment Steps

**Step 1: Prepare Your Repository**
```bash
cd phishing_app
git add .
git commit -m "Ready for deployment"
git push origin main
```

**Step 2: Create Railway Account**
1. Go to [https://railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Authorize Railway to access your repositories

**Step 3: Deploy Project**
1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select your `phishing_app` repository
4. Railway auto-detects Python environment

**Step 4: Configure Environment**
1. Railway creates variables automatically
2. Add additional variable:
   - Key: `PYTHONUNBUFFERED`
   - Value: `1`

**Step 5: Set Start Command**
1. In Settings tab, add:
   ```
   python run_api.py
   ```

**Step 6: Deploy**
1. Railway automatically starts deployment
2. Monitor logs in the console
3. Wait for "Deployment successful" message
4. Get your API URL from "Networking" tab

**Step 7: Test Your Deployment**
```bash
# Replace with your Railway URL
curl https://your-railway-url.railway.app/health

# Test prediction
curl -X POST https://your-railway-url.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'
```

**Cost:** $0 (Free $5/month credits)  
**Time:** 10 minutes

---

## Option 2: Streamlit Cloud (UI Only - Free Forever) 🎨

### Prerequisites
- Streamlit app at `src/phishing/ui/app.py`
- GitHub account
- (Optional) Deployed API somewhere else

### Deployment Steps

**Step 1: Sign Up**
1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "Sign up"
3. Choose GitHub for authentication
4. Authorize Streamlit

**Step 2: Deploy App**
1. Click "Create app"
2. Select your repository and branch
3. Enter path: `src/phishing/ui/app.py`
4. Click "Deploy"

**Step 3: Configure API Connection**
1. Edit `src/phishing/ui/app.py`
2. Update API URL:
   ```python
   API_URL = "https://your-railway-api.railway.app"
   ```
3. Push to GitHub
4. Streamlit Cloud auto-redeploys

**Step 4: Access Your App**
1. Streamlit Cloud provides a public URL
2. Share the link!

**Cost:** $0 (Forever)  
**Time:** 5 minutes

---

## Option 3: Oracle Cloud (Always Free) 🚀

### Prerequisites
- Oracle Cloud account (free tier, no credit card needed)
- SSH client installed on your machine

### Deployment Steps

**Step 1: Create Oracle Account**
1. Go to [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)
2. Click "Sign Up"
3. Create free account (always-free tier available)
4. Verify email

**Step 2: Create VM Instance**
1. Login to Oracle Cloud Console
2. Go to Compute → Instances
3. Click "Create Instance"
4. Select:
   - Image: Ubuntu 22.04 (free eligible)
   - Shape: Ampere (free eligible)
   - Availability: Any free region
5. Generate and download SSH key
6. Click "Create"

**Step 3: Connect to VM**
```bash
# Make key readable
chmod 600 /path/to/your-key.key

# Connect
ssh ubuntu@your-instance-public-ip -i /path/to/your-key.key
```

**Step 4: Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install python3.10 python3-pip git python3.10-venv -y

# Verify installation
python3.10 --version
pip3 --version
```

**Step 5: Clone Repository**
```bash
git clone https://github.com/yourusername/phishing_app.git
cd phishing_app
```

**Step 6: Create Virtual Environment**
```bash
python3.10 -m venv venv
source venv/bin/activate
```

**Step 7: Install Python Packages**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 8: Run Application**
```bash
# Run API in background
nohup python run_api.py > api.log 2>&1 &

# Or run Streamlit UI in background
nohup streamlit run src/phishing/ui/app.py --server.port 8501 > ui.log 2>&1 &

# View logs
tail -f api.log
```

**Step 9: Open Firewall Ports**
1. In Oracle Console, go to VCN → Security Lists
2. Select your security list
3. Add Ingress Rule:
   - Source: 0.0.0.0/0
   - Port: 8000 (for API)
   - Protocol: TCP
4. Add another for port 8501 (for UI)

**Step 10: Access Your App**
```
API: http://your-instance-ip:8000
UI: http://your-instance-ip:8501
```

**Cost:** $0 (Always-free tier)  
**Time:** 20 minutes

---

## Option 4: Render (Free Tier) 🎯

### Prerequisites
- GitHub account with pushed code
- Render account

### Deployment Steps

**Step 1: Create Render Account**
1. Go to [https://render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render

**Step 2: Create Web Service**
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Choose your `phishing_app` repo

**Step 3: Configure Service**
- **Name:** phishing-api
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python run_api.py`
- **Instance Type:** Free

**Step 4: Deploy**
1. Click "Create Web Service"
2. Render starts deployment
3. Monitor logs
4. Get your service URL

**Step 5: Test**
```bash
curl https://your-render-url.onrender.com/health
```

**Cost:** Free tier  
**Note:** Spins down after 15 mins of inactivity (on free tier)  
**Time:** 10 minutes

---

## Option 5: Fly.io (Free Tier) 🛫

### Prerequisites
- Docker installed locally
- Fly.io account

### Deployment Steps

**Step 1: Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

**Step 2: Authenticate**
```bash
flyctl auth login
```

**Step 3: Launch App**
```bash
cd phishing_app
flyctl launch
```

Follow the prompts:
- App name: phishing-api
- Choose region (any)
- Choose not to add database

**Step 4: Deploy**
```bash
flyctl deploy
```

**Step 5: Check Status**
```bash
flyctl status
flyctl open
```

**Cost:** Free tier  
**Time:** 10 minutes

---

## Comparison Summary

| Feature | Railway | Streamlit | Oracle | Render | Fly.io |
|---------|---------|-----------|--------|--------|--------|
| API Support | ✅ | ❌ | ✅ | ✅ | ✅ |
| UI Support | ✅ | ✅ | ✅ | ✅ | ✅ |
| Free Cost | $5 credits/mo | Forever | Forever | Free tier | Free tier |
| Setup Time | 10 min | 5 min | 20 min | 10 min | 10 min |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Post-Deployment Checklist

After deploying, verify everything works:

- [ ] API health check: `/health` endpoint returns 200
- [ ] Prediction works: `/predict` accepts POST requests
- [ ] Batch predictions work: `/predict-batch` accepts multiple URLs
- [ ] API documentation accessible: `/docs` (FastAPI Swagger)
- [ ] UI loads correctly (if deployed)
- [ ] UI can connect to API
- [ ] Error handling works

---

## Troubleshooting

### Port Binding Issues
**Problem:** "Port already in use" or "Permission denied"  
**Solution:** 
- Railway/Render/Fly.io use PORT env var automatically
- Settings already configured to read PORT env var

### Module Not Found Errors
**Problem:** "No module named 'src.phishing'"  
**Solution:**
- Ensure `requirements.txt` has all dependencies
- Check run_api.py adds src to path (already done)

### API Connection Timeouts
**Problem:** Streamlit UI can't reach API  
**Solution:**
- Ensure API is fully deployed and running
- Check API URL in UI code is correct
- Use full HTTPS URL with domain, not localhost

### Out of Memory
**Problem:** App keeps crashing  
**Solution:**
- Free tiers have limited memory (usually 512MB-1GB)
- Our app uses ~200-300MB, should fit
- Check no memory leaks in logs

---

## Next Steps

1. **Monitor Performance:** Check logs regularly
2. **Set Up Monitoring:** Use platform's built-in monitoring
3. **Add Custom Domain:** Most platforms support custom domains
4. **Scale Up:** If needed, upgrade from free tier
5. **Backup:** Regular GitHub backups of your code

---

## Need Help?

- Check deployment logs in the platform console
- Review settings are correct
- Test locally first with `python run_api.py`
- Check GitHub Issues for similar problems
- Review our DEPLOYMENT.md for detailed info

Happy deploying! 🎉
