FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV BIOMED_HOST=138.68.73.241:8081
ENV DJANGO_SETTINGS_MODULE=MedsRecognition.settings

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]