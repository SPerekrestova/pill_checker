FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./MedsRecognition /app/MedsRecognition
COPY manage.py /app/

EXPOSE 8000

CMD ["gunicorn", "MedsRecognition.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]