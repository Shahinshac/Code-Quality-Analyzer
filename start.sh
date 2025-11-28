#!/usr/bin/env bash
set -e

# Default model path
MODEL_PATH=${MODEL_PATH:-/app/models/code_quality_model.joblib}
MODEL_URL=${MODEL_URL:-}
PORT=${PORT:-5000}

# Ensure models directory exists
mkdir -p $(dirname "$MODEL_PATH")

# If a model URL is provided and the model path doesn't exist, attempt to download
if [ -n "$MODEL_URL" ] && [ ! -f "$MODEL_PATH" ]; then
  echo "Downloading model from $MODEL_URL to $MODEL_PATH"
  curl -L --silent "$MODEL_URL" -o "$MODEL_PATH" || (echo "Failed to download model"; exit 1)
  echo "Model downloaded"
fi

# Print a small message
if [ -f "$MODEL_PATH" ]; then
  echo "Model found at $MODEL_PATH"
else
  echo "Warning: Model not found at $MODEL_PATH; ML predictions will be disabled"
fi

# Start Gunicorn on the provided port
exec gunicorn code_quality_analyzer.wsgi:app -b 0.0.0.0:$PORT -w 4
