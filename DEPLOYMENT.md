# Quick Deployment Guide - Code Quality Analyzer

Your app is ready to deploy! Choose the easiest method below.

---

## 🚀 Option 1: Railway (EASIEST - 5 Minutes)

**Best for**: Fastest deployment, free tier available

### Steps:

1. **Go to Railway**: https://railway.app/new

2. **Click "Deploy from GitHub repo"**

3. **Authenticate with GitHub** and select:
   - Repository: `Shahinshac/Code-Quality-Analyzer`
   - Branch: `main`

4. **Railway auto-detects your Dockerfile** and starts building

5. **Wait 2-3 minutes** for build to complete

6. **Get your URL**:
   - Click on your deployment
   - Go to "Settings" → "Generate Domain"
   - Your app will be live at: `https://your-app-name.up.railway.app`

**Done!** ✅ Your app is live with HTTPS

**Cost**: Free tier: $5 credit/month, then ~$5/month for basic usage

---

## 🎯 Option 2: Render (Also Easy - 10 Minutes)

**Best for**: Free tier with auto-sleep, good for demos

### Steps:

1. **Go to Render**: https://render.com/

2. **Sign up/Login** with GitHub

3. **Click "New +" → "Web Service"**

4. **Connect Repository**:
   - Find `Code-Quality-Analyzer`
   - Click "Connect"

5. **Configure**:
   - Name: `code-quality-analyzer`
   - Environment: `Docker`
   - Region: Choose closest to you
   - Instance Type: `Free` or `Starter ($7/mo)`

6. **Advanced Settings** (optional):
   - Add environment variable if needed:
     - Key: `MODEL_PATH`
     - Value: `/app/models/code_quality_model.joblib`

7. **Click "Create Web Service"**

8. **Wait 3-5 minutes** for deployment

9. **Access your app** at: `https://code-quality-analyzer.onrender.com`

**Cost**: Free (sleeps after 15 min inactivity), or $7/mo always-on

---

## 🐳 Option 3: Using Pre-Built Docker Image (Any Platform)

**Your GitHub Actions automatically builds and publishes to GHCR!**

### Pull and Run Locally:

```powershell
# Pull the latest image
docker pull ghcr.io/shahinshac/code-quality-analyzer:latest

# Run it
docker run -d -p 5000:5000 ghcr.io/shahinshac/code-quality-analyzer:latest

# Access at http://localhost:5000
```

### Deploy to Cloud Platforms Using GHCR Image:

**Render** (Deploy from Registry):
1. New Web Service → "Deploy an existing image"
2. Image URL: `ghcr.io/shahinshac/code-quality-analyzer:latest`
3. Deploy

**Fly.io**:
```powershell
# Install Fly CLI first
fly auth login
fly apps create code-quality-analyzer
fly deploy --image ghcr.io/shahinshac/code-quality-analyzer:latest
```

**Google Cloud Run**:
```powershell
gcloud run deploy code-quality-analyzer \
  --image ghcr.io/shahinshac/code-quality-analyzer:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 🔄 Automatic Updates

Every time you push to `main` branch:
1. ✅ GitHub Actions builds new Docker image
2. ✅ Pushes to GHCR automatically
3. 🔄 Redeploy on your platform to get latest version

### Railway Auto-Deploy:
- Settings → "Watch Paths" → `**/*` (auto-deploys on push)

### Render Auto-Deploy:
- Settings → "Auto-Deploy" → Enable (auto-deploys on push)

---

## ⚙️ Optional: Environment Variables

Add these in your hosting platform's dashboard if needed:

| Variable | Value | Purpose |
|----------|-------|---------|
| `MODEL_PATH` | `/app/models/code_quality_model.joblib` | ML model location |
| `MODEL_URL` | `https://your-s3-url/model.joblib` | Download model from S3 |
| `PORT` | `5000` | Server port (auto-set by most platforms) |

---

## 🎯 Recommended: Railway

**Why Railway?**
- ✅ Simplest setup (literally 3 clicks)
- ✅ Auto-detects Dockerfile
- ✅ Free $5/month credit
- ✅ HTTPS automatically
- ✅ Auto-deploy on git push
- ✅ Great for hobby projects

**Start here**: https://railway.app/new

---

## 📊 Check Your Deployment Status

### GitHub Container Registry:
- View packages: https://github.com/Shahinshac?tab=packages
- Latest image: `ghcr.io/shahinshac/code-quality-analyzer:latest`

### GitHub Actions Build:
- Check builds: https://github.com/Shahinshac/Code-Quality-Analyzer/actions
- Last successful build creates the Docker image

---

## 🆘 Troubleshooting

### Build Fails on Platform?
- Check that Dockerfile exists in repo root ✅ (it does)
- Verify GitHub Actions built successfully
- Use pre-built GHCR image instead

### Can't Access App?
- Check if container is running
- Verify port mapping (5000)
- Check platform logs for errors

### Need Help?
- Railway Docs: https://docs.railway.app/
- Render Docs: https://render.com/docs
- GitHub Issues: https://github.com/Shahinshac/Code-Quality-Analyzer/issues

---

## 🎉 Next Steps After Deployment

1. **Test your live app** - Upload code samples
2. **Share the URL** - Get feedback from users
3. **Monitor usage** - Check platform dashboard
4. **Scale if needed** - Upgrade instance size
5. **Add custom domain** (optional) - Most platforms support this

---

**Ready to deploy?** Pick Railway or Render and follow the steps above! 🚀
