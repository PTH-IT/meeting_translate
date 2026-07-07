FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
COPY backend/app/ ./app/
COPY backend/config.py .
COPY backend/entrypoint.py .

EXPOSE 8000

CMD ["python", "entrypoint.py"]
