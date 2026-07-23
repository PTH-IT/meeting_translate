FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install --prefer-binary -r requirements.txt

COPY backend/app/ ./app/
COPY backend/config.py .
COPY backend/entrypoint.py .

EXPOSE 8000

CMD ["python", "entrypoint.py"]
