# Code Quality Analyzer with AI

A minimal prototype for an AI-powered code quality analyzer. This project is a small, extendable demo that includes:

- AST-based parsing to extract code metrics
- Rule-based detectors for code smells (long functions, unused imports, deep nesting)
 - Rule-based detectors for code smells (long functions, unused imports, deep nesting); includes Python linting (`flake8`, `pylint`) and basic Java heuristics for long methods and deep nesting
- A simple ML classifier using scikit-learn to classify code snippets as "good" or "bad"
- A CLI to analyze files and a small Flask web UI to upload and analyze code
 - A CLI to analyze files and a small Flask web UI to upload and analyze code (includes autofix option using `autopep8`) 
- Sample dataset and unit tests

## Quickstart

1. Create and activate a Python environment (>= 3.9 recommended).
2. Install requirements:

```powershell
pip install -r requirements.txt
```

3. Train a small demo model (optional):

```powershell
python -m code_quality_analyzer.cli train --dataset datasets/synthetic_dataset.csv --model-out models/code_quality_model.joblib
```

4. Analyze a Python file:

```powershell
python -m code_quality_analyzer.cli analyze --file examples/bad_example.py --model models/code_quality_model.joblib
```

5. Run the web app:

```powershell
python -m code_quality_analyzer.webapp
```

## Project Structure

- `code_quality_analyzer/` - main package
  - `parser.py` - AST parsing and feature extraction
  - `detectors.py` - rule-based detectors for code smells
  - `ml_classifier.py` - model training and prediction helpers
  - `suggestion_engine.py` - auto-fix suggestions
  - `cli.py` - CLI wrapper
  - `webapp.py` - Flask demo for uploading and analyzing code
- `datasets/` - small synthetic datasets
- `examples/` - sample Python files
- `tests/` - unit tests
- `requirements.txt` - required Python packages

## Notes
This project is a prototype; you can extend it with:
- More rule checks (pylint/flake8 integration)
 - More rule checks (pylint/flake8 integration) — this prototype includes a basic flake8 integration which will report common issues.
- Better ML dataset and more sophisticated features (token-based embeddings)
- Auto-fix engine that rewrites code (using `ast` and `astor` or `libcst`)
- CI integration for SCAN across repositories

Contributions & improvements are welcome.

## Hosting / Deployment

This repo contains a Dockerfile and a `docker-compose.yml` to run the Flask web app behind Gunicorn. The container exposes port 5000.

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

### Deploying with GHCR and Vercel (Recommended)

1. Build & push your Docker image to GitHub Container Registry (GHCR):

```powershell
docker build -t ghcr.io/<GH_USER>/code-quality-analyzer:latest .
echo <GH_PAT> | docker login ghcr.io -u <GH_USER> --password-stdin
docker push ghcr.io/<GH_USER>/code-quality-analyzer:latest
```

2. Configure Vercel to use the container image:
- In Vercel dashboard, import your project
- Choose 'Deploy from Registry' and set the image `ghcr.io/<GH_USER>/code-quality-analyzer:latest`
- Set `MODEL_URL`, `MODEL_PATH`, `DATABASE_URL` and other secrets as environment variables
> Note: If you added a `vercel.json` file that included a `builds` entry referencing `@vercel/docker`, remove it to let the dashboard use the "Deploy from Registry" registry option. Vercel will otherwise try to use the unsupported builder and fail.

3. Automate publishing images with GitHub Actions (workflow included):
  - There is a GitHub Actions workflow `.github/workflows/docker-publish-ghcr.yml` in this repo that builds and pushes your Docker image on each `main` push. Ensure GitHub Packages is enabled for your account and that `GITHUB_TOKEN` has the appropriate permissions.

4. Optional: Trigger automatic redeploy on Vercel after GHCR publish
- Add the following secrets to your GitHub repository: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
- The workflow will automatically call the Vercel deploy action to trigger a redeploy after image publish.



### Vercel (Docker-based deployment)

Vercel supports building and running containers. We provide a `Dockerfile` combined with `vercel.json` to build with `@vercel/docker`.

Steps:

1. Sign in to Vercel and connect the GitHub repo.
2. Add environment variables under the project settings:
  - `MODEL_URL` (optional) — URL to download the model at startup (e.g., `https://.../code_quality_model.joblib`). If not supplied, mount the model into the container via the `models/` folder (not possible on Vercel in free tiers), or bake the model into the image.
  - `MODEL_PATH` — path where the model will be available (default: `/app/models/code_quality_model.joblib`).
3. Vercel will use the provided `vercel.json` to build the Docker image. The app runs with `gunicorn`, and the `start.sh` script binds to the provided `PORT` environment variable.

Important notes for Vercel:

- Vercel provides ephemeral containers. If you need persistent model storage, host the model on S3/GCS/Azure Blob, and set `MODEL_URL` for the app to download it at startup.
- Alternatively, store the model inside the image, but this requires rebuilding the image on each model update.
- Set `MODEL_URL` under Vercel project > Settings > Environment Variables; the app will download the model during startup.

Contributions & improvements are welcome.