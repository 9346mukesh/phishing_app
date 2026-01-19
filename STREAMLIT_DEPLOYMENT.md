# 🎨 Streamlit Cloud Deployment Guide

Deploy your Phishing Detection UI to Streamlit Cloud (FREE FOREVER!)

## Prerequisites

- ✅ GitHub account with code pushed
- ✅ Deployed Render API (you have this!)
- ✅ Streamlit Cloud account

## Step 1: Create Streamlit Cloud Account (2 mins)

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "Sign in" → "Continue with GitHub"
3. Authorize Streamlit to access your repositories

## Step 2: Deploy Your App (2 mins)

1. In Streamlit Cloud dashboard, click **"New app"**
2. Select your repository: `phishing_app`
3. Select branch: `main`
4. Enter main file path: `src/phishing/ui/app.py`
5. Click **"Deploy"**

Streamlit will automatically detect and use:
- `requirements.txt` for dependencies
- `.streamlit/config.toml` for configuration
- `.streamlit/secrets.toml` for secrets (API_URL)

## Step 3: Add API URL (1 min)

Once deployed:

1. Click the **"☰" menu** (top right)
2. Select **"Settings"** → **"Secrets"**
3. Add your Render API URL:

```toml
API_URL = "https://phishing-detection-api-fvdu.onrender.com"
```

4. Click "Rerun" or wait for auto-refresh

## Step 4: Test Your App

Once deployed, click the URL to test:
- Enter a URL to check
- Click "Check URL"
- See instant prediction!

## Features Available

✅ Single URL detection
✅ Batch URL detection (CSV upload)
✅ Real-time predictions
✅ Confidence scores
✅ Visual indicators
✅ API health monitoring

## Costs

- **Streamlit Cloud:** FREE ✨ (unlimited usage)
- **Render API:** FREE ($5/month credits)
- **Total:** $0/month for production deployment!

## Troubleshooting

**App won't load?**
- Check API_URL in Settings → Secrets
- Verify Render API is running

**Predictions failing?**
- Check Render API logs
- Verify URL format
- Check internet connection

**Performance issues?**
- Render free tier spins down after 15 mins (first request may be slow)
- This is normal for free tier

---

## Next Steps

1. ✅ API deployed on Render
2. ✅ UI deployed on Streamlit Cloud
3. Share your URL with others!
4. Monitor usage in both dashboards
5. Consider paid tiers if you get high traffic
