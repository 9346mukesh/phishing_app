# 🎯 RENDER CLOUD DEPLOYMENT - COMPLETE GUIDE

Deploy your Phishing Detection System to Render Cloud for FREE in 10 minutes!

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step-by-Step Guide](#step-by-step-guide)
3. [Configuration Details](#configuration-details)
4. [Testing Your Deployment](#testing-your-deployment)
5. [Troubleshooting](#troubleshooting)
6. [Additional Services (Optional)](#additional-services-optional)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **GitHub Account** - Your code must be in a GitHub repository
- ✅ **Code Pushed to GitHub** - Latest version of your code
- ✅ **Render Account** - Create a free account (uses GitHub login)

### Verify Your GitHub Setup

```bash
# Make sure your code is on GitHub
cd /Users/mukeshkumarreddy/phishing_app

# Check if you have a git repository
git status

# Verify remote is set to GitHub
git remote -v

# Make sure everything is pushed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

## Step-by-Step Guide

### **STEP 1: Create Render Account** (2 minutes)

1. Open your browser and go to **[https://render.com](https://render.com)**

2. Click the **"Get Started"** button in the top right

3. You'll see signup options. Click **"Sign up with GitHub"**

4. GitHub will ask you to authorize Render:
   - Review the permissions (Render needs access to your repos)
   - Click **"Authorize render-oss"**

5. Render will create your account and redirect to the dashboard

6. You should now see the Render dashboard with:
   - Option to create new services
   - Your GitHub repositories

**✅ Done! You now have a Render account.**

---

### **STEP 2: Create a New Web Service** (3 minutes)

This is where you'll deploy your API.

1. In the Render dashboard, look for the **"New +"** button (usually top right)

2. Click **"New +"** → Select **"Web Service"**

3. You'll see "Connect a repository" section

4. Find your `phishing_app` repository in the list:
   - If you don't see it, click **"Connect account"** to authorize more repos

5. Click **"Connect"** next to your `phishing_app` repository

**✅ Done! Your repository is connected to Render.**

---

### **STEP 3: Configure Your Service** (3 minutes)

This is the most important part. Fill in the configuration carefully.

#### **Basic Information**

- **Name:** `phishing-api` (or any name you prefer)
  - This becomes part of your URL
  - Can't change later without redeploying

- **Environment:** Select **"Python 3"**
  - Render auto-detects this, but verify it's Python 3

- **Region:** Choose any region
  - Default is usually fine (select closest to you for lower latency)
  - Free tier works in all regions

#### **Build and Start Commands**

These tell Render how to run your app:

**Build Command:**
```
pip install -r requirements.txt
```
- Render runs this command to install Python dependencies
- Reads from your `requirements.txt` file

**Start Command:**
```
python run_api.py
```
- This is the command to actually start your API
- Render runs this after the build completes

#### **Instance Type**

- Select **"Free"** tier
  - 0.5 GB RAM
  - Limited vCPU
  - Spins down after 15 minutes of inactivity
  - Perfect for testing and demo purposes

#### **Advanced Settings (Optional)**

You can leave these as default, but here are useful options:

- **Auto-Deploy:** Set to "Yes" (auto-redeploys on GitHub push)
- **Scaling:** Free tier can't scale, so this doesn't matter

---

### **STEP 4: Create the Service** (30 seconds)

1. Scroll down and click **"Create Web Service"**

2. Render will:
   - Clone your GitHub repository
   - Install dependencies
   - Build your application
   - Start your service

3. You'll see a build log. Watch it for any errors:
   ```
   === Building...
   === Installing dependencies...
   === Running start command...
   === Service started on port 8000
   ```

**✅ Service created! It's now deploying...**

---

### **STEP 5: Wait for Deployment** (2-3 minutes)

Your deployment is now running. Here's what to expect:

1. **Build Phase** (1-2 minutes)
   - Render downloads your code
   - Installs Python packages
   - You'll see green checkmarks as it progresses

2. **Launch Phase** (30 seconds)
   - Your API starts
   - Render tests if it's responding

3. **Success** ✅
   - You'll see "Live" status
   - Your API URL appears at the top

The URL format is: `https://phishing-api.onrender.com`

---

### **STEP 6: Get Your API URL** (30 seconds)

1. On the service page, look for the blue URL at the top
   - Example: `https://phishing-api.onrender.com`

2. Copy this URL - you'll need it for testing

3. This URL is now **publicly accessible** and stays the same!

**✅ Your API is live!**

---

## Configuration Details

### Understanding the Environment

Render automatically provides these environment variables:

```
PORT=10000          # Render assigns a random port
RENDER=true         # Indicates running on Render
NODE_ENV=production # Production environment
```

**Our app already handles this!** The settings.py file reads the PORT environment variable automatically.

### Viewing Logs

To debug or monitor your service:

1. In the Render dashboard, click your service name
2. Go to the **"Logs"** tab
3. You'll see real-time logs from your application

Example log output:
```
INFO:     Uvicorn running on http://0.0.0.0:10000
INFO:     Application startup complete
```

### Service Settings

After deployment, you can:

1. **Auto-redeploy:** Enable in Settings
   - Service auto-deploys when you push to GitHub

2. **Environment Variables:** Add secrets
   - Settings → Environment → Add key-value pairs
   - Useful for API keys, secrets, etc.

3. **Restart Service:** Restart from Logs tab
   - Restarts your service if needed

---

## Testing Your Deployment

### Quick Health Check

Test if your API is running:

```bash
# Replace phishing-api with your actual service name
curl https://phishing-api.onrender.com/health

# Expected response:
# {"status":"ok","version":"1.0.0"}
```

### Test Single URL Prediction

```bash
curl -X POST https://phishing-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com"}'

# Expected response:
# {
#   "url": "https://www.google.com",
#   "is_phishing": false,
#   "confidence": 0.95,
#   "features_extracted": 30
# }
```

### Test Batch Predictions

```bash
curl -X POST https://phishing-api.onrender.com/predict-batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.google.com",
      "https://www.github.com",
      "http://phishing-example.fake"
    ]
  }'

# Expected response: Array of predictions
```

### View API Documentation

Open in your browser:
```
https://phishing-api.onrender.com/docs
```

This opens the interactive Swagger UI where you can test all endpoints!

---

## Troubleshooting

### Issue 1: Deployment Keeps Failing

**Symptoms:** Red X marks in build log, deployment fails

**Solutions:**

1. Check if dependencies are in `requirements.txt`:
   ```bash
   cat requirements.txt
   ```
   Should list all your Python packages

2. Verify your code works locally:
   ```bash
   python run_api.py
   # Should start without errors
   ```

3. Check the logs for specific errors:
   - Go to Render dashboard → Logs tab
   - Look for error messages
   - Common issues:
     - Missing module (add to requirements.txt)
     - Syntax error (fix and push to GitHub)
     - Port binding issue (shouldn't happen - we handle PORT env var)

4. Try redeploying:
   - Click "Manual Deploy" → "Latest Commit"

### Issue 2: API Returns 502 Bad Gateway

**Symptoms:** Curl returns `502 Bad Gateway` error

**Causes & Solutions:**

1. **Service crashed** - Check logs:
   ```bash
   curl https://phishing-api.onrender.com/health
   # If 502, service isn't responding
   ```

2. **Memory issue** - Free tier has limited RAM:
   - Try accessing health endpoint
   - If still fails, restart service

3. **Cold start** - Render spins down free services after 15 mins:
   - First request after inactivity takes 30-40 seconds
   - Subsequent requests are instant

### Issue 3: Health Check Returns 404

**Symptoms:** `curl` returns 404 Not Found

**Solutions:**

1. Verify endpoint exists:
   - Should be: `/health`
   - Not: `/api/health` or `/v1/health`

2. Check if API is actually running:
   - Look at Logs tab for startup messages

3. Wait a bit - deployment takes 2-3 minutes:
   - Try again after 1 minute

### Issue 4: Service Spins Down (Free Tier)

**Symptoms:** First request takes 30+ seconds, then fast

**Explanation:**
- Free tier automatically stops after 15 minutes of no requests
- First request "wakes up" the service
- This is normal and expected

**Solutions:**
- Use a monitoring service to ping your API periodically
- Or upgrade to a paid plan ($7/month)

---

## Additional Services (Optional)

### Deploy UI with Render

You can also deploy the Streamlit UI with Render:

1. Go to Render dashboard → **"New +"** → **"Web Service"**
2. Select your repository again
3. Configure:
   - **Name:** `phishing-ui`
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `streamlit run src/phishing/ui/app.py --server.port 8501`
4. Deploy!

The UI will need to know your API URL:

```python
# In src/phishing/ui/app.py
API_URL = "https://phishing-api.onrender.com"  # Your API URL
```

### Monitor Your Service

Render provides monitoring:

1. Click your service
2. Go to **"Metrics"** tab
3. See:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

---

## Key Points to Remember

✅ **Free tier specs:**
- 0.5 GB RAM
- Shared CPU
- No auto-scaling
- Spins down after 15 minutes inactivity

✅ **Your API URL:**
- Format: `https://phishing-api.onrender.com`
- Public and accessible 24/7
- Never changes once created

✅ **Updates:**
- Push to GitHub
- Render auto-redeploys (if enabled)
- Or manually deploy from Render dashboard

✅ **Costs:**
- Free tier: $0
- Upgrade anytime if needed

---

## What's Next?

1. ✅ **Deploy your API** ← You are here
2. **Add custom domain** (optional)
   - Render supports custom domains ($10/month)
3. **Monitor your API**
   - Set up alerts
   - Track usage
4. **Deploy UI** (optional)
   - Deploy to Streamlit Cloud (free) or Render
5. **Scale up** (if needed)
   - Move to paid tier ($7+/month)

---

## Support & Help

If something goes wrong:

1. **Check Logs** - Always the first step
   - Render dashboard → Your service → Logs tab

2. **Review DEPLOYMENT.md**
   - General deployment guide
   - Troubleshooting section

3. **Test Locally First**
   ```bash
   python run_api.py
   ```
   - If works locally but not on Render, it's an environment issue

4. **Check GitHub Issues**
   - Look for similar problems

5. **Render Documentation**
   - https://render.com/docs

---

## Success Checklist

- [ ] Render account created
- [ ] GitHub repo connected
- [ ] Service deployed to Render
- [ ] API URL obtained
- [ ] Health check passes
- [ ] Prediction test works
- [ ] API documentation accessible at /docs
- [ ] Logs show no errors

**If all checked ✅ → You're deployed! Congratulations! 🎉**

---

**Deployed successfully? Share your API URL and get feedback!**

Example:
```
My Phishing Detection API is live at:
https://phishing-api.onrender.com
Try: https://phishing-api.onrender.com/docs
```

Happy deploying! 🚀
