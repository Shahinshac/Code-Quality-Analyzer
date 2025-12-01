# Code Quality Analyzer - Complete Setup Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)

---

## Local Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- (Optional) Docker Desktop

### Step 1: Clone the Repository

```powershell
git clone https://github.com/Shahinshac/Code-Quality-Analyzer.git
cd Code-Quality-Analyzer
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- scikit-learn, pandas, joblib (ML)
- flake8, pylint, autopep8 (Python linters)
- pytest (testing)
- streamlit (alternative UI)
- gunicorn (production server)

### Step 4: (Optional) Install Language-Specific Linters

For enhanced multi-language analysis:

**JavaScript/TypeScript:**
```powershell
npm install -g eslint
```

**Java (Windows - Chocolatey):**
```powershell
choco install checkstyle
```

**C/C++ (Windows - Chocolatey):**
```powershell
choco install cppcheck
```

**Go:**
```powershell
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

**Rust:**
```powershell
rustup component add clippy
```

**Ruby:**
```powershell
gem install rubocop
```

**PHP:**
```powershell
composer global require squizlabs/php_codesniffer
```

### Step 5: Train ML Model (Optional)

```powershell
# Create models directory
New-Item -ItemType Directory -Force -Path models

# Train a demo model
python -m code_quality_analyzer.cli train --dataset datasets/synthetic_dataset.csv --model-out models/code_quality_model.joblib
```

### Step 6: Run the Application

**Flask Web App:**
```powershell
python -m code_quality_analyzer.webapp
```
Access at: http://localhost:5000

**Streamlit UI:**
```powershell
streamlit run streamlit_app.py
```
Access at: http://localhost:8501

**CLI Analysis:**
```powershell
# Analyze a Python file
python -m code_quality_analyzer.cli analyze --file examples/bad_example.py --model models/code_quality_model.joblib

# Analyze any supported language file
python -m code_quality_analyzer.cli analyze --file your-code.js
```

### Step 7: Run Tests

```powershell
pytest tests/
```

---

## Docker Deployment

### Step 1: Build Docker Image Locally

```powershell
docker build -t code-quality-analyzer:latest .
```

### Step 2: Run Container Locally

```powershell
# Run with default settings
docker run -d -p 5000:5000 code-quality-analyzer:latest

# Run with custom model path
docker run -d -p 5000:5000 `
  -e MODEL_PATH=/app/models/code_quality_model.joblib `
  -v ${PWD}/models:/app/models `
  code-quality-analyzer:latest

# Run with model from URL
docker run -d -p 5000:5000 `
  -e MODEL_URL=https://your-bucket.s3.amazonaws.com/model.joblib `
  -e MODEL_PATH=/app/models/model.joblib `
  code-quality-analyzer:latest
```

### Step 3: Test the Container

```powershell
# Check if running
docker ps

# View logs
docker logs <container-id>

# Access the app
Start-Process http://localhost:5000
```

### Step 4: Use Docker Compose

```powershell
docker-compose up --build
```

---

## Cloud Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Create Railway account**: https://railway.app
2. **Create new project** → "Deploy from GitHub repo"
3. **Select repository**: `Shahinshac/Code-Quality-Analyzer`
4. **Railway auto-detects Dockerfile** and deploys
5. **Set environment variables** (optional):
   - `MODEL_PATH=/app/models/code_quality_model.joblib`
   - `MODEL_URL=<your-s3-url>` (if using S3)
6. **Get deployment URL** from Railway dashboard

**Cost**: Free tier available, ~$5/month for basic usage

### Option 2: Render

1. **Create Render account**: https://render.com
2. **New** → **Web Service**
3. **Connect GitHub repository**
4. **Configuration**:
   - Environment: `Docker`
   - Build Command: (auto-detected)
   - Start Command: (auto-detected from Dockerfile)
5. **Environment Variables** (optional):
   - `MODEL_PATH=/app/models/code_quality_model.joblib`
6. **Deploy**

**Cost**: Free tier available (sleeps after inactivity), $7/month for always-on

### Option 3: Fly.io

1. **Install Fly CLI**:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

2. **Login and Launch**:
```powershell
fly auth login
fly launch
```

3. **Follow prompts**:
   - App name: `code-quality-analyzer`
   - Region: Choose closest to you
   - Postgres/Redis: No

4. **Deploy**:
```powershell
fly deploy
```

5. **Set secrets** (optional):
```powershell
fly secrets set MODEL_URL=your-s3-url
```

**Cost**: Free tier available, ~$3/month for basic app

### Option 4: Google Cloud Run

1. **Install Google Cloud SDK**: https://cloud.google.com/sdk/docs/install

2. **Authenticate**:
```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Build and push to Google Container Registry**:
```powershell
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/code-quality-analyzer
```

4. **Deploy to Cloud Run**:
```powershell
gcloud run deploy code-quality-analyzer `
  --image gcr.io/YOUR_PROJECT_ID/code-quality-analyzer `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated
```

**Cost**: Pay-per-use, free tier includes 2 million requests/month

### Option 5: AWS ECS/Fargate

1. **Install AWS CLI**: https://aws.amazon.com/cli/

2. **Authenticate**:
```powershell
aws configure
```

3. **Create ECR repository**:
```powershell
aws ecr create-repository --repository-name code-quality-analyzer
```

4. **Build and push**:
```powershell
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker build -t code-quality-analyzer .
docker tag code-quality-analyzer:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/code-quality-analyzer:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/code-quality-analyzer:latest
```

5. **Deploy via ECS Console** or use AWS Copilot:
```powershell
copilot init
copilot deploy
```

**Cost**: Varies, typically $10-30/month for small app

### Option 6: Pull from GitHub Container Registry (GHCR)

**Every push to `main` automatically builds and publishes to GHCR!**

```powershell
# Pull the latest pre-built image
docker pull ghcr.io/shahinshac/code-quality-analyzer:latest

# Run it
docker run -d -p 5000:5000 ghcr.io/shahinshac/code-quality-analyzer:latest
```

Use this image on any platform that supports Docker:
- Railway: Deploy from Docker registry
- Render: Deploy from Docker registry  
- Azure Container Instances
- Digital Ocean App Platform

---

## GitHub Actions CI/CD Setup

### Automatic Deployment (Already Configured!)

The repository includes `.github/workflows/docker-publish-ghcr.yml` which automatically:

1. ✅ Builds Docker image on every push to `main`
2. ✅ Pushes to GitHub Container Registry (GHCR)
3. ✅ Supports multi-architecture (amd64, arm64)
4. ✅ Uses build cache for faster builds
5. ⚙️ Optionally uploads models to S3

### Enable GHCR Package Publishing

1. **Go to repository Settings** → **Actions** → **General**
2. **Workflow permissions** → Select **Read and write permissions**
3. **Save**

### (Optional) Configure S3 Model Storage

1. **Create S3 bucket** for model storage

2. **Add GitHub Secrets**:
   - Go to repository **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Add:
     - `AWS_ACCESS_KEY_ID` → Your AWS access key
     - `AWS_SECRET_ACCESS_KEY` → Your AWS secret key

3. **Add GitHub Variables**:
   - Click **Variables** tab → **New repository variable**
   - Add:
     - `AWS_REGION` → `us-east-1` (or your region)
     - `AWS_S3_BUCKET` → Your bucket name

4. **Push to main** → Workflow automatically uploads model to S3

### View Build Status

- **Actions tab**: https://github.com/Shahinshac/Code-Quality-Analyzer/actions
- **Packages tab**: https://github.com/Shahinshac?tab=packages

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MODEL_PATH` | Path to ML model file | No | `/app/models/code_quality_model.joblib` |
| `MODEL_URL` | URL to download model at startup | No | - |
| `PORT` | Port for Flask app | No | `5000` |
| `FLASK_ENV` | Flask environment | No | `production` |

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution**: Change port or kill existing process:
```powershell
# Find process on port 5000
netstat -ano | findstr :5000
# Kill process
taskkill /PID <PID> /F
```

### Issue: Docker build fails
**Solution**: Ensure Docker Desktop is running and you have enough disk space:
```powershell
docker system prune -a
```

### Issue: GitHub Actions workflow fails
**Solution**: 
1. Check Actions tab for error details
2. Ensure workflow permissions are set to "Read and write"
3. Verify secrets are correctly configured

### Issue: ML model not found
**Solution**: 
1. Train a model locally: `python -m code_quality_analyzer.cli train --dataset datasets/synthetic_dataset.csv --model-out models/code_quality_model.joblib`
2. Or set `MODEL_URL` to download from S3
3. Or run without ML (detection still works)

---

## Quick Start Checklist

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] (Optional) Train ML model
- [ ] Run locally (`python -m code_quality_analyzer.webapp`)
- [ ] Test at http://localhost:5000
- [ ] Choose deployment platform (Railway/Render/Fly.io/etc.)
- [ ] Push to GitHub (auto-builds to GHCR)
- [ ] Deploy using GHCR image

---

## Support

- **Issues**: https://github.com/Shahinshac/Code-Quality-Analyzer/issues
- **Discussions**: https://github.com/Shahinshac/Code-Quality-Analyzer/discussions
- **Documentation**: See README.md for detailed features

---

**Last Updated**: December 2025
