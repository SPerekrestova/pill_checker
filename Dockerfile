FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV BIOMED_HOST=138.68.73.241:8081
ENV DJANGO_SETTINGS_MODULE=MedsRecognition.settings

WORKDIR /app

RUN apt update && \
    apt install -y python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY MedsRecognition /app/
COPY manage.py /app/

EXPOSE 8000

CMD ["gunicorn", "MedsRecognition.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]