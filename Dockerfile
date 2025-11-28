FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV MODEL_PATH=/app/models/code_quality_model.joblib
EXPOSE 5000

# Copy a small start script that ensures the model is present and starts Gunicorn binding to $PORT
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
