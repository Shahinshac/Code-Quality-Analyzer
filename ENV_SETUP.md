# Environment Configuration Guide

## Quick Start

The project now uses `.env` file for configuration. Simply run:

```bash
python run.py
```

## Environment Variables

### Created Files:
- **`.env`** - Your local environment configuration (ignored by git)
- **`.env.example`** - Template for other developers
- **`run.py`** - New launcher that loads .env automatically

### Available Variables:

#### Flask Configuration
```env
FLASK_APP=code_quality_analyzer.webapp
FLASK_ENV=development
FLASK_DEBUG=0
```

#### Model Configuration
```env
MODEL_PATH=models/code_quality_model.joblib
# MODEL_URL=https://your-url.com/model.joblib  # Optional: auto-download
```

#### Server Configuration
```env
HOST=127.0.0.1
PORT=5000
```

#### AWS S3 (Optional - for deployment)
```env
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_S3_BUCKET=your_bucket
# AWS_REGION=us-east-1
```

## Running the Application

### Method 1: Using run.py (Recommended)
```bash
python run.py
```

### Method 2: Using Flask CLI
```bash
flask run
```

### Method 3: Docker
```bash
docker-compose up
```

## Current Configuration

✅ **Environment is now active!**

Your app is running at: **http://127.0.0.1:5000**

Configuration loaded from `.env`:
- Server: 127.0.0.1:5000
- Debug: False
- Model: models/code_quality_model.joblib

## Customization

To change settings, edit `.env`:

```env
# Change port
PORT=8080

# Enable debug mode
FLASK_DEBUG=1

# Use different model location
MODEL_PATH=/path/to/your/model.joblib
```

Then restart: `python run.py`
