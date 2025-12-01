# Code Quality Analyzer with AI

A comprehensive AI-powered code quality analyzer with multi-language support. This tool analyzes code quality across multiple programming languages using:

- **Multi-language parsing** to extract code metrics from Python, JavaScript, TypeScript, Java, C++, Go, Rust, Ruby, and PHP
- **Rule-based detectors** for code smells (long functions, unused imports, deep nesting, complexity)
- **Language-specific linters** integration (flake8, pylint, ESLint, Checkstyle, cppcheck, golangci-lint, clippy, RuboCop, PHP_CodeSniffer)
- **ML classifier** using scikit-learn to classify code snippets as "good" or "bad"
- **CLI** to analyze files and **Flask web UI** to upload and analyze code with autofix options
- Sample dataset and comprehensive unit tests

## Supported Languages

| Language       | Parser Type | Linter Integration       | Status |
|----------------|-------------|--------------------------|--------|
| Python         | AST         | flake8, pylint           | ✅ Full |
| JavaScript/TS  | Regex       | ESLint                   | ✅ Full |
| Java           | Regex       | Checkstyle, PMD          | ✅ Full |
| C/C++          | Regex       | cppcheck, clang-tidy     | ✅ Full |
| Go             | Regex       | golangci-lint            | ✅ Full |
| Rust           | Regex       | clippy                   | ✅ Full |
| Ruby           | Regex       | RuboCop                  | ✅ Full |
| PHP            | Regex       | PHP_CodeSniffer          | ✅ Full |

## Quickstart

1. Create and activate a Python environment (>= 3.9 recommended).
2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. (Optional) Install language-specific linters for enhanced analysis:

```powershell
# JavaScript/TypeScript
npm install -g eslint

# Java (Ubuntu/Debian)
apt-get install checkstyle

# C/C++ (Ubuntu/Debian)
apt-get install cppcheck

# Go
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Rust
rustup component add clippy

# Ruby
gem install rubocop

# PHP
composer global require squizlabs/php_codesniffer
```

4. Train a small demo model (optional):

```powershell
python -m code_quality_analyzer.cli train --dataset datasets/synthetic_dataset.csv --model-out models/code_quality_model.joblib
```

5. Analyze any supported file:

```powershell
# Python
python -m code_quality_analyzer.cli analyze --file examples/bad_example.py --model models/code_quality_model.joblib

# JavaScript
python -m code_quality_analyzer.cli analyze --file app.js --model models/code_quality_model.joblib

# Java
python -m code_quality_analyzer.cli analyze --file Main.java --model models/code_quality_model.joblib

# Any supported language (auto-detected by extension)
python -m code_quality_analyzer.cli analyze --file <your-file> --model models/code_quality_model.joblib
```

6. Run the web app:

```powershell
python -m code_quality_analyzer.webapp
```

## Project Structure

- `code_quality_analyzer/` - main package
  - `parser.py` - Multi-language parsing and feature extraction (Python AST, regex-based for others)
  - `detectors.py` - Rule-based detectors and linter integrations for all supported languages
  - `ml_classifier.py` - Model training and prediction helpers
  - `suggestion_engine.py` - Auto-fix suggestions
  - `cli.py` - CLI wrapper with multi-language support
  - `webapp.py` - Flask demo for uploading and analyzing code
- `datasets/` - Small synthetic datasets
- `examples/` - Sample files in various languages
- `tests/` - Unit tests
- `requirements.txt` - Required Python packages

## Multi-Language Analysis Examples

### Python Analysis
```python
from code_quality_analyzer.parser import extract_features_from_file
from code_quality_analyzer.detectors import RuleBasedDetector

features = extract_features_from_file('script.py')
detector = RuleBasedDetector()
issues = detector.detect_all_languages(source_code, 'python')
```

### JavaScript/TypeScript Analysis
```python
features = extract_features_from_file('app.js')
issues = detector.detect_all_languages(source_code, 'javascript')
```

### Java Analysis
```python
features = extract_features_from_file('Main.java')
issues = detector.detect_all_languages(source_code, 'java')
```

Language detection is automatic based on file extension.

## Notes
This project supports comprehensive multi-language analysis. You can extend it with:
- Tree-sitter integration for more precise AST parsing across all languages
- Better ML dataset with language-specific embeddings
- Enhanced auto-fix engine using language-specific AST rewriters
- CI integration for scanning across multi-language repositories
- Custom rule definitions per language

Contributions & improvements are welcome.

## Hosting / Deployment

This repo contains a Dockerfile and `docker-compose.yml` to run the Flask web app behind Gunicorn. The container exposes port 5000.

Build and run locally with Docker:

```powershell
docker build -t code-quality-analyzer:latest .
docker run --rm -p 5000:5000 -v ${PWD}\models:/app/models -e MODEL_PATH=/app/models/code_quality_model.joblib code-quality-analyzer:latest
```

Using Docker Compose:

```powershell
docker-compose up --build
```

Heroku / PaaS (example): create an app, set a BUILDPACK or use the Docker container; the included `Procfile` runs Gunicorn for you.

```powershell
heroku create
git push heroku main
heroku ps:scale web=1
```

Note: Ensure model file `models/code_quality_model.joblib` is included or set the `MODEL_PATH` environment variable pointing to the model artifact.

### Production Deployment with GitHub Container Registry (Recommended)

**Best deployment method** - No size limits, full multi-language support, ML features included.

#### Automatic Deployment with GitHub Actions

The project includes automated CI/CD that builds and publishes Docker images to GitHub Container Registry (GHCR) on every push to main:

1. **GitHub Actions automatically:**
   - Builds multi-architecture Docker image (linux/amd64, linux/arm64)
   - Pushes to `ghcr.io/<YOUR_USERNAME>/code-quality-analyzer:latest`
   - Optionally uploads ML models to S3 (if configured)
   - Uses build cache for faster subsequent builds

2. **Pull and run the pre-built image:**

```powershell
# Pull latest image from GHCR
docker pull ghcr.io/shahinshac/code-quality-analyzer:latest

# Run the container
docker run -d -p 5000:5000 \
  -e MODEL_PATH=/app/models/code_quality_model.joblib \
  ghcr.io/shahinshac/code-quality-analyzer:latest
```

3. **Deploy to any cloud platform:**
   - **Railway**: Connect GitHub repo, auto-deploys from GHCR
   - **Render**: Deploy from Docker registry
   - **Fly.io**: `fly launch` from Dockerfile
   - **Google Cloud Run**: Deploy from container registry
   - **AWS ECS/Fargate**: Use GHCR image
   - **Azure Container Instances**: Pull from GHCR

#### Manual Build and Push (Optional)

```powershell
# Build locally
docker build -t ghcr.io/<YOUR_USERNAME>/code-quality-analyzer:latest .

# Login to GHCR
echo <GITHUB_TOKEN> | docker login ghcr.io -u <YOUR_USERNAME> --password-stdin

# Push to GHCR
docker push ghcr.io/<YOUR_USERNAME>/code-quality-analyzer:latest
```

#### Optional: S3 Model Storage

Configure these GitHub repository secrets/variables to enable S3 model upload:

**Secrets:**
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

**Variables:**
- `AWS_REGION` - AWS region (default: us-east-1)
- `AWS_S3_BUCKET` - S3 bucket name for model storage

The workflow will automatically upload models to S3 and generate presigned URLs for download.

Contributions & improvements are welcome.