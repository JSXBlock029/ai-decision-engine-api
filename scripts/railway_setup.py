"""
Railway Deployment Setup
Complete Railway deployment guide
"""

from pathlib import Path
import json

def create_railway_setup_guide():
    """Create Railway setup guide"""
    
    guide = """# Railway Deployment - Step by Step

## You're on the Railway "New Project" Screen!

Follow these steps:

---

## Step 1: Select GitHub Repository

1. **Click "GitHub Repository"** (it's already highlighted)
2. Railway will ask you to connect GitHub (if not already connected)
3. Authorize Railway to access your repositories
4. Select your repository: `ai-decision-engine-api` (or whatever you named it)

---

## Step 2: Railway Auto-Detection

Railway will automatically:
- Detect it's a Python project
- Find `api/requirements.txt`
- Set up the build process

**If it doesn't auto-detect:**
- Go to Settings → Build
- Build Command: `pip install -r api/requirements.txt`
- Start Command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Step 3: Configure Environment Variables

Go to **Variables** tab and add:

```
API_ENV=production
PORT=8000
```

(These are optional, Railway handles PORT automatically)

---

## Step 4: Deploy!

1. Railway will start building automatically
2. Watch the build logs
3. Wait for "Deploy successful"
4. Get your URL: `your-app.railway.app`

---

## Step 5: Verify Deployment

1. Click on your service
2. Go to **Settings** → **Generate Domain**
3. You'll get a URL like: `your-app.railway.app`
4. Test it: `https://your-app.railway.app/health`

---

## Step 6: Update API Key Configuration

After deployment, you'll need to:

1. Go to Railway dashboard
2. Click on your service
3. Go to **Variables**
4. Add your API keys (if needed)

---

## Troubleshooting

### Build Fails
- Check `api/requirements.txt` exists
- Verify Python version (Railway uses 3.11 by default)
- Check build logs for errors

### App Won't Start
- Verify start command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Check PORT is set (Railway sets this automatically)
- Review logs in Railway dashboard

### API Not Responding
- Check health endpoint: `/health`
- Verify all dependencies installed
- Check environment variables

---

## Next Steps After Deployment

1. ✅ Test your API: `https://your-app.railway.app/health`
2. ✅ Update marketing content with your Railway URL
3. ✅ Post on Reddit/Twitter with your live URL
4. ✅ Get first users!

---

## Railway Free Tier Limits

- $5 credit/month (usually enough for small API)
- 500 hours free compute
- Free SSL included
- Free subdomain

**Cost: $0/month** (as long as you stay within limits)

---

## Pro Tips

1. **Monitor Usage**: Check Railway dashboard for usage
2. **Set Up Alerts**: Get notified if service goes down
3. **Use Custom Domain**: Add your domain later (when you have one)
4. **Scale Gradually**: Only upgrade if needed

---

*You're almost there! Just click "GitHub Repository" and follow the prompts!*

"""
    
    with open("RAILWAY_DEPLOYMENT_STEPS.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("Railway deployment guide created: RAILWAY_DEPLOYMENT_STEPS.md")

def verify_railway_readiness():
    """Verify project is ready for Railway"""
    print("="*60)
    print("VERIFYING RAILWAY READINESS")
    print("="*60)
    print()
    
    checks = {
        "api/main.py": Path("api/main.py").exists(),
        "api/requirements.txt": Path("api/requirements.txt").exists(),
        "railway.json": Path("railway.json").exists(),
        ".gitignore": Path(".gitignore").exists()
    }
    
    all_ok = True
    for item, exists in checks.items():
        status = "[OK]" if exists else "[MISSING]"
        print(f"{status} {item}")
        if not exists:
            all_ok = False
    
    print()
    if all_ok:
        print("[SUCCESS] Project is ready for Railway deployment!")
    else:
        print("[WARNING] Some files missing, but Railway can still deploy")
    
    print()
    print("Next steps:")
    print("1. Click 'GitHub Repository' on Railway")
    print("2. Select your repository")
    print("3. Railway will auto-detect and deploy!")
    print()
    
    return all_ok

if __name__ == "__main__":
    create_railway_setup_guide()
    verify_railway_readiness()

