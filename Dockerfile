# Dockerfile
FROM python:3.10-slim

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set non-sensitive defaults (you can override these at runtime)
ENV BIOMED_HOST=165.232.73.98:8081 \
    DJANGO_SETTINGS_MODULE=MedsRecognition.settings

WORKDIR /app

# Install system dependencies and remove cache to keep the image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY ./MedsRecognition /app/MedsRecognition
COPY manage.py /app/

EXPOSE 8000

# Use Gunicorn to serve your Django application
CMD ["gunicorn", "MedsRecognition.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]